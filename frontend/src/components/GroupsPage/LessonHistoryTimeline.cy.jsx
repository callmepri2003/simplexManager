import React from 'react'
import LessonHistoryTimeline from './LessonHistoryTimeline'

describe.skip('LessonHistoryTimeline Attendance', () => {
  it('renders logically', () => {
    cy.fixture('lessonHistoryTimeline/lessons1.json').then((data)=>{
      cy.mount(<LessonHistoryTimeline {...data} />)

      cy.get('[data-cy="student1"]').should('exist');

      // If they're present it should be green
      cy.get('[data-cy="student1"]').should('have.class', 'bg-success');

      // If they're not present it should be blue
      cy.get('[data-cy="student2"]').should('have.class', 'bg-primary');

    })
  })

  it('toggles colour on click', () => {
    cy.fixture('lessonHistoryTimeline/lessons1.json').then((data)=>{

      cy.mount(<LessonHistoryTimeline {...data}/>)

      cy.get('[data-cy="student1"]').click()

      // After clicking it should turn blue
      cy.get('[data-cy="student1"]').should('have.class', 'bg-primary')


      cy.get('[data-cy="student1"]').click()
      cy.get('[data-cy="student2"]').click()

      // After clicking it should turn green
      cy.get('[data-cy="student1"]').should('have.class', 'bg-success')
      cy.get('[data-cy="student2"]').should('have.class', 'bg-success')


    })
  })

  it('updates upon save', ()=>{
    cy.fixture('lessonHistoryTimeline/lessons1.json').then((data)=>{
      cy.mount(<LessonHistoryTimeline {...data}/>)
      
      cy.get('[data-cy="student1"]').click()
      cy.get('[data-cy="saveAttendance"]').click()
      cy.get('[data-cy="saveAttendance"]').should('not.exist')
    })
  })

  // it('instantly adds new lessons to the list, upon creation', ()=>{
  //   cy.mount(<LessonHistoryTimeline {...data}/>)

  //   // The create lesson form should disappear

  //   // the newly created lesson should be in the list

  // })
})

describe('LessonHistoryTimeline Resources', () => {
  it('Uploads resources and shows them', ()=>{
    
    cy.fixture('lessonHistoryTimeline/lessonsGET1.json').then((data)=>{
      cy.mount(<LessonHistoryTimeline {...data}/>)
      cy.intercept('POST', '**/api/lessons/', { fixture: 'LessonHistoryTimeline/createLessonForm/lessons-.json' }).as('createLesson');
      cy.intercept('POST', '**/api/attendances/bulk/', { fixture: 'LessonHistoryTimeline/createLessonForm/attendances-bulk-.json' }).as('createBulkAttendance');
      cy.intercept('POST', '**/api/resources/bulk/', { fixture: 'LessonHistoryTimeline/createLessonForm/resources-bulk-.json' }).as('createBulkAttendance');

      cy.get('[data-cy="addLesson"]').click()
      cy.get('[data-cy="selectStudents"]').click()
      cy.get('[data-cy="selectStudentsOptionstudent2"]').click()
      cy.get('input[data-cy="uploadResource"]').selectFile('cypress/fixtures/test-file.pdf', { force: true });
      cy.get('[data-cy="createLesson"]').contains('Create Lesson').click({ force: true });
    })
    cy.wait('@createLesson').then((interception) => {
      // expect(interception.request.body).to.have.property('date');
      // expect(interception.request.body).to.have.property('selectedStudents');
      console.log(interception);
    });

    cy.get('[data-cy="LessonCard79"]').scrollTo()
  })

})