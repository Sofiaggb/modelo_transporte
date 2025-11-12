import { useState, useEffect } from 'react';
import ProblemForm from '../components/forms/ProblemForm';
import SolutionTable from '../components/tables/SolutionTable';
import { transportAPI } from '../services/api';
import SolutionResults from './SolutionResults';

const Home = () => {
  const [problems, setProblems] = useState([]);
  const [selectedProblem, setSelectedProblem] = useState(null);
  const [solution, setSolution] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadProblems();
  }, []);

  const loadProblems = async () => {
    try {
      const data = await transportAPI.getProblems();
      setProblems(data);
    } catch (error) {
      console.error('Error loading problems:', error);
    }
  };

  const handleCreateProblem = async (problemData) => {
    try {
      await transportAPI.createProblem(problemData);
      await loadProblems();
      alert('Problema creado exitosamente!');
    } catch (error) {
      console.error('Error creating problem:', error);
    }
  };

  const handleSolve = async (method) => {
    if (!selectedProblem) return;
    
    setLoading(true);
    try {
      const result = await transportAPI.solveProblem(selectedProblem.id, method);
      setSolution(result);
    } catch (error) {
      console.error('Error solving problem:', error);
      alert('Error al resolver el problema');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 p-6">
      <div className="max-w-7xl mx-auto">
        <div className='flex gap-8'>
            <div>
            <h3>UPTAIET - San Cristóbal</h3>
        <h3>Materia: Investigación de operaciones </h3>

            {/* </div>
            <div> */}
        <h3>Nombre: Sofia Gaitán </h3>
        <h3>CI: 31.469.702 </h3>
        <h3>Sección: SID3E</h3>

            </div>
        </div>
        
        <h1 className="text-3xl text-center font-bold text-gray-800 mb-8">
          Sistema de Modelos de Transporte 
        </h1>

        <div className="">
          {/* Formulario */}
          <div>
            <ProblemForm onSubmit={handleCreateProblem} />
          </div>

          {/* Lista de problemas y soluciones */}
          <div className="space-y-6">
            {/* Selección de problema */}
            <div className="bg-white p-6 rounded-lg shadow-md">
              <h2 className="text-xl font-bold mb-4">Problemas Existentes</h2>
              <select
                value={selectedProblem?.id || ''}
                onChange={(e) => {
                  const problem = problems.find(p => p.id === parseInt(e.target.value));
                  setSelectedProblem(problem);
                  setSolution(null);
                }}
                className="w-full p-2 border border-gray-300 rounded"
              >
                <option value="">Seleccionar problema</option>
                {problems.map(problem => (
                  <option key={problem.id} value={problem.id}>
                    {problem.name}
                  </option>
                ))}
              </select>

              {/* Métodos de solución */}
              {selectedProblem && (
                <div className="mt-4">
                  <h3 className="font-semibold mb-2">Métodos de solución:</h3>
                  <div className="flex gap-2">
                    {['northwest', 'min_cost', 'vogel'].map(method => (
                      <button
                        key={method}
                        onClick={() => handleSolve(method)}
                        disabled={loading}
                        className="bg-green-500 text-white px-3 py-1 rounded hover:bg-green-600 disabled:bg-gray-400"
                      >
                        {method === 'northwest' ? 'Esq. Noroeste' : 
                         method === 'min_cost' ? 'Costo Mínimo' : 'Vogel'}
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Resultados */}
            {solution && (
            <SolutionResults 
                solution={solution} 
                problem={selectedProblem} 
            />
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Home;