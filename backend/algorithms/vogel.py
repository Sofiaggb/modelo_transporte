from typing import List, Dict, Any, Tuple, Optional
import copy
from algorithms.balance import balance_transport_problem
from algorithms.transport_analysis import analyze_solution, basic_variables_to_dict_list, fix_degeneration
from schemas.schema_transport import BasicVariable
from algorithms.transport_summary import generate_transport_summary
from algorithms.transport_conclusion import generate_final_conclusion

def vogel_approximation(supply: List[int], demand: List[int], costs: List[List[float]]) -> dict:
    """
    Método de Vogel con detección EXPLÍCITA de empates en penalizaciones
    """
    balanced_data = balance_transport_problem(supply, demand, costs)
    balanced_supply = balanced_data["supply"]
    balanced_demand = balanced_data["demand"]
    balanced_costs = balanced_data["costs"]
    balance_info = balanced_data["balance_info"]
    
    # Solución principal con detección de empates
    main_solution, main_steps, main_cost, main_basic_vars, all_ties = _solve_vogel_with_explicit_tie_detection(
        balanced_supply, balanced_demand, balanced_costs, balance_info
    )
    print('all_ties >>' , all_ties)
    
    # Buscar soluciones alternativas basadas en empates REALES
    alternative_solutions = _generate_alternative_solutions_from_ties(
        balanced_supply, balanced_demand, balanced_costs, balance_info, all_ties
    )
    
    print('alternative_solutions >>' , alternative_solutions)
    # ✅ CORREGIR DEGENERACIÓN
    main_solution, degenerated_cells = fix_degeneration(
        main_solution, balanced_supply, balanced_demand, balanced_costs, balance_info
    )

    # Análisis final de la solución
    analysis = analyze_solution(supply, demand, costs, main_solution, balance_info)
    
    transport_summary = generate_transport_summary(
        supply, demand, costs, main_solution, balance_info, "vogel", degenerated_cells
    )


    # Generar conclusión final
    final_conclusion = generate_final_conclusion(
        {
            'main_solution': main_solution,
            'total_cost': analysis['total_cost'],
            'transport_summary': transport_summary,
            'basic_variables': analysis['basic_variables'],
            'required_basic_variables': analysis['required_basic_variables']
        },
        alternative_solutions,
        supply, demand, costs, balance_info,
        "vogel"
    )
    
    return {
        'main_solution': main_solution,
        'total_cost': analysis['total_cost'],
        'steps': main_steps,
        'balance_info': balance_info,
        'alternative_solutions': alternative_solutions,
        'has_multiple_solutions': len(alternative_solutions) > 0,
        'all_ties_detected': all_ties,
        # Información de análisis
        'basic_variables': analysis['basic_variables'],
        'non_basic_variables': analysis['non_basic_variables'],
        'is_balanced': analysis['is_balanced'],
        'total_supply': analysis['total_supply'],
        'total_demand': analysis['total_demand'],
        'degeneracy_info': analysis['degeneracy_info'],
        'm': analysis['m'],
        'n': analysis['n'],
        'required_basic_variables': analysis['required_basic_variables'],
        'actual_basic_variables': analysis['actual_basic_variables'],
        'has_degeneracy': analysis['has_degeneracy'],
        'transport_summary': transport_summary,
        'final_conclusion': final_conclusion
    }

