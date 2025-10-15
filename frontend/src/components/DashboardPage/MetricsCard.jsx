import MetricCard from './MetricCard';

export default function MetricsCards({ data }) {
  return (
    <div className="row g-3 mb-4">
      <div className="col-md-3">
        <MetricCard
          title="Total Students"
          value={data.amountOfEnrolments.amountOfEnrolments}
          change={data.amountOfEnrolments.change}
          trend={data.amountOfEnrolments.trend}
          icon="bi-people-fill"
          color="#004aad"
          bgColor="#e7f1ff"
        />
      </div>
      <div className="col-md-3">
        <MetricCard
          title="Avg Attendance"
          value={`${data.attendanceInformation.attendanceRate.toFixed(0)}%`}
          change={data.attendanceInformation.change}
          trend={data.attendanceInformation.trend}
          icon="bi-clipboard-check-fill"
          color="#004aad"
          bgColor="#e7f1ff"
        />
    </div>  
    <div className="col-md-3">
        <MetricCard
          title="Term Revenue"
          value={`$${data.revenueInformation.revenue}`}
          change={data.revenueInformation.change}
          trend={data.revenueInformation.trend}
          icon="bi-cash-coin"
          color="#17a2b8"
          bgColor="#d1ecf1"
        />
      </div>
      {/* <div className="col-md-3">
        <MetricCard
          title="Payment Rate"
          value={`${data.paymentRate.value}%`}
          change={data.paymentRate.change}
          trend={data.paymentRate.trend}
          icon="bi-credit-card-fill"
          color="#6c757d"
          bgColor="#e9ecef"
        />
      </div> */}
    </div>
  );
}