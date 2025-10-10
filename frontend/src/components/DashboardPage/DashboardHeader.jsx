export default function DashboardHeader({ selectedTerm, onTermChange }) {
  return (
    <div className="row mb-4">
      <div className="col-12">
        <div className="d-flex justify-content-between align-items-center">
          <div>
            <h2 className="fw-bold mb-1" style={{ color: '#004aad' }}>Analytics Dashboard</h2>
            <p className="text-muted mb-0">Track performance and student engagement</p>
          </div>
          <div className="d-flex gap-2">
            <select 
              className="form-select" 
              value={selectedTerm}
              onChange={(e) => onTermChange(e.target.value)}
              style={{ width: '200px' }}
            >
              <option value="2024-1">Term 1 2024</option>
              <option value="2024-2">Term 2 2024</option>
              <option value="2024-3">Term 3 2024</option>
              <option value="2024-4">Term 4 2024</option>
              <option value="2024-year">Full Year 2024</option>
            </select>
          </div>
        </div>
      </div>
    </div>
  );
}