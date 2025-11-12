from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import time
import algorithms.northwest_corner as northwest
import algorithms.vogel as vogel
import algorithms.min_cost as min_cost
import algorithms.balance as balance
from config.db_conexion import get_db, engine
from models.mod_transport import Base, ModelTransportProblem, ModelProblemExecution
from schemas.schema_transport import *

# Crear tablas
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Sistema de Modelos de Transporte",
    description="API para resolver problemas de transporte en investigación de operaciones",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # URL de tu frontend
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos los métodos
    allow_headers=["*"],  # Permite todos los headers
)

@app.get("/")
def read_root():
    return {"message": "Sistema de Modelos de Transporte - IO"}


@app.post("/problems/", response_model=TransportProblem)
def create_problem(problem: TransportProblemCreate, db: Session = Depends(get_db)):
    total_supply = sum(problem.supply)
    total_demand = sum(problem.demand)
    
    # Determinar si requiere balanceo y cómo
    requires_balance = total_supply != total_demand
    balance_type = None
    if requires_balance:
        if total_supply > total_demand:
            balance_type = "columna_ficticia"
        else:
            balance_type = "fila_ficticia"
    
    balance_info = {
        "balanced": requires_balance,
        "original_supply": problem.supply,
        "original_demand": problem.demand,
        "balanced_supply": problem.supply,
        "balanced_demand": problem.demand,
        "ficticious_row": None,
        "ficticious_col": None,
        "balance_type": balance_type,
        "difference": abs(total_supply - total_demand),
        "explanation": f"Oferta ({total_supply}) = Demanda ({total_demand}) - Balanceado" if not requires_balance 
                      else f"Oferta ({total_supply}) ≠ Demanda ({total_demand}) - Requiere {balance_type}"
    }
    
    db_problem = ModelTransportProblem(
        name=problem.name,
        description=problem.description,
        supply=problem.supply,
        demand=problem.demand,
        costs=problem.costs,
        balance_info=balance_info
    )
    
    db.add(db_problem)
    db.commit()
    db.refresh(db_problem)
    return db_problem

@app.get("/problems/", response_model=list[TransportProblem])
def list_problems(db: Session = Depends(get_db)):
    return db.query(ModelTransportProblem).all()



# main.py - actualizar solve_problem
@app.post("/problems/{problem_id}/solve", response_model=SolutionResponse)
def solve_problem(problem_id: int, solution_req: SolutionRequest, db: Session = Depends(get_db)):
    # Obtener problema
    problem = db.query(ModelTransportProblem).filter(ModelTransportProblem.id == problem_id).first()
    if not problem:
        raise HTTPException(status_code=404, detail="Problema no encontrado")
    
    # Balancear el problema ANTES de resolver
    balanced_data = balance.balance_transport_problem(problem.supply, problem.demand, problem.costs)
    balanced_supply = balanced_data["supply"]
    balanced_demand = balanced_data["demand"] 
    balanced_costs = balanced_data["costs"]
    balance_info = balanced_data["balance_info"]

    # Actualizar el balance_info en la base de datos
    problem.balance_info = balance_info
    db.commit()
    
    # Seleccionar algoritmo
    start_time = time.time()
     
    if solution_req.method == "northwest":
        result = northwest.northwest_corner(balanced_supply, balanced_demand, balanced_costs)
    elif solution_req.method == "vogel":
        result = vogel.vogel_approximation(balanced_supply, balanced_demand, balanced_costs)
    elif solution_req.method == "min_cost":
        result = min_cost.min_cost_method(balanced_supply, balanced_demand, balanced_costs)
    else:
        raise HTTPException(status_code=400, detail="Método no válido")
    
    execution_time = time.time() - start_time
    
    # Guardar ejecución
    execution = ModelProblemExecution(
        problem_id=problem_id,
        method=solution_req.method,
        execution_time=execution_time,
        solution_matrix=result['main_solution'],
        total_cost=result['total_cost'],
        step_by_step=result['steps']
    )
    db.add(execution)
    db.commit()
    db.refresh(execution)
    
    return SolutionResponse(
        problem_id=problem_id,
        method=solution_req.method,
        main_solution=result['main_solution'],
        total_cost=result['total_cost'],
        step_by_step=result['steps'],
        execution_time=execution_time,
        alternative_solutions=result.get('alternative_solutions', []),
        has_multiple_solutions=result.get('has_multiple_solutions', False),
        tie_scenarios=result.get('tie_scenarios', []),
        # Nueva información de análisis
        basic_variables=result['basic_variables'],
        non_basic_variables=result['non_basic_variables'],
        is_balanced=result['is_balanced'],
        total_supply=result['total_supply'],
        total_demand=result['total_demand'],
        degeneracy_info=result['degeneracy_info'],
        m=result['m'],
        n=result['n'],
        required_basic_variables=result['required_basic_variables'],
        actual_basic_variables=result['actual_basic_variables'],
        has_degeneracy=result['has_degeneracy'],
        transport_summary=result['transport_summary'],
        final_conclusion=result['final_conclusion']
    )



@app.get("/problems/{problem_id}/executions")
def get_problem_executions(problem_id: int, db: Session = Depends(get_db)):
    executions = db.query(ModelProblemExecution).filter(ModelProblemExecution.problem_id == problem_id).all()
    return executions