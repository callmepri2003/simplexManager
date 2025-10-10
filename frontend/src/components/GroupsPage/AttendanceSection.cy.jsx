import AttendanceSection from "./AttendanceSection";

describe('AttendanceSection Component', () => {
  const lessonWithAttendances = {
    id: 1,
    date: '2024-01-15',
    notes: 'Algebra intro',
    attendances: [
      { id: 1, tutoringStudent: 101, present: true, paid: false, homework: true },
      { id: 2, tutoringStudent: 102, present: false, paid: true, homework: false }
    ]
  };

  const students = [
    { id: 101, name: 'John Doe' },
    { id: 102, name: 'Jane Smith' }
  ];

  const lessonWithoutAttendances = {
    id: 2,
    date: '2024-01-16',
    notes: 'Geometry basics',
    attendances: []
  };

  beforeEach(() => {
    // Intercept API calls with fixtures
    cy.intercept('PUT', '/api/attendances/*', { fixture: 'groupsExplorePage/attendanceSection/editAttendanceResponse.json' }).as('editAttendance');
  });

  it('should display empty state when no students are enrolled', () => {
    cy.mount(<AttendanceSection lesson={lessonWithAttendances} students={[]} />);
    
    cy.contains('No Students Enrolled').should('be.visible');
    cy.contains('Add students to this lesson to track attendance').should('be.visible');
    cy.get('[data-cy^="mark-roll-btn"]').should('not.exist');
  });

  it('should display attendance summary when collapsed', () => {
    cy.mount(<AttendanceSection lesson={lessonWithAttendances} students={students} />);
    
    cy.get('[data-cy="attendance-summary-1"]').should('be.visible');
    cy.contains('Present').parent().contains('1/2');
    cy.contains('Paid').parent().contains('1');
    cy.contains('Homework').parent().contains('1');
  });

  it('should expand attendance list when Mark Roll is clicked', () => {
    cy.mount(<AttendanceSection lesson={lessonWithAttendances} students={students} />);
    
    cy.get('[data-cy="mark-roll-btn-1"]').click();
    
    cy.get('[data-cy="attendance-list-1"]').should('be.visible');
    cy.get('[data-cy="attendance-row-101"]').should('exist');
    cy.get('[data-cy="attendance-row-102"]').should('exist');
  });

  it('should load existing attendance data correctly when expanded', () => {
    cy.mount(<AttendanceSection lesson={lessonWithAttendances} students={students} />);
    
    cy.get('[data-cy="mark-roll-btn-1"]').click();
    
    // Check John Doe's attendance
    cy.get('[data-cy="attendance-present-101"]').should('be.checked');
    cy.get('[data-cy="attendance-paid-101"]').should('not.be.checked');
    cy.get('[data-cy="attendance-homework-101"]').should('be.checked');
    
    // Check Jane Smith's attendance
    cy.get('[data-cy="attendance-present-102"]').should('not.be.checked');
    cy.get('[data-cy="attendance-paid-102"]').should('be.checked');
    cy.get('[data-cy="attendance-homework-102"]').should('not.be.checked');
  });

  it('should toggle attendance fields when checkboxes are clicked', () => {
    cy.mount(<AttendanceSection lesson={lessonWithAttendances} students={students} />);
    
    cy.get('[data-cy="mark-roll-btn-1"]').click();
    
    // Toggle present for John Doe (was true, should become false)
    cy.get('[data-cy="attendance-present-101"]').click();
    cy.get('[data-cy="attendance-present-101"]').should('not.be.checked');
    
    // Toggle paid for John Doe (was false, should become true)
    cy.get('[data-cy="attendance-paid-101"]').click();
    cy.get('[data-cy="attendance-paid-101"]').should('be.checked');
  });

  it('should submit correct attendance data when Submit Changes is clicked', () => {
    cy.mount(<AttendanceSection lesson={lessonWithAttendances} students={students} />);
    
    cy.get('[data-cy="mark-roll-btn-1"]').click();
    
    // Make some changes
    cy.get('[data-cy="attendance-present-101"]').click(); // Toggle to false
    cy.get('[data-cy="attendance-paid-101"]').click();    // Toggle to true
    
    cy.get('[data-cy="submit-attendance-1"]').click();
    
    // Verify first student's PUT request
    cy.wait('@editAttendance').its('request.body').should('deep.equal', {
      lesson: 1,
      tutoringStudent: 101,
      present: false,
      paid: true,
      homework: true
    });
    
    // Verify second student's PUT request
    cy.wait('@editAttendance').its('request.body').should('deep.equal', {
      lesson: 1,
      tutoringStudent: 102,
      present: false,
      paid: true,
      homework: false
    });
  });

  it('should collapse attendance list when Hide Roll is clicked', () => {
    cy.mount(<AttendanceSection lesson={lessonWithAttendances} students={students} />);
    
    cy.get('[data-cy="mark-roll-btn-1"]').click();
    cy.get('[data-cy="attendance-list-1"]').should('be.visible');
    
    cy.get('[data-cy="mark-roll-btn-1"]').click();
    cy.get('[data-cy="attendance-list-1"]').should('not.exist');
    cy.get('[data-cy="attendance-summary-1"]').should('be.visible');
  });

  it('should handle lessons with no existing attendance records', () => {
    cy.mount(<AttendanceSection lesson={lessonWithoutAttendances} students={students} />);
    
    cy.get('[data-cy="mark-roll-btn-2"]').click();
    
    // All checkboxes should be unchecked
    cy.get('[data-cy="attendance-present-101"]').should('not.be.checked');
    cy.get('[data-cy="attendance-paid-101"]').should('not.be.checked');
    cy.get('[data-cy="attendance-homework-101"]').should('not.be.checked');
    cy.get('[data-cy="attendance-present-102"]').should('not.be.checked');
    cy.get('[data-cy="attendance-paid-102"]').should('not.be.checked');
    cy.get('[data-cy="attendance-homework-102"]').should('not.be.checked');
  });

  it('should display student names correctly in the table', () => {
    cy.mount(<AttendanceSection lesson={lessonWithAttendances} students={students} />);
    
    cy.get('[data-cy="mark-roll-btn-1"]').click();
    
    cy.get('[data-cy="attendance-row-101"]').contains('John Doe');
    cy.get('[data-cy="attendance-row-102"]').contains('Jane Smith');
  });

  it('should make multiple attendance changes and submit all at once', () => {
    cy.mount(<AttendanceSection lesson={lessonWithAttendances} students={students} />);
    
    cy.get('[data-cy="mark-roll-btn-1"]').click();
    
    // Make multiple changes
    cy.get('[data-cy="attendance-present-101"]').click();
    cy.get('[data-cy="attendance-homework-101"]').click();
    cy.get('[data-cy="attendance-present-102"]').click();
    cy.get('[data-cy="attendance-paid-102"]').click();
    
    cy.get('[data-cy="submit-attendance-1"]').click();
    
    // Should make 2 API calls (one per student)
    cy.get('@editAttendance.all').should('have.length', 2);
  });
});