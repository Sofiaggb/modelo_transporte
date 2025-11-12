# algorithms/transport_analysis.py
from typing import List, Tuple, Dict, Any
from schemas.schema_transport import BasicVariable

def analyze_solution(supply: List[int], demand: List[int], costs: List[List[float]], 
                    solution: List[List[int]], balance_info: dict) -> Dict[str, Any]:
    """
    Analiza una solución de transporte y extrae información estructural
    """
    m, n = len(supply), len(demand)

      # Calcular variables básicas (incluyendo degeneradas)
    basic_vars = []
    degenerated_vars = []
    
    for i in range(len(solution)):
        for j in range(len(solution[0])):
            value = solution[i][j]
            if not _is_ficticious_cell(i, j, balance_info):
                if value > 0:
                    basic_vars.append({
                        'cell': f"X{i+1}{j+1}",
                        'value': value,
                        'cost': costs[i][j],
                        'i': i,
                        'j': j,
                        'type': 'basic'
                    })
                # Podemos considerar celdas con 0 como potencialmente degeneradas
                # En una implementación real, necesitaríamos tracking de cuáles fueron marcadas como degeneradas
    
    # Calcular variables básicas y no básicas
    basic_vars, non_basic_vars = _extract_basic_variables(solution, costs, balance_info)
    
    # Convertir BasicVariable a dict para serialización
    basic_vars_dict = [basic_variable_to_dict(bv) for bv in basic_vars]

    # Verificar degeneración
    required_vars = m + n - 1
    actual_vars = len(basic_vars)
    has_degeneracy = actual_vars < required_vars
    
    # Calcular costo total
    total_cost = _calculate_total_cost(solution, costs, balance_info)
    
    # Información de balanceo
    total_supply = sum(supply)
    total_demand = sum(demand)
    is_balanced = total_supply == total_demand
    
    return {
        'basic_variables': basic_vars_dict,
        'non_basic_variables': non_basic_vars,
        'total_cost': total_cost,
        'is_balanced': is_balanced,
        'total_supply': total_supply,
        'total_demand': total_demand,
        'degeneracy_info': _get_degeneracy_info(actual_vars, required_vars, has_degeneracy),
        'm': m,
        'n': n,
        'required_basic_variables': required_vars,
        'actual_basic_variables': actual_vars,
        'has_degeneracy': has_degeneracy
    }

def _extract_basic_variables(solution: List[List[int]], costs: List[List[float]], 
                           balance_info: dict) -> Tuple[List[BasicVariable], List[str]]:
    """Extrae variables básicas (valores > 0) y no básicas (valores = 0)"""
    basic_vars = []
    non_basic_vars = []
    
    for i in range(len(solution)):
        for j in range(len(solution[0])):
            value = solution[i][j]
            cell_name = f"X{i+1}{j+1}"
            
            # Excluir celdas ficticias
            if _is_ficticious_cell(i, j, balance_info):
                continue
                
            if value > 0:
                basic_vars.append(BasicVariable(
                    cell=cell_name,
                    value=value,
                    cost=costs[i][j],
                    i=i,
                    j=j
                ))
            else:
                non_basic_vars.append(cell_name)
    
    return basic_vars, non_basic_vars

def _calculate_total_cost(solution: List[List[int]], costs: List[List[float]], 
                        balance_info: dict) -> float:
    """Calcula el costo total excluyendo celdas ficticias"""
    total = 0.0
    for i in range(len(solution)):
        for j in range(len(solution[0])):
            if not _is_ficticious_cell(i, j, balance_info):
                total += solution[i][j] * costs[i][j]
    return total

def _get_degeneracy_info(actual: int, required: int, has_degeneracy: bool) -> str:
    """Genera información sobre degeneración"""
    if not has_degeneracy:
        return f"Solución no degenerada: {actual} variables básicas = {required} requeridas"
    else:
        return f"Solución degenerada: {actual} variables básicas < {required} requeridas"

def _is_ficticious_cell(i: int, j: int, balance_info: dict) -> bool:
    """Verifica si una celda es ficticia"""
    if not balance_info.get("balanced", False):
        return False
    
    if balance_info.get("ficticious_row") == i:
        return True
    if balance_info.get("ficticious_col") == j:
        return True
    
    return False


