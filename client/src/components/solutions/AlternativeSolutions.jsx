// import { useState } from 'react';
// import SolutionTable from '../tables/SolutionTable';
// import StepByStepViewer from '../steps/StepByStepViewer';

// const AlternativeSolutions = ({ alternatives, mainSolution, mainCost }) => {
//   const [selectedAlt, setSelectedAlt] = useState(0);
//   const [activeTab, setActiveTab] = useState('solution'); // 'solution' o 'steps'

//   if (!alternatives || alternatives.length === 0) {
//     return null;
//   }

//   const currentAlt = alternatives[selectedAlt];

//   return (
//     <div className="bg-white rounded-lg shadow-md p-6">
//       <h3 className="text-xl font-bold mb-4">Soluciones Alternativas</h3>
      
//       {/* Selector de soluciones alternativas */}
//       <div className="mb-4">
//         <label className="block text-gray-700 mb-2">
//           Seleccionar solución alternativa ({alternatives.length} disponibles):
//         </label>
//         <select
//           value={selectedAlt}
//           onChange={(e) => {
//             setSelectedAlt(parseInt(e.target.value));
//             setActiveTab('solution');
//           }}
//           className="w-full p-2 border border-gray-300 rounded"
//         >
//           {alternatives.map((alt, index) => (
//             <option key={index} value={index}>
//               Alternativa {index + 1} - {alt.tie_break_reason} (Costo: {alt.total_cost})
//             </option>
//           ))}
//         </select>
//       </div>

//       {/* Tabs para solución alternativa */}
//       <div className="mb-4 border-b">
//         <nav className="flex">
//           <button
//             onClick={() => setActiveTab('solution')}
//             className={`px-4 py-2 font-medium ${
//               activeTab === 'solution'
//                 ? 'border-b-2 border-blue-500 text-blue-600'
//                 : 'text-gray-500 hover:text-gray-700'
//             }`}
//           >
//             Solución
//           </button>
//           <button
//             onClick={() => setActiveTab('steps')}
//             className={`px-4 py-2 font-medium ${
//               activeTab === 'steps'
//                 ? 'border-b-2 border-blue-500 text-blue-600'
//                 : 'text-gray-500 hover:text-gray-700'
//             }`}
//           >
//             Paso a Paso
//           </button>
//           <button
//             onClick={() => setActiveTab('analysis')}
//             className={`px-4 py-2 font-medium ${
//               activeTab === 'analysis'
//                 ? 'border-b-2 border-blue-500 text-blue-600'
//                 : 'text-gray-500 hover:text-gray-700'
//             }`}
//           >
//             Análisis
//           </button>
//         </nav>
//       </div>

//       {/* Contenido de los tabs */}
//       {activeTab === 'solution' && (
//         <>
//           {/* Información de la solución alternativa seleccionada */}
//           <div className="mb-4 p-4 bg-blue-50 rounded">
//             <h4 className="font-bold mb-2">Información de la Solución Alternativa:</h4>
//             <p><strong>Razón del desempate:</strong> {currentAlt.tie_break_reason}</p>
//             <p><strong>Costo total:</strong> {currentAlt.total_cost}</p>
//             <p><strong>Comparación con solución principal:</strong> 
//               <span className={currentAlt.total_cost === mainCost ? 'text-green-600' : 'text-red-600'}>
//                 {currentAlt.total_cost === mainCost ? ' Mismo costo' : ` Diferencia: ${Math.abs(currentAlt.total_cost - mainCost)}`}
//               </span>
//             </p>
//           </div>

//           {/* Tabla de la solución alternativa */}
//           <SolutionTable 
//             solution={currentAlt.solution_matrix}
//             costs={mainSolution.costs}
//             supply={mainSolution.supply}
//             demand={mainSolution.demand}
//           />
//         </>
//       )}

//       {activeTab === 'steps' && currentAlt.steps && (
//         <StepByStepViewer 
//           steps={currentAlt.steps}
//           costs={mainSolution.costs}
//           supply={mainSolution.supply}
//           demand={mainSolution.demand}
//         />
//       )}

//       {activeTab === 'analysis' && currentAlt.transport_summary && (
//         <div className="space-y-4">
//           {/* Información del transport_summary */}
//           <div className="bg-gray-50 p-4 rounded">
//             <h4 className="font-bold mb-2">Resumen de Transporte</h4>
//             <p><strong>Variables básicas requeridas:</strong> {currentAlt.transport_summary.basic_variables_count}</p>
//             <p><strong>Variables básicas actuales:</strong> {currentAlt.transport_summary.basic_variables_list}</p>
//             <p><strong>Cálculo de costo:</strong> {currentAlt.transport_summary.total_cost_calculation}</p>
//             <p><strong>Estado:</strong> {currentAlt.transport_summary.degeneracy_info}</p>
//             <p><strong>Método usado:</strong> {currentAlt.transport_summary.method_used}</p>
//           </div>

