import { useState } from "react";
import { editAttendance, postBulkAttendances } from "../../services/api";

export default function AttendanceSection({ lesson, students }) {
  const [isExpanded, setIsExpanded] = useState(false);
  const [attendance, setAttendance] = useState({});
  const [isLoading, setIsLoading] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const lessonId = lesson.id;
  
  const handleMarkRoll = async () => {
    if (!isExpanded) {
      setIsLoading(true);
      try {
        // Use attendance data from lesson prop
        const existingAttendance = lesson.attendances || [];
        
        const attendanceMap = {};
        students.forEach(student => {
          // Match by tutoringStudent field instead of studentId
          const existing = existingAttendance.find(a => a.tutoringStudent === student.id);
          attendanceMap[student.id] = {
            id: existing?.id,
            present: existing?.present || false,
            paid: existing?.paid || false,
            homework: existing?.homework || false
          };
        });
        setAttendance(attendanceMap);
      } catch (error) {
        console.error('Error loading attendance:', error);
      } finally {
        setIsLoading(false);
      }
    }
    setIsExpanded(!isExpanded);
  };

  const toggleAttendanceField = (studentId, field) => {
    setAttendance(prev => ({
      ...prev,
      [studentId]: {
        ...prev[studentId],
        [field]: !prev[studentId]?.[field]
      }
    }));
  };

  const handleBulkSave = async () => {
    setIsSaving(true);
    try {
      const updatePromises = Object.entries(attendance).map(([studentId, data]) => {
        const attendanceData = {
          lesson: lessonId,
          tutoringStudent: parseInt(studentId),
          present: data.present,
          paid: data.paid,
          homework: data.homework
        };
        
        // Edit existing attendance record
        if (data.id) {
          return editAttendance(data.id, attendanceData);
        }
        // Skip if no ID (shouldn't happen in this flow)
        return Promise.resolve();
      });
      
      await Promise.all(updatePromises);
      console.log('Attendance saved successfully');
    } catch (error) {
      console.error('Error saving attendance:', error);
      // Optionally show error message to user
    } finally {
      setIsSaving(false);
    }
  };

  const getAttendanceSummary = () => {
    // Use lesson.attendances for summary when collapsed
    const attendanceData = isExpanded ? attendance : {};
    
    if (!isExpanded && lesson.attendances) {
      const values = lesson.attendances;
      const present = values.filter(a => a.present).length;
      const paid = values.filter(a => a.paid).length;
      const homework = values.filter(a => a.homework).length;
      return { present, paid, homework, total: students.length };
    }
    
    const values = Object.values(attendanceData);
    if (values.length === 0) return null;
    
    const present = values.filter(a => a.present).length;
    const paid = values.filter(a => a.paid).length;
    const homework = values.filter(a => a.homework).length;
    
    return { present, paid, homework, total: students.length };
  };

  const summary = getAttendanceSummary();
  const hasStudents = students && students.length > 0;

  return (
    <div className="mt-4" data-cy={`attendance-section-${lessonId}`}>
      <div className="card shadow-sm border-0">
        <div className="card-header bg-white border-bottom py-3">
          <div className="d-flex justify-content-between align-items-center">
            <h5 className="mb-0 fw-semibold" style={{ color: '#004aad' }}>
              <i className="bi bi-clipboard-check me-2"></i>
              Attendance
            </h5>
            {hasStudents && (
              <button
                className="btn btn-primary px-4"
                style={{ backgroundColor: '#004aad', borderColor: '#004aad' }}
                onClick={handleMarkRoll}
                disabled={isLoading}
                data-cy={`mark-roll-btn-${lessonId}`}
              >
                {isLoading ? (
                  <>
                    <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                    Loading...
                  </>
                ) : isExpanded ? (
                  <>
                    <i className="bi bi-chevron-up me-2"></i>
                    Hide Roll
                  </>
                ) : (
                  <>
                    <i className="bi bi-pencil-square me-2"></i>
                    Mark Roll
                  </>
                )}
              </button>
            )}
          </div>
        </div>

        <div className="card-body p-4">
          {/* Empty State */}
          {!hasStudents && (
            <div className="text-center py-5">
              <div className="mb-3">
                <i className="bi bi-people" style={{ fontSize: '3rem', color: '#004aad', opacity: 0.3 }}></i>
              </div>
              <h6 className="text-muted mb-2">No Students Enrolled</h6>
              <p className="text-muted small mb-0">Add students to this lesson to track attendance</p>
            </div>
          )}

          {/* Summary when collapsed */}
          {hasStudents && !isExpanded && summary && summary.total > 0 && (
            <div className="row g-3" data-cy={`attendance-summary-${lessonId}`}>
              <div className="col-md-4">
                <div className="p-3 rounded" style={{ backgroundColor: '#f8f9fa' }}>
                  <div className="d-flex align-items-center">
                    <div>
                      <div className="text-muted small">Present</div>
                      <div className="fs-4 fw-semibold" style={{ color: '#004aad' }}>
                        {summary.present}<span className="fs-6 text-muted">/{summary.total}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              <div className="col-md-4">
                <div className="p-3 rounded" style={{ backgroundColor: '#f8f9fa' }}>
                  <div className="d-flex align-items-center">
                    <div>
                      <div className="text-muted small">Paid</div>
                      <div className="fs-4 fw-semibold text-success">{summary.paid}</div>
                    </div>
                  </div>
                </div>
              </div>
              <div className="col-md-4">
                <div className="p-3 rounded" style={{ backgroundColor: '#f8f9fa' }}>
                  <div className="d-flex align-items-center">
                    <div>
                      <div className="text-muted small">Homework</div>
                      <div className="fs-4 fw-semibold text-warning">{summary.homework}</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Expanded attendance list */}
          {hasStudents && isExpanded && (
            <div className="mt-2" data-cy={`attendance-list-${lessonId}`}>
              {/* Quick actions */}
              <div className="d-flex justify-content-between align-items-center mb-4">
                <button
                  className="btn btn-success px-4"
                  onClick={handleBulkSave}
                  disabled={isSaving}
                  data-cy={`submit-attendance-${lessonId}`}
                >
                  {isSaving ? (
                    <>
                      <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                      Saving...
                    </>
                  ) : (
                    <>
                      <i className="bi bi-check-circle me-2"></i>
                      Submit Changes
                    </>
                  )}
                </button>
              </div>

              <div className="table-responsive">
                <table className="table table-hover align-middle">
                  <thead style={{ backgroundColor: '#f8f9fa' }}>
                    <tr>
                      <th className="py-3 ps-4" style={{ width: '40%' }}>Student Name</th>
                      <th className="text-center py-3" style={{ width: '20%' }}>
                        <i className="bi bi-person-check me-2" style={{ color: '#004aad' }}></i>
                        Present
                      </th>
                      <th className="text-center py-3" style={{ width: '20%' }}>
                        <i className="bi bi-cash-coin me-2 text-success"></i>
                        Paid
                      </th>
                      <th className="text-center py-3" style={{ width: '20%' }}>
                        <i className="bi bi-journal-check me-2 text-warning"></i>
                        Homework
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    {students.map((student) => (
                      <tr
                        key={student.id}
                        data-cy={`attendance-row-${student.id}`}
                        className="border-bottom"
                      >
                        <td className="py-3 ps-4">
                          <div className="d-flex align-items-center">
                            <div className="rounded-circle bg-primary bg-opacity-10 p-2 me-3" style={{ width: '40px', height: '40px' }}>
                              <i className="bi bi-person-fill" style={{ color: '#004aad' }}></i>
                            </div>
                            <span className="fw-medium">{student.name}</span>
                          </div>
                        </td>
                        <td className="text-center py-3">
                          <div className="form-check d-flex justify-content-center">
                            <input
                              type="checkbox"
                              className="form-check-input"
                              style={{ width: '1.5rem', height: '1.5rem', cursor: 'pointer' }}
                              checked={attendance[student.id]?.present || false}
                              onChange={() => toggleAttendanceField(student.id, 'present')}
                              data-cy={`attendance-present-${student.id}`}
                            />
                          </div>
                        </td>
                        <td className="text-center py-3">
                          <div className="form-check d-flex justify-content-center">
                            <input
                              type="checkbox"
                              className="form-check-input"
                              style={{ width: '1.5rem', height: '1.5rem', cursor: 'pointer' }}
                              checked={attendance[student.id]?.paid || false}
                              onChange={() => toggleAttendanceField(student.id, 'paid')}
                              data-cy={`attendance-paid-${student.id}`}
                            />
                          </div>
                        </td>
                        <td className="text-center py-3">
                          <div className="form-check d-flex justify-content-center">
                            <input
                              type="checkbox"
                              className="form-check-input"
                              style={{ width: '1.5rem', height: '1.5rem', cursor: 'pointer' }}
                              checked={attendance[student.id]?.homework || false}
                              onChange={() => toggleAttendanceField(student.id, 'homework')}
                              data-cy={`attendance-homework-${student.id}`}
                            />
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}