def _solve_vogel_with_explicit_tie_detection(supply: List[int], demand: List[int], costs: List[List[float]],
                                            balance_info: dict) -> tuple:
    """Resuelve Vogel con detección EXPLÍCITA de empates"""
    m, n = len(supply), len(demand)
    solution = [[0] * n for _ in range(m)]
    remaining_supply = supply.copy()
    remaining_demand = demand.copy()
    costs_copy = copy.deepcopy(costs)
    
    steps = []
    total_cost = 0
    step_count = 0
    basic_vars = []
    all_ties = []  # Todos los empates detectados
    
    # Paso 0: Información inicial
    steps.append({
        'step_number': step_count,
        'description': 'Inicio - Método de Aproximación de Vogel',
        'current_matrix': [row.copy() for row in solution],
        'current_cost': total_cost,
        'explanation': f'Problema: {m} orígenes, {n} destinos. Variables básicas requeridas: {m + n - 1}',
        'basic_variables': basic_variables_to_dict_list(basic_vars),
        'assignment': None
    })
    step_count += 1

    
    
    while sum(remaining_supply) > 0 and sum(remaining_demand) > 0:
        # Calcular penalizaciones CORRECTAMENTE
        row_penalties, row_penalties_info = _calculate_row_penalties_detailed(remaining_supply, remaining_demand, costs_copy)
        col_penalties, col_penalties_info = _calculate_col_penalties_detailed(remaining_supply, remaining_demand, costs_copy)
        
        # Encontrar máxima penalización
        max_row_pen = max([p for p in row_penalties if p >= 0], default=-1)
        max_col_pen = max([p for p in col_penalties if p >= 0], default=-1)
        
        # DETECTAR EMPATES EN PENALIZACIONES MÁXIMAS
        row_ties = [i for i, p in enumerate(row_penalties) if p == max_row_pen and p > 0]
        col_ties = [j for j, p in enumerate(col_penalties) if p == max_col_pen and p > 0]
        
        # Determinar dirección (fila o columna)
        use_row = max_row_pen >= max_col_pen
        direction = "fila" if use_row else "columna"
        max_penalty = max_row_pen if use_row else max_col_pen
        
        # REGISTRAR EMPATES SI LOS HAY
        current_step_ties = []

        print(f"[Paso {step_count}] Penalizaciones fila: {row_penalties}, col: {col_penalties}")


        # Registrar todos los empates detectados, no solo de la dirección elegida
        if len(row_ties) > 1:
            all_ties.append({
                'step': step_count,
                'type': 'penalty_tie',
                'ties': row_ties.copy(),
                'penalty_value': max_row_pen,
                'direction': 'fila',
                'description': f"Empate en penalización de fila: {max_row_pen} en filas {[r+1 for r in row_ties]}"
            })

        if len(col_ties) > 1:
            all_ties.append({
                'step': step_count,
                'type': 'penalty_tie',
                'ties': col_ties.copy(),
                'penalty_value': max_col_pen,
                'direction': 'columna',
                'description': f"Empate en penalización de columna: {max_col_pen} en columnas {[c+1 for c in col_ties]}"
            })

        
        # SELECCIONAR ELEMENTO (usando primera opción por defecto)
        if use_row:
            selected_index = row_ties[0] if row_ties else -1
            if selected_index == -1:
                break
                
            # Encontrar columna con menor costo en esa fila
            available_cols = [j for j in range(n) if remaining_demand[j] > 0 and costs_copy[selected_index][j] < float('inf')]
            if not available_cols:
                break
                
            min_cost = min([costs_copy[selected_index][j] for j in available_cols])
            candidate_cols = [j for j in available_cols if costs_copy[selected_index][j] == min_cost]
            
            # DETECTAR EMPATE EN COSTOS MÍNIMOS
            if len(candidate_cols) > 1:
                tie_info = {
                    'step': step_count,
                    'type': 'min_cost_tie',
                    'ties': candidate_cols.copy(),
                    'cost_value': min_cost,
                    'direction': 'columna',
                    'row': selected_index,
                    'description': f"Empate en costo mínimo: {min_cost} en columnas {[c+1 for c in candidate_cols]} de fila {selected_index+1}"
                }
                current_step_ties.append(tie_info)
                all_ties.append(tie_info)
            
            selected_col = candidate_cols[0]
            i, j = selected_index, selected_col
            
            # Información detallada para explicación
            penalty_info = row_penalties_info[selected_index]
            tie_reason = f"Penalización fila {max_row_pen} (≥ columna {max_col_pen}). {penalty_info}. Mínimo costo: {min_cost}"
            
        else:
            selected_index = col_ties[0] if col_ties else -1
            if selected_index == -1:
                break
                
            # Encontrar fila con menor costo en esa columna
            available_rows = [i for i in range(m) if remaining_supply[i] > 0 and costs_copy[i][selected_index] < float('inf')]
            if not available_rows:
                break
                
            min_cost = min([costs_copy[i][selected_index] for i in available_rows])
            candidate_rows = [i for i in available_rows if costs_copy[i][selected_index] == min_cost]
            
            # DETECTAR EMPATE EN COSTOS MÍNIMOS
            if len(candidate_rows) > 1:
                tie_info = {
                    'step': step_count,
                    'type': 'min_cost_tie',
                    'ties': candidate_rows.copy(),
                    'cost_value': min_cost,
                    'direction': 'fila',
                    'col': selected_index,
                    'description': f"Empate en costo mínimo: {min_cost} en filas {[r+1 for r in candidate_rows]} de columna {selected_index+1}"
                }
                current_step_ties.append(tie_info)
                all_ties.append(tie_info)
            
            selected_row = candidate_rows[0]
            i, j = selected_row, selected_index
            
            # Información detallada para explicación
            penalty_info = col_penalties_info[selected_index]
            tie_reason = f"Penalización columna {max_col_pen} (> fila {max_row_pen}). {penalty_info}. Mínimo costo: {min_cost}"
        
        # ASIGNACIÓN
        x = min(remaining_supply[i], remaining_demand[j])
        solution[i][j] = x
        
        # Solo sumar costo si no es celda ficticia
        if not _is_ficticious_cell(i, j, balance_info):
            total_cost += x * costs[i][j]
        
        # Registrar variable básica si no es ficticia
        if x > 0 and not _is_ficticious_cell(i, j, balance_info):
            basic_vars.append(BasicVariable(
                cell=f"X{i+1}{j+1}",
                value=x,
                cost=costs[i][j],
                i=i,
                j=j
            ))
        
        step_description = f'Asignar {x} unidades en X{i+1}{j+1}'
        step_explanation = (f'Penalización máxima: {max_penalty} ({direction}). '
                          f'Asignación: min({remaining_supply[i]}, {remaining_demand[j]}) = {x}. '
                          f'{tie_reason}')
        
        # Agregar información de empates si los hay
        if current_step_ties:
            tie_descriptions = [tie['description'] for tie in current_step_ties]
            step_explanation += f" | EMPATES: {'; '.join(tie_descriptions)}"
        
        steps.append({
            'step_number': step_count,
            'description': step_description,
            'current_matrix': [row.copy() for row in solution],
            'current_cost': total_cost,
            'explanation': step_explanation,
            'basic_variables': basic_variables_to_dict_list(basic_vars),
            'assignment': f"X{i+1}{j+1}"
        })



        # Detectar caso especial de empate real (para rutas alternativas)
        if current_step_ties and remaining_supply[i] == remaining_demand[j]:
            for tie_case in current_step_ties:
                if tie_case['type'] in ('penalty_tie', 'min_cost_tie'):
                    alt_ties = tie_case['ties']
                    if len(alt_ties) > 1:
                        for alt in alt_ties[1:]:
                            alt_solution = copy.deepcopy(solution)
                            alt_supply = remaining_supply.copy()
                            alt_demand = remaining_demand.copy()
                            alt_costs = copy.deepcopy(costs_copy)
                            
                            # Determinar coordenadas alternativas según la dirección del empate
                            if tie_case['direction'] == 'fila':
                                alt_i, alt_j = i, alt
                            else:
                                alt_i, alt_j = alt, j
                            
                            alt_x = min(alt_supply[alt_i], alt_demand[alt_j])
                            alt_solution[alt_i][alt_j] = alt_x
                            alt_total_cost = total_cost + alt_x * costs[alt_i][alt_j]
                            
                            # Registrar la rama alternativa
                            all_ties.append({
                                'step': step_count,
                                'type': 'real_branch',
                                'chosen_cell': f"X{i+1}{j+1}",
                                'alternative_cell': f"X{alt_i+1}{alt_j+1}",
                                'alt_solution_snapshot': alt_solution,
                                'alt_total_cost': alt_total_cost,
                                'description': f"Alternativa por empate entre X{i+1}{j+1} y X{alt_i+1}{alt_j+1} (oferta = demanda)"
                            })





        
        # Actualizar oferta y demanda
        remaining_supply[i] -= x
        remaining_demand[j] -= x
        
        # Actualizar matriz de costos
        if remaining_supply[i] == 0:
            for col in range(n):
                costs_copy[i][col] = float('inf')
        if remaining_demand[j] == 0:
            for row in range(m):
                costs_copy[row][j] = float('inf')
        
        step_count += 1
    
    # Paso final
    steps.append({
        'step_number': step_count,
        'description': 'Solución final de Vogel',
        'current_matrix': [row.copy() for row in solution],
        'current_cost': total_cost,
        'explanation': f'Solución básica factible inicial obtenida. Costo total: {total_cost}',
        'basic_variables': basic_variables_to_dict_list(basic_vars),
        'assignment': None
    })
    
    return solution, steps, total_cost, basic_vars, all_ties









