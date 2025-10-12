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
import { useGetDashboardData } from '../services/api';

export default function DashboardPage() {
  // Calculate default date range (last 90 days)
  const [dateRange, setDateRange] = useState(() => {
    const end = new Date();
    const start = new Date();
    start.setDate(start.getDate() - 90);
    return {
      start: start.toISOString().split('T')[0],
      end: end.toISOString().split('T')[0]
    };
  });

  // Fetch dashboard data with the current date range
  const [dashboardData, loading, error] = useGetDashboardData(
    dateRange.start,
    dateRange.end
  );

  // Handle date range change
  const handleDateRangeChange = (newRange) => {
    setDateRange(newRange);
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
  if (!dashboardData) {
    return (
      <div className="container-fluid py-4" style={{ backgroundColor: '#f8f9fa', minHeight: '100vh' }}>
        <div className="alert alert-info" role="alert">
          <h4 className="alert-heading">No Data Available</h4>
          <p>There is no dashboard data available for the selected date range.</p>
        </div>
      </div>
    );
  }

  // Extract data from API response
  const {
    metricsData,
    attendanceData,
    revenueData,
    groupPerformance,
    engagementDistribution,
    atRiskStudents,
    topPerformers
  } = dashboardData;

  return (
    <div className="container-fluid py-4" style={{ backgroundColor: '#f8f9fa', minHeight: '100vh' }}>
      <DashboardHeader 
        dateRange={dateRange}
        onDateRangeChange={handleDateRangeChange}
      />

      <MetricsCards data={metricsData} />

      <div className="row g-3 mb-4">
        <div className="col-lg-8">
          <AttendanceTrendsChart data={attendanceData} />
        </div>
        <div className="col-lg-4">
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
      </div>
    </div>
  );
}