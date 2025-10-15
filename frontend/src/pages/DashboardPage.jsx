// Dashboard/Dashboard.jsx
import { useState, useMemo } from 'react';
import MetricsCards from '../components/DashboardPage/MetricsCard';
import AtRiskStudents from '../components/DashboardPage/AtRiskStudents';
import AttendanceTrendsChart from '../components/DashboardPage/AttendanceTrendsChart';
import DashboardHeader from '../components/DashboardPage/DashboardHeader';
import GroupPerformanceChart from '../components/DashboardPage/GroupPerformanceChart';
import RevenueChart from '../components/DashboardPage/RevenueChart';
import StudentEngagementChart from '../components/DashboardPage/StudentEngagementChart';
import TopPerformers from '../components/DashboardPage/TopPerformers';
import { useGetAnalytics } from '../services/api';

export default function DashboardPage() {
  // Default term range: current NSW school term (e.g. "25T3")
  const [termRange, setTermRange] = useState(() => {
    const now = new Date();
    const year = now.getFullYear() % 100; // e.g. 2025 → 25
    const month = now.getMonth() + 1;

    let term;
    if (month >= 1 && month <= 3) term = 1;        // Jan–Mar → Term 1
    else if (month >= 4 && month <= 6) term = 2;   // Apr–Jun → Term 2
    else if (month >= 7 && month <= 9) term = 3;   // Jul–Sep → Term 3
    else term = 4;                                 // Oct–Dec → Term 4

    return `${year}T${term}`;
  });

  // Fetch dashboard data with the current NSW school term
  const [analyticsData, loading, error] = useGetAnalytics(termRange);


  // Handle date range change
  const handleTermChange = (newTerm) => {
    setTermRange(newTerm);
  };

  // Show loading state
  if (loading) {
    return (
      <div className="container-fluid py-4" style={{ backgroundColor: '#f8f9fa', minHeight: '100vh' }}>
        <div className="d-flex justify-content-center align-items-center" style={{ minHeight: '60vh' }}>
          <div className="spinner-border text-primary" role="status" style={{ width: '3rem', height: '3rem' }}>
            <span className="visually-hidden">Loading...</span>
          </div>
        </div>
      </div>
    );
  }

  // Show error state
  if (error) {
    return (
      <div className="container-fluid py-4" style={{ backgroundColor: '#f8f9fa', minHeight: '100vh' }}>
        <div className="alert alert-danger" role="alert">
          <h4 className="alert-heading">Error Loading Dashboard</h4>
          <p>Unable to load dashboard data. Please try refreshing the page.</p>
          <hr />
          <p className="mb-0">{error.message || 'Unknown error occurred'}</p>
        </div>
      </div>
    );
  }

  // Show empty state if no data
  // if (!dashboardData) {
  //   return (
  //     <div className="container-fluid py-4" style={{ backgroundColor: '#f8f9fa', minHeight: '100vh' }}>
  //       <div className="alert alert-info" role="alert">
  //         <h4 className="alert-heading">No Data Available</h4>
  //         <p>There is no dashboard data available for the selected date range.</p>
  //       </div>
  //     </div>
  //   );
  // }

  // Extract data from API response
  const {
    amount_of_enrolments,
    revenue_information,
    attendance_information,
    weekly_attendance_information
  } = analyticsData;
  console.log(amount_of_enrolments);
  return (
    <div className="container-fluid py-4" style={{ backgroundColor: '#f8f9fa', minHeight: '100vh' }}>
      <DashboardHeader term={termRange} onTermChange={handleTermChange} />

  
      <MetricsCards data={{
        "amountOfEnrolments": amount_of_enrolments,
        "revenueInformation": revenue_information,
        "attendanceInformation": attendance_information,
      }} />

       <div className="row g-3 mb-4">
        <div className="col-lg-8">
          <AttendanceTrendsChart data={weekly_attendance_information} />
        </div>
      </div>
      {/*  <div className="col-lg-4">
          <StudentEngagementChart data={engagementDistribution} />
        </div>
      </div>

      <div className="row g-3 mb-4">
        <div className="col-12">
          <RevenueChart data={revenueData} />
        </div>
      </div>

      <div className="row g-3 mb-4">
        <div className="col-12">
          <GroupPerformanceChart data={groupPerformance} />
        </div>
      </div>

      <div className="row g-3">
        <div className="col-lg-6">
          <AtRiskStudents students={atRiskStudents} />
        </div>
        <div className="col-lg-6">
          <TopPerformers students={topPerformers} />
        </div>
      </div> */}
    </div>
  );
}