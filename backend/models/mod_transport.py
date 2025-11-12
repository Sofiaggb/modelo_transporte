from sqlalchemy import Column, Integer, String, Float, Text, JSON, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from config.db_conexion import Base

class ModelTransportProblem(Base):
    __tablename__ = "transport_problems"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement="auto")
    name = Column(String(100), nullable=False)
    description = Column(Text)
    
    # Datos del problema
    supply = Column(JSON)  # [100, 150, 200]
    demand = Column(JSON)  # [80, 120, 150, 100]
    costs = Column(JSON)   # [[8, 6, 10, 9], [9, 12, 13, 7], [14, 9, 16, 5]]
    
    # Método seleccionado
    method = Column(String(20))  # northwest, vogel, min_cost
    
    # Resultados
    solution = Column(JSON)  # Matriz solución
    total_cost = Column(Float)
    steps = Column(JSON)  # Pasos del algoritmo
    balance_info = Column(JSON, nullable=True) # si la oferta y demanda esta desbalanceada
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relación con ejecuciones
    executions = relationship("ModelProblemExecution", back_populates="problem")



class ModelProblemExecution(Base):
    __tablename__ = "problem_executions"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement="auto")
    problem_id = Column(Integer, ForeignKey("transport_problems.id"))
    
    # Parámetros de ejecución
    method = Column(String(20), nullable=False)
    execution_time = Column(Float)  # Tiempo en segundos
    
    # Resultados
    solution_matrix = Column(JSON)
    total_cost = Column(Float)
    step_by_step = Column(JSON)  # Pasos detallados
    
    executed_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relación
    problem = relationship("ModelTransportProblem", back_populates="executions")