def _calculate_row_penalties_detailed(remaining_supply: List[int], remaining_demand: List[int], 
                                    costs: List[List[float]]) -> Tuple[List[float], List[str]]:
    """Calcula penalizaciones por fila con información detallada"""
    m = len(remaining_supply)
    penalties = []
    penalties_info = []
    
    for i in range(m):
        if remaining_supply[i] > 0:
            # Obtener costos válidos de la fila
            valid_costs = []
            for j in range(len(remaining_demand)):
                if remaining_demand[j] > 0 and costs[i][j] < float('inf'):
                    valid_costs.append((costs[i][j], j))
            
            if len(valid_costs) >= 2:
                # Ordenar por costo y tomar los dos menores
                sorted_costs = sorted(valid_costs, key=lambda x: x[0])
                min1_cost, min1_col = sorted_costs[0]
                min2_cost, min2_col = sorted_costs[1]
                penalty = min2_cost - min1_cost
                penalties.append(penalty)
                penalties_info.append(f"Fila {i+1}: min1=X{i+1}{min1_col+1}({min1_cost}), min2=X{i+1}{min2_col+1}({min2_cost}), penalización={penalty}")
            elif len(valid_costs) == 1:
                min_cost, min_col = valid_costs[0]
                penalties.append(min_cost)
                penalties_info.append(f"Fila {i+1}: único costo X{i+1}{min_col+1}({min_cost})")
            else:
                penalties.append(-1)
                penalties_info.append(f"Fila {i+1}: sin celdas disponibles")
        else:
            penalties.append(-1)
            penalties_info.append(f"Fila {i+1}: sin oferta")
    
    return penalties, penalties_info

