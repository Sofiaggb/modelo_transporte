from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime

class TransportProblemBase(BaseModel):
    name: str
    description: Optional[str] = None
    supply: List[int]
    demand: List[int]
    costs: List[List[float]]

class TransportProblemCreate(TransportProblemBase):
    pass

# En schemas/schema_transport.py - agregar esto
class BalanceInfo(BaseModel):
    balanced: bool
    original_supply: List[int]
    original_demand: List[int]
    balanced_supply: List[int]
    balanced_demand: List[int]
    ficticious_row: Optional[int] = None  # Índice de fila ficticia
    ficticious_col: Optional[int] = None  # Índice de columna ficticia
    explanation: str

class TransportProblem(TransportProblemBase):
    id: int
    method: Optional[str] = None
    solution: Optional[List[List[int]]] = None
    total_cost: Optional[float] = None
    steps: Optional[List[Dict[str, Any]]] = None
    balance_info: Optional[BalanceInfo] = None  # ← NUEVO
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class SolutionRequest(BaseModel):
    method: str  # "northwest", "vogel", "min_cost"

# class StepByStep(BaseModel):
#     step_number: int
#     description: str
#     current_matrix: List[List[int]]
#     current_cost: float
#     explanation: str


# class SolutionResponse(BaseModel):
#     problem_id: int
#     method: str
#     main_solution: List[List[int]]
#     total_cost: float
#     step_by_step: List[StepByStep]
#     execution_time: float
#     alternative_solutions: List[AlternativeSolution] = []  # Nuevo
#     has_multiple_solutions: bool = False  # Nuevo
#     tie_scenarios: List[str] = []  # Escenarios de empate encontrados

# schemas/schema_transport.py - agregar estos esquemas
class BasicVariable(BaseModel):
    cell: str  # Ejemplo: "X11", "X23"
    value: int
    cost: float
    i: int  # Fila
    j: int  # Columna

class TransportationSolution(BaseModel):
    solution_matrix: List[List[int]]
    total_cost: float
    basic_variables: List[BasicVariable]
    non_basic_variables: List[str]  # Celdas que son 0
    is_balanced: bool
    total_supply: int
    total_demand: int
    degeneracy_info: str  # Información sobre degeneración

class StepByStep(BaseModel):
    step_number: int
    description: str
    current_matrix: List[List[int]]
    current_cost: float
    explanation: str
    basic_variables: List[BasicVariable]  # Nuevo
    assignment: Optional[str] = None  # Celda asignada en este paso


# schemas/schema_transport.py - agregar esto
class FinalConclusion(BaseModel):
    best_solution_index: int  # 0 = principal, 1 = primera alternativa, etc.
    best_solution_cost: float
    is_main_solution_best: bool
    cost_difference: float  # Diferencia con la segunda mejor solución
    interpretation: str  # Explicación de las variables básicas
    cost_breakdown: str  # Explicación del cálculo de costo
    recommendations: List[str]  # Recomendaciones finales
    efficiency_note: str  # Nota sobre eficiencia

class TransportSummary(BaseModel):
    basic_variables_count: str
    basic_variables_list: str
    total_cost_calculation: str
    degeneracy_info: str
    step_by_step_text: List[str]
    method_used: str


class AlternativeSolution(BaseModel):
    solution_matrix: List[List[int]]
    total_cost: float
    steps: List[StepByStep]
    tie_break_reason: str  # Por qué se eligió esta variante
    transport_summary: TransportSummary



class SolutionResponse(BaseModel):
    problem_id: int
    method: str
    main_solution: List[List[int]]
    total_cost: float
    step_by_step: List[StepByStep]
    execution_time: float
    alternative_solutions: List[AlternativeSolution] = []
    has_multiple_solutions: bool = False
    tie_scenarios: List[str] = []
    
    # Nueva información estructural
    basic_variables: List[BasicVariable]
    non_basic_variables: List[str]
    is_balanced: bool
    total_supply: int
    total_demand: int
    degeneracy_info: str
    m: int  # Número de filas (orígenes)
    n: int  # Número de columnas (destinos)
    required_basic_variables: int  # m + n - 1
    actual_basic_variables: int
    has_degeneracy: bool

     #  Resumen textual
    transport_summary: TransportSummary

    #  Conclusión final
    final_conclusion: FinalConclusion



