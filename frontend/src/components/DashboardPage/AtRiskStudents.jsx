export default function AtRiskStudents({ students }) {
  return (
    <div className="card border-0 shadow-sm">
      <div className="card-body">
        <h5 className="fw-semibold mb-4" style={{ color: '#dc3545' }}>
          <i className="bi bi-exclamation-triangle-fill me-2"></i>
          Students At Risk
        </h5>
        <div className="list-group list-group-flush">
          {students.map((student) => (
            <div key={student.id} className="list-group-item border-0 px-0">
              <div className="d-flex justify-content-between align-items-start">
                <div className="d-flex align-items-center">
                  <div className="rounded-circle bg-danger bg-opacity-10 p-2 me-3" style={{ width: '45px', height: '45px' }}>
                    <i className="bi bi-person-fill fs-5" style={{ color: '#dc3545' }}></i>
                  </div>
                  <div>
                    <h6 className="mb-1 fw-semibold">{student.name}</h6>
                    <small className="text-muted">Last absence: {student.lastAbsence}</small>
                  </div>
                </div>
                <div className="text-end">
                  <div className="mb-1">
                    <span className="badge bg-warning text-dark">
                      {student.attendance}% attendance
                    </span>
                  </div>
                  <div>
                    <span className="badge bg-info text-dark">
                      {student.payment}% paid
                    </span>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
        <button className="btn btn-outline-danger w-100 mt-3">
          View All At-Risk Students
        </button>
      </div>
    </div>
  );
}