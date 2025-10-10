import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

export default function RevenueChart({ data }) {
  return (
    <div className="card border-0 shadow-sm">
      <div className="card-body">
        <h5 className="fw-semibold mb-4" style={{ color: '#004aad' }}>
          <i className="bi bi-currency-dollar me-2"></i>
          Revenue Overview
        </h5>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
            <XAxis dataKey="month" stroke="#6c757d" />
            <YAxis stroke="#6c757d" />
            <Tooltip />
            <Legend />
            <Bar dataKey="revenue" fill="#17a2b8" name="Revenue ($)" radius={[8, 8, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}