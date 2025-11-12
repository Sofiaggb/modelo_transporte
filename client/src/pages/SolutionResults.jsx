// import { useState } from 'react';
// import StepByStepViewer from '../components/steps/StepByStepViewer';
// import AlternativeSolutions from '../components/solutions/AlternativeSolutions';
// import SolutionTable from '../components/tables/SolutionTable';

// const SolutionResults = ({ solution, problem }) => {
//   const [activeTab, setActiveTab] = useState('main');

//   if (!solution) {
//     return <div className="text-gray-500">No hay solución para mostrar</div>;
//   }

//   const tabs = [
//     { id: 'main', name: 'Solución Principal' },
//     { id: 'steps', name: 'Paso a Paso' },
//     { id: 'alternatives', name: 'Soluciones Alternativas' },
//     { id: 'analysis', name: 'Análisis' }
//   ];

//   // Usar transport_summary para la información
//   const transportSummary = solution.transport_summary;

//   return (
//     <div className="bg-white rounded-lg shadow-md">
//       {/* Tabs de navegación */}
//       <div className="border-b">
//         <nav className="flex">
//           {tabs.map(tab => (
//             <button
//               key={tab.id}
//               onClick={() => setActiveTab(tab.id)}
//               className={`px-4 py-2 font-medium ${
//                 activeTab === tab.id
//                   ? 'border-b-2 border-blue-500 text-blue-600'
//                   : 'text-gray-500 hover:text-gray-700'
//               }`}
//             >
//               {tab.name}
//             </button>
//           ))}
//         </nav>
//       </div>

//       {/* Contenido de los tabs */}
//       <div className="p-6">
//         {activeTab === 'main' && (
//           <div>
//             <h2 className="text-2xl font-bold mb-4">Solución Principal</h2>
            
//             {/* Información desde transport_summary */}
//             <div className="grid grid-cols-2 gap-4 mb-6">
//               <div className="bg-gray-50 p-4 rounded">
//                 <p><strong>Método:</strong> {solution.method}</p>
//                 <p><strong>Costo Total:</strong> {solution.total_cost}</p>
//                 <p><strong>Tiempo de ejecución:</strong> {solution.execution_time?.toFixed(4)}s</p>
//               </div>
//               <div className="bg-gray-50 p-4 rounded">
//                 <p><strong>Variables básicas:</strong> {transportSummary?.basic_variables_count}</p>
//                 <p><strong>Estado:</strong> {transportSummary?.degeneracy_info}</p>
//                 <p><strong>Método usado:</strong> {transportSummary?.method_used}</p>
//               </div>
//             </div>
            
//             <SolutionTable 
//               solution={solution.main_solution}
//               costs={problem.costs}
//               supply={problem.supply}
//               demand={problem.demand}
//             />

//             {/* Variables básicas desde transport_summary */}
//             {transportSummary?.basic_variables_list && (
//               <div className="mt-4 p-4 bg-blue-50 rounded">
//                 <h4 className="font-semibold mb-2">Variables Básicas:</h4>
//                 <p>{transportSummary.basic_variables_list}</p>
//               </div>
//             )}
//           </div>
//         )}

//         {activeTab === 'steps' && (
//           <StepByStepViewer 
//             steps={solution.step_by_step}
//             costs={problem.costs}
//             supply={problem.supply}
//             demand={problem.demand}
//           />
//         )}

//         {activeTab === 'alternatives' && solution.has_multiple_solutions && (
//           <AlternativeSolutions 
//             alternatives={solution.alternative_solutions}
//             mainSolution={problem}
//             mainCost={solution.total_cost}
//           />
//         )}

//         {activeTab === 'alternatives' && !solution.has_multiple_solutions && (
//           <div className="text-center py-8 text-gray-500">
//             No hay soluciones alternativas disponibles
//           </div>
//         )}

