const SolutionTable = ({ solution, costs, supply, demand }) => {
  if (!solution) return null;

  return (
    <div className="bg-white p-6 rounded-lg shadow-md">
      <h3 className="text-xl font-bold mb-4">Solución de Transporte</h3>
      
      <div className="overflow-x-auto">
        <table className="w-full border-collapse border border-gray-300">
          <thead>
            <tr className="bg-gray-100">
              <th className="border border-gray-300 p-2">Origen/Destino</th>
              {demand?.map((_, colIndex) => (
                <th key={colIndex} className="border border-gray-300 p-2">
                  Destino {colIndex + 1}
                </th>
              ))}
              <th className="border border-gray-300 p-2 bg-gray-200">Oferta</th>
            </tr>
          </thead>
          <tbody>
            {solution.map((row, rowIndex) => (
              <tr key={rowIndex}>
                <td className="border border-gray-300 p-2 bg-gray-100 font-semibold">
                  Origen {rowIndex + 1}
                </td>
                {row.map((cell, colIndex) => (
                  <td key={colIndex} className="border border-gray-300 p-2 text-center">
                    <div className={`font-semibold ${cell > 0 ? 'text-green-600' : 'text-gray-400'}`}>
                      {cell > 0 ? cell : '0'}
                    </div>
                    <div className="text-xs text-gray-500">
                      Costo: {costs?.[rowIndex]?.[colIndex]}
                    </div>
                  </td>
                ))}
                <td className="border border-gray-300 p-2 bg-gray-200 font-semibold text-center">
                  {supply?.[rowIndex]}
                </td>
              </tr>
            ))}
            {/* Fila de demanda */}
            <tr>
              <td className="border border-gray-300 p-2 bg-gray-200 font-semibold">Demanda</td>
              {demand?.map((demanValue, colIndex) => (
                <td key={colIndex} className="border border-gray-300 p-2 bg-gray-200 font-semibold text-center">
                  {demanValue}
                </td>
              ))}
              <td className="border border-gray-300 p-2 bg-gray-300 font-semibold text-center">
                {supply?.reduce((a, b) => a + b, 0)}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default SolutionTable;