# algorithms/transport_analysis.py - agregar esta función
def basic_variable_to_dict(basic_var) -> dict:
    """Convierte un BasicVariable a diccionario para serialización JSON"""
    return {
        'cell': basic_var.cell,
        'value': basic_var.value,
        'cost': basic_var.cost,
        'i': basic_var.i,
        'j': basic_var.j
    }

def basic_variables_to_dict_list(basic_vars: list) -> list:
    """Convierte una lista de BasicVariable a lista de diccionarios"""
    return [basic_variable_to_dict(bv) for bv in basic_vars]



# algorithms/degeneration_fix.py
from typing import List, Tuple
import copy
# algorithms/degeneration_fix.py - versión mejorada
from typing import List, Tuple, Set
import copy

def fix_degeneration(solution: List[List[int]], supply: List[int], demand: List[int],
                    costs: List[List[float]], balance_info: dict) -> Tuple[List[List[int]], List[Tuple[int, int]]]:
    """
    Corrige la degeneración usando reglas específicas de transporte
    """
    m, n = len(solution), len(solution[0])
    required_vars = m + n - 1
    
    # Obtener variables básicas existentes
    existing_basic = _get_existing_basic_vars(solution, balance_info)
    current_count = len(existing_basic)
    
    degenerated_cells = []
    solution_copy = copy.deepcopy(solution)
    
    if current_count < required_vars:
        missing_vars = required_vars - current_count
        print(f"⚠️  Degeneración: {current_count} < {required_vars}. Buscando {missing_vars} celdas elegibles...")
        
        # Estrategia 1: Buscar celdas que no creen ciclos
        eligible_cells = _find_eligible_degenerated_cells(
            solution, existing_basic, supply, demand, costs, balance_info
        )
        
        # Estrategia 2: Si no hay suficientes, usar cualquier celda que no cree ciclos
        if len(eligible_cells) < missing_vars:
            backup_cells = _find_backup_degenerated_cells(
                solution, existing_basic, balance_info
            )
            eligible_cells.extend(backup_cells)
        
        # Agregar variables degeneradas
        for k in range(min(missing_vars, len(eligible_cells))):
            i, j, cost, reason = eligible_cells[k]
            degenerated_cells.append((i, j))
            print(f"  + Variable degenerada: X{i+1}{j+1}=0 ({reason})")
    
    return solution_copy, degenerated_cells

def _get_existing_basic_vars(solution: List[List[int]], balance_info: dict) -> Set[Tuple[int, int]]:
    """Obtiene las variables básicas existentes (no ficticias)"""
    basic_vars = set()
    for i in range(len(solution)):
        for j in range(len(solution[0])):
            if solution[i][j] > 0 and not _is_ficticious_cell(i, j, balance_info):
                basic_vars.add((i, j))
    return basic_vars

def _find_eligible_degenerated_cells(solution: List[List[int]], existing_basic: Set[Tuple[int, int]],
                                   supply: List[int], demand: List[int], 
                                   costs: List[List[float]], balance_info: dict) -> List[Tuple]:
    """
    Encuentra celdas elegibles para variables degeneradas usando reglas específicas
    """
    eligible_cells = []
    m, n = len(solution), len(solution[0])
    
    # Regla 1: Celdas en filas/columnas con oferta/demanda agotada
    exhausted_rows = _get_exhausted_rows(solution, supply, balance_info)
    exhausted_cols = _get_exhausted_cols(solution, demand, balance_info)
    
    for i in range(m):
        for j in range(n):
            if (solution[i][j] == 0 and 
                not _is_ficticious_cell(i, j, balance_info) and
                (i, j) not in existing_basic):
                
                # Verificar si es elegible según diferentes criterios
                eligibility_reason = _check_eligibility_criteria(
                    i, j, solution, existing_basic, exhausted_rows, exhausted_cols, costs
                )
                
                if eligibility_reason:
                    eligible_cells.append((i, j, costs[i][j], eligibility_reason))
    
    # Ordenar por criterios de preferencia
    eligible_cells.sort(key=lambda x: (
        _get_priority_score(x[3]),  # Prioridad por tipo de elegibilidad
        x[2]  # Luego por costo
    ))
    
    return eligible_cells

