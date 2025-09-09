import { useEffect } from "react";
import { useNavigate } from "react-router-dom";

export default function LogoutPage() {
  const navigate = useNavigate();

  useEffect(() => {
    // Clear JWT token
    localStorage.clear();

    // Redirect
    navigate("/login");
  }, [navigate]);

  return null; // or a loading spinner/message
}
