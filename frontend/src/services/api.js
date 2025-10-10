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

    // Don't intercept refresh token requests to avoid infinite loops
    if (originalRequest.url?.includes('/api/token/refresh/')) {
      localStorage.removeItem("authTokens");
      console.log('Refresh token expired - clearing auth');
      // Optionally redirect to login
      // window.location.href = '/login';
      return Promise.reject(error);
    }

    // Only handle 401 errors once per request
    if (error.response?.status !== 401 || originalRequest._retry) {
      return Promise.reject(error);
    }

    // Queue requests while refresh is in progress
    if (isRefreshing) {
      return new Promise((resolve, reject) => {
        failedQueue.push({ resolve, reject });
      }).then((token) => {
        originalRequest.headers.Authorization = `Bearer ${token}`;
        return API(originalRequest);
      });
    }

    // Start token refresh process
    originalRequest._retry = true;
    isRefreshing = true;

    try {
      const tokens = JSON.parse(localStorage.getItem("authTokens") || "{}");

      if (!tokens?.refresh) {
        throw new Error("No refresh token available");
      }

      const { data } = await API.post("/api/token/refresh/", {
        refresh: tokens.refresh,
      });

      // Update tokens
      const newTokens = { ...tokens, access: data.access };
      localStorage.setItem("authTokens", JSON.stringify(newTokens));
      API.defaults.headers.Authorization = `Bearer ${data.access}`;

      // Retry queued requests
      processQueue(null, data.access);
      console.log('Token refreshed successfully');
      return API(originalRequest);
    } catch (err) {
      // Clear auth tokens on refresh failure
      localStorage.removeItem("authTokens");
      processQueue(err, null);
      console.log('Token refresh failed - user logged out');
      // Optionally redirect to login
      // window.location.href = '/login';
      return Promise.reject(err);
    } finally {
      isRefreshing = false;
    }
  }
);

// ----- Auth -----
export const login = (username, password) => API.post("/api/token/", { username, password });
export const refreshToken = (refresh) => API.post("/api/token/refresh/", { refresh });

// ----- Groups Services -----

// GET *
export function useGetAllGroups(){
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    API.get('/api/groups/')
      .then(res => {
        setData(res.data);
      })
      .catch(err => {
        console.error("Error fetching groups:", err);
        setError(err);
      })
      .finally(() => {
        setLoading(false);
      });

  }, [])
  return [data, loading, error]
}

// GET :id
export function useGetGroup(id){
  const [groupInformation, setGroupInformation] = useState(null);
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    API.get(`/api/groups/${id}/`)
      .then(res => setGroupInformation(res.data))
      .catch(err => setError(err))
      .finally(() => setLoading(false))
  }, [id])
  return [groupInformation, loading, error]
}

// ----- Attendance Services -----

// POST (Bulk)
export async function postBulkAttendances(attendanceData) {
  try {
    const res = await API.post('/api/attendances/bulk/', attendanceData);
    return res.data; // success
  } catch (err) {
    throw err; // let caller handle error
  }
}

// PUT (Edit single attendance)
export async function editAttendance(id, attendanceData) {
  try {
    const res = await API.put(`/api/attendances/${id}/`, attendanceData);
    return res.data;
  } catch (err) {
    throw err;
  }
}


// ----- Lesson Services -----
export async function newLesson(lessonData){
  try {
    return API.post('/api/lessons/', lessonData);
  } catch (err) {
    throw err;
  }
}

export async function deleteLesson(id){
  try {
    return API.delete(`/api/lessons/${id}/`);
  } catch (err) {
    throw err;
  }
}

// ----- Resource Services -----
export async function newResources(resourceData){
  try {
    return API.post('/api/resources/', resourceData, {
      headers: { "Content-Type": "multipart/form-data" }
    });
  } catch (err) {
    throw err;
  }
}

export default API;
