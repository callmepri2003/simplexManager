// components/DashboardPage/DashboardHeader.jsx
import { useState } from "react";

export default function DashboardHeader({ term, onTermChange }) {
  // Detect current year
  const currentYear = new Date().getFullYear() % 100;

  // List of term options
  const termOptions = [
    { label: "Term 1", value: `T1` },
    { label: "Term 2", value: `T2` },
    { label: "Term 3", value: `T3` },
    { label: "Term 4", value: `T4` },
  ];

  // Format readable title like "2025 - Term 3"
  const displayTerm = `${20}${term.slice(0, 2)} - Term ${term.slice(3)}`;

  return (
    <div className="mb-4">
      <div className="d-flex justify-content-between align-items-center mb-3">
        <div>
          <h1 className="h2 mb-1" style={{ color: "#004aad", fontWeight: 600 }}>
            Dashboard
          </h1>
          <p className="text-muted mb-0">{displayTerm}</p>
        </div>

        <div className="btn-group">
          {termOptions.map((option) => (
            <button
              key={option.value}
              type="button"
              className={`btn ${
                term.endsWith(option.value)
                  ? "btn-primary"
                  : "btn-outline-primary"
              }`}
              onClick={() => onTermChange(`${currentYear}${option.value}`)}
            >
              {option.label}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