def _calculate_col_penalties_detailed(remaining_supply: List[int], remaining_demand: List[int],
                                    costs: List[List[float]]) -> Tuple[List[float], List[str]]:
    """Calcula penalizaciones por columna con información detallada"""
    n = len(remaining_demand)
    penalties = []
    penalties_info = []
    
    for j in range(n):
        if remaining_demand[j] > 0:
            # Obtener costos válidos de la columna
            valid_costs = []
            for i in range(len(remaining_supply)):
                if remaining_supply[i] > 0 and costs[i][j] < float('inf'):
                    valid_costs.append((costs[i][j], i))
            
            if len(valid_costs) >= 2:
                # Ordenar por costo y tomar los dos menores
                sorted_costs = sorted(valid_costs, key=lambda x: x[0])
                min1_cost, min1_row = sorted_costs[0]
                min2_cost, min2_row = sorted_costs[1]
                penalty = min2_cost - min1_cost
                penalties.append(penalty)
                penalties_info.append(f"Columna {j+1}: min1=X{min1_row+1}{j+1}({min1_cost}), min2=X{min2_row+1}{j+1}({min2_cost}), penalización={penalty}")
            elif len(valid_costs) == 1:
                min_cost, min_row = valid_costs[0]
                penalties.append(min_cost)
                penalties_info.append(f"Columna {j+1}: único costo X{min_row+1}{j+1}({min_cost})")
            else:
                penalties.append(-1)
                penalties_info.append(f"Columna {j+1}: sin celdas disponibles")
        else:
            penalties.append(-1)
            penalties_info.append(f"Columna {j+1}: sin demanda")
    
    return penalties, penalties_info





