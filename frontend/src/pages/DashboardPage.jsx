// Dashboard/Dashboard.jsx
import { useState } from 'react';
import MetricsCards from '../components/DashboardPage/MetricsCard';
import AtRiskStudents from '../components/DashboardPage/AtRiskStudents';
import AttendanceTrendsChart from '../components/DashboardPage/AttendanceTrendsChart';
import DashboardHeader from '../components/DashboardPage/DashboardHeader';
import GroupPerformanceChart from '../components/DashboardPage/GroupPerformanceChart';
import RevenueChart from '../components/DashboardPage/RevenueChart';
import StudentEngagementChart from '../components/DashboardPage/StudentEngagementChart';
import TopPerformers from '../components/DashboardPage/TopPerformers';
import ComingSoonSplash from './DashboardComingSoon'
export default function DashboardPage() {
  return <ComingSoonSplash />;
  const [selectedTerm, setSelectedTerm] = useState('2024-3');

  // Mock data - replace with real data later
  const metricsData = {
    totalStudents: { value: 247, change: 12, trend: 'up' },
    avgAttendance: { value: 89.2, change: 3.5, trend: 'up' },
    termRevenue: { value: 28450, change: 8, trend: 'up' },
    paymentRate: { value: 94.7, change: -1.2, trend: 'down' }
  };

  const attendanceData = [
    { week: 'Week 1', rate: 92 },
    { week: 'Week 2', rate: 88 },
    { week: 'Week 3', rate: 91 },
    { week: 'Week 4', rate: 85 },
    { week: 'Week 5', rate: 89 },
    { week: 'Week 6', rate: 93 },
    { week: 'Week 7', rate: 87 },
    { week: 'Week 8', rate: 90 },
  ];

  const revenueData = [
    { month: 'Jan', revenue: 4200 },
    { month: 'Feb', revenue: 4500 },
    { month: 'Mar', revenue: 4800 },
    { month: 'Apr', revenue: 5100 },
    { month: 'May', revenue: 4900 },
    { month: 'Jun', revenue: 5300 },
  ];

  const groupPerformance = [
    { name: 'Year 12 Ext 1', attendance: 95, payment: 98, homework: 92 },
    { name: 'Year 11 Adv', attendance: 88, payment: 95, homework: 85 },
    { name: 'Junior Maths', attendance: 91, payment: 92, homework: 88 },
    { name: 'Year 10', attendance: 86, payment: 89, homework: 82 },
  ];

  const engagementDistribution = [
    { name: 'High (>90%)', value: 45, color: '#004aad' },
    { name: 'Medium (70-90%)', value: 35, color: '#17a2b8' },
    { name: 'Low (<70%)', value: 12, color: '#ffc107' },
    { name: 'At Risk', value: 8, color: '#dc3545' },
  ];

  const atRiskStudents = [
    { id: 1, name: 'John Smith', attendance: 65, payment: 70, lastAbsence: '3 days ago' },
    { id: 2, name: 'Emma Wilson', attendance: 72, payment: 60, lastAbsence: '1 week ago' },
    { id: 3, name: 'Michael Brown', attendance: 68, payment: 75, lastAbsence: '5 days ago' },
  ];

  const topPerformers = [
    { id: 1, name: 'Sarah Johnson', engagement: 98, streak: 12 },
    { id: 2, name: 'David Lee', engagement: 96, streak: 10 },
    { id: 3, name: 'Alice Chen', engagement: 95, streak: 15 },
  ];

  return (
    <div className="container-fluid py-4" style={{ backgroundColor: '#f8f9fa', minHeight: '100vh' }}>
      <DashboardHeader 
        selectedTerm={selectedTerm}
        onTermChange={setSelectedTerm}
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