//         {activeTab === 'analysis' && (
//           <div className="space-y-4">
//             {/* Información desde transport_summary */}
//             {transportSummary && (
//               <div className="bg-gray-50 p-4 rounded">
//                 <h3 className="font-bold mb-2">Resumen de Transporte</h3>
//                 <p><strong>Variables básicas:</strong> {transportSummary.basic_variables_count}</p>
//                 <p><strong>Lista de variables:</strong> {transportSummary.basic_variables_list}</p>
//                 <p><strong>Cálculo de costo:</strong> {transportSummary.total_cost_calculation}</p>
//                 <p><strong>Estado:</strong> {transportSummary.degeneracy_info}</p>
//                 {transportSummary.has_degeneration && (
//                   <p><strong>Variables degeneradas:</strong> {transportSummary.degenerated_variables_count}</p>
//                 )}
//               </div>
//             )}

//             {/* Paso a paso textual */}
//             {transportSummary?.step_by_step_text && 
//              transportSummary.step_by_step_text.length > 0 && (
//               <div className="bg-green-50 p-4 rounded">
//                 <h3 className="font-bold mb-2">Resumen de Pasos:</h3>
//                 <ul className="list-disc list-inside space-y-1">
//                   {transportSummary.step_by_step_text.map((step, index) => (
//                     <li key={index}>{step}</li>
//                   ))}
//                 </ul>
//               </div>
//             )}

//             {/* Conclusión final */}
//             {solution.final_conclusion && (
//               <>
//                 <div className="bg-blue-50 p-4 rounded">
//                   <h3 className="font-bold mb-2">Conclusión Final</h3>
//                   <p className="whitespace-pre-line">{solution.final_conclusion.interpretation}</p>
//                 </div>

//                 <div className="bg-yellow-50 p-4 rounded">
//                   <h3 className="font-bold mb-2">Desglose de Costos</h3>
//                   <pre className="whitespace-pre-wrap">{solution.final_conclusion.cost_breakdown}</pre>
//                 </div>

//                 {solution.final_conclusion.recommendations && (
//                   <div className="bg-red-50 p-4 rounded">
//                     <h3 className="font-bold mb-2">Recomendaciones</h3>
//                     <ul className="list-disc list-inside">
//                       {solution.final_conclusion.recommendations.map((rec, index) => (
//                         <li key={index}>{rec}</li>
//                       ))}
//                     </ul>
//                   </div>
//                 )}
//               </>
//             )}

//             {/* Escenarios de empate */}
//             {solution.tie_scenarios && solution.tie_scenarios.length > 0 && (
//               <div className="bg-purple-50 p-4 rounded">
//                 <h3 className="font-bold mb-2">Escenarios de Empate Detectados</h3>
//                 <ul className="list-disc list-inside">
//                   {solution.tie_scenarios.map((scenario, index) => (
//                     <li key={index}>{scenario}</li>
//                   ))}
//                 </ul>
//               </div>
//             )}
//           </div>
//         )}
//       </div>
//     </div>
//   );
// };

// export default SolutionResults;



import { useState } from 'react';
import StepByStepViewer from '../components/steps/StepByStepViewer';
import AlternativeSolutions from '../components/solutions/AlternativeSolutions';
import SolutionTable from '../components/tables/SolutionTable';
import TransportSummary from '../components/analysis/TransportSummary';

