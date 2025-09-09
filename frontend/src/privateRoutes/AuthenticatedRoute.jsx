import { Navigate } from "react-router-dom";

export default function AuthenticatedRoute({ children }) {
  const authTokens = JSON.parse(localStorage.getItem("authTokens") || "null");

  return authTokens?.access ? children : <Navigate to="/login" />;
}
