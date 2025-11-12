const API_BASE = 'http://localhost:8000';

export const transportAPI = {
  // Obtener todos los problemas
  getProblems: async () => {
    const response = await fetch(`${API_BASE}/problems`);
    return await response.json();
  },

  // Crear nuevo problema
  createProblem: async (problemData) => {
    const response = await fetch(`${API_BASE}/problems`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(problemData)
    });
    return await response.json();
  },

  // Resolver problema
  solveProblem: async (problemId, method) => {
    const response = await fetch(`${API_BASE}/problems/${problemId}/solve`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ method })
    });
    return await response.json();
  }
};