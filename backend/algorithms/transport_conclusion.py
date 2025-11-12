# algorithms/final_conclusion.py - VERSIÓN COMPLETA CORREGIDA
from typing import List, Dict, Any

def generate_final_conclusion(main_solution: Dict, alternative_solutions: List[Dict], 
                            supply: List[int], demand: List[int], 
                            costs: List[List[float]], balance_info: dict,
                            method: str) -> Dict[str, Any]:
    """
    Genera la conclusión final analizando la solución más económica
    """
    # Determinar el tipo de método
    is_northwest = (method.lower() == "northwest")
    
    # Encontrar la mejor solución
    if not alternative_solutions:
        best_solution = main_solution
        best_index = 0
        cost_difference = 0
        has_alternatives = False
    else:
        all_solutions = [main_solution] + alternative_solutions
        best_solution = min(all_solutions, key=lambda x: x['total_cost'])
        best_index = all_solutions.index(best_solution)
        has_alternatives = True
        
        if len(all_solutions) > 1:
            sorted_solutions = sorted(all_solutions, key=lambda x: x['total_cost'])
            cost_difference = sorted_solutions[1]['total_cost'] - best_solution['total_cost']
        else:
            cost_difference = 0
    
    # Generar interpretación
    interpretation = _generate_interpretation(best_solution, supply, demand, is_northwest, balance_info, method)
    
    # Generar desglose de costo
    cost_breakdown = _generate_cost_breakdown(best_solution, costs, balance_info, is_northwest, method)
    
    # Generar recomendaciones
    recommendations = _generate_recommendations(best_solution, cost_difference, has_alternatives, is_northwest, method)
    
    # Nota de eficiencia
    efficiency_note = _generate_efficiency_note(best_solution, cost_difference, is_northwest, method)
    
    return {
        'best_solution_index': best_index,
        'best_solution_cost': best_solution['total_cost'],
        'is_main_solution_best': best_index == 0,
        'cost_difference': cost_difference,
        'interpretation': interpretation,
        'cost_breakdown': cost_breakdown,
        'recommendations': recommendations,
        'efficiency_note': efficiency_note,
        'method_used': method,
        'has_alternative_solutions': has_alternatives
    }





def _generate_interpretation(solution: Dict, supply: List[int], demand: List[int], 
                           is_northwest: bool, balance_info: dict, method: str) -> str:
    """Genera una explicación en formato párrafo continuo como conclusión"""
    basic_vars = solution.get('transport_summary', {}).get('basic_variables_list', '')
    total_cost = solution.get('total_cost', 0)
    
    # Parsear variables básicas
    vars_list = basic_vars.split(", ")
    real_assignments = []
    ficticious_assignments = []
    
    for var in vars_list:
        if '=' in var:
            var_name, value = var.split('=')
            clean_value = value.replace(' ⚠️', '')
            row_char = var_name[0]
            col_num = var_name[1:]
            
            is_ficticious = _is_ficticious_route(row_char, col_num, balance_info)
            
            if is_ficticious:
                ficticious_assignments.append(f"{var_name}={clean_value}")
            else:
                real_assignments.append(f"{var_name}={clean_value}")
    
    # Construir el párrafo explicativo
    interpretation = "La solución aproximada "
    
    if method.lower() == "northwest":
        interpretation += "mediante el método de la Esquina Noroeste "
    elif method.lower() == "min_cost":
        interpretation += "mediante el método del Costo Mínimo "
    elif method.lower() == "vogel":
        interpretation += "mediante el método de Aproximación de Vogel "
    
    interpretation += f"establece las siguientes asignaciones: "
    
    # Describir las asignaciones reales
    if real_assignments:
        interpretation += "las rutas de transporte son "
        assignments_desc = []
        for assignment in real_assignments:
            var_name, value = assignment.split('=')
            row_char = var_name[0]
            col_num = var_name[1:]
            
            origin_name = _get_origin_name(row_char, supply, False)
            dest_name = _get_destination_name(col_num, demand, False)
            
            assignments_desc.append(f"{var_name}={value} unidades de {origin_name} a {dest_name}")
        
        interpretation += ", ".join(assignments_desc)
        interpretation += ". "
    
    # Describir asignaciones ficticias si existen
    if ficticious_assignments:
        interpretation += "Además, se incluyen rutas ficticias para balancear el problema: "
        fict_desc = []
        for assignment in ficticious_assignments:
            var_name, value = assignment.split('=')
            fict_desc.append(f"{var_name}={value} unidades")
        interpretation += ", ".join(fict_desc)
        interpretation += ". "
    
    # Calcular unidades totales reales (excluyendo ficticias)
    total_real_units = 0
    for assignment in real_assignments:
        _, value = assignment.split('=')
        total_real_units += int(value)
    
    interpretation += f"El transporte total comprende {total_real_units} unidades reales "
    
    if ficticious_assignments:
        total_fict_units = sum(int(assign.split('=')[1]) for assign in ficticious_assignments)
        interpretation += f"más {total_fict_units} unidades ficticias para balanceo. "
    
    # Información de costos
    interpretation += f"El costo total de transporte asciende a {total_cost} unidades monetarias, "
    interpretation += f"calculado como la suma de los productos de las unidades transportadas por sus respectivos costos en cada ruta seleccionada."
    
    # Información sobre degeneración si existe
    degeneracy_info = solution.get('transport_summary', {}).get('degeneracy_info', '')
    if "degenerada" in degeneracy_info.lower():
        interpretation += " Cabe destacar que esta es una solución degenerada, lo que significa que requiere variables artificiales para completar el número requerido de variables básicas."
    else:
        interpretation += " La solución obtenida es una solución básica factible no degenerada."
    
    # Balanceo
    if balance_info.get("balanced", False):
        interpretation += f" El problema fue balanceado previamente {balance_info.get('explanation', 'para igualar oferta y demanda')}."
    
    return interpretation

