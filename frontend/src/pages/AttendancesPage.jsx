import React, { useState, useMemo } from 'react';
import { useGetAllAttendances, useGetAllStudents, useGetAllLessons, useGetAllGroups } from "../services/api";

// Utility function to group attendances by lesson
const groupByLesson = (attendances) => {
  const grouped = {};
  attendances.forEach(att => {
    if (!grouped[att.lesson]) {
      grouped[att.lesson] = [];
    }
    grouped[att.lesson].push(att);
  });
  return grouped;
};

// Header Component with Filters
function AttendanceHeader({ stats, filters, onFilterChange }) {
  const { invoiceStatus, dateRange, selectedStudent, selectedGroup, searchQuery } = filters;

  return (
    <div className="row mb-4">
      <div className="col-12">
        <div className="d-flex justify-content-between align-items-center mb-3">
          <h2 className="mb-0" style={{ color: '#004aad', fontWeight: 600 }}>
            Attendance Overview
          </h2>
          <div className="btn-group" role="group">
            <button
              type="button"
              className={`btn ${invoiceStatus === 'all' ? 'btn-primary' : 'btn-outline-primary'}`}
              onClick={() => onFilterChange('invoiceStatus', 'all')}
              style={{ 
                borderColor: '#004aad', 
                color: invoiceStatus === 'all' ? '#fff' : '#004aad', 
                backgroundColor: invoiceStatus === 'all' ? '#004aad' : 'transparent' 
              }}
            >
              All
            </button>
            <button
              type="button"
              className={`btn ${invoiceStatus === 'invoiced' ? 'btn-primary' : 'btn-outline-primary'}`}
              onClick={() => onFilterChange('invoiceStatus', 'invoiced')}
              style={{ 
                borderColor: '#004aad', 
                color: invoiceStatus === 'invoiced' ? '#fff' : '#004aad', 
                backgroundColor: invoiceStatus === 'invoiced' ? '#004aad' : 'transparent' 
              }}
            >
              Invoiced
            </button>
            <button
              type="button"
              className={`btn ${invoiceStatus === 'not-invoiced' ? 'btn-primary' : 'btn-outline-primary'}`}
              onClick={() => onFilterChange('invoiceStatus', 'not-invoiced')}
              style={{ 
                borderColor: '#004aad', 
                color: invoiceStatus === 'not-invoiced' ? '#fff' : '#004aad', 
                backgroundColor: invoiceStatus === 'not-invoiced' ? '#004aad' : 'transparent' 
              }}
            >
              Not Invoiced
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

// Advanced Filters Component
function AdvancedFilters({ filters, onFilterChange, students, groups, lessons }) {
  const [showFilters, setShowFilters] = useState(false);
  
  const dateRanges = [
    { value: 'all', label: 'All Time' },
    { value: 'today', label: 'Today' },
    { value: 'week', label: 'This Week' },
    { value: 'month', label: 'This Month' },
    { value: 'custom', label: 'Custom Range' },
  ];

  const activeFiltersCount = [
    filters.selectedStudent !== 'all',
    filters.selectedGroup !== 'all',
    filters.dateRange !== 'all',
    filters.searchQuery !== '',
  ].filter(Boolean).length;

  return (
    <div className="row mb-4">
      <div className="col-12">
        <div className="card border-0 shadow-sm" style={{ borderRadius: '12px' }}>
          <div className="card-body">
            <div className="d-flex justify-content-between align-items-center mb-3">
              <div className="d-flex align-items-center gap-2">
                <h6 className="mb-0" style={{ color: '#004aad', fontWeight: 600 }}>
                  Advanced Filters
                </h6>
                {activeFiltersCount > 0 && (
                  <span className="badge bg-primary" style={{ backgroundColor: '#004aad' }}>
                    {activeFiltersCount} active
                  </span>
                )}
              </div>
              <button 
                className="btn btn-sm btn-link text-decoration-none" 
                onClick={() => setShowFilters(!showFilters)}
                style={{ color: '#004aad' }}
              >
                {showFilters ? 'Hide' : 'Show'} Filters
              </button>
            </div>
            
            {showFilters && (
              <div className="row g-3">
                <div className="col-md-3">
                  <label className="form-label" style={{ fontSize: '0.875rem', fontWeight: 500 }}>
                    Search Lessons
                  </label>
                  <input
                    type="text"
                    className="form-control"
                    placeholder="Search by lesson ID..."
                    value={filters.searchQuery}
                    onChange={(e) => onFilterChange('searchQuery', e.target.value)}
                    style={{ fontSize: '0.875rem' }}
                  />
                </div>
                
                <div className="col-md-3">
                  <label className="form-label" style={{ fontSize: '0.875rem', fontWeight: 500 }}>
                    Student
                  </label>
                  <select 
                    className="form-select"
                    value={filters.selectedStudent}
                    onChange={(e) => onFilterChange('selectedStudent', e.target.value)}
                    style={{ fontSize: '0.875rem' }}
                  >
                    <option value="all">All Students</option>
                    {students && students.map(student => (
                      <option key={student.id} value={student.id}>
                        {student.name}
                      </option>
                    ))}
                  </select>
                </div>
                
                <div className="col-md-3">
                  <label className="form-label" style={{ fontSize: '0.875rem', fontWeight: 500 }}>
                    Group
                  </label>
                  <select 
                    className="form-select"
                    value={filters.selectedGroup}
                    onChange={(e) => onFilterChange('selectedGroup', e.target.value)}
                    style={{ fontSize: '0.875rem' }}
                  >
                    <option value="all">All Groups</option>
                    {groups && groups.map(group => (
                      <option key={group.id} value={group.id}>
                        Group {group.id}
                      </option>
                    ))}
                  </select>
                </div>
                
                <div className="col-md-3">
                  <label className="form-label" style={{ fontSize: '0.875rem', fontWeight: 500 }}>
                    Date Range
                  </label>
                  <select 
                    className="form-select"
                    value={filters.dateRange}
                    onChange={(e) => onFilterChange('dateRange', e.target.value)}
                    style={{ fontSize: '0.875rem' }}
                  >
                    {dateRanges.map(range => (
                      <option key={range.value} value={range.value}>
                        {range.label}
                      </option>
                    ))}
                  </select>
                </div>
                
                {filters.dateRange === 'custom' && (
                  <>
                    <div className="col-md-3">
                      <label className="form-label" style={{ fontSize: '0.875rem', fontWeight: 500 }}>
                        From Date
                      </label>
                      <input
                        type="date"
                        className="form-control"
                        value={filters.customStartDate || ''}
                        onChange={(e) => onFilterChange('customStartDate', e.target.value)}
                        style={{ fontSize: '0.875rem' }}
                      />
                    </div>
                    
                    <div className="col-md-3">
                      <label className="form-label" style={{ fontSize: '0.875rem', fontWeight: 500 }}>
                        To Date
                      </label>
                      <input
                        type="date"
                        className="form-control"
                        value={filters.customEndDate || ''}
                        onChange={(e) => onFilterChange('customEndDate', e.target.value)}
                        style={{ fontSize: '0.875rem' }}
                      />
                    </div>
                  </>
                )}
                
                <div className="col-12">
                  <button 
                    className="btn btn-outline-secondary btn-sm"
                    onClick={() => {
                      onFilterChange('selectedStudent', 'all');
                      onFilterChange('selectedGroup', 'all');
                      onFilterChange('dateRange', 'all');
                      onFilterChange('searchQuery', '');
                      onFilterChange('customStartDate', '');
                      onFilterChange('customEndDate', '');
                    }}
                    style={{ fontSize: '0.875rem' }}
                  >
                    Clear All Filters
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

// Stats Cards Component
function StatsCards({ stats }) {
  const cards = [
    { title: 'Total Attendances', value: stats.total, icon: 'fa-clipboard-list', color: '#004aad' },
    { title: 'Invoiced', value: stats.invoiced, icon: 'fa-credit-card', color: '#17a2b8' },
    { title: 'Not Invoiced', value: stats.notInvoiced, icon: 'fa-clock', color: '#ffc107' },
    { title: 'Unique Lessons', value: stats.uniqueLessons, icon: 'fa-book', color: '#28a745' },
  ];

  return (
    <div className="row g-3 mb-4">
      {cards.map((card, idx) => (
        <div key={idx} className="col-lg-3 col-md-6">
          <div className="card border-0 shadow-sm h-100" style={{ borderRadius: '12px' }}>
            <div className="card-body">
              <div className="d-flex justify-content-between align-items-start mb-2">
                <div 
                  className="rounded-circle d-flex align-items-center justify-content-center"
                  style={{ 
                    width: '48px', 
                    height: '48px', 
                    backgroundColor: `${card.color}15`,
                    color: card.color
                  }}
                >
                  <i className={`fas ${card.icon}`} style={{ fontSize: '1.25rem' }}></i>
                </div>
              </div>
              <h6 className="text-muted mb-2" style={{ fontSize: '0.875rem', fontWeight: 500 }}>
                {card.title}
              </h6>
              <h3 className="mb-0" style={{ color: card.color, fontWeight: 700 }}>
                {card.value}
              </h3>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}

// Lesson Card Component
function LessonCard({ lessonId, attendances, studentsMap, lessonsMap }) {
  const [expanded, setExpanded] = useState(false);
  const hasInvoice = attendances.some(att => att.local_invoice);
  const invoiceInfo = attendances.find(att => att.local_invoice)?.local_invoice;
  const lessonData = lessonsMap[lessonId];

  return (
    <div className="card border-0 shadow-sm mb-3" style={{ borderRadius: '12px' }}>
      <div 
        className="card-header bg-white border-0 d-flex justify-content-between align-items-center"
        style={{ cursor: 'pointer', padding: '1.25rem' }}
        onClick={() => setExpanded(!expanded)}
      >
        <div>
          <h5 className="mb-1" style={{ color: '#004aad', fontWeight: 600 }}>
            Lesson {lessonId}
          </h5>
          <div className="d-flex gap-3 align-items-center">
            <small className="text-muted">
              {attendances.length} {attendances.length === 1 ? 'student' : 'students'}
            </small>
            {lessonData && (
              <>
                {lessonData.date && (
                  <small className="text-muted">
                    <i className="far fa-calendar-alt me-1"></i>
                    {new Date(lessonData.date).toLocaleDateString('en-AU', { 
                      day: 'numeric', 
                      month: 'short', 
                      year: 'numeric' 
                    })}
                  </small>
                )}
                {lessonData.group && (
                  <small className="badge" style={{ backgroundColor: '#e7f3ff', color: '#004aad', fontSize: '0.75rem' }}>
                    <i className="fas fa-users me-1"></i>
                    Group {lessonData.group}
                  </small>
                )}
              </>
            )}
          </div>
        </div>
        <div className="d-flex align-items-center gap-3">
          {hasInvoice && (
            <span className="badge" style={{ backgroundColor: '#17a2b8', padding: '0.5rem 0.75rem', fontSize: '0.75rem' }}>
              Invoiced
            </span>
          )}
          <i className={`bi bi-chevron-${expanded ? 'up' : 'down'}`} style={{ fontSize: '1.25rem', color: '#004aad' }}></i>
        </div>
      </div>
      
      {expanded && (
        <div className="card-body" style={{ padding: '1.25rem', backgroundColor: '#f8f9fa' }}>
          {hasInvoice && invoiceInfo && (
            <div className="alert alert-info mb-3" style={{ borderRadius: '8px', backgroundColor: '#e7f3ff', borderColor: '#b3d9ff' }}>
              <h6 className="alert-heading mb-2" style={{ fontSize: '0.875rem', fontWeight: 600 }}>
                Invoice Details
              </h6>
              <div className="row g-2" style={{ fontSize: '0.8rem' }}>
                <div className="col-md-6">
                  <strong>Invoice ID:</strong> {invoiceInfo.stripeInvoiceId || 'N/A'}
                </div>
                <div className="col-md-6">
                  <strong>Status:</strong> <span className={`badge ${invoiceInfo.is_paid ? 'bg-success' : 'bg-warning'} text-dark`}>{invoiceInfo.status}</span>
                </div>
                <div className="col-md-6">
                  <strong>Amount Due:</strong> ${invoiceInfo.amount_due_in_dollars}
                </div>
                <div className="col-md-6">
                  <strong>Created:</strong> {invoiceInfo.created_formatted}
                </div>
              </div>
            </div>
          )}
          
          <div className="table-responsive">
            <table className="table table-hover mb-0">
              <thead style={{ backgroundColor: '#fff' }}>
                <tr>
                  <th style={{ fontSize: '0.875rem', fontWeight: 600, color: '#6c757d', borderBottom: '2px solid #dee2e6' }}>Student</th>
                  <th style={{ fontSize: '0.875rem', fontWeight: 600, color: '#6c757d', borderBottom: '2px solid #dee2e6' }}>Present</th>
                  <th style={{ fontSize: '0.875rem', fontWeight: 600, color: '#6c757d', borderBottom: '2px solid #dee2e6' }}>Homework</th>
                  <th style={{ fontSize: '0.875rem', fontWeight: 600, color: '#6c757d', borderBottom: '2px solid #dee2e6' }}>Paid</th>
                </tr>
              </thead>
              <tbody>
                {attendances.map(att => {
                  const student = studentsMap[att.tutoringStudent];
                  return (
                    <tr key={att.id}>
                      <td style={{ fontSize: '0.875rem', verticalAlign: 'middle' }}>
                        <div className="d-flex align-items-center">
                          <div className="rounded-circle bg-primary d-flex align-items-center justify-content-center text-white me-2" 
                               style={{ width: '32px', height: '32px', fontSize: '0.875rem', fontWeight: 600 }}>
                            {student?.name?.[0]?.toUpperCase() || 'S'}
                          </div>
                          <div>
                            <div style={{ fontWeight: 500 }}>
                              {student?.name || `Student ${att.tutoringStudent}`}
                            </div>
                            <small className="text-muted">ID: {att.tutoringStudent}</small>
                          </div>
                        </div>
                      </td>
                      <td style={{ verticalAlign: 'middle' }}>
                        {att.present ? 
                          <span className="badge bg-success">
                            <i className="fas fa-check me-1"></i>
                            Present
                          </span> : 
                          <span className="badge bg-danger">
                            <i className="fas fa-times me-1"></i>
                            Absent
                          </span>
                        }
                      </td>
                      <td style={{ verticalAlign: 'middle' }}>
                        {att.homework ? 
                          <span className="badge bg-success">
                            <i className="fas fa-check me-1"></i>
                            Done
                          </span> : 
                          <span className="badge bg-secondary">
                            <i className="fas fa-times me-1"></i>
                            Not Done
                          </span>
                        }
                      </td>
                      <td style={{ verticalAlign: 'middle' }}>
                        {att.paid ? 
                          <span className="badge bg-success">
                            <i className="fas fa-check me-1"></i>
                            Paid
                          </span> : 
                          <span className="badge bg-warning text-dark">
                            <i className="fas fa-clock me-1"></i>
                            Unpaid
                          </span>
                        }
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}

// Main Component
export default function AttendancePage() {
  const [attendanceData, attendanceLoading, attendanceError] = useGetAllAttendances();
  const [studentsData, studentsLoading, studentsError] = useGetAllStudents();
  const [lessonsData, lessonsLoading, lessonsError] = useGetAllLessons();
  const [groupsData, groupsLoading, groupsError] = useGetAllGroups();
  
  const [filters, setFilters] = useState({
    invoiceStatus: 'all',
    dateRange: 'all',
    selectedStudent: 'all',
    selectedGroup: 'all',
    searchQuery: '',
    customStartDate: '',
    customEndDate: '',
  });

  const handleFilterChange = (key, value) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  const studentsMap = useMemo(() => {
    if (!studentsData) return {};
    return studentsData.reduce((acc, student) => {
      acc[student.id] = student;
      return acc;
    }, {});
  }, [studentsData]);

  const lessonsMap = useMemo(() => {
    if (!lessonsData) return {};
    return lessonsData.reduce((acc, lesson) => {
      acc[lesson.id] = lesson;
      return acc;
    }, {});
  }, [lessonsData]);

  // Apply all filters
  const filteredData = useMemo(() => {
    if (!attendanceData) return [];
    
    let filtered = [...attendanceData];

    // Invoice status filter
    switch (filters.invoiceStatus) {
      case 'invoiced':
        filtered = filtered.filter(att => att.local_invoice !== null);
        break;
      case 'not-invoiced':
        filtered = filtered.filter(att => att.local_invoice === null);
        break;
    }

    // Student filter
    if (filters.selectedStudent !== 'all') {
      filtered = filtered.filter(att => att.tutoringStudent === parseInt(filters.selectedStudent));
    }

    // Group filter
    if (filters.selectedGroup !== 'all') {
      filtered = filtered.filter(att => {
        const lesson = lessonsMap[att.lesson];
        return lesson && lesson.group === parseInt(filters.selectedGroup);
      });
    }

    // Date range filter
    if (filters.dateRange !== 'all') {
      const now = new Date();
      const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
      
      filtered = filtered.filter(att => {
        const lesson = lessonsMap[att.lesson];
        if (!lesson || !lesson.date) return false;
        
        const lessonDate = new Date(lesson.date);
        
        switch (filters.dateRange) {
          case 'today':
            const lessonDay = new Date(lessonDate.getFullYear(), lessonDate.getMonth(), lessonDate.getDate());
            return lessonDay.getTime() === today.getTime();
          case 'week':
            const weekAgo = new Date(today);
            weekAgo.setDate(weekAgo.getDate() - 7);
            return lessonDate >= weekAgo && lessonDate <= now;
          case 'month':
            const monthAgo = new Date(today);
            monthAgo.setMonth(monthAgo.getMonth() - 1);
            return lessonDate >= monthAgo && lessonDate <= now;
          case 'custom':
            if (filters.customStartDate && filters.customEndDate) {
              const start = new Date(filters.customStartDate);
              const end = new Date(filters.customEndDate);
              end.setHours(23, 59, 59, 999);
              return lessonDate >= start && lessonDate <= end;
            }
            return true;
          default:
            return true;
        }
      });
    }

    // Search filter
    if (filters.searchQuery) {
      filtered = filtered.filter(att => 
        att.lesson.toString().includes(filters.searchQuery)
      );
    }

    return filtered;
  }, [attendanceData, filters, lessonsMap]);

  const stats = useMemo(() => {
    if (!filteredData) return { total: 0, invoiced: 0, notInvoiced: 0, uniqueLessons: 0 };
    
    return {
      total: filteredData.length,
      invoiced: filteredData.filter(att => att.local_invoice !== null).length,
      notInvoiced: filteredData.filter(att => att.local_invoice === null).length,
      uniqueLessons: new Set(filteredData.map(att => att.lesson)).size,
    };
  }, [filteredData]);

  const groupedAttendances = useMemo(() => {
    return groupByLesson(filteredData);
  }, [filteredData]);

  const sortedLessonIds = useMemo(() => {
    return Object.keys(groupedAttendances).sort((a, b) => Number(b) - Number(a));
  }, [groupedAttendances]);

  const loading = attendanceLoading || studentsLoading || lessonsLoading || groupsLoading;
  const error = attendanceError || studentsError || lessonsError || groupsError;

  if (loading) {
    return (
      <div className="container-fluid py-4" style={{ backgroundColor: '#f8f9fa', minHeight: '100vh' }}>
        <div className="d-flex justify-content-center align-items-center" style={{ height: '50vh' }}>
          <div className="spinner-border" style={{ color: '#004aad', width: '3rem', height: '3rem' }} role="status">
            <span className="visually-hidden">Loading...</span>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container-fluid py-4" style={{ backgroundColor: '#f8f9fa', minHeight: '100vh' }}>
        <div className="alert alert-danger" role="alert">
          <h4 className="alert-heading">Error Loading Data</h4>
          <p>{error.message || 'An error occurred while loading data.'}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container-fluid py-4" style={{ backgroundColor: '#f8f9fa', minHeight: '100vh' }}>
      <AttendanceHeader stats={stats} filters={filters} onFilterChange={handleFilterChange} />
      <AdvancedFilters 
        filters={filters} 
        onFilterChange={handleFilterChange}
        students={studentsData}
        groups={groupsData}
        lessons={lessonsData}
      />
      <StatsCards stats={stats} />
      
      <div className="row">
        <div className="col-12">
          {sortedLessonIds.length > 0 ? (
            sortedLessonIds.map(lessonId => (
              <LessonCard 
                key={lessonId}
                lessonId={lessonId}
                attendances={groupedAttendances[lessonId]}
                studentsMap={studentsMap}
                lessonsMap={lessonsMap}
              />
            ))
          ) : (
            <div className="card border-0 shadow-sm" style={{ borderRadius: '12px' }}>
              <div className="card-body text-center py-5">
                <i className="fas fa-inbox" style={{ fontSize: '3rem', color: '#6c757d' }}></i>
                <h5 className="mt-3 mb-2" style={{ color: '#6c757d' }}>No Attendances Found</h5>
                <p className="text-muted">Try adjusting your filters to see more results.</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}