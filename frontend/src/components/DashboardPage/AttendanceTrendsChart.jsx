import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

export default function AttendanceTrendsChart({ data }) {
  // Custom tooltip to show percentage
  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white border rounded shadow-sm p-2">
          <p className="mb-1 fw-semibold">{payload[0].payload.week}</p>
          <p className="mb-0 text-primary">
            Attendance: <strong>{payload[0].value.toFixed(2)}%</strong>
          </p>
        </div>
      );
    }
    return null;
  };

  console.log(data);

  return (
    <div className="card border-0 shadow-sm h-100">
      <div className="card-body">
        <div className="d-flex justify-content-between align-items-center mb-4">
          <h5 className="fw-semibold mb-0" style={{ color: '#004aad' }}>
            <i className="bi bi-graph-up me-2"></i>
            Attendance Trends
          </h5>
          {/* Future: Add weekly/termly toggle */}
          {/* <div className="btn-group btn-group-sm" role="group">
            <button type="button" className="btn btn-outline-primary active">Weekly</button>
            <button type="button" className="btn btn-outline-primary">Termly</button>
          </div> */}
        </div>
        
        {data && data.length > 0 ? (
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={data}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
              <XAxis 
                dataKey="week" 
                stroke="#6c757d"
                style={{ fontSize: '0.875rem' }}
              />
              <YAxis 
                stroke="#6c757d" 
                domain={[0, 100]}
                style={{ fontSize: '0.875rem' }}
                label={{ value: 'Attendance (%)', angle: -90, position: 'insideLeft' }}
              />
              <Tooltip content={<CustomTooltip />} />
              <Legend 
                wrapperStyle={{ fontSize: '0.875rem' }}
                iconType="line"
              />
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
        ) : (
          <div className="text-center text-muted py-5">
            <i className="bi bi-graph-up" style={{ fontSize: '3rem' }}></i>
            <p className="mt-3">No attendance data available for this term</p>
          </div>
        )}
      </div>
    </div>
  );
}