def _generate_alternative_solutions_from_ties(supply, demand, costs, balance_info, all_ties):
    """Genera soluciones alternativas REALES forzando elecciones diferentes"""
    alternative_solutions = []
    if not all_ties:
        return []

    print(f"Analizando {len(all_ties)} empates para generar alternativas...")
    
    # Obtener solución principal para comparación
    main_solution = _get_main_solution_from_ties(supply, demand, costs, balance_info)
    
    for tie in all_ties:
        if tie['type'] in ('penalty_tie', 'min_cost_tie') and len(tie['ties']) > 1:
            print(f"Procesando empate: {tie['description']}")
            
            for alt_choice in tie['ties'][1:]:  # Probar todas las alternativas excepto la primera
                print(f"  Probando alternativa: {alt_choice}")
                
                # Resolver forzando la elección alternativa
                alt_result = _solve_with_forced_choice(
                    supply, demand, costs, balance_info, 
                    tie['step'], tie, alt_choice
                )
                
                if alt_result and alt_result['solution_matrix']:
                    # Verificar que sea diferente a la solución principal
                    is_different = _is_solution_different(
                        alt_result['solution_matrix'], 
                        main_solution
                    )
                    
                    if is_different:
                        # Analizar la solución alternativa
                        analysis = analyze_solution(supply, demand, costs, alt_result['solution_matrix'], balance_info)
                        
                        # Corregir degeneración si es necesario
                        fixed_solution, degenerated_cells = fix_degeneration(
                            alt_result['solution_matrix'], supply, demand, costs, balance_info
                        )
                        
                        # Generar summary
                        alt_summary = generate_transport_summary(
                            supply, demand, costs, fixed_solution, 
                            balance_info, "vogel", degenerated_cells
                        )

                        tie_break_reason = (
                            f"Alternativa por empate en paso {tie['step']}: "
                            f"{tie['description']} -> Elegida opción {alt_choice+1}"
                        )

                        # Crear solución alternativa completa con todos los campos requeridos
                        alternative_solution = {
                            "solution_matrix": fixed_solution,
                            "total_cost": alt_result['total_cost'],
                            "steps": alt_result.get('steps', []),  # Campo requerido
                            "tie_break_reason": tie_break_reason,
                            "transport_summary": alt_summary,
                            "basic_variables": analysis['basic_variables'],
                            "non_basic_variables": analysis['non_basic_variables'],
                            "is_balanced": analysis['is_balanced'],
                            "total_supply": analysis['total_supply'],
                            "total_demand": analysis['total_demand'],
                            "degeneracy_info": analysis['degeneracy_info'],
                            "m": analysis['m'],
                            "n": analysis['n'],
                            "required_basic_variables": analysis['required_basic_variables'],
                            "actual_basic_variables": analysis['actual_basic_variables'],
                            "has_degeneracy": analysis['has_degeneracy']
                        }
                        
                        alternative_solutions.append(alternative_solution)
                        print(f"  ✅ Alternativa encontrada con costo: {alt_result['total_cost']}")
                    else:
                        print(f"  ❌ Alternativa idéntica a la principal")
                else:
                    print(f"  ❌ No se pudo generar solución alternativa")

    print(f"Se generaron {len(alternative_solutions)} soluciones alternativas")
    return alternative_solutions



