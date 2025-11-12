from typing import List, Dict, Any, Tuple
import copy
from algorithms.balance import balance_transport_problem
from algorithms.transport_analysis import analyze_solution, basic_variables_to_dict_list, fix_degeneration
from schemas.schema_transport import BasicVariable
from algorithms.transport_summary import generate_transport_summary
from algorithms.transport_conclusion import generate_final_conclusion

def min_cost_method(supply: List[int], demand: List[int], costs: List[List[float]]) -> dict:
    """
    Método del Costo Mínimo con análisis completo y múltiples soluciones
    """
    balanced_data = balance_transport_problem(supply, demand, costs)
    balanced_supply = balanced_data["supply"]
    balanced_demand = balanced_data["demand"]
    balanced_costs = balanced_data["costs"]
    balance_info = balanced_data["balance_info"]
    
    m, n = len(balanced_supply), len(balanced_demand)
    
    # Solución principal
    main_solution, main_steps, main_cost, main_basic_vars = _solve_min_cost(
        balanced_supply, balanced_demand, balanced_costs, balance_info, "primera_ocurrencia"
    )

    # ✅ CORREGIR DEGENERACIÓN en la solución principal
    main_solution, degenerated_cells = fix_degeneration(
        main_solution, balanced_supply, balanced_demand, balanced_costs, balance_info
    )
    
      # Buscar soluciones alternativas
    alternative_solutions = _find_alternative_min_cost_solutions(
        balanced_supply, balanced_demand, balanced_costs, balance_info
    )
    
    # También corregir degeneración en soluciones alternativas
    corrected_alternatives = []
    for alt_solution in alternative_solutions:
        corrected_alt, _ = fix_degeneration(
            alt_solution['solution_matrix'], balanced_supply, balanced_demand, balanced_costs, balance_info
        )
        alt_solution['solution_matrix'] = corrected_alt
        corrected_alternatives.append(alt_solution)
    
  
    # Análisis final de la solución
    analysis = analyze_solution(supply, demand, costs, main_solution, balance_info)

    transport_summary = generate_transport_summary( supply, demand, costs, main_solution, balance_info, "min_cost", degenerated_cells )

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
        "min_cost"
    )

    return {
        'main_solution': main_solution,
        'total_cost': analysis['total_cost'],
        'steps': main_steps,
        'balance_info': balance_info,
        'alternative_solutions': alternative_solutions,
        'has_multiple_solutions': len(alternative_solutions) > 0,
        'tie_scenarios': _get_tie_scenarios(balanced_costs),
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

def _solve_min_cost(supply: List[int], demand: List[int], costs: List[List[float]], 
                   balance_info: dict, tie_break_strategy: str) -> tuple:
    """Resuelve usando una estrategia específica para desempates"""
    m, n = len(supply), len(demand)
    solution = [[0] * n for _ in range(m)]
    remaining_supply = supply.copy()
    remaining_demand = demand.copy()
    costs_copy = copy.deepcopy(costs)
    
    steps = []
    total_cost = 0
    step_count = 0
    basic_vars = []
    
    # Paso 0: Información inicial
    steps.append({
        'step_number': step_count,
        'description': 'Inicio - Método del Costo Mínimo',
        'current_matrix': [row.copy() for row in solution],
        'current_cost': total_cost,
        'explanation': f'Problema: {m} orígenes, {n} destinos. Variables básicas requeridas: {m + n - 1}',
        'basic_variables': [],
        'assignment': None
    })
    step_count += 1
    
    # Paso de balanceo si es necesario
    if balance_info["balanced"]:
        steps.append({
            'step_number': step_count,
            'description': 'Balanceo del problema',
            'current_matrix': [row.copy() for row in solution],
            'current_cost': total_cost,
            'explanation': balance_info["explanation"],
            'basic_variables': [],
            'assignment': None
        })
        step_count += 1
    
    while sum(remaining_supply) > 0 and sum(remaining_demand) > 0:
        # Encontrar todas las celdas con costo mínimo
        min_cost_val = float('inf')
        candidate_cells = []
        
        for i in range(m):
            for j in range(n):
                if (remaining_supply[i] > 0 and remaining_demand[j] > 0 and 
                    costs_copy[i][j] < float('inf')):
                    if costs_copy[i][j] < min_cost_val:
                        min_cost_val = costs_copy[i][j]
                        candidate_cells = [(i, j)]
                    elif costs_copy[i][j] == min_cost_val:
                        candidate_cells.append((i, j))
        
        if not candidate_cells:
            break
            
        # Aplicar estrategia de desempate
        if tie_break_strategy == "primera_ocurrencia":
            i, j = candidate_cells[0]
            tie_reason = f"Se eligió la primera celda con costo mínimo {min_cost_val}"
        elif tie_break_strategy == "mayor_asignacion":
            # Elegir la celda que permite mayor asignación
            max_assign = 0
            best_cell = candidate_cells[0]
            for cell_i, cell_j in candidate_cells:
                assign = min(remaining_supply[cell_i], remaining_demand[cell_j])
                if assign > max_assign:
                    max_assign = assign
                    best_cell = (cell_i, cell_j)
            i, j = best_cell
            tie_reason = f"Se eligió celda que permite mayor asignación ({max_assign} unidades)"
        else:  # menor_indice
            i, j = sorted(candidate_cells)[0]
            tie_reason = f"Se eligió celda con menores índices (fila {i+1}, columna {j+1})"
        
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
        step_explanation = (f'Costo mínimo encontrado: {min_cost_val}. '
                          f'Asignación: min({remaining_supply[i]}, {remaining_demand[j]}) = {x}. '
                          f'{tie_reason}')
        
        steps.append({
            'step_number': step_count,
            'description': step_description,
            'current_matrix': [row.copy() for row in solution],
            'current_cost': total_cost,
            'explanation': step_explanation,
            'basic_variables': basic_variables_to_dict_list(basic_vars),
            'assignment': f"X{i+1}{j+1}"
        })
        
        remaining_supply[i] -= x
        remaining_demand[j] -= x
        
        # Marcar celdas como usadas
        if remaining_supply[i] == 0:
            for col in range(n):
                costs_copy[i][col] = float('inf')
        if remaining_demand[j] == 0:
            for row in range(m):
                costs_copy[row][j] = float('inf')
        
        step_count += 1
    
    # Paso final: Resumen de la solución
    steps.append({
        'step_number': step_count,
        'description': 'Solución final del Costo Mínimo',
        'current_matrix': [row.copy() for row in solution],
        'current_cost': total_cost,
        'explanation': f'Solución básica factible inicial obtenida. Costo total: {total_cost}',
        'basic_variables': basic_variables_to_dict_list(basic_vars),
        'assignment': None
    })
    
    return solution, steps, total_cost, basic_vars

# def _find_alternative_min_cost_solutions(supply: List[int], demand: List[int], 
#                                        costs: List[List[float]], balance_info: dict) -> List[Dict]:
#     """Encuentra soluciones alternativas usando diferentes estrategias de desempate"""
#     alternative_solutions = []
    
#     # Diferentes estrategias de desempate
#     strategies = [
#         ("mayor_asignacion", "Priorizar celdas que permiten mayor asignación"),
#         ("menor_indice", "Priorizar celdas con menores índices (fila, columna)")
#     ]
    
#     for strategy, description in strategies:
#         alt_solution, alt_steps, alt_cost, alt_basic_vars = _solve_min_cost(
#             supply, demand, costs, balance_info, strategy
#         )
        
#         # Análisis de la solución alternativa
#         alt_analysis = analyze_solution(supply, demand, costs, alt_solution, balance_info)

#           # Generar resumen textual para la solución alternativa
#         alt_transport_summary = generate_transport_summary(
#             supply, demand, costs, alt_solution, balance_info, f"min_cost_{strategy}"
#         )
        
#          # Convertir steps para que basic_variables sean dict
#         converted_steps = []
#         for step in alt_steps:
#             converted_step = step.copy()
#             if 'basic_variables' in step and step['basic_variables']:
#                 if isinstance(step['basic_variables'][0], BasicVariable):
#                     converted_step['basic_variables'] = basic_variables_to_dict_list(step['basic_variables'])
#             converted_steps.append(converted_step)

#         alternative_solutions.append({
#             'solution_matrix': alt_solution,
#             'total_cost': alt_cost,
#             'steps': converted_steps,
#             'tie_break_reason': description,
#             # Información de análisis para solución alternativa
#             'basic_variables': alt_analysis['basic_variables'],
#             'non_basic_variables': alt_analysis['non_basic_variables'],
#             'is_balanced': alt_analysis['is_balanced'],
#             'total_supply': alt_analysis['total_supply'],
#             'total_demand': alt_analysis['total_demand'],
#             'degeneracy_info': alt_analysis['degeneracy_info'],
#             'm': alt_analysis['m'],
#             'n': alt_analysis['n'],
#             'required_basic_variables': alt_analysis['required_basic_variables'],
#             'actual_basic_variables': alt_analysis['actual_basic_variables'],
#             'has_degeneracy': alt_analysis['has_degeneracy'],
#             #  Resumen textual para solución alternativa
#             'transport_summary': alt_transport_summary
#         })
    
#     return alternative_solutions







def _find_alternative_min_cost_solutions(supply: List[int], demand: List[int], 
                                       costs: List[List[float]], balance_info: dict) -> List[Dict]:
    """Encuentra soluciones alternativas basadas en empates reales de costos mínimos"""
    alternative_solutions = []
    
    # Primero, resolver una vez para detectar todos los empates
    _, _, _, _, all_ties = _solve_min_cost_with_tie_detection(
        supply, demand, costs, balance_info
    )
    
    print(f"Empates detectados: {len(all_ties)}")
    
    # Generar soluciones alternativas para cada empate detectado
    for tie in all_ties:
        print(f"Procesando empate: {tie['description']}")
        
        # Las alternativas son todas las celdas excepto la primera
        for alt_choice in tie['ties'][1:]:
            print(f"  Probando alternativa: {alt_choice}")
            
            # Resolver forzando la elección alternativa
            alt_result = _solve_min_cost_with_forced_choice(
                supply, demand, costs, balance_info, tie['step'], tie, alt_choice
            )
            
            if alt_result and alt_result['solution_matrix']:
                # Verificar que sea diferente a la solución principal
                main_solution = _get_main_min_cost_solution(supply, demand, costs, balance_info)
                is_different = _is_solution_different(
                    alt_result['solution_matrix'], main_solution
                )
                
                if is_different:
                    # Analizar la solución alternativa
                    alt_analysis = analyze_solution(supply, demand, costs, alt_result['solution_matrix'], balance_info)
                    
                    # Corregir degeneración
                    fixed_solution, degenerated_cells = fix_degeneration(
                        alt_result['solution_matrix'], supply, demand, costs, balance_info
                    )
                    
                    # Generar summary
                    alt_transport_summary = generate_transport_summary(
                        supply, demand, costs, fixed_solution, balance_info, "min_cost"
                    )
                    
                    # CORREGIDO: Mostrar la celda alternativa correctamente
                    tie_break_reason = (
                        f"Alternativa por empate en paso {tie['step']}: "
                        f"{tie['description']} -> Elegida celda X{alt_choice[0]+1}{alt_choice[1]+1}"
                    )
                    
                    alternative_solutions.append({
                        'solution_matrix': fixed_solution,
                        'total_cost': alt_result['total_cost'],
                        'steps': alt_result['steps'],
                        'tie_break_reason': tie_break_reason,
                        'transport_summary': alt_transport_summary,
                        'basic_variables': alt_analysis['basic_variables'],
                        'non_basic_variables': alt_analysis['non_basic_variables'],
                        'is_balanced': alt_analysis['is_balanced'],
                        'total_supply': alt_analysis['total_supply'],
                        'total_demand': alt_analysis['total_demand'],
                        'degeneracy_info': alt_analysis['degeneracy_info'],
                        'm': alt_analysis['m'],
                        'n': alt_analysis['n'],
                        'required_basic_variables': alt_analysis['required_basic_variables'],
                        'actual_basic_variables': alt_analysis['actual_basic_variables'],
                        'has_degeneracy': alt_analysis['has_degeneracy']
                    })
                    print(f"  ✅ Alternativa encontrada con costo: {alt_result['total_cost']}")
                else:
                    print(f"  ❌ Alternativa idéntica a la principal")
            else:
                print(f"  ❌ No se pudo generar solución alternativa")
    
    return alternative_solutions

def _solve_min_cost_with_tie_detection(supply: List[int], demand: List[int], costs: List[List[float]], 
                                      balance_info: dict) -> tuple:
    """Resuelve el método del costo mínimo detectando todos los empates"""
    m, n = len(supply), len(demand)
    solution = [[0] * n for _ in range(m)]
    remaining_supply = supply.copy()
    remaining_demand = demand.copy()
    costs_copy = copy.deepcopy(costs)
    
    steps = []
    total_cost = 0
    step_count = 0
    basic_vars = []
    all_ties = []
    
    # Paso inicial
    steps.append({
        'step_number': step_count,
        'description': 'Inicio - Método del Costo Mínimo',
        'current_matrix': [row.copy() for row in solution],
        'current_cost': total_cost,
        'explanation': f'Problema: {m} orígenes, {n} destinos. Variables básicas requeridas: {m + n - 1}',
        'basic_variables': [],
        'assignment': None
    })
    step_count += 1
    
    while sum(remaining_supply) > 0 and sum(remaining_demand) > 0:
        # Encontrar todas las celdas con costo mínimo
        min_cost_val = float('inf')
        candidate_cells = []
        
        for i in range(m):
            for j in range(n):
                if (remaining_supply[i] > 0 and remaining_demand[j] > 0 and 
                    costs_copy[i][j] < float('inf')):
                    if costs_copy[i][j] < min_cost_val:
                        min_cost_val = costs_copy[i][j]
                        candidate_cells = [(i, j)]
                    elif costs_copy[i][j] == min_cost_val:
                        candidate_cells.append((i, j))
        
        if not candidate_cells:
            break
        
        # DETECTAR EMPATE
        if len(candidate_cells) > 1:
            tie_info = {
                'step': step_count,
                'type': 'min_cost_tie',
                'ties': candidate_cells.copy(),
                'cost_value': min_cost_val,
                'description': f"Empate en costo mínimo {min_cost_val} en {len(candidate_cells)} celdas: {['X'+str(c[0]+1)+str(c[1]+1) for c in candidate_cells]}"
            }
            all_ties.append(tie_info)
            print(f"[Paso {step_count}] Empate detectado: {tie_info['description']}")
        
        # Elegir la primera celda (estrategia por defecto)
        i, j = candidate_cells[0]
        
        x = min(remaining_supply[i], remaining_demand[j])
        solution[i][j] = x
        
        if not _is_ficticious_cell(i, j, balance_info):
            total_cost += x * costs[i][j]
        
        if x > 0 and not _is_ficticious_cell(i, j, balance_info):
            basic_vars.append(BasicVariable(
                cell=f"X{i+1}{j+1}",
                value=x,
                cost=costs[i][j],
                i=i,
                j=j
            ))
        
        step_description = f'Asignar {x} unidades en X{i+1}{j+1}'
        step_explanation = (f'Costo mínimo encontrado: {min_cost_val}. '
                          f'Asignación: min({remaining_supply[i]}, {remaining_demand[j]}) = {x}. '
                          f'Se eligió la primera celda con costo mínimo {min_cost_val}')
        
        if len(candidate_cells) > 1:
            step_explanation += f" | EMPATE: {len(candidate_cells)} opciones disponibles"
        
        steps.append({
            'step_number': step_count,
            'description': step_description,
            'current_matrix': [row.copy() for row in solution],
            'current_cost': total_cost,
            'explanation': step_explanation,
            'basic_variables': basic_variables_to_dict_list(basic_vars),
            'assignment': f"X{i+1}{j+1}"
        })
        
        remaining_supply[i] -= x
        remaining_demand[j] -= x
        
        # Marcar celdas como usadas
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
        'description': 'Solución final del Costo Mínimo',
        'current_matrix': [row.copy() for row in solution],
        'current_cost': total_cost,
        'explanation': f'Solución básica factible inicial obtenida. Costo total: {total_cost}',
        'basic_variables': basic_variables_to_dict_list(basic_vars),
        'assignment': None
    })
    
    return solution, steps, total_cost, basic_vars, all_ties

