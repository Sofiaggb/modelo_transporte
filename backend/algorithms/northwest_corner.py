# algorithms/northwest_corner.py
from algorithms.balance import balance_transport_problem, is_ficticious_cell
from typing import List, Dict, Any
from algorithms.transport_analysis import analyze_solution, basic_variables_to_dict_list, fix_degeneration
from schemas.schema_transport import BasicVariable
from algorithms.transport_summary import generate_transport_summary
from algorithms.transport_conclusion import generate_final_conclusion


def northwest_corner(supply: List[int], demand: List[int], costs: List[List[float]]) -> dict:
    """
    Método de la Esquina Noroeste con análisis completo
    """
    balanced_data = balance_transport_problem(supply, demand, costs)
    balanced_supply = balanced_data["supply"]
    balanced_demand = balanced_data["demand"]
    balanced_costs = balanced_data["costs"]
    balance_info = balanced_data["balance_info"]
    
    m, n = len(balanced_supply), len(balanced_demand)
    solution = [[0] * n for _ in range(m)]
    remaining_supply = balanced_supply.copy()
    remaining_demand = balanced_demand.copy()
    
    steps = []
    total_cost = 0
    step_count = 0
    basic_vars = []
    
    # Paso 0: Información inicial
    steps.append({
        'step_number': step_count,
        'description': 'Inicio - Problema de Transporte',
        'current_matrix': [row.copy() for row in solution],
        'current_cost': total_cost,
        'explanation': f'Problema: {m} orígenes, {n} destinos. Variables básicas requeridas: {m + n - 1}',
        'basic_variables': []
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
            'basic_variables': []
        })
        step_count += 1
    
    # Algoritmo de Esquina Noroeste
    i, j = 0, 0
    
    while i < m and j < n:
        x = min(remaining_supply[i], remaining_demand[j])
        solution[i][j] = x
        
        # Solo sumar costo si no es celda ficticia
        if not is_ficticious_cell(i, j, balance_info):
            total_cost += x * balanced_costs[i][j]
        
        # Registrar variable básica
        if x > 0 and not is_ficticious_cell(i, j, balance_info):
            basic_vars.append(BasicVariable(
                cell=f"X{i+1}{j+1}",
                value=x,
                cost=balanced_costs[i][j],
                i=i,
                j=j
            ))
        
        step_description = f'Asignar {x} unidades en X{i+1}{j+1}'
        step_explanation = f'Esquina noroeste: min({remaining_supply[i]}, {remaining_demand[j]}) = {x}'
        
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
        
        if remaining_supply[i] == 0:
            i += 1
        else:
            j += 1
        
        step_count += 1

         # ✅ CORREGIR DEGENERACIÓN
    solution, degenerated_cells = fix_degeneration(
        solution, balanced_supply, balanced_demand, balanced_costs, balance_info
    )
    
    # Agregar paso de degeneración si se aplicó
    if degenerated_cells:
        degeneration_step = {
            'step_number': step_count,
            'description': 'Corrección de degeneración',
            'current_matrix': [row.copy() for row in solution],
            'current_cost': total_cost,
            'explanation': f'Se agregaron {len(degenerated_cells)} variables básicas degeneradas (valor 0) para completar m+n-1 = {m+n-1} variables requeridas'
        }
        steps.append(degeneration_step)
        step_count += 1
    
    # Análisis final de la solución
    analysis = analyze_solution(supply, demand, costs, solution, balance_info)

    transport_summary = generate_transport_summary( supply, demand, costs, solution, balance_info, "northwest", degenerated_cells )


    # Generar conclusión final
        # Para Northwest: NO hay soluciones alternativas (siempre es única)
    alternative_solutions = []
    final_conclusion = generate_final_conclusion(
        {
            'main_solution': solution,
            'total_cost': analysis['total_cost'],
            'transport_summary': transport_summary,
            'basic_variables': analysis['basic_variables'],
            'required_basic_variables': analysis['required_basic_variables']
        },
        alternative_solutions,
        supply, demand, costs, balance_info,
        "northwest"
    )

    return {
        'main_solution': solution,
        'total_cost': analysis['total_cost'],
        'steps': steps,
        'balance_info': balance_info,
        'alternative_solutions': [],
        'has_multiple_solutions': False,
        'tie_scenarios': [],
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






# from typing import List
# # algorithms/northwest_corner.py
# from .balance import balance_transport_problem

# def northwest_corner(supply: List[int], demand: List[int], costs: List[List[float]]) -> dict:
#     """
#     Método de la Esquina Noroeste con balanceo automático
#     """
#     # Balancear el problema primero
#     balanced_data = balance_transport_problem(supply, demand, costs)
#     balanced_supply = balanced_data["supply"]
#     balanced_demand = balanced_data["demand"]
#     balanced_costs = balanced_data["costs"]
#     balance_info = balanced_data["balance_info"]
    
#     m, n = len(balanced_supply), len(balanced_demand)
#     solution = [[0] * n for _ in range(m)]
#     remaining_supply = balanced_supply.copy()
#     remaining_demand = balanced_demand.copy()
    
#     steps = []
#     total_cost = 0
#     step_count = 0
    
#     # Paso 0: Mostrar información de balanceo si aplica
#     if balance_info["balanced"]:
#         steps.append({
#             'step_number': 0,
#             'description': 'Balanceo del problema',
#             'current_matrix': [row.copy() for row in solution],
#             'current_cost': total_cost,
#             'explanation': balance_info["explanation"]
#         })
    
#     i, j = 0, 0
    
#     while i < m and j < n:
#         step_count += 1
#         x = min(remaining_supply[i], remaining_demand[j])
        
#         solution[i][j] = x
#         # Solo sumar costo si no es celda ficticia
#         if not is_ficticious_cell(i, j, balance_info):
#             total_cost += x * balanced_costs[i][j]
        
#         steps.append({
#             'step_number': step_count,
#             'description': f'Asignar {x} unidades en posición ({i+1},{j+1})',
#             'current_matrix': [row.copy() for row in solution],
#             'current_cost': total_cost,
#             'explanation': f'Esquina noroeste: min({remaining_supply[i]}, {remaining_demand[j]}) = {x}'
#         })
        
#         remaining_supply[i] -= x
#         remaining_demand[j] -= x
        
#         if remaining_supply[i] == 0:
#             i += 1
#         else:
#             j += 1
    
#     return {
#         'solution': solution,
#         'total_cost': total_cost,
#         'steps': steps,
#         'balance_info': balance_info  # ← Incluir info de balanceo
#     }

# def is_ficticious_cell(i: int, j: int, balance_info: dict) -> bool:
#     """Verifica si una celda es ficticia"""
#     if balance_info["ficticious_row"] == i:
#         return True
#     if balance_info["ficticious_col"] == j:
#         return True
#     return False