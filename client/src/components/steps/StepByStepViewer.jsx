import { useState } from 'react';

const StepByStepViewer = ({ steps, costs, supply, demand }) => {
  const [currentStep, setCurrentStep] = useState(0);

  if (!steps || steps.length === 0) {
    return <div className="text-gray-500">No hay pasos disponibles</div>;
  }

  const step = steps[currentStep];
  const isFirst = currentStep === 0;
  const isLast = currentStep === steps.length - 1;

  // Convertir notación Xij a A1, B2, etc.
  const convertNotation = (cell) => {
    if (!cell || !cell.startsWith('X')) return cell;
    const row = parseInt(cell[1]) + 1;
    const col = parseInt(cell[2]) + 1;
    const rowChar = String.fromCharCode(64 + row); // A, B, C, etc.
    return `${rowChar}${col}`;
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h3 className="text-xl font-bold mb-4">Paso a Paso de la Solución</h3>
      
      {/* Navegación */}
      <div className="flex justify-between items-center mb-4">
        <button
          onClick={() => setCurrentStep(Math.max(0, currentStep - 1))}
          disabled={isFirst}
          className="bg-blue-500 text-white px-4 py-2 rounded disabled:bg-gray-300"
        >
          Anterior
        </button>
        
        <div className="text-center">
          <span className="font-semibold">
            Paso {step.step_number + 1} de {steps.length}
          </span>
          <div className="text-sm text-gray-600">
            {Math.round(((currentStep + 1) / steps.length) * 100)}% completado
          </div>
        </div>
        
        <button
          onClick={() => setCurrentStep(Math.min(steps.length - 1, currentStep + 1))}
          disabled={isLast}
          className="bg-blue-500 text-white px-4 py-2 rounded disabled:bg-gray-300"
        >
          Siguiente
        </button>
      </div>

      {/* Barra de progreso */}
      <div className="w-full bg-gray-200 rounded-full h-2 mb-4">
        <div 
          className="bg-blue-600 h-2 rounded-full transition-all duration-300"
          style={{ width: `${((currentStep + 1) / steps.length) * 100}%` }}
        ></div>
      </div>

      {/* Información del paso actual */}
      <div className="mb-4 p-4 bg-gray-50 rounded border">
        <h4 className="font-bold text-lg mb-2 text-blue-800">{step.description}</h4>
        <p className="text-gray-700 mb-3">{step.explanation}</p>
        
        {step.assignment && (
          <div className="bg-yellow-100 p-3 rounded border border-yellow-300">
            <strong>Asignación actual:</strong> {convertNotation(step.assignment)}
          </div>
        )}
      </div>

      {/* Matriz del paso actual */}
      <div className="mb-4">
        <h4 className="font-semibold mb-2">Matriz Actual:</h4>
        <div className="overflow-x-auto">
          <table className="min-w-full border-collapse border border-gray-300">
            <thead>
              <tr className="bg-gray-100">
                <th className="border border-gray-300 p-2">Origen/Destino</th>
                {demand?.map((_, colIndex) => (
                  <th key={colIndex} className="border border-gray-300 p-2">
                    D{colIndex + 1}
                  </th>
                ))}
                <th className="border border-gray-300 p-2 bg-gray-200">Oferta</th>
              </tr>
            </thead>
            <tbody>
              {step.current_matrix.map((row, rowIndex) => (
                <tr key={rowIndex}>
                  <td className="border border-gray-300 p-2 bg-gray-100 font-semibold">
                    O{rowIndex + 1}
                  </td>
                  {row.map((cell, colIndex) => (
                    <td key={colIndex} className="border border-gray-300 p-2 text-center">
                      <div className={`font-semibold text-lg ${
                        cell > 0 ? 'text-green-600 bg-green-50' : 'text-gray-400'
                      }`}>
                        {cell}
                      </div>
                      <div className="text-xs text-gray-500">
                        Costo: {costs?.[rowIndex]?.[colIndex]}
                      </div>
                    </td>
                  ))}
                  <td className="border border-gray-300 p-2 bg-gray-200 font-semibold">
                    {supply?.[rowIndex]}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Variables básicas */}
      {step.basic_variables && step.basic_variables.length > 0 && (
        <div className="mb-4">
          <h4 className="font-semibold mb-2">Variables Básicas Acumuladas:</h4>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
            {step.basic_variables.map((variable, index) => (
              <div key={index} className="bg-blue-50 p-2 rounded border border-blue-200 text-sm">
                <div className="font-semibold">{convertNotation(variable.cell)} = {variable.value}</div>
                <div className="text-xs text-gray-600">Costo: {variable.cost}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Costo acumulado */}
      <div className="mt-4 p-3 bg-green-50 rounded border border-green-200">
        <strong>Costo acumulado:</strong> {step.current_cost}
      </div>
    </div>
  );
};

export default StepByStepViewer;