def _solve_min_cost_with_forced_choice(supply, demand, costs, balance_info, target_step, tie, forced_choice):
    """Resuelve forzando una elección específica en el paso objetivo"""
    try:
        m, n = len(supply), len(demand)
        solution = [[0] * n for _ in range(m)]
        remaining_supply = supply.copy()
        remaining_demand = demand.copy()
        costs_copy = copy.deepcopy(costs)
        
        state = {'total_cost': 0}
        step_count = 0
        steps = []
        basic_vars = []
        
        # Paso inicial
        steps.append({
            'step_number': step_count,
            'description': 'Inicio - Método del Costo Mínimo (Alternativa)',
            'current_matrix': [row.copy() for row in solution],
            'current_cost': state['total_cost'],
            'explanation': f'Alternativa por empate: {tie["description"]}',
            'basic_variables': [],
            'assignment': None
        })
        step_count += 1
        
        # Avanzar hasta el paso anterior al objetivo
        while (sum(remaining_supply) > 0 and sum(remaining_demand) > 0 and 
               step_count < target_step):
            assignment_made = _make_min_cost_assignment_with_steps(
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
            i, j = forced_choice  # forced_choice es una tupla (i, j)
            
            # Verificar que la celda alternativa sea válida
            if (remaining_supply[i] > 0 and remaining_demand[j] > 0 and 
                costs_copy[i][j] < float('inf')):
                
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
                    assignment_made = _make_min_cost_assignment_with_steps(
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
                    'description': 'Solución final alternativa del Costo Mínimo',
                    'current_matrix': [row.copy() for row in solution],
                    'current_cost': state['total_cost'],
                    'explanation': f'Solución alternativa obtenida. Costo total: {state["total_cost"]}',
                    'basic_variables': basic_variables_to_dict_list(basic_vars),
                    'assignment': None
                })
                
                # Recalcular costo final para consistencia
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

