import axios from "axios";

const API = axios.create({
  baseURL: process.env.APIBASEURL,
});

API.interceptors.request.use((req) => {
  const tokens = localStorage.getItem("authTokens");
  if (tokens) {
    req.headers.Authorization = `Bearer ${JSON.parse(tokens).access}`;
  }
  return req;
});

// ----- Auth -----
export const login = (username, password) =>
  API.post("/api/token/", { username, password });

export const refreshToken = (refresh) =>
  API.post("/api/token/refresh/", { refresh });

// ----- Protected Endpoints -----
export const getDashboard = () => API.get("/dashboard");
export const getAdminPanel = () => API.get("/admin");

export default API;
