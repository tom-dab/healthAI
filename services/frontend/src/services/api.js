import axios from "axios";

const api = axios.create({
  baseURL: "http://localhost:8000",
  timeout: 5000
});

export const getUsers = () => api.get("/users");
export const getExercises = () => api.get("/exercises");
export const getFoods = () => api.get("/foods");
export const getMetrics = () => api.get("/metrics");

export default api;