def _solve_with_forced_choice(supply, demand, costs, balance_info, target_step, tie, forced_choice):
    """Resuelve Vogel forzando una elección específica en el paso objetivo"""
    try:
        m, n = len(supply), len(demand)
        solution = [[0] * n for _ in range(m)]
        remaining_supply = supply.copy()
        remaining_demand = demand.copy()
        costs_copy = copy.deepcopy(costs)
        
        # Usar un diccionario mutable para el costo total
        state = {'total_cost': 0}
        step_count = 0
        steps = []
        basic_vars = []
        
        # Paso inicial
        steps.append({
            'step_number': step_count,
            'description': 'Inicio - Método de Aproximación de Vogel (Alternativa)',
            'current_matrix': [row.copy() for row in solution],
            'current_cost': state['total_cost'],
            'explanation': f'Alternativa por empate: {tie["description"]}',
            'basic_variables': basic_variables_to_dict_list(basic_vars),
            'assignment': None
        })
        step_count += 1
        
        # Avanzar hasta el paso anterior al objetivo
        while (sum(remaining_supply) > 0 and sum(remaining_demand) > 0 and 
               step_count < target_step):
            assignment_made = _make_standard_vogel_assignment_with_steps(
                remaining_supply, remaining_demand, costs_copy, 
                solution, state, balance_info, costs,
                steps, step_count, basic_vars
            )
            if assignment_made:
                step_count += 1
            else:
                break
        
        # En el paso objetivo, forzar la elección alternativa
        if step_count == target_step and sum(remaining_supply) > 0 and sum(remaining_demand) > 0:
            if tie['type'] == 'penalty_tie':
                if tie['direction'] == 'fila':
                    i = forced_choice
                    available_cols = [j for j in range(n) if remaining_demand[j] > 0 and costs_copy[i][j] < float('inf')]
                    if available_cols:
                        min_cost = min([costs_copy[i][j] for j in available_cols])
                        candidate_cols = [j for j in available_cols if costs_copy[i][j] == min_cost]
                        j = candidate_cols[0]
                    else:
                        return None
                else:
                    j = forced_choice
                    available_rows = [i for i in range(m) if remaining_supply[i] > 0 and costs_copy[i][j] < float('inf')]
                    if available_rows:
                        min_cost = min([costs_copy[i][j] for i in available_rows])
                        candidate_rows = [i for i in available_rows if costs_copy[i][j] == min_cost]
                        i = candidate_rows[0]
                    else:
                        return None
            
            elif tie['type'] == 'min_cost_tie':
                if tie['direction'] == 'columna':
                    i = tie['row']
                    j = forced_choice
                else:
                    j = tie['col']
                    i = forced_choice
            
            # Aplicar asignación forzada
            x = min(remaining_supply[i], remaining_demand[j])
            solution[i][j] = x
            
            if not _is_ficticious_cell(i, j, balance_info):
                state['total_cost'] += x * costs[i][j]
            
            if x > 0 and not _is_ficticious_cell(i, j, balance_info):
                basic_vars.append(BasicVariable(
                    cell=f"X{i+1}{j+1}",
                    value=x,
                    cost=costs[i][j],
                    i=i,
                    j=j
                ))
            
            # Registrar el paso forzado
            step_description = f'Asignar {x} unidades en X{i+1}{j+1} (Alternativa forzada)'
            step_explanation = f'Alternativa por empate: {tie["description"]}. Asignación: min({remaining_supply[i]}, {remaining_demand[j]}) = {x}'
            
            steps.append({
                'step_number': step_count,
                'description': step_description,
                'current_matrix': [row.copy() for row in solution],
                'current_cost': state['total_cost'],
                'explanation': step_explanation,
                'basic_variables': basic_variables_to_dict_list(basic_vars),
                'assignment': f"X{i+1}{j+1}"
            })
            
            remaining_supply[i] -= x
            remaining_demand[j] -= x
            
            # Actualizar matriz de costos
            if remaining_supply[i] == 0:
                for col in range(n):
                    costs_copy[i][col] = float('inf')
            if remaining_demand[j] == 0:
                for row in range(m):
                    costs_copy[row][j] = float('inf')
            
            step_count += 1
            
            # Continuar con el resto normalmente
            while sum(remaining_supply) > 0 and sum(remaining_demand) > 0:
                assignment_made = _make_standard_vogel_assignment_with_steps(
                    remaining_supply, remaining_demand, costs_copy, 
                    solution, state, balance_info, costs,
                    steps, step_count, basic_vars
                )
                if assignment_made:
                    step_count += 1
                else:
                    break
            
            # Paso final
            steps.append({
                'step_number': step_count,
                'description': 'Solución final alternativa de Vogel',
                'current_matrix': [row.copy() for row in solution],
                'current_cost': state['total_cost'],
                'explanation': f'Solución alternativa obtenida. Costo total: {state["total_cost"]}',
                'basic_variables': basic_variables_to_dict_list(basic_vars),
                'assignment': None
            })
            
            # Recalcular el costo final para asegurar consistencia
            final_cost = 0
            for i in range(m):
                for j in range(n):
                    if solution[i][j] > 0 and not _is_ficticious_cell(i, j, balance_info):
                        final_cost += solution[i][j] * costs[i][j]
            
            return {
                'solution_matrix': solution,
                'total_cost': final_cost,
                'steps': steps,
                'basic_variables': basic_vars
            }
        
        return None
        
    except Exception as e:
        print(f"Error en solución forzada: {e}")
        import traceback
        traceback.print_exc()
        return None