//           {/* Paso a paso textual */}
//           {currentAlt.transport_summary.step_by_step_text && 
//            currentAlt.transport_summary.step_by_step_text.length > 0 && (
//             <div className="bg-green-50 p-4 rounded">
//               <h4 className="font-bold mb-2">Resumen de Pasos:</h4>
//               <ul className="list-disc list-inside space-y-1">
//                 {currentAlt.transport_summary.step_by_step_text.map((step, index) => (
//                   <li key={index} className="text-sm">{step}</li>
//                 ))}
//               </ul>
//             </div>
//           )}

//           {/* Información de degeneración */}
//           <div className="bg-yellow-50 p-4 rounded">
//             <h4 className="font-bold mb-2">Análisis de Degeneración</h4>
//             <p>{currentAlt.transport_summary.degeneracy_info}</p>
//             <p><strong>Variables degeneradas:</strong> {currentAlt.transport_summary.degenerated_variables_count || 0}</p>
//             <p><strong>Tiene degeneración:</strong> {currentAlt.transport_summary.has_degeneration ? 'Sí' : 'No'}</p>
//           </div>
//         </div>
//       )}
//     </div>
//   );
// };

// export default AlternativeSolutions;



import { useState } from 'react';
import SolutionTable from '../tables/SolutionTable';
import StepByStepViewer from '../steps/StepByStepViewer';
import TransportSummary from '../analysis/TransportSummary';

const AlternativeSolutions = ({ alternatives, mainSolution, mainCost }) => {
  const [selectedAlt, setSelectedAlt] = useState(0);
  const [activeTab, setActiveTab] = useState('solution'); // 'solution', 'steps', 'summary'

  if (!alternatives || alternatives.length === 0) {
    return null;
  }

  const currentAlt = alternatives[selectedAlt];

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h3 className="text-xl font-bold mb-4">Soluciones Alternativas</h3>
      
      {/* Selector de soluciones alternativas */}
      <div className="mb-4">
        <label className="block text-gray-700 mb-2">
          Seleccionar solución alternativa ({alternatives.length} disponibles):
        </label>
        <select
          value={selectedAlt}
          onChange={(e) => {
            setSelectedAlt(parseInt(e.target.value));
            setActiveTab('solution');
          }}
          className="w-full p-2 border border-gray-300 rounded"
        >
          {alternatives.map((alt, index) => (
            <option key={index} value={index}>
              Alternativa {index + 1} - {alt.tie_break_reason} (Costo: {alt.total_cost})
            </option>
          ))}
        </select>
      </div>

      {/* Información de comparación */}
      <div className="mb-4 p-4 bg-blue-50 rounded border border-blue-200">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-center">
          <div>
            <p className="text-sm text-gray-600">Costo Principal</p>
            <p className="text-lg font-bold">{mainCost}</p>
          </div>
          <div>
            <p className="text-sm text-gray-600">Costo Alternativa</p>
            <p className={`text-lg font-bold ${
              currentAlt.total_cost === mainCost ? 'text-green-600' : 'text-blue-600'
            }`}>
              {currentAlt.total_cost}
            </p>
          </div>
          <div>
            <p className="text-sm text-gray-600">Diferencia</p>
            <p className={`text-lg font-bold ${
              currentAlt.total_cost === mainCost ? 'text-green-600' : 'text-orange-600'
            }`}>
              {currentAlt.total_cost === mainCost ? 'Igual' : Math.abs(currentAlt.total_cost - mainCost)}
            </p>
          </div>
        </div>
        <p className="text-center mt-2 text-sm text-gray-600">
          <strong>Razón del desempate:</strong> {currentAlt.tie_break_reason}
        </p>
      </div>

      {/* Tabs para solución alternativa */}
      <div className="mb-4 border-b">
        <nav className="flex">
          <button
            onClick={() => setActiveTab('solution')}
            className={`px-4 py-2 font-medium ${
              activeTab === 'solution'
                ? 'border-b-2 border-blue-500 text-blue-600'
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            🗂️ Solución
          </button>
          <button
            onClick={() => setActiveTab('steps')}
            className={`px-4 py-2 font-medium ${
              activeTab === 'steps'
                ? 'border-b-2 border-blue-500 text-blue-600'
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            🔄 Paso a Paso
          </button>
          <button
            onClick={() => setActiveTab('summary')}
            className={`px-4 py-2 font-medium ${
              activeTab === 'summary'
                ? 'border-b-2 border-blue-500 text-blue-600'
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            📊 Resumen Completo
          </button>
        </nav>
      </div>

      {/* Contenido de los tabs */}
      {activeTab === 'solution' && (
        <SolutionTable 
          solution={currentAlt.solution_matrix}
          costs={mainSolution.costs}
          supply={mainSolution.supply}
          demand={mainSolution.demand}
        />
      )}

      {activeTab === 'steps' && currentAlt.steps && (
        <StepByStepViewer 
          steps={currentAlt.steps}
          costs={mainSolution.costs}
          supply={mainSolution.supply}
          demand={mainSolution.demand}
        />
      )}

      {activeTab === 'summary' && currentAlt.transport_summary && (
        <TransportSummary transportSummary={currentAlt.transport_summary} />
      )}
    </div>
  );
};

export default AlternativeSolutions;