# Funciones auxiliares (las mismas que antes)
def _is_ficticious_route(row_char: str, col_num: str, balance_info: dict) -> bool:
    if not balance_info.get("balanced", False):
        return False
    row_idx = ord(row_char.upper()) - 65
    col_idx = int(col_num) - 1
    if balance_info.get("ficticious_row") == row_idx:
        return True
    if balance_info.get("ficticious_col") == col_idx:
        return True
    return False

def _get_origin_name(row_char: str, supply: List[int], is_ficticious: bool) -> str:
    if is_ficticious:
        return "origen ficticio"
    names = ["Planta A", "Planta B", "Planta C", "Planta D", "Planta E", "Planta F"]
    idx = ord(row_char.upper()) - 65
    return names[idx] if idx < len(names) else f"Origen {row_char}"

def _get_destination_name(col_num: str, demand: List[int], is_ficticious: bool) -> str:
    if is_ficticious:
        return "destino ficticio"
    names = ["Centro 1", "Centro 2", "Centro 3", "Centro 4", "Centro 5", "Centro 6"]
    idx = int(col_num) - 1
    return names[idx] if idx < len(names) else f"Destino {col_num}"


# def _generate_interpretation(solution: Dict, supply: List[int], demand: List[int], 
#                            is_northwest: bool, balance_info: dict, method: str) -> str:
#     """Genera la explicación de las variables básicas"""
#     basic_vars = solution.get('transport_summary', {}).get('basic_variables_list', '')
    
#     # Nombres de métodos
#     method_names = {
#         "northwest": "ESQUINA NOROESTE",
#         "vogel": "APROXIMACIÓN DE VOGEL", 
#         "min_cost": "COSTO MÍNIMO"
#     }
    
#     method_display = method_names.get(method.lower(), method.upper())
#     interpretation = f"INTERPRETACIÓN DE LA SOLUCIÓN ({method_display}):\n\n"
    
#     if is_northwest:
#         interpretation += "El método de la Esquina Noroeste asigna unidades comenzando desde la celda superior izquierda:\n\n"
#     else:
#         interpretation += "Las variables básicas representan las rutas seleccionadas:\n\n"
    
#     # Información sobre balanceo
#     if balance_info.get("balanced", False):
#         interpretation += f"💡 {balance_info.get('explanation', 'Problema balanceado')}\n\n"
    
