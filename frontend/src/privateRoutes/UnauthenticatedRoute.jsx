import { Navigate } from "react-router-dom";

export default function UnauthenticatedRoute({ children }) {
  const authTokens = JSON.parse(localStorage.getItem("authTokens") || "null");
  
  return authTokens?.access ? <Navigate to="/"/> :  children;
}
