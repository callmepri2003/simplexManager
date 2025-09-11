import axios from "axios";
import { useEffect, useState } from "react";

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

// ----- Groups Services -----
export function useAllGroups(){
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    API.get('/api/groups/')
      .then(res => setData(res.data))
      .catch(err => setError(err))
      .finally(() => setLoading(false))
  }, [])
  return [data, loading, error]
}

export default API;
