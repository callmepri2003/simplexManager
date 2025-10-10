export default function TopPerformers({ students }) {
  return (
    <div className="card border-0 shadow-sm">
      <div className="card-body">
        <h5 className="fw-semibold mb-4" style={{ color: '#004aad' }}>
          <i className="bi bi-trophy-fill me-2"></i>
          Top Performers
        </h5>
        <div className="list-group list-group-flush">
          {students.map((student, index) => (
            <div key={student.id} className="list-group-item border-0 px-0">
              <div className="d-flex justify-content-between align-items-center">
                <div className="d-flex align-items-center">
                  <div className="rounded-circle bg-primary bg-opacity-10 p-2 me-3 position-relative" style={{ width: '45px', height: '45px' }}>
                    <i className="bi bi-person-fill fs-5" style={{ color: '#004aad' }}></i>
                    {index === 0 && (
                      <span className="position-absolute top-0 start-100 translate-middle">
                        <i className="bi bi-star-fill text-warning"></i>
                      </span>
                    )}
                  </div>
                  <div>
                    <h6 className="mb-1 fw-semibold">{student.name}</h6>
                    <small className="text-muted">
                      <i className="bi bi-fire text-danger me-1"></i>
                      {student.streak} week streak
                    </small>
                  </div>
                </div>
                <div>
                  <div className="badge" style={{ fontSize: '1rem', padding: '0.5rem 0.75rem', backgroundColor: '#004aad', color: 'white' }}>
                    {student.engagement}%
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
        <button className="btn w-100 mt-3" style={{ backgroundColor: '#004aad', color: 'white', borderColor: '#004aad' }}>
          View All High Performers
        </button>
      </div>
    </div>
  );
}