# Las funciones _make_min_cost_assignment_with_steps, _get_main_min_cost_solution, 
# _is_solution_different y _is_ficticious_cell se mantienen igual


def _make_min_cost_assignment_with_steps(remaining_supply, remaining_demand, costs_copy, 
                                       solution, state, balance_info, original_costs,
                                       steps, step_count, basic_vars):
    """Realiza una asignación del costo mínimo con registro de pasos"""
    m, n = len(remaining_supply), len(remaining_demand)
    
    # Encontrar celda con costo mínimo
    min_cost_val = float('inf')
    candidate_cells = []
    
    for i in range(m):
        for j in range(n):
            if (remaining_supply[i] > 0 and remaining_demand[j] > 0 and 
                costs_copy[i][j] < float('inf')):
                if costs_copy[i][j] < min_cost_val:
                    min_cost_val = costs_copy[i][j]
                    candidate_cells = [(i, j)]
                elif costs_copy[i][j] == min_cost_val:
                    candidate_cells.append((i, j))
    
    if not candidate_cells:
        return False
    
    # Elegir la primera celda
    i, j = candidate_cells[0]
    
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
    step_explanation = f'Costo mínimo encontrado: {min_cost_val}. Asignación: min({remaining_supply[i]}, {remaining_demand[j]}) = {x}'
    
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