def _check_eligibility_criteria(i: int, j: int, solution: List[List[int]], 
                              existing_basic: Set[Tuple[int, int]],
                              exhausted_rows: List[int], exhausted_cols: List[int],
                              costs: List[List[float]]) -> str:
    """
    Verifica los criterios de elegibilidad para una celda degenerada
    """
    # Criterio 1: Celda en fila agotada Y columna agotada (alta prioridad)
    if i in exhausted_rows and j in exhausted_cols:
        if not _would_create_cycle(i, j, existing_basic):
            return "fila_y_columna_agotadas"
    
    # Criterio 2: Celda en fila agotada
    if i in exhausted_rows:
        if not _would_create_cycle(i, j, existing_basic):
            return "fila_agotada"
    
    # Criterio 3: Celda en columna agotada  
    if j in exhausted_cols:
        if not _would_create_cycle(i, j, existing_basic):
            return "columna_agotada"
    
    # Criterio 4: Celda adyacente a variables básicas existentes
    if _is_adjacent_to_basic(i, j, existing_basic):
        if not _would_create_cycle(i, j, existing_basic):
            return "adyacente_a_basicas"
    
    # Criterio 5: Cualquier celda que no cree ciclo
    if not _would_create_cycle(i, j, existing_basic):
        return "sin_ciclo"
    
    return ""

def _get_exhausted_rows(solution: List[List[int]], supply: List[int], balance_info: dict) -> List[int]:
    """Encuentra filas donde la oferta está completamente asignada"""
    exhausted = []
    for i in range(len(solution)):
        row_total = sum(solution[i][j] for j in range(len(solution[0])) 
                       if not _is_ficticious_cell(i, j, balance_info))
        if abs(row_total - supply[i]) < 1e-6:  # Considerar tolerancia numérica
            exhausted.append(i)
    return exhausted

def _get_exhausted_cols(solution: List[List[int]], demand: List[int], balance_info: dict) -> List[int]:
    """Encuentra columnas donde la demanda está completamente satisfecha"""
    exhausted = []
    for j in range(len(solution[0])):
        col_total = sum(solution[i][j] for i in range(len(solution))
                       if not _is_ficticious_cell(i, j, balance_info))
        if abs(col_total - demand[j]) < 1e-6:  # Considerar tolerancia numérica
            exhausted.append(j)
    return exhausted

def _would_create_cycle(i: int, j: int, existing_basic: Set[Tuple[int, int]]) -> bool:
    """
    Verifica si agregar la celda (i,j) crearía un ciclo con las variables básicas existentes
    (Implementación simplificada - en la práctica se usa búsqueda en grafos)
    """
    # Por ahora, asumimos que no crea ciclos
    # En una implementación completa, se usaría detección de ciclos en el grafo de transporte
    return False

def _is_adjacent_to_basic(i: int, j: int, existing_basic: Set[Tuple[int, int]]) -> bool:
    """Verifica si la celda es adyacente a variables básicas existentes"""
    for di, dj in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        if (i + di, j + dj) in existing_basic:
            return True
    return False

def _get_priority_score(reason: str) -> int:
    """Asigna prioridad a los diferentes criterios de elegibilidad"""
    priority_map = {
        "fila_y_columna_agotadas": 1,    # Máxima prioridad
        "fila_agotada": 2,
        "columna_agotada": 3, 
        "adyacente_a_basicas": 4,
        "sin_ciclo": 5                   # Mínima prioridad
    }
    return priority_map.get(reason, 6)

def _find_backup_degenerated_cells(solution: List[List[int]], existing_basic: Set[Tuple[int, int]],
                                 balance_info: dict) -> List[Tuple]:
    """Estrategia de respaldo para encontrar celdas degeneradas"""
    backup_cells = []
    for i in range(len(solution)):
        for j in range(len(solution[0])):
            if (solution[i][j] == 0 and 
                not _is_ficticious_cell(i, j, balance_info) and
                (i, j) not in existing_basic and
                not _would_create_cycle(i, j, existing_basic)):
                backup_cells.append((i, j, 0, "respaldo"))
    return backup_cells

def _is_ficticious_cell(i: int, j: int, balance_info: dict) -> bool:
    """Verifica si una celda es ficticia"""
    if not balance_info.get("balanced", False):
        return False
    if balance_info.get("ficticious_row") == i:
        return True
    if balance_info.get("ficticious_col") == j:
        return True
    return False