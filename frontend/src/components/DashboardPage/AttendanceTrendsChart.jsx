import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

export default function AttendanceTrendsChart({ data }) {
  return (
    <div className="card border-0 shadow-sm h-100">
      <div className="card-body">
        <div className="d-flex justify-content-between align-items-center mb-4">
          <h5 className="fw-semibold mb-0" style={{ color: '#004aad' }}>
            <i className="bi bi-graph-up me-2"></i>
            Attendance Trends
          </h5>
          <div className="btn-group btn-group-sm" role="group">
            <button type="button" className="btn btn-outline-primary active">Weekly</button>
            <button type="button" className="btn btn-outline-primary">Monthly</button>
          </div>
        </div>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
            <XAxis dataKey="week" stroke="#6c757d" />
            <YAxis stroke="#6c757d" domain={[0, 100]} />
            <Tooltip />
            <Legend />
            <Line 
              type="monotone" 
              dataKey="rate" 
              stroke="#004aad" 
              strokeWidth={3}
              dot={{ fill: '#004aad', r: 5 }}
              activeDot={{ r: 7 }}
              name="Attendance Rate (%)"
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}