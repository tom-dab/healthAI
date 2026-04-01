import axios from "axios";

const api = axios.create({
  baseURL: "http://localhost:8000",
  timeout: 5000
});

// Intercepteur pour ajouter automatiquement le token JWT
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("authToken");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// ─── AUTHENTIFICATION ───
export const authAPI = {
  login: (email, password) => api.post("/auth/login", { email, password }),
  register: (userData) => api.post("/auth/register", userData),
  getProfile: () => api.get("/auth/profile"),
  updateProfile: (userData) => api.put("/auth/profile", userData),
  logout: () => api.post("/auth/logout")
};

// ─── UTILISATEURS ───
export const usersAPI = {
  getUsers: (params = {}) => api.get("/api/v1/users", { params }),
  getUser: (id) => api.get(`/api/v1/users/${id}`),
  createUser: (userData) => api.post("/api/v1/users", userData),
  updateUser: (id, userData) => api.put(`/api/v1/users/${id}`, userData),
  deleteUser: (id) => api.delete(`/api/v1/users/${id}`)
};

// ─── NUTRITION ───
export const nutritionAPI = {
  getNutritionItems: (params = {}) => api.get("/api/v1/nutrition", { params }),
  getNutritionItem: (id) => api.get(`/api/v1/nutrition/${id}`),
  createNutritionItem: (itemData) => api.post("/api/v1/nutrition", itemData),
  updateNutritionItem: (id, itemData) => api.put(`/api/v1/nutrition/${id}`, itemData),
  deleteNutritionItem: (id) => api.delete(`/api/v1/nutrition/${id}`),

  // Food Logs
  getFoodLogs: (userId, params = {}) => api.get(`/api/v1/users/${userId}/food-logs`, { params }),
  createFoodLog: (userId, logData) => api.post(`/api/v1/users/${userId}/food-logs`, logData),
  deleteFoodLog: (userId, logId) => api.delete(`/api/v1/users/${userId}/food-logs/${logId}`)
};

// ─── EXERCICES ───
export const exercisesAPI = {
  getExercises: (params = {}) => api.get("/api/v1/exercises", { params }),
  getExercise: (id) => api.get(`/api/v1/exercises/${id}`),
  createExercise: (exerciseData) => api.post("/api/v1/exercises", exerciseData),
  updateExercise: (id, exerciseData) => api.put(`/api/v1/exercises/${id}`, exerciseData),
  deleteExercise: (id) => api.delete(`/api/v1/exercises/${id}`),

  // Workout Logs
  getWorkoutLogs: (userId, params = {}) => api.get(`/api/v1/users/${userId}/workout-logs`, { params }),
  createWorkoutLog: (userId, logData) => api.post(`/api/v1/users/${userId}/workout-logs`, logData),
  deleteWorkoutLog: (userId, logId) => api.delete(`/api/v1/users/${userId}/workout-logs/${logId}`)
};

// ─── FONCTIONS DE COMPATIBILITÉ (pour migration progressive) ───
export const getUsers = () => usersAPI.getUsers();
export const getExercises = () => exercisesAPI.getExercises();
export const getFoods = () => nutritionAPI.getNutritionItems();
export const getMetrics = () => Promise.resolve({ data: [] }); // TODO: implémenter métriques

export default api;