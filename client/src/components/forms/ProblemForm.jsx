import { useState } from 'react';

const ProblemForm = ({ onSubmit }) => {
  const [formData, setFormData] = useState({
    name: '',
    numOrigins: 3,  // Número inicial de orígenes
    numDestinations: 3, // Número inicial de destinos
    supply: Array(3).fill(''),
    demand: Array(3).fill(''),
    costs: Array(3).fill().map(() => Array(3).fill(''))
  });

  // Actualizar número de orígenes
  const updateOrigins = (newCount) => {
    const count = parseInt(newCount);
    setFormData(prev => ({
      ...prev,
      numOrigins: count,
      supply: Array(count).fill('').map((_, i) => prev.supply[i] || ''),
      costs: Array(count).fill().map((_, i) => 
        Array(prev.numDestinations).fill('').map((_, j) => prev.costs[i]?.[j] || '')
      )
    }));
  };

  // Actualizar número de destinos
  const updateDestinations = (newCount) => {
    const count = parseInt(newCount);
    setFormData(prev => ({
      ...prev,
      numDestinations: count,
      demand: Array(count).fill('').map((_, i) => prev.demand[i] || ''),
      costs: prev.costs.map(row => 
        Array(count).fill('').map((_, j) => row[j] || '')
      )
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const processedData = {
      name: formData.name,
      supply: formData.supply.map(Number),
      demand: formData.demand.map(Number),
      costs: formData.costs.map(row => row.map(Number))
    };
    onSubmit(processedData);
  };

  const updateSupply = (index, value) => {
    const newSupply = [...formData.supply];
    newSupply[index] = value;
    setFormData({ ...formData, supply: newSupply });
  };

  const updateDemand = (index, value) => {
    const newDemand = [...formData.demand];
    newDemand[index] = value;
    setFormData({ ...formData, demand: newDemand });
  };

  const updateCost = (row, col, value) => {
    const newCosts = formData.costs.map(r => [...r]);
    newCosts[row][col] = value;
    setFormData({ ...formData, costs: newCosts });
  };

  return (
    <form onSubmit={handleSubmit} className="bg-white p-6 rounded-lg shadow-md text-center justify-center">
      <h2 className="text-2xl font-bold mb-4">Nuevo Problema de Transporte</h2>
      
      {/* Nombre del problema */}
      <div className="flex gap-6 justify-center">
      <div className="mb-4">
      <div className="mb-4">
        <label className="block text-gray-700 mb-2">Nombre del problema</label>
        <input
          type="text"
          value={formData.name}
          onChange={(e) => setFormData({...formData, name: e.target.value})}
          className="w-full p-2 border border-gray-300 rounded"
          required
        />
      </div>

      {/* Configuración de dimensiones */}
      <div className="grid grid-cols-2 gap-4 mb-6">
        <div>
          <label className="block text-gray-700 mb-2">Número de Ofertas</label>
          <select
            value={formData.numOrigins}
            onChange={(e) => updateOrigins(e.target.value)}
            className="w-full p-2 border border-gray-300 rounded"
          >
            {[2, 3, 4, 5, 6].map(num => (
              <option key={num} value={num}>{num} ofertas</option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-gray-700 mb-2">Número de Destinos</label>
          <select
            value={formData.numDestinations}
            onChange={(e) => updateDestinations(e.target.value)}
            className="w-full p-2 border border-gray-300 rounded"
          >
            {[2, 3, 4, 5, 6].map(num => (
              <option key={num} value={num}>{num} destinos</option>
            ))}
          </select>
        </div>
      </div>

      {/* Oferta y Demanda */}
      <div className="grid grid-cols-2 gap-4 mb-6">
        <div>
          <h3 className="font-semibold mb-2">Oferta </h3>
          {formData.supply.map((value, index) => (
            <div key={index} className="flex items-center mb-2">
              <span className="w-20 text-gray-600">Oferta {index + 1}:</span>
              <input
                type="number"
                value={value}
                onChange={(e) => updateSupply(index, e.target.value)}
                className="flex-1 p-2 border border-gray-300 rounded"
                placeholder="Cantidad"
                min="0"
                required
              />
            </div>
          ))}
        </div>

        <div>
          <h3 className="font-semibold mb-2">Demanda </h3>
          {formData.demand.map((value, index) => (
            <div key={index} className="flex items-center mb-2">
              <span className="w-20 text-gray-600">Destino {index + 1}:</span>
              <input
                type="number"
                value={value}
                onChange={(e) => updateDemand(index, e.target.value)}
                className="flex-1 p-2 border border-gray-300 rounded"
                placeholder="Cantidad"
                min="0"
                required
              />
            </div>
          ))}
        </div>
      </div>
      </div>

      {/* Matriz de Costos */}
      <div className="mb-6">
        <h3 className="font-semibold mb-2">Matriz de Costos</h3>
        <div className="border rounded-lg p-4 overflow-x-auto">
          <table className="min-w-full">
            <thead>
              <tr>
                <th className="p-2 bg-gray-100 border"></th>
                {formData.demand.map((_, colIndex) => (
                  <th key={colIndex} className="p-2 bg-gray-100 border font-semibold">
                    Destino {colIndex + 1}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {formData.costs.map((row, rowIndex) => (
                <tr key={rowIndex}>
                  <td className="p-2 bg-gray-100 border font-semibold">
                    Oferta {rowIndex + 1}
                  </td>
                  {row.map((cost, colIndex) => (
                    <td key={colIndex} className="p-1 border">
                      <input
                        type="number"
                        value={cost}
                        onChange={(e) => updateCost(rowIndex, colIndex, e.target.value)}
                        className="w-20 p-2 border border-gray-300 rounded text-center"
                        placeholder="Costo"
                        min="0"
                        step="0.01"
                        required
                      />
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
      </div>

      <button
        type="submit"
        className="bg-blue-500 text-white m-auto flex px-6 py-2 rounded hover:bg-blue-600 font-semibold"
      >
        Crear Problema
      </button>
    </form>
  );
};

export default ProblemForm;