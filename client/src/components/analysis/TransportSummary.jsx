const TransportSummary = ({ transportSummary }) => {
  if (!transportSummary) {
    return <div className="text-gray-500">No hay información de resumen disponible</div>;
  }

  return (
    <div className="space-y-4">
      {/* Variables básicas */}
      <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
        <h3 className="font-bold text-lg text-blue-800 mb-3">📊 Variables Básicas</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <p className="font-semibold text-gray-700">Cálculo requerido:</p>
            <p className="text-lg">{transportSummary.basic_variables_count}</p>
          </div>
          <div>
            <p className="font-semibold text-gray-700">Lista de variables:</p>
            <div className="bg-white p-3 rounded border">
              {transportSummary.basic_variables_list.split(', ').map((variable, index) => (
                <span 
                  key={index}
                  className={`inline-block px-2 py-1 rounded text-sm mr-2 mb-2 ${
                    variable.includes('⚠️') ? 'bg-yellow-100 text-yellow-800 border border-yellow-300' : 'bg-green-100 text-green-800 border border-green-300'
                  }`}
                >
                  {variable}
                </span>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Cálculo del costo total */}
      <div className="bg-green-50 p-4 rounded-lg border border-green-200">
        <h3 className="font-bold text-lg text-green-800 mb-3">💰 Cálculo del Costo Total</h3>
        <div className="bg-white p-4 rounded border">
          <code className="text-lg font-mono bg-gray-100 px-3 py-2 rounded block">
            {transportSummary.total_cost_calculation}
          </code>
        </div>
      </div>

      {/* Información de degeneración */}
      {/* <div className={`p-4 rounded-lg border ${
        transportSummary.has_degeneration 
          ? 'bg-yellow-50 border-yellow-300' 
          : 'bg-green-50 border-green-300'
      }`}>
        <h3 className="font-bold text-lg mb-3">
          {transportSummary.has_degeneration ? '⚠️ Estado de la Solución' : '✅ Estado de la Solución'}
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <p className="font-semibold text-gray-700">Información:</p>
            <p className={transportSummary.has_degeneration ? 'text-yellow-700' : 'text-green-700'}>
              {transportSummary.degeneracy_info}
            </p>
          </div>
          {transportSummary.has_degeneration && (
            <div>
              <p className="font-semibold text-gray-700">Variables degeneradas:</p>
              <p className="text-yellow-700">{transportSummary.degenerated_variables_count}</p>
            </div>
          )}
        </div>
      </div> */}

      {/* Método usado */}
      {/* <div className="bg-purple-50 p-4 rounded-lg border border-purple-200">
        <h3 className="font-bold text-lg text-purple-800 mb-3">🔧 Método de Solución</h3>
        <div className="bg-white p-3 rounded border">
          <span className="inline-block px-3 py-1 bg-purple-100 text-purple-800 rounded-full font-semibold">
            {transportSummary.method_used.toUpperCase()}
          </span>
        </div>
      </div> */}

      {/* Paso a paso textual */}
      {transportSummary.step_by_step_text && transportSummary.step_by_step_text.length > 0 && (
        <div className="bg-gray-50 p-4 rounded-lg border border-gray-200">
          <h3 className="font-bold text-lg text-gray-800 mb-3">📝 Resumen de Pasos</h3>
          <div className="bg-white p-4 rounded border space-y-2">
            {transportSummary.step_by_step_text.map((step, index) => (
              <div key={index} className="flex items-start">
                <span className="bg-blue-100 text-blue-800 rounded-full w-6 h-6 flex items-center justify-center text-sm font-semibold mr-3 mt-1 flex-shrink-0">
                  {index + 1}
                </span>
                <p className="text-gray-700">{step}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default TransportSummary;