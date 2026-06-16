import React, { useState, useMemo } from 'react';
import { useGetAllAttendances, useGetAllGroups, useGetAllLessons, useGetAllStudents } from '../services/api';

// Utility function to group attendances by lesson
const groupByLesson = (attendances) => {
  const grouped = {};
  attendances.forEach(att => {
    const lessonId = att.lesson?.id || att.lesson;
    if (!grouped[lessonId]) {
      grouped[lessonId] = [];
    }
    grouped[lessonId].push(att);
  });
  return grouped;
};

// Filter functions
const filterByDateRange = (lessonDate, dateRange, customStartDate, customEndDate) => {
  if (!lessonDate) return false;
  
  const now = new Date();
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
  const lessonDateObj = new Date(lessonDate);
  
  switch (dateRange) {
    case 'today':
      const lessonDay = new Date(lessonDateObj.getFullYear(), lessonDateObj.getMonth(), lessonDateObj.getDate());
      return lessonDay.getTime() === today.getTime();
    case 'week':
      const weekAgo = new Date(today);
      weekAgo.setDate(weekAgo.getDate() - 7);
      return lessonDateObj >= weekAgo && lessonDateObj <= now;
    case 'month':
      const monthAgo = new Date(today);
      monthAgo.setMonth(monthAgo.getMonth() - 1);
      return lessonDateObj >= monthAgo && lessonDateObj <= now;
    case 'custom':
      if (customStartDate && customEndDate) {
        const start = new Date(customStartDate);
        const end = new Date(customEndDate);
        end.setHours(23, 59, 59, 999);
        return lessonDateObj >= start && lessonDateObj <= end;
      }
      return true;
    default:
      return true;
  }
};