const SolutionResults = ({ solution, problem }) => {
  const [activeTab, setActiveTab] = useState('main');

  if (!solution) {
    return <div className="text-gray-500">No hay solución para mostrar</div>;
  }

  const tabs = [
    { id: 'main', name: '🗂️ Solución Principal' },
    { id: 'steps', name: '🔄 Paso a Paso' },
    { id: 'alternatives', name: '🔀 Soluciones Alternativas' },
    { id: 'summary', name: '📊 Resumen Completo' },
    { id: 'analysis', name: '📈 Análisis Final' }
  ];

  return (
    <div className="bg-white rounded-lg shadow-md">
      {/* Tabs de navegación */}
      <div className="border-b">
        <nav className="flex overflow-x-auto">
          {tabs.map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-4 py-2 font-medium whitespace-nowrap ${
                activeTab === tab.id
                  ? 'border-b-2 border-blue-500 text-blue-600'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              {tab.name}
            </button>
          ))}
        </nav>
      </div>

      {/* Contenido de los tabs */}
      <div className="p-6">
        {activeTab === 'main' && (
          <div className="space-y-6">
            <div>
              <h2 className="text-2xl font-bold mb-4">Solución Principal</h2>
              <SolutionTable 
                solution={solution.main_solution}
                costs={problem.costs}
                supply={problem.supply}
                demand={problem.demand}
              />
            </div>
            
            {/* Información básica */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-blue-50 p-4 rounded border border-blue-200">
                <p className="font-semibold text-blue-800">Método</p>
                <p className="text-lg">{solution.method}</p>
              </div>
              <div className="bg-green-50 p-4 rounded border border-green-200">
                <p className="font-semibold text-green-800">Costo Total</p>
                <p className="text-lg">{solution.total_cost}</p>
              </div>
              <div className="bg-purple-50 p-4 rounded border border-purple-200">
                <p className="font-semibold text-purple-800">Tiempo</p>
                <p className="text-lg">{solution.execution_time?.toFixed(4)}s</p>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'steps' && (
          <StepByStepViewer 
            steps={solution.step_by_step}
            costs={problem.costs}
            supply={problem.supply}
            demand={problem.demand}
          />
        )}

        {activeTab === 'alternatives' && solution.has_multiple_solutions && (
          <AlternativeSolutions 
            alternatives={solution.alternative_solutions}
            mainSolution={problem}
            mainCost={solution.total_cost}
          />
        )}

        {activeTab === 'alternatives' && !solution.has_multiple_solutions && (
          <div className="text-center py-8 text-gray-500">
            No hay soluciones alternativas disponibles
          </div>
        )}

        {activeTab === 'summary' && solution.transport_summary && (
          <TransportSummary transportSummary={solution.transport_summary} />
        )}

        {activeTab === 'analysis' && solution.final_conclusion && (
          <div className="space-y-6">
            {/* Conclusión final */}
            <div className="bg-blue-50 p-6 rounded-lg border border-blue-200">
              <h3 className="font-bold text-xl text-blue-800 mb-4">🎯 Conclusión Final</h3>
              <p className="text-gray-700 whitespace-pre-line leading-relaxed">
                {solution.final_conclusion.interpretation}
              </p>
            </div>

            {/* Desglose de costos */}
            <div className="bg-green-50 p-6 rounded-lg border border-green-200">
              <h3 className="font-bold text-xl text-green-800 mb-4">💰 Desglose de Costos</h3>
              <pre className="bg-white p-4 rounded border text-gray-700 whitespace-pre-wrap font-mono">
                {solution.final_conclusion.cost_breakdown}
              </pre>
            </div>

            {/* Recomendaciones */}
            {solution.final_conclusion.recommendations && (
              <div className="bg-yellow-50 p-6 rounded-lg border border-yellow-200">
                <h3 className="font-bold text-xl text-yellow-800 mb-4">💡 Recomendaciones</h3>
                <ul className="space-y-2">
                  {solution.final_conclusion.recommendations.map((rec, index) => (
                    <li key={index} className="flex items-start">
                      <span className="bg-yellow-100 text-yellow-800 rounded-full w-6 h-6 flex items-center justify-center text-sm font-semibold mr-3 mt-1 flex-shrink-0">
                        {index + 1}
                      </span>
                      <span className="text-gray-700">{rec}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Eficiencia */}
            {solution.final_conclusion.efficiency_note && (
              <div className="bg-purple-50 p-6 rounded-lg border border-purple-200">
                <h3 className="font-bold text-xl text-purple-800 mb-4">⚡ Eficiencia</h3>
                <p className="text-gray-700">{solution.final_conclusion.efficiency_note}</p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default SolutionResults;