#     # Parsear variables básicas
#     vars_list = basic_vars.split(", ")
#     real_routes = 0
#     ficticious_routes = 0
    
#     for i, var in enumerate(vars_list, 1):
#         if '=' in var:
#             var_name, value = var.split('=')
#             row_char = var_name[0]
#             col_num = var_name[1]
            
#             # Verificar si es ficticia
#             is_ficticious = _is_ficticious_route(row_char, col_num, balance_info)
            
#             # Obtener nombres
#             row_name = _get_origin_name(row_char, supply, is_ficticious)
#             col_name = _get_destination_name(col_num, demand, is_ficticious)
            
#             if is_ficticious:
#                 ficticious_routes += 1
#                 explanation = _get_ficticious_explanation(row_char, col_num, balance_info)
#                 if is_northwest:
#                     interpretation += f"Paso {i}: {var_name} = {value} ⚠️ (FICTICIO - {explanation})\n"
#                 else:
#                     interpretation += f"• {var_name} = {value} ⚠️ (FICTICIO - {explanation})\n"
#             else:
#                 real_routes += 1
#                 if is_northwest:
#                     interpretation += f"Paso {i}: {var_name} = {value} (de {row_name} a {col_name})\n"
#                 else:
#                     interpretation += f"• {var_name} = {value} (de {row_name} a {col_name})\n"
    
#     # Resumen
#     interpretation += f"\n📊 RESUMEN:\n"
#     interpretation += f"• Rutas reales: {real_routes}\n"
#     if ficticious_routes > 0:
#         interpretation += f"• Rutas ficticias: {ficticious_routes}\n"
#     interpretation += f"• Total: {len(vars_list)} rutas"
    
#     return interpretation


# def _generate_cost_breakdown(solution: Dict, costs: List[List[float]], balance_info: dict,
#                            is_northwest: bool, method: str) -> str:
#     """Genera la explicación del cálculo de costo final"""
#     calculation = solution.get('transport_summary', {}).get('total_cost_calculation', '')
#     total_cost = solution['total_cost']
    
#     breakdown = "DESGLOSE DEL COSTO TOTAL:\n\n"
    
#     if is_northwest:
#         breakdown += "Cálculo secuencial (Esquina Noroeste):\n\n"
#     else:
#         breakdown += "Suma de costos por ruta:\n\n"
    
#     has_ficticious = False
    
#     if ' + ' in calculation and ' = ' in calculation:
#         calculation_part = calculation.split(' = ')[0]
#         terms = calculation_part.split(' + ')
        
#         for i, term in enumerate(terms, 1):
#             if '×' in term:
#                 cost_val, units = term.split('×')
#                 cost_num = float(cost_val)
                
#                 if is_northwest:
#                     breakdown += f"Asignación {i}: {cost_val} × {units} = {cost_num * float(units)}"
#                 else:
#                     breakdown += f"{i}. {cost_val} × {units}"
                
#                 if cost_num == 0:
#                     breakdown += " ⚠️ (FICTICIO)"
#                     has_ficticious = True
                
#                 breakdown += "\n"
    
#     breakdown += f"\nSUMA TOTAL: {total_cost}"
    
#     if has_ficticious:
#         breakdown += "\n\n💡 Los costos ficticios (0) no afectan el total real."
    
#     return breakdown



def _generate_cost_breakdown(solution: Dict, costs: List[List[float]], balance_info: dict,
                           is_northwest: bool, method: str) -> str:
    """Genera el desglose del costo final de forma concisa"""
    calculation = solution.get('transport_summary', {}).get('total_cost_calculation', '')
    total_cost = solution['total_cost']
    
    breakdown = "CÁLCULO DEL COSTO TOTAL:\n\n"
    
    if ' + ' in calculation and ' = ' in calculation:
        calculation_part = calculation.split(' = ')[0]
        terms = calculation_part.split(' + ')
        
        for i, term in enumerate(terms, 1):
            if '×' in term:
                cost_val, units = term.split('×')
                cost_num = float(cost_val)
                partial_cost = cost_num * float(units)
                
                if cost_num == 0:
                    breakdown += f"{cost_val} × {units} = {partial_cost} (ficticio)\n"
                else:
                    breakdown += f"{cost_val} × {units} = {partial_cost}\n"
    
    breakdown += f"\nTOTAL: {total_cost} unidades monetarias"
    
    return breakdown