def _make_standard_vogel_assignment_with_steps(remaining_supply, remaining_demand, costs_copy, 
                                             solution, state, balance_info, original_costs,
                                             steps, step_count, basic_vars):
    """Realiza una asignación estándar de Vogel con registro de pasos"""
    m, n = len(remaining_supply), len(remaining_demand)
    
    # Calcular penalizaciones básicas
    row_penalties = _calculate_simple_row_penalties(remaining_supply, remaining_demand, costs_copy)
    col_penalties = _calculate_simple_col_penalties(remaining_supply, remaining_demand, costs_copy)
    
    max_row_pen = max([p for p in row_penalties if p >= 0], default=-1)
    max_col_pen = max([p for p in col_penalties if p >= 0], default=-1)
    
    if max_row_pen == -1 and max_col_pen == -1:
        return False
    
    use_row = max_row_pen >= max_col_pen
    
    if use_row:
        row_ties = [i for i, p in enumerate(row_penalties) if p == max_row_pen and p > 0]
        if not row_ties:
            return False
        i = row_ties[0]
        available_cols = [j for j in range(n) if remaining_demand[j] > 0 and costs_copy[i][j] < float('inf')]
        if not available_cols:
            return False
        min_cost = min([costs_copy[i][j] for j in available_cols])
        candidate_cols = [j for j in available_cols if costs_copy[i][j] == min_cost]
        j = candidate_cols[0]
        direction = "fila"
        penalty_value = max_row_pen
    else:
        col_ties = [j for j, p in enumerate(col_penalties) if p == max_col_pen and p > 0]
        if not col_ties:
            return False
        j = col_ties[0]
        available_rows = [i for i in range(m) if remaining_supply[i] > 0 and costs_copy[i][j] < float('inf')]
        if not available_rows:
            return False
        min_cost = min([costs_copy[i][j] for i in available_rows])
        candidate_rows = [i for i in available_rows if costs_copy[i][j] == min_cost]
        i = candidate_rows[0]
        direction = "columna"
        penalty_value = max_col_pen
    
    x = min(remaining_supply[i], remaining_demand[j])
    solution[i][j] = x
    
    if not _is_ficticious_cell(i, j, balance_info):
        state['total_cost'] += x * original_costs[i][j]
    
    if x > 0 and not _is_ficticious_cell(i, j, balance_info):
        basic_vars.append(BasicVariable(
            cell=f"X{i+1}{j+1}",
            value=x,
            cost=original_costs[i][j],
            i=i,
            j=j
        ))
    
    # Registrar el paso
    step_description = f'Asignar {x} unidades en X{i+1}{j+1}'
    step_explanation = f'Penalización máxima: {penalty_value} ({direction}). Asignación: min({remaining_supply[i]}, {remaining_demand[j]}) = {x}'
    
    steps.append({
        'step_number': step_count,
        'description': step_description,
        'current_matrix': [row.copy() for row in solution],
        'current_cost': state['total_cost'],
        'explanation': step_explanation,
        'basic_variables': basic_variables_to_dict_list(basic_vars),
        'assignment': f"X{i+1}{j+1}"
    })
    
    remaining_supply[i] -= x
    remaining_demand[j] -= x
    
    if remaining_supply[i] == 0:
        for col in range(n):
            costs_copy[i][col] = float('inf')
    if remaining_demand[j] == 0:
        for row in range(m):
            costs_copy[row][j] = float('inf')
    
    return True


def _calculate_simple_row_penalties(remaining_supply, remaining_demand, costs):
    """Calcula penalizaciones simples por fila"""
    m = len(remaining_supply)
    penalties = []
    
    for i in range(m):
        if remaining_supply[i] > 0:
            valid_costs = [costs[i][j] for j in range(len(remaining_demand)) 
                          if remaining_demand[j] > 0 and costs[i][j] < float('inf')]
            if len(valid_costs) >= 2:
                sorted_costs = sorted(valid_costs)
                penalties.append(sorted_costs[1] - sorted_costs[0])
            elif len(valid_costs) == 1:
                penalties.append(valid_costs[0])
            else:
                penalties.append(-1)
        else:
            penalties.append(-1)
    
    return penalties


def _calculate_simple_col_penalties(remaining_supply, remaining_demand, costs):
    """Calcula penalizaciones simples por columna"""
    n = len(remaining_demand)
    penalties = []
    
    for j in range(n):
        if remaining_demand[j] > 0:
            valid_costs = [costs[i][j] for i in range(len(remaining_supply)) 
                          if remaining_supply[i] > 0 and costs[i][j] < float('inf')]
            if len(valid_costs) >= 2:
                sorted_costs = sorted(valid_costs)
                penalties.append(sorted_costs[1] - sorted_costs[0])
            elif len(valid_costs) == 1:
                penalties.append(valid_costs[0])
            else:
                penalties.append(-1)
        else:
            penalties.append(-1)
    
    return penalties

def _is_solution_different(sol1, sol2):
    """Verifica si dos soluciones son diferentes"""
    if not sol2:
        return True
    
    for i in range(len(sol1)):
        for j in range(len(sol1[0])):
            if sol1[i][j] != sol2[i][j]:
                return True
    return False

