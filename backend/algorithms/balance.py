# algorithms/balance.py
from typing import List

def balance_transport_problem(supply: List[int], demand: List[int], costs: List[List[float]]) -> dict:
    """
    Balancea un problema de transporte agregando fila/columna ficticia
    """
    total_supply = sum(supply)
    total_demand = sum(demand)
    
    balanced_supply = supply.copy()
    balanced_demand = demand.copy()
    balanced_costs = [row.copy() for row in costs]
    
    balance_info = {
        "balanced": False,
        "original_supply": supply.copy(),
        "original_demand": demand.copy(),
        "balanced_supply": supply.copy(),
        "balanced_demand": demand.copy(),
        "ficticious_row": None,
        "ficticious_col": None,
        "explanation": "No se requirió balanceo"
    }
    
    # Caso 1: Oferta > Demanda (agregar columna ficticia)
    if total_supply > total_demand:
        difference = total_supply - total_demand
        balanced_demand.append(difference)  # Columna ficticia
        
        # Agregar costos 0 para la nueva columna
        for i in range(len(balanced_costs)):
            balanced_costs[i].append(0)
        
        balance_info.update({
            "balanced": True,
            "balanced_demand": balanced_demand.copy(),
            "ficticious_col": len(balanced_demand) - 1,
            "explanation": f"Oferta ({total_supply}) > Demanda ({total_demand}). Se agregó columna ficticia con demanda {difference} y costos 0"
        })
    
    # Caso 2: Demanda > Oferta (agregar fila ficticia)
    elif total_demand > total_supply:
        difference = total_demand - total_supply
        balanced_supply.append(difference)  # Fila ficticia
        
        # Agregar fila de costos 0
        new_row = [0] * len(balanced_costs[0])
        balanced_costs.append(new_row)
        
        balance_info.update({
            "balanced": True,
            "balanced_supply": balanced_supply.copy(),
            "ficticious_row": len(balanced_supply) - 1,
            "explanation": f"Demanda ({total_demand}) > Oferta ({total_supply}). Se agregó fila ficticia con oferta {difference} y costos 0"
        })
    
    return {
        "supply": balanced_supply,
        "demand": balanced_demand,
        "costs": balanced_costs,
        "balance_info": balance_info
    }


# algorithms/balance_utils.py (crear este archivo)
def is_ficticious_cell(i: int, j: int, balance_info: dict) -> bool:
    """
    Verifica si una celda es ficticia (fila o columna agregada para balanceo)
    
    Args:
        i: Índice de fila
        j: Índice de columna 
        balance_info: Información del balanceo del problema
    
    Returns:
        bool: True si la celda es ficticia
    """
    if not balance_info or not balance_info.get("balanced", False):
        return False
    
    # Verificar si es fila ficticia
    ficticious_row = balance_info.get("ficticious_row")
    if ficticious_row is not None and i == ficticious_row:
        return True
    
    # Verificar si es columna ficticia
    ficticious_col = balance_info.get("ficticious_col") 
    if ficticious_col is not None and j == ficticious_col:
        return True
    
    return False