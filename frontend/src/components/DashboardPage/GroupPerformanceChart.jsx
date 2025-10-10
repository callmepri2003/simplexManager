import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

export default function GroupPerformanceChart({ data }) {
  return (
    <div className="card border-0 shadow-sm">
      <div className="card-body">
        <h5 className="fw-semibold mb-4" style={{ color: '#004aad' }}>
          <i className="bi bi-bar-chart-fill me-2"></i>
          Group Performance
        </h5>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
            <XAxis dataKey="name" stroke="#6c757d" />
            <YAxis stroke="#6c757d" domain={[0, 100]} />
            <Tooltip />
            <Legend />
            <Bar dataKey="attendance" fill="#004aad" name="Attendance (%)" radius={[4, 4, 0, 0]} />
            <Bar dataKey="payment" fill="#17a2b8" name="Payment (%)" radius={[4, 4, 0, 0]} />
            <Bar dataKey="homework" fill="#6c757d" name="Homework (%)" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}