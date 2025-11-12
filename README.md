# 📦 Sistema de Transporte - Documentación

## 📋 Descripción General

Sistema completo para resolver problemas de transporte mediante métodos de optimización, incluyendo detección de múltiples soluciones óptimas y análisis detallado paso a paso.

## 🚀 Características Principales

### ✅ Métodos Implementados
- **Método de Aproximación de Vogel** - Con detección de empates y soluciones alternativas
- **Método del Costo Mínimo** - Con análisis de rutas óptimas múltiples
- **Balanceo automático** de problemas desequilibrados
- **Detección de degeneración** y corrección automática

### 🔍 Funcionalidades Avanzadas
- **Solución paso a paso** con explicaciones detalladas
- **Múltiples soluciones alternativas** cuando existen empates
- **Análisis completo** de variables básicas y no básicas
- **Resúmenes ejecutivos** con interpretación de resultados
- **Cálculo de costos** con desglose detallado

## 🏗️ Estructura del Proyecto

```
backend/
├── algorithms/
│   ├── balance.py              # Balanceo de problemas
│   ├── min_cost.py            # Método del costo mínimo
│   ├── vogel.py               # Método de Vogel
│   ├── transport_analysis.py  # Análisis de soluciones
│   ├── transport_summary.py   # Resúmenes ejecutivos
│   └── transport_conclusion.py # Conclusiones finales
├── schemas/
│   └── schema_transport.py    # Esquemas de datos
└── main.py                    # API principal
```

## 📊 Esquema de Respuesta

### Estructura Principal
```json
{
  "problem_id": 1,
  "method": "vogel|min_cost",
  "main_solution": [[...]],
  "total_cost": 335,
  "step_by_step": [...],
  "alternative_solutions": [...],
  "has_multiple_solutions": true,
  "basic_variables": [...],
  "transport_summary": {...},
  "final_conclusion": {...}
}
```

### Ejemplo de Paso por Paso
```json
{
  "step_number": 1,
  "description": "Asignar 15 unidades en X12",
  "current_matrix": [[...]],
  "current_cost": 0,
  "explanation": "Penalización máxima: 11.0 (fila)...",
  "basic_variables": [...],
  "assignment": "X12"
}
```

## 🎯 Métodos de Resolución

### Método de Vogel
**Características:**
- Calcula penalizaciones por fila y columna
- Selecciona la dirección con mayor penalización
- Detecta empates en penalizaciones y costos mínimos
- Genera soluciones alternativas para empates reales

**Estrategias de desempate:**
- Penalización máxima (fila/columna)
- Costo mínimo dentro de la dirección seleccionada
- Oferta = demanda simultánea

### Método del Costo Mínimo
**Características:**
- Selecciona siempre la celda con menor costo disponible
- Detecta empates de costos idénticos
- Genera alternativas probando diferentes celdas empatadas
- Estrategias de desempate configurables

## 🔧 Configuración y Uso

### Instalación
```bash
# Clonar el proyecto
git clone <repository-url>

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar servidor
uvicorn main:app --reload
```

### Endpoints Disponibles

#### POST /problems
Crear nuevo problema de transporte
```json
{
  "name": "Problema Ejemplo",
  "description": "Problema con 3 orígenes y 4 destinos",
  "supply": [15, 25, 10],
  "demand": [5, 15, 15, 10],
  "costs": [
    [10, 0, 20, 11],
    [12, 7, 9, 20],
    [0, 14, 16, 18]
  ]
}
```

#### POST /problems/{id}/solve
Resolver problema con método específico
```json
{
  "method": "vogel|min_cost"
}
```

### Ejemplo de Uso Completo

```python
# Crear problema
problem_data = {
    "supply": [15, 25, 10],
    "demand": [5, 15, 15, 10],
    "costs": [
        [10, 0, 20, 11],
        [12, 7, 9, 20],
        [0, 14, 16, 18]
    ]
}

# Resolver con Vogel
result = vogel_approximation(
    problem_data["supply"],
    problem_data["demand"], 
    problem_data["costs"]
)

# Analizar resultados
print(f"Costo total: {result['total_cost']}")
print(f"Variables básicas: {len(result['basic_variables'])}")
print(f"Soluciones alternativas: {len(result['alternative_solutions'])}")
```

## 📈 Análisis de Resultados

### Información Proporcionada
- **Solución principal** - Asignación óptima encontrada
- **Costo total** - Cálculo detallado del costo
- **Variables básicas** - Rutas utilizadas en la solución
- **Variables no básicas** - Rutas no utilizadas
- **Degeneración** - Información sobre solución degenerada
- **Soluciones alternativas** - Rutas óptimas equivalentes

### Interpretación de Resultados

#### Solución Degenerada
```json
{
  "degeneracy_info": "Solución degenerada: 5 variables básicas < 7 requeridas",
  "has_degeneracy": true
}
```

#### Múltiples Soluciones
```json
{
  "has_multiple_solutions": true,
  "alternative_solutions": [
    {
      "solution_matrix": [[...]],
      "total_cost": 315,
      "tie_break_reason": "Alternativa por empate..."
    }
  ]
}
```

## 🔍 Detección de Empates

### Tipos de Empates Detectados

#### En Método Vogel
- **Empate en penalizaciones** - Múltiples filas/columnas con misma penalización máxima
- **Empate en costos mínimos** - Múltiples celdas con mismo costo mínimo
- **Empate real** - Cuando oferta = demanda en múltiples opciones

#### En Método Costo Mínimo
- **Empate de costos** - Múltiples celdas con idéntico costo mínimo
- **Celdas ficticias** - Múltiples rutas con costo cero

### Ejemplo de Empate Detectado
```json
{
  "step": 2,
  "type": "penalty_tie",
  "ties": [1, 2, 3],
  "penalty_value": 7.0,
  "description": "Empate en penalización de columna: 7.0 en columnas [2, 3, 4]"
}
```

## 🛠️ Funciones Principales

### Balanceo Automático
```python
balanced_data = balance_transport_problem(supply, demand, costs)
```
- Agrega filas/columnas ficticias según necesidad
- Mantiene integridad del problema original
- Proporciona información del balanceo

### Corrección de Degeneración
```python
fixed_solution, degenerated_cells = fix_degeneration(
    solution, supply, demand, costs, balance_info
)
```
- Identifica soluciones degeneradas
- Agrega variables básicas cero donde sea necesario
- Mantiene optimalidad de la solución

### Análisis de Solución
```python
analysis = analyze_solution(supply, demand, costs, solution, balance_info)
```
- Calcula variables básicas y no básicas
- Verifica balanceo y degeneración
- Proporciona métricas completas

## 📝 Consideraciones Importantes

### Limitaciones
- Problemas deben ser de tamaño razonable para rendimiento
- Costos deben ser números reales positivos
- Oferta y demanda deben ser enteros no negativos

### Mejores Prácticas
- Verificar balanceo antes de resolver
- Revisar múltiples soluciones cuando existan
- Considerar degeneración en interpretación
- Validar datos de entrada