def _get_main_min_cost_solution(supply, demand, costs, balance_info):
    """Obtiene la solución principal para comparación"""
    main_solution, _, _, _, _ = _solve_min_cost_with_tie_detection(
        supply, demand, costs, balance_info
    )
    return main_solution

def _is_solution_different(sol1, sol2):
    """Verifica si dos soluciones son diferentes"""
    if not sol2:
        return True
    
    for i in range(len(sol1)):
        for j in range(len(sol1[0])):
            if sol1[i][j] != sol2[i][j]:
                return True
    return False












def _get_tie_scenarios(costs: List[List[float]]) -> List[str]:
    """Identifica escenarios de empate en la matriz de costos"""
    tie_scenarios = []
    
    # Buscar costos repetidos por fila
    for i in range(len(costs)):
        row = [cost for cost in costs[i] if cost < float('inf')]
        unique_costs = set()
        repeated_costs = set()
        
        for cost in row:
            if cost in unique_costs:
                repeated_costs.add(cost)
            else:
                unique_costs.add(cost)
        
        for cost in repeated_costs:
            count = row.count(cost)
            if count > 1:
                tie_scenarios.append(f"Fila {i+1}: {count} celdas con costo {cost}")
    
    # Buscar costos repetidos por columna
    for j in range(len(costs[0])):
        col = [costs[i][j] for i in range(len(costs)) if costs[i][j] < float('inf')]
        unique_costs = set()
        repeated_costs = set()
        
        for cost in col:
            if cost in unique_costs:
                repeated_costs.add(cost)
            else:
                unique_costs.add(cost)
        
        for cost in repeated_costs:
            count = col.count(cost)
            if count > 1:
                tie_scenarios.append(f"Columna {j+1}: {count} celdas con costo {cost}")
    
    # Buscar costos globales repetidos
    all_costs = [cost for row in costs for cost in row if cost < float('inf')]
    cost_counts = {}
    for cost in all_costs:
        cost_counts[cost] = cost_counts.get(cost, 0) + 1
    
    for cost, count in cost_counts.items():
        if count > 2:  # Si aparece en más de 2 celdas
            tie_scenarios.append(f"Costo {cost} aparece en {count} celdas diferentes")
    
    return tie_scenarios

def _is_ficticious_cell(i: int, j: int, balance_info: dict) -> bool:
    """Verifica si una celda es ficticia"""
    if not balance_info.get("balanced", False):
        return False
    
    if balance_info.get("ficticious_row") == i:
        return True
    if balance_info.get("ficticious_col") == j:
        return True
    
    return False

