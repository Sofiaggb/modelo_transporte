# algorithms/transport_summary.py
from typing import List, Dict, Any, Tuple
from algorithms.transport_analysis import analyze_solution

# algorithms/transport_summary.py - función actualizada
def generate_transport_summary(supply: List[int], demand: List[int], 
                             costs: List[List[float]], solution: List[List[int]],
                             balance_info: dict, method: str, 
                             degenerated_cells: List[Tuple[int, int]] = None) -> Dict[str, Any]:
    """
    Genera un resumen textual del problema de transporte INCLUYENDO variables degeneradas
    """
    
    if degenerated_cells is None:
        degenerated_cells = []
    
    m, n = len(supply), len(demand)
    
    # Calcular variables básicas REALES (incluyendo degeneradas)
    basic_vars_list, degenerated_vars_list = _get_all_basic_variables(
        solution, costs, balance_info, degenerated_cells
    )
    
    # 1. Variables básicas: m + n - 1 = x
    basic_vars_count = f"m + n - 1 = {m} + {n} - 1 = {m + n - 1}"
    
    # 2. Lista de variables básicas CON degeneradas
    all_basic_vars_str = _generate_basic_variables_list_with_degenerated(
        basic_vars_list, degenerated_vars_list
    )
    
    # 3. Cálculo del costo total (excluyendo degeneradas)
    total_cost_calc = _generate_total_cost_calculation(solution, costs, balance_info)
    
    # 4. Información de degeneración actualizada
    total_basic_vars = len(basic_vars_list) + len(degenerated_vars_list)
    degeneracy_text = _generate_degeneracy_text_updated(
        total_basic_vars, m + n - 1, len(degenerated_vars_list)
    )
    
    # 5. Pasos en texto simple
    # step_by_step_text = _generate_step_by_step_text(solution, costs, method, degenerated_cells)
    step_by_step_text = _generate_step_by_step_text(solution, costs, method)
    
    return {
        'basic_variables_count': basic_vars_count,
        'basic_variables_list': all_basic_vars_str,
        'total_cost_calculation': total_cost_calc,
        'degeneracy_info': degeneracy_text,
        'step_by_step_text': step_by_step_text,
        'method_used': method,
        'has_degeneration': len(degenerated_vars_list) > 0,
        'degenerated_variables_count': len(degenerated_vars_list)
    }

def _get_all_basic_variables(solution: List[List[int]], costs: List[List[float]],
                           balance_info: dict, degenerated_cells: List[Tuple[int, int]]) -> tuple:
    """Obtiene TODAS las variables básicas (normales + degeneradas)"""
    basic_vars = []      # Variables con valor > 0
    degenerated_vars = [] # Variables degeneradas (valor 0)
    
    # Variables normales (valor > 0)
    for i in range(len(solution)):
        for j in range(len(solution[0])):
            value = solution[i][j]
            if value > 0 and not _is_ficticious_cell(i, j, balance_info):
                basic_vars.append({
                    'cell': f"X{i+1}{j+1}",
                    'value': value,
                    'cost': costs[i][j],
                    'i': i,
                    'j': j,
                    'type': 'basic'
                })
    
    # Variables degeneradas
    for i, j in degenerated_cells:
        degenerated_vars.append({
            'cell': f"X{i+1}{j+1}",
            'value': 0,
            'cost': costs[i][j],
            'i': i,
            'j': j,
            'type': 'degenerated'
        })
    
    return basic_vars, degenerated_vars

def _generate_basic_variables_list_with_degenerated(basic_vars: list, degenerated_vars: list) -> str:
    """Genera la lista de variables básicas INCLUYENDO las degeneradas en formato A1, B2, etc."""
    all_vars = []
    
    # Variables normales
    for var in basic_vars:
        row_char = chr(65 + var['i'])  # 65 = 'A', 66 = 'B', etc.
        all_vars.append(f"{row_char}{var['j']+1}={var['value']}")
    
    # Variables degeneradas (con indicador)
    for var in degenerated_vars:
        row_char = chr(65 + var['i'])  # 65 = 'A', 66 = 'B', etc.
        all_vars.append(f"{row_char}{var['j']+1}=0 ⚠️")
    
    return ", ".join(all_vars)

def _generate_degeneracy_text_updated(actual_vars: int, required_vars: int, degenerated_count: int) -> str:
    """Genera texto sobre degeneración actualizado"""
    if actual_vars < required_vars:
        return f"Solución degenerada: {actual_vars} variables básicas < {required_vars} requeridas"
    elif degenerated_count > 0:
        return f"Solución corregida: {actual_vars} variables básicas = {required_vars} requeridas ({degenerated_count} degeneradas)"
    else:
        return f"Solución no degenerada: {actual_vars} variables básicas = {required_vars} requeridas"
    


