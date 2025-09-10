import { Navigate } from "react-router-dom";

export default function AdminRoute({ children }) {
  const authTokens = JSON.parse(localStorage.getItem("authTokens") || "null");

  const isAdmin =
    authTokens?.roles?.includes("Admin") && Boolean(authTokens?.access);

  return isAdmin ? children : <Navigate to="/unauthorised" />;
}