def _get_main_solution_from_ties(supply, demand, costs, balance_info):
    """Obtiene la solución principal para comparación"""
    main_solution, _, _, _, _ = _solve_vogel_with_explicit_tie_detection(
        supply, demand, costs, balance_info
    )
    return main_solution

def _is_ficticious_cell(i: int, j: int, balance_info: dict) -> bool:
    """Verifica si una celda es ficticia"""
    if not balance_info.get("balanced", False):
        return False
    
    if balance_info.get("ficticious_row") == i:
        return True
    if balance_info.get("ficticious_col") == j:
        return True
    
    return False


# def _generate_alternative_solutions_from_ties(supply, demand, costs, balance_info, all_ties):
#     alternative_solutions = []
#     if not all_ties:
#         return []

#     for tie in all_ties:
#         if tie['type'] in ('penalty_tie', 'min_cost_tie') and len(tie['ties']) > 1:
#             for alt_choice in tie['ties'][1:]:
#                 alt_solution, alt_steps, alt_cost, alt_vars, _ = _solve_vogel_with_explicit_tie_detection(
#                     supply, demand, costs, balance_info
#                 )

#                 alt_summary = generate_transport_summary(
#                     supply,
#                     demand,
#                     costs,
#                     alt_solution,
#                     balance_info,
#                     "vogel",
#                     []
#                 )

#                 # ✅ Agregamos el campo faltante
#                 tie_break_reason = (
#                     f"Alternativa generada por empate en {tie['direction']} "
#                     f"con penalización/costo {tie.get('penalty_value', tie.get('cost_value', 'N/A'))} "
#                     f"en paso {tie['step']}. "
#                     f"Descripción: {tie.get('description', 'Sin descripción')}"
#                 )

#                 alternative_solutions.append({
#                     "steps": alt_steps,
#                     "transport_summary": alt_summary,
#                     "solution_matrix": alt_solution,
#                     "total_cost": alt_cost,
#                     "basic_variables": alt_vars,
#                     "has_degeneracy": len(alt_vars) < (len(supply) + len(demand) - 1),
#                     "tie_break_reason": tie_break_reason  # ← AQUÍ SE AGREGA
#                 })
#     return alternative_solutions


# def _is_ficticious_cell(i: int, j: int, balance_info: dict) -> bool:
#     """Verifica si una celda es ficticia"""
#     if not balance_info.get("balanced", False):
#         return False
    
#     if balance_info.get("ficticious_row") == i:
#         return True
#     if balance_info.get("ficticious_col") == j:
#         return True
    
#     return False


# def _generate_alternative_solutions_from_ties(
#     supply: List[int],
#     demand: List[int],
#     costs: List[List[float]],
#     balance_info: dict,
#     all_ties: List[Dict]
# ) -> List[Dict]:
#     """Genera soluciones alternativas basadas en empates detectados (penalización, costo o ramas reales)"""
#     alternative_solutions = []

#     if not all_ties:
#         return []

#     # Agrupar empates por paso
#     ties_by_step = {}
#     for tie in all_ties:
#         step = tie['step']
#         if step not in ties_by_step:
#             ties_by_step[step] = []
#         ties_by_step[step].append(tie)

#     # Analizar cada grupo de empates
#     for step, ties in ties_by_step.items():
#         for tie in ties:
#             # ✅ Caso 1: Empates en penalización o costo mínimo
#             if tie['type'] in ('penalty_tie', 'min_cost_tie') and len(tie['ties']) > 1:
#                 for alt_choice in tie['ties'][1:]:  # probar las alternativas desde la segunda opción
#                     alt_solution = _solve_with_alternative_choice(
#                         supply, demand, costs, balance_info, step, tie, alt_choice
#                     )
#                     if alt_solution and alt_solution not in alternative_solutions:
#                         alternative_solutions.append(alt_solution)

#             # ✅ Caso 2: Empate real (cuando oferta = demanda)
#             elif tie['type'] == 'real_branch':
#                 alt_solution = {
#                     'step': tie['step'],
#                     'chosen_cell': tie['chosen_cell'],
#                     'alternative_cell': tie['alternative_cell'],
#                     'matrix': tie['alt_solution_snapshot'],
#                     'total_cost': tie['alt_total_cost'],
#                     'description': tie['description']
#                 }
#                 # Evitar duplicados
#                 if alt_solution not in alternative_solutions:
#                     alternative_solutions.append(alt_solution)

#     return alternative_solutions





