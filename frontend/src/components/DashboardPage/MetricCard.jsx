export default function MetricCard({ title, value, change, trend, icon, color, bgColor }) {
  return (
    <div className="card border-0 shadow-sm h-100">
      <div className="card-body">
        <div className="d-flex justify-content-between align-items-start mb-3">
          <div>
            <p className="text-muted mb-1 small">{title}</p>
            <h3 className="fw-bold mb-0" style={{ color }}>{value}</h3>
          </div>
          <div className="rounded-circle p-3" style={{ backgroundColor: bgColor }}>
            <i className={`bi ${icon} fs-4`} style={{ color }}></i>
          </div>
        </div>
        <div className="d-flex align-items-center">
          <span className={`badge ${trend === '+' ? 'bg-success' : 'bg-danger'} bg-opacity-10 ${trend === '+' ? 'text-success' : 'text-danger'} me-2`}>
            <i className={`bi ${trend === '+' ? 'bi-arrow-up' : 'bi-arrow-down'} me-1`}></i>
            {trend === '+' ? '+' : ''}{change}%
          </span>
          <small className="text-muted">vs last term</small>
        </div>
      </div>
    </div>
  );
}