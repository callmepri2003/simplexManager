import axios from "axios";

const API = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
});

// ----- Request interceptor -----
API.interceptors.request.use((req) => {
  const tokens = localStorage.getItem("authTokens");
  if (tokens) {
    req.headers.Authorization = `Bearer ${JSON.parse(tokens).access}`;
  }
  return req;
});

// ----- Response interceptor for token refresh -----
let isRefreshing = false;
let failedQueue = [];

const processQueue = (error, token = null) => {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token);
    }
  });
  failedQueue = [];
};

API.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        // queue the request until refresh finishes
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        }).then((token) => {
          originalRequest.headers.Authorization = `Bearer ${token}`;
          return API(originalRequest);
        });
      }

      originalRequest._retry = true;
      isRefreshing = true;

      const tokens = JSON.parse(localStorage.getItem("authTokens") || "{}");

      if (!tokens?.refresh) {
        isRefreshing = false;
        return Promise.reject(error);
      }

      try {
        const { data } = await API.post("/api/token/refresh/", {
          refresh: tokens.refresh,
        });

        const newTokens = { ...tokens, access: data.access };
        localStorage.setItem("authTokens", JSON.stringify(newTokens));

        API.defaults.headers.Authorization = `Bearer ${data.access}`;

        processQueue(null, data.access);

        return API(originalRequest);
      } catch (err) {
        processQueue(err, null);
        return Promise.reject(err);
      } finally {
        isRefreshing = false;
      }
    }

    return Promise.reject(error);
  }
);

// ----- Auth -----
export const login = (username, password) => API.post("/api/token/", { username, password });
export const refreshToken = (refresh) => API.post("/api/token/refresh/", { refresh });

// ----- Protected Endpoints -----
export const getDashboard = () => API.get("/dashboard");
export const getAdminPanel = () => API.get("/admin");

// ----- Groups Services -----
export const AllGroups = () => API.get("/api/groups/");

export const CreateGroup = (data) => API.post("/api/groups/", data);

export const RetrieveGroup = (id) => API.get(`/api/groups/${id}/`);

export const UpdateGroup = (id, data) => API.put(`/api/groups/${id}/`, data);

export const DeleteGroup = (id) => API.delete(`/api/groups/${id}/`);

// ----- Lesson Roll Services -----

// Get lesson roll data
export const getLessonRoll = (lessonId) => API.get(`/api/lessons/${lessonId}/roll/`);

// Update lesson roll (POST)
export const updateLessonRoll = (lessonId, data) => API.post(`/api/lessons/${lessonId}/roll/`, data);

// Update lesson roll (PUT)
export const updateLessonRollPut = (lessonId, data) => API.put(`/api/lessons/${lessonId}/roll/`, data);

// Reset lesson roll
export const resetLessonRoll = (lessonId) => API.delete(`/api/lessons/${lessonId}/roll/reset/`);

// Get lesson attendance summary
export const getLessonRollSummary = (lessonId) => API.get(`/api/lessons/${lessonId}/roll/summary/`);

export const getLessonByGroup = (groupId) => API.get(`/api/lessons/group/${groupId}/`);

export default API;