def _generate_total_cost_calculation(solution: List[List[int]], costs: List[List[float]],
                                   balance_info: dict) -> str:
    """Genera el cálculo del costo total en formato: 2×10 + 0×5 + 1×15 + ... = 340"""
    calculation_parts = []
    total_cost = 0
    
    for i in range(len(solution)):
        for j in range(len(solution[0])):
            value = solution[i][j]
            # Solo incluir celdas no ficticias con valor > 0
            if value > 0 and not _is_ficticious_cell(i, j, balance_info):
                cost = costs[i][j]
                calculation_parts.append(f"{cost}×{value}")
                total_cost += cost * value
    
    calculation_str = " + ".join(calculation_parts)
    return f"{calculation_str} = {total_cost}"

def _generate_degeneracy_text(analysis: Dict[str, Any]) -> str:
    """Genera texto sobre degeneración"""
    required = analysis['required_basic_variables']
    actual = analysis['actual_basic_variables']
    
    if analysis['has_degeneracy']:
        return f"Solución degenerada: {actual} variables básicas < {required} requeridas"
    else:
        return f"Solución no degenerada: {actual} variables básicas = {required} requeridas"

def _generate_step_by_step_text(solution: List[List[int]], costs: List[List[float]],
                              method: str) -> List[str]:
    """Genera pasos en texto simple (puedes personalizar según el método)"""
    steps = []
    
    if method == "northwest":
        steps = _generate_northwest_steps_text(solution, costs)
    elif method == "min_cost":
        steps = _generate_min_cost_steps_text(solution, costs)
    elif method == "vogel":
        steps = _generate_vogel_steps_text(solution, costs)
    
    return steps

def _generate_northwest_steps_text(solution: List[List[int]], costs: List[List[float]]) -> List[str]:
    """Genera pasos para el método de la esquina noroeste"""
    steps = []
    m, n = len(solution), len(solution[0])
    
    steps.append("MÉTODO DE LA ESQUINA NOROESTE")
    steps.append("────────────────────────────")
    
    i, j = 0, 0
    step_num = 1
    
    while i < m and j < n:
        value = solution[i][j]
        if value > 0:
            row_char = chr(65 + i)
            steps.append(f"Paso {step_num}: Asignar {value} unidades en {row_char}{j+1}")
            step_num += 1
        
        # Simular movimiento de esquina noroeste
        if i < m - 1 and solution[i][j] > 0:
            i += 1
        else:
            j += 1
    
    return steps

def _generate_min_cost_steps_text(solution: List[List[int]], costs: List[List[float]]) -> List[str]:
    """Genera pasos para el método del costo mínimo"""
    steps = []
    
    steps.append("MÉTODO DEL COSTO MÍNIMO")
    steps.append("──────────────────────")
    
    # Encontrar asignaciones en orden de costo (simplificado)
    assignments = []
    for i in range(len(solution)):
        for j in range(len(solution[0])):
            if solution[i][j] > 0:
                assignments.append((i, j, solution[i][j], costs[i][j]))
    
    # Ordenar por costo
    assignments.sort(key=lambda x: x[3])
    
    for step_num, (i, j, value, cost) in enumerate(assignments, 1):
        row_char = chr(65 + i)
        steps.append(f"Paso {step_num}: Asignar {value} unidades en {row_char}{j+1} (costo: {cost})")
    
    return steps

def _generate_vogel_steps_text(solution: List[List[int]], costs: List[List[float]]) -> List[str]:
    """Genera pasos para el método de Vogel"""
    steps = []
    
    steps.append("MÉTODO DE APROXIMACIÓN DE VOGEL")
    steps.append("──────────────────────────────")
    
    # Simulación simplificada de pasos de Vogel
    assignments = []
    for i in range(len(solution)):
        for j in range(len(solution[0])):
            if solution[i][j] > 0:
                assignments.append((i, j, solution[i][j]))
    
    for step_num, (i, j, value) in enumerate(assignments, 1):
        row_char = chr(65 + i)
        steps.append(f"Paso {step_num}: Asignar {value} unidades en {row_char}{j+1}")
    
    return steps

def _is_ficticious_cell(i: int, j: int, balance_info: dict) -> bool:
    """Verifica si una celda es ficticia"""
    if not balance_info.get("balanced", False):
        return False
    
    if balance_info.get("ficticious_row") == i:
        return True
    if balance_info.get("ficticious_col") == j:
        return True
    
    return False