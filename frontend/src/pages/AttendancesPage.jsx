import React, { useState } from 'react';
import { useGetAllAttendances } from "../services/api";

export default function AttendancePage() {
  const [data, loading, error] = useGetAllAttendances();
  const [selectedAttendance, setSelectedAttendance] = useState(null);
  const [filterStudent, setFilterStudent] = useState('all');
  const [filterLesson, setFilterLesson] = useState('all');
  const [showInvoiceModal, setShowInvoiceModal] = useState(false);
  const [selectedInvoice, setSelectedInvoice] = useState(null);

  // Group attendances by lesson
  const groupedByLesson = data?.reduce((acc, attendance) => {
    const lessonId = attendance.lesson;
    if (!acc[lessonId]) {
      acc[lessonId] = [];
    }
    acc[lessonId].push(attendance);
    return acc;
  }, {}) || {};

  // Get unique students and lessons for filters
  const uniqueStudents = [...new Set(data?.map(a => a.tutoringStudent) || [])];
  const uniqueLessons = [...new Set(data?.map(a => a.lesson) || [])];

  // Filter data
  const filteredData = data?.filter(attendance => {
    const studentMatch = filterStudent === 'all' || attendance.tutoringStudent === parseInt(filterStudent);
    const lessonMatch = filterLesson === 'all' || attendance.lesson === parseInt(filterLesson);
    return studentMatch && lessonMatch;
  }) || [];

  const handleViewInvoice = (invoice) => {
    setSelectedInvoice(invoice);
    setShowInvoiceModal(true);
  };

  const getStatusBadge = (attendance) => {
    if (attendance.paid) return <span className="badge bg-success">Paid</span>;
    if (attendance.local_invoice) return <span className="badge bg-warning text-dark">Invoiced</span>;
    if (attendance.present) return <span className="badge bg-info">Present</span>;
    return <span className="badge bg-secondary">Pending</span>;
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-AU', {
      style: 'currency',
      currency: 'AUD'
    }).format(amount / 100);
  };

  const formatDate = (timestamp) => {
    return new Date(timestamp * 1000).toLocaleDateString('en-AU', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

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

  if (error) {
    return (
      <div className="container-fluid py-4" style={{ backgroundColor: '#f8f9fa', minHeight: '100vh' }}>
        <div className="alert alert-danger" role="alert" data-cy="error-alert">
          <h4 className="alert-heading">Error Loading Attendances</h4>
          <p>{error.message || 'An error occurred while loading attendance data.'}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container-fluid py-4" style={{ backgroundColor: '#f8f9fa', minHeight: '100vh' }}>
      {/* Header */}
      <div className="row mb-3">
        <div className="col">
          <div className="card border-0 shadow-sm">
            <div className="card-body">
              <h1 className="h4 mb-1" data-cy="page-title">
                <i className="bi bi-calendar-check me-2"></i>
                Attendance Management
              </h1>
              <p className="text-muted mb-0 small">Track student attendance, homework, and payments</p>
            </div>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="row mb-3">
        <div className="col">
          <div className="card border-0 shadow-sm">
            <div className="card-body">
              <div className="row g-3">
                <div className="col-md-6">
                  <label className="form-label small text-muted text-uppercase mb-1">Filter by Student</label>
                  <select 
                    className="form-select" 
                    value={filterStudent}
                    onChange={(e) => setFilterStudent(e.target.value)}
                    data-cy="student-filter"
                  >
                    <option value="all">All Students</option>
                    {uniqueStudents.map(studentId => (
                      <option key={studentId} value={studentId}>Student {studentId}</option>
                    ))}
                  </select>
                </div>
                <div className="col-md-6">
                  <label className="form-label small text-muted text-uppercase mb-1">Filter by Lesson</label>
                  <select 
                    className="form-select"
                    value={filterLesson}
                    onChange={(e) => setFilterLesson(e.target.value)}
                    data-cy="lesson-filter"
                  >
                    <option value="all">All Lessons</option>
                    {uniqueLessons.sort((a, b) => a - b).map(lessonId => (
                      <option key={lessonId} value={lessonId}>Lesson {lessonId}</option>
                    ))}
                  </select>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Statistics Cards */}
      <div className="row g-3 mb-3">
        <div className="col-lg-3 col-md-6">
          <div className="card border-0 shadow-sm h-100" data-cy="total-attendances-card">
            <div className="card-body">
              <div className="d-flex justify-content-between align-items-center">
                <div>
                  <p className="text-muted text-uppercase mb-1 small fw-semibold">Total Records</p>
                  <h3 className="mb-0">{filteredData.length}</h3>
                </div>
                <div className="bg-primary bg-opacity-10 rounded p-3">
                  <i className="bi bi-journal-text text-primary fs-4"></i>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div className="col-lg-3 col-md-6">
          <div className="card border-0 shadow-sm h-100" data-cy="present-card">
            <div className="card-body">
              <div className="d-flex justify-content-between align-items-center">
                <div>
                  <p className="text-muted text-uppercase mb-1 small fw-semibold">Present</p>
                  <h3 className="mb-0">{filteredData.filter(a => a.present).length}</h3>
                </div>
                <div className="bg-success bg-opacity-10 rounded p-3">
                  <i className="bi bi-check-circle text-success fs-4"></i>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div className="col-lg-3 col-md-6">
          <div className="card border-0 shadow-sm h-100" data-cy="paid-card">
            <div className="card-body">
              <div className="d-flex justify-content-between align-items-center">
                <div>
                  <p className="text-muted text-uppercase mb-1 small fw-semibold">Paid</p>
                  <h3 className="mb-0">{filteredData.filter(a => a.paid).length}</h3>
                </div>
                <div className="bg-info bg-opacity-10 rounded p-3">
                  <i className="bi bi-currency-dollar text-info fs-4"></i>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div className="col-lg-3 col-md-6">
          <div className="card border-0 shadow-sm h-100" data-cy="homework-card">
            <div className="card-body">
              <div className="d-flex justify-content-between align-items-center">
                <div>
                  <p className="text-muted text-uppercase mb-1 small fw-semibold">Homework Done</p>
                  <h3 className="mb-0">{filteredData.filter(a => a.homework).length}</h3>
                </div>
                <div className="bg-warning bg-opacity-10 rounded p-3">
                  <i className="bi bi-book text-warning fs-4"></i>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Attendance Table */}
      <div className="row">
        <div className="col">
          <div className="card border-0 shadow-sm">
            <div className="card-header bg-white border-0 py-3">
              <h5 className="mb-0">Attendance Records</h5>
            </div>
            <div className="card-body p-0">
              <div className="table-responsive">
                <table className="table table-hover align-middle mb-0" data-cy="attendance-table">
                  <thead className="table-light">
                    <tr>
                      <th className="px-3 py-3 small text-muted text-uppercase fw-semibold">ID</th>
                      <th className="py-3 small text-muted text-uppercase fw-semibold">Lesson</th>
                      <th className="py-3 small text-muted text-uppercase fw-semibold">Student</th>
                      <th className="py-3 text-center small text-muted text-uppercase fw-semibold">Present</th>
                      <th className="py-3 text-center small text-muted text-uppercase fw-semibold">Homework</th>
                      <th className="py-3 text-center small text-muted text-uppercase fw-semibold">Status</th>
                      <th className="py-3 text-center small text-muted text-uppercase fw-semibold">Invoice</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredData.length === 0 ? (
                      <tr>
                        <td colSpan="7" className="text-center py-5 text-muted">
                          <i className="bi bi-inbox d-block mb-2" style={{ fontSize: '3rem', opacity: 0.3 }}></i>
                          <p className="mb-0">No attendance records found</p>
                        </td>
                      </tr>
                    ) : (
                      filteredData.map((attendance) => (
                        <tr key={attendance.id} data-cy={`attendance-row-${attendance.id}`}>
                          <td className="px-3">
                            <span className="badge bg-light text-dark">{attendance.id}</span>
                          </td>
                          <td>
                            <span>Lesson {attendance.lesson}</span>
                          </td>
                          <td>
                            <span className="text-muted">Student {attendance.tutoringStudent}</span>
                          </td>
                          <td className="text-center">
                            {attendance.present ? (
                              <i className="bi bi-check-circle-fill text-success fs-5"></i>
                            ) : (
                              <i className="bi bi-x-circle text-muted fs-5"></i>
                            )}
                          </td>
                          <td className="text-center">
                            {attendance.homework ? (
                              <i className="bi bi-check-circle-fill text-success fs-5"></i>
                            ) : (
                              <i className="bi bi-x-circle text-muted fs-5"></i>
                            )}
                          </td>
                          <td className="text-center">
                            {getStatusBadge(attendance)}
                          </td>
                          <td className="text-center">
                            {attendance.local_invoice ? (
                              <button
                                className="btn btn-sm btn-outline-primary"
                                onClick={() => handleViewInvoice(attendance.local_invoice)}
                                data-cy={`view-invoice-${attendance.id}`}
                              >
                                <i className="bi bi-receipt me-1"></i>
                                View
                              </button>
                            ) : (
                              <span className="text-muted">—</span>
                            )}
                          </td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Invoice Modal */}
      {showInvoiceModal && selectedInvoice && (
        <div 
          className="modal fade show d-block" 
          tabIndex="-1" 
          style={{ backgroundColor: 'rgba(0,0,0,0.5)' }}
          data-cy="invoice-modal"
        >
          <div className="modal-dialog modal-lg modal-dialog-centered modal-dialog-scrollable">
            <div className="modal-content border-0 shadow">
              <div className="modal-header border-0">
                <h5 className="modal-title">
                  <i className="bi bi-receipt me-2"></i>
                  Invoice Details
                </h5>
                <button 
                  type="button" 
                  className="btn-close" 
                  onClick={() => setShowInvoiceModal(false)}
                  data-cy="close-invoice-modal"
                ></button>
              </div>
              <div className="modal-body">
                {selectedInvoice.get_stripe_invoice ? (
                  <>
                    {/* Invoice Header */}
                    <div className="card bg-light border-0 mb-3">
                      <div className="card-body">
                        <div className="row">
                          <div className="col-md-6 mb-3">
                            <p className="text-muted text-uppercase small mb-1 fw-semibold">Invoice Number</p>
                            <p className="mb-0">{selectedInvoice.get_stripe_invoice.number}</p>
                          </div>
                          <div className="col-md-6 mb-3">
                            <p className="text-muted text-uppercase small mb-1 fw-semibold">Status</p>
                            <p className="mb-0">
                              <span className={`badge ${
                                selectedInvoice.get_stripe_invoice.status === 'paid' ? 'bg-success' :
                                selectedInvoice.get_stripe_invoice.status === 'open' ? 'bg-warning text-dark' :
                                'bg-secondary'
                              }`}>
                                {selectedInvoice.get_stripe_invoice.status.toUpperCase()}
                              </span>
                            </p>
                          </div>
                        </div>
                        <div className="row">
                          <div className="col-md-6 mb-3">
                            <p className="text-muted text-uppercase small mb-1 fw-semibold">Customer</p>
                            <p className="mb-1">{selectedInvoice.get_stripe_invoice.customer_name}</p>
                            <p className="text-muted small mb-0">{selectedInvoice.get_stripe_invoice.customer_email}</p>
                          </div>
                          <div className="col-md-6 mb-3">
                            <p className="text-muted text-uppercase small mb-1 fw-semibold">Created</p>
                            <p className="mb-0">{formatDate(selectedInvoice.get_stripe_invoice.created)}</p>
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Custom Fields */}
                    {selectedInvoice.get_stripe_invoice.custom_fields && (
                      <div className="mb-3">
                        <h6 className="mb-2">Billing Information</h6>
                        {selectedInvoice.get_stripe_invoice.custom_fields.map((field, idx) => (
                          <div key={idx} className="d-flex justify-content-between py-2 border-bottom">
                            <span className="text-muted small">{field.name}</span>
                            <span>{field.value}</span>
                          </div>
                        ))}
                      </div>
                    )}

                    {/* Line Items */}
                    <div className="mb-3">
                      <h6 className="mb-2">Line Items</h6>
                      <div className="table-responsive">
                        <table className="table table-sm">
                          <thead className="table-light">
                            <tr>
                              <th className="small text-muted text-uppercase fw-semibold">Description</th>
                              <th className="text-center small text-muted text-uppercase fw-semibold">Quantity</th>
                              <th className="text-end small text-muted text-uppercase fw-semibold">Unit Price</th>
                              <th className="text-end small text-muted text-uppercase fw-semibold">Amount</th>
                            </tr>
                          </thead>
                          <tbody>
                            {selectedInvoice.get_stripe_invoice.lines.data.map((line) => (
                              <tr key={line.id}>
                                <td>{line.description}</td>
                                <td className="text-center">{line.quantity}</td>
                                <td className="text-end">{formatCurrency(parseInt(line.pricing.unit_amount_decimal))}</td>
                                <td className="text-end">{formatCurrency(line.amount)}</td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </div>

                    {/* Totals */}
                    <div className="card bg-primary bg-opacity-10 border-0">
                      <div className="card-body">
                        <div className="d-flex justify-content-between mb-2">
                          <span>Subtotal</span>
                          <span>{formatCurrency(selectedInvoice.get_stripe_invoice.subtotal)}</span>
                        </div>
                        <div className="d-flex justify-content-between mb-2">
                          <span>Tax</span>
                          <span>{formatCurrency(selectedInvoice.get_stripe_invoice.total - selectedInvoice.get_stripe_invoice.subtotal)}</span>
                        </div>
                        <div className="d-flex justify-content-between pt-2 border-top">
                          <span className="h5 mb-0">Total</span>
                          <span className="h5 mb-0 text-primary">{formatCurrency(selectedInvoice.get_stripe_invoice.total)}</span>
                        </div>
                      </div>
                    </div>

                    {/* Payment Info */}
                    {selectedInvoice.get_stripe_invoice.due_date && (
                      <div className="alert alert-info mt-3 mb-0" role="alert">
                        <i className="bi bi-info-circle me-2"></i>
                        <strong>Due Date:</strong> {formatDate(selectedInvoice.get_stripe_invoice.due_date)}
                      </div>
                    )}
                  </>
                ) : (
                  <div className="text-center py-5">
                    <p className="text-muted">No invoice details available</p>
                  </div>
                )}
              </div>
              <div className="modal-footer border-0">
                {selectedInvoice.get_stripe_invoice?.hosted_invoice_url && (
                  <a
                    href={selectedInvoice.get_stripe_invoice.hosted_invoice_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="btn btn-outline-primary"
                    data-cy="view-stripe-invoice"
                  >
                    <i className="bi bi-box-arrow-up-right me-2"></i>
                    View on Stripe
                  </a>
                )}
                {selectedInvoice.get_stripe_invoice?.invoice_pdf && (
                  <a
                    href={selectedInvoice.get_stripe_invoice.invoice_pdf}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="btn btn-primary"
                    data-cy="download-pdf"
                  >
                    <i className="bi bi-download me-2"></i>
                    Download PDF
                  </a>
                )}
                <button 
                  type="button" 
                  className="btn btn-secondary" 
                  onClick={() => setShowInvoiceModal(false)}
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      <style>{`
        @import url('https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css');
        @import url('https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css');
      `}</style>
    </div>
  );
}