def _generate_recommendations(solution: Dict, cost_difference: float, 
                            has_alternatives: bool, is_northwest: bool, method: str) -> List[str]:
    """Genera recomendaciones basadas en el análisis"""
    recommendations = ["RECOMENDACIONES FINALES:"]
    
    if is_northwest:
        recommendations.append("• Método: Esquina Noroeste (solución básica factible)")
        recommendations.append("• Garantiza factibilidad pero no optimalidad")
        recommendations.append("• Para optimalidad, use Vogel o Costo Mínimo")
    else:
        if cost_difference > 0:
            recommendations.append(f"• Esta solución ahorra {cost_difference} vs alternativas")
        
        if has_alternatives:
            recommendations.append("• Solución aproximada entre variantes analizadas")
        else:
            recommendations.append("• Solución única del método")
    
    # Análisis estructural
    basic_vars = solution.get('basic_variables', [])
    required = solution.get('required_basic_variables', 0)
    
    if len(basic_vars) == required:
        recommendations.append("• Solución no degenerada (rutas óptimas)")
    else:
        recommendations.append("• Solución degenerada (menos rutas de las requeridas)")
    
    # Verificar ficticias
    has_ficticious = any(var.get('cost', 0) == 0 for var in basic_vars)
    if has_ficticious:
        recommendations.append("• Incluye rutas ficticias para balanceo")
    
    return recommendations


def _generate_efficiency_note(solution: Dict, cost_difference: float, 
                            is_northwest: bool, method: str) -> str:
    """Genera nota sobre eficiencia"""
    if is_northwest:
        return "EFICIENCIA: Solución básica factible. No garantiza optimalidad."
    else:
        if cost_difference > 10:
            return f"EFICIENCIA: aproximada con ahorro significativo ({cost_difference})."
        elif cost_difference > 0:
            return f"EFICIENCIA: aproximada con pequeño margen ({cost_difference})."
        else:
            return "EFICIENCIA: Solución aproximada única."


def _is_ficticious_route(row_char: str, col_num: str, balance_info: dict) -> bool:
    """Determina si una ruta es ficticia"""
    if not balance_info.get("balanced", False):
        return False
    
    row_index = ord(row_char) - 65
    col_index = int(col_num) - 1
    
    if balance_info.get("ficticious_row") == row_index:
        return True
    if balance_info.get("ficticious_col") == col_index:
        return True
    
    return False


def _get_ficticious_explanation(row_char: str, col_num: str, balance_info: dict) -> str:
    """Explica por qué la ruta es ficticia"""
    row_index = ord(row_char) - 65
    col_index = int(col_num) - 1
    
    if balance_info.get("ficticious_row") == row_index:
        return "Origen ficticio para demanda excedente"
    if balance_info.get("ficticious_col") == col_index:
        return "Destino ficticio para oferta excedente"
    
    return "Ruta de balanceo"


def _get_origin_name(row_char: str, supply: List[int], is_ficticious: bool = False) -> str:
    """Convierte letra de fila en nombre de origen"""
    if is_ficticious:
        return "Origen Ficticio"
    
    origins = ["Fábrica A", "Fábrica B", "Fábrica C", "Fábrica D", "Fábrica E"]
    index = ord(row_char) - 65
    
    if index < len(origins):
        if index < len(supply):
            return f"{origins[index]}"
        return f"{origins[index]} (ficticia)"
    return f"Origen {row_char}"


def _get_destination_name(col_num: str, demand: List[int], is_ficticious: bool = False) -> str:
    """Convierte número de columna en nombre de destino"""
    if is_ficticious:
        return "Destino Ficticio"
    
    destinations = ["Almacén 1", "Almacén 2", "Almacén 3", "Almacén 4", "Almacén 5"]
    index = int(col_num) - 1
    
    if index < len(destinations):
        if index < len(demand):
            return f"{destinations[index]}"
        return f"{destinations[index]} (ficticio)"
    return f"Destino {col_num}"