// Header Component with Filters
function AttendanceHeader({ stats, filters, onFilterChange }) {
  const { invoiceStatus } = filters;

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

  // Get unique tutoring weeks from lessons
  const uniqueWeeks = useMemo(() => {
    if (!lessons) return [];
    const weeks = lessons.map(l => {
      if (typeof l.tutoringWeek === 'object') {
        return { id: l.tutoringWeek.id, index: l.tutoringWeek.index, term: l.tutoringWeek.term };
      }
      return { id: l.tutoringWeek, index: l.tutoringWeek, term: null };
    }).filter(w => w.id != null);
    
    // Remove duplicates based on id
    const uniqueMap = new Map();
    weeks.forEach(w => uniqueMap.set(w.id, w));
    return Array.from(uniqueMap.values()).sort((a, b) => b.index - a.index);
  }, [lessons]);

  const activeFiltersCount = [
    filters.selectedStudent !== 'all',
    filters.selectedGroup !== 'all',
    filters.selectedWeek !== 'all',
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
                        {group.course || group.tutor || `Group ${group.id}`}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="col-md-3">
                  <label className="form-label" style={{ fontSize: '0.875rem', fontWeight: 500 }}>
                    Tutoring Week
                  </label>
                  <select 
                    className="form-select"
                    value={filters.selectedWeek}
                    onChange={(e) => onFilterChange('selectedWeek', e.target.value)}
                    style={{ fontSize: '0.875rem' }}
                  >
                    <option value="all">All Weeks</option>
                    {uniqueWeeks.map(week => (
                      <option key={week.id} value={week.id}>
                        Week {week.index}{week.term ? ` - Term ${week.term}` : ''}
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
                      onFilterChange('selectedWeek', 'all');
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
function LessonCard({ lessonId, attendances }) {
  const [expanded, setExpanded] = useState(false);
  const hasInvoice = attendances.some(att => att.local_invoice);  
  // Get lesson data from first attendance (they all have same lesson)
  const lessonData = attendances[0]?.lesson;

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
            {lessonData?.tutoringWeek && (
              <span className="ms-2 badge" style={{ backgroundColor: '#28a745', fontSize: '0.75rem' }}>
                Week {typeof lessonData.tutoringWeek === 'object' 
                  ? lessonData.tutoringWeek.index || lessonData.tutoringWeek.id
                  : lessonData.tutoringWeek}
              </span>
            )}
          </h5>
          <div className="d-flex gap-3 align-items-center flex-wrap">
            <small className="text-muted">
              <i className="fas fa-users me-1"></i>
              {attendances.length} {attendances.length === 1 ? 'student' : 'students'}
            </small>
            {lessonData?.date && (
              <small className="text-muted">
                <i className="far fa-calendar-alt me-1"></i>
                {new Date(lessonData.date).toLocaleDateString('en-AU', { 
                  weekday: 'short',
                  day: 'numeric', 
                  month: 'short', 
                  year: 'numeric',
                  hour: '2-digit',
                  minute: '2-digit'
                })}
              </small>
            )}
            {lessonData?.group && (
              <small className="badge" style={{ backgroundColor: '#e7f3ff', color: '#004aad', fontSize: '0.75rem' }}>
                <i className="fas fa-layer-group me-1"></i>
                {typeof lessonData.group === 'object' 
                  ? (lessonData.group.course || `Group ${lessonData.group.id}`)
                  : `Group ${lessonData.group}`}
              </small>
            )}
          </div>
        </div>
        <div className="d-flex align-items-center gap-3">
          {hasInvoice && (
            <span className="badge" style={{ backgroundColor: '#17a2b8', padding: '0.5rem 0.75rem', fontSize: '0.75rem' }}>
              <i className="fas fa-file-invoice me-1"></i>
              Invoiced
            </span>
          )}
          <i className={`fas fa-chevron-${expanded ? 'up' : 'down'}`} style={{ fontSize: '1.25rem', color: '#004aad' }}></i>
        </div>
      </div>
      
      {expanded && (
        <div className="card-body" style={{ padding: '1.25rem', backgroundColor: '#f8f9fa' }}>
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
                {console.log(attendances)}
                {attendances.map(att => {
                  const student = att.tutoringStudent;
                  const studentName = typeof student === 'object' ? student.name : `Student ${student}`;
                  const studentId = typeof student === 'object' ? student.id : student;
                  
                  return (
                    <tr key={att.id}>
                      <td style={{ fontSize: '0.875rem', verticalAlign: 'middle' }}>
                        <div className="d-flex align-items-center">
                          <div className="rounded-circle bg-primary d-flex align-items-center justify-content-center text-white me-2" 
                               style={{ width: '32px', height: '32px', fontSize: '0.875rem', fontWeight: 600 }}>
                            {studentName[0]?.toUpperCase() || 'S'}
                          </div>
                          <div>
                            <div style={{ fontWeight: 500 }}>
                              {studentName}
                            </div>
                            <small className="text-muted">ID: {studentId}</small>
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
                        {att.local_invoice.is_paid ? 
                          <span className="badge bg-success">
                            <i className="fas fa-dollar-sign me-1"></i>
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
    selectedWeek: 'all',
    searchQuery: '',
    customStartDate: '',
    customEndDate: '',
  });

  const handleFilterChange = (key, value) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };

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
      filtered = filtered.filter(att => {
        const studentId = typeof att.tutoringStudent === 'object' 
          ? att.tutoringStudent.id 
          : att.tutoringStudent;
        return studentId === parseInt(filters.selectedStudent);
      });
    }

    // Group filter
    if (filters.selectedGroup !== 'all') {
      filtered = filtered.filter(att => {
        const lesson = att.lesson;
        if (!lesson) return false;
        const groupId = typeof lesson.group === 'object' ? lesson.group.id : lesson.group;
        return groupId === parseInt(filters.selectedGroup);
      });
    }

    // Tutoring Week filter
    if (filters.selectedWeek !== 'all') {
      filtered = filtered.filter(att => {
        const lesson = att.lesson;
        if (!lesson) return false;
        const weekId = typeof lesson.tutoringWeek === 'object' 
          ? lesson.tutoringWeek.id 
          : lesson.tutoringWeek;
        return weekId === parseInt(filters.selectedWeek);
      });
    }

    // Date range filter
    if (filters.dateRange !== 'all') {
      filtered = filtered.filter(att => {
        const lesson = att.lesson;
        if (!lesson || !lesson.date) return false;
        return filterByDateRange(
          lesson.date, 
          filters.dateRange, 
          filters.customStartDate, 
          filters.customEndDate
        );
      });
    }

    // Search filter
    if (filters.searchQuery) {
      filtered = filtered.filter(att => {
        const lessonId = att.lesson?.id || att.lesson;
        return lessonId.toString().includes(filters.searchQuery);
      });
    }

    return filtered;
  }, [attendanceData, filters]);

  const stats = useMemo(() => {
    if (!filteredData) return { total: 0, invoiced: 0, notInvoiced: 0, uniqueLessons: 0 };
    
    return {
      total: filteredData.length,
      invoiced: filteredData.filter(att => att.local_invoice !== null).length,
      notInvoiced: filteredData.filter(att => att.local_invoice === null).length,
      uniqueLessons: new Set(filteredData.map(att => att.lesson?.id || att.lesson)).size,
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