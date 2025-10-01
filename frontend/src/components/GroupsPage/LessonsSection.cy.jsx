import React from 'react'
import LessonsSection from './LessonsSection'

describe('<LessonsSection />', () => {
  it('renders', () => {
    // see: https://on.cypress.io/mounting-react
    cy.intercept('POST', '**/api/lessons/', { fixture: 'groupsExplorePage/lessonSection/postLessonsResponse1.json'}).as('postLesson');
    const groupId = "1";
    const lessons = [
      {
          "id": 115,
          "attendances": [],
          "resources": [],
          "notes": null,
          "date": "2025-09-28T11:53:35.268678+10:00",
          "group": 1
      }
    ]
    cy.mount(<LessonsSection groupId={groupId} lessons={lessons} />)

    cy.get('[data-cy="newLessonFormDateInput"]').type('2024-12-15T14:30');
    
    // Submit
    cy.get('[data-cy="newLessonSubmit"]').click();
    cy.contains('Sunday 15 December 2024');


  })

  it('uploads single file', () => {
    cy.intercept('POST', '**/api/lessons/', { fixture: 'groupsExplorePage/lessonSection/postLessonsResponse1.json'}).as('postLesson');
    const groupId = "1";
    const lessons = [
      {
          "id": 115,
          "attendances": [],
          "resources": [],
          "notes": null,
          "date": "2025-09-28T11:53:35.268678+10:00",
          "group": 1
      }
    ]
    cy.mount(<LessonsSection groupId={groupId} lessons={lessons} />)
    cy.get('[data-cy="file-input"]').selectFile('cypress/fixtures/test1.pdf', { force: true });
    cy.get('[data-cy="uploaded-file-0"]').should('contain', 'test1.pdf');
  });

  it('uploads multiple files', () => {
    cy.intercept('POST', '**/api/lessons/', { fixture: 'groupsExplorePage/lessonSection/postLessonsResponse1.json'}).as('postLesson');
    const groupId = "1";
    const lessons = [
      {
          "id": 115,
          "attendances": [],
          "resources": [],
          "notes": null,
          "date": "2025-09-28T11:53:35.268678+10:00",
          "group": 1
      }
    ]
    cy.mount(<LessonsSection groupId={groupId} lessons={lessons} />)
    cy.get('[data-cy="file-input"]').selectFile([
      'cypress/fixtures/test1.pdf',
      'cypress/fixtures/test2.pdf'
    ], { force: true });
    
    cy.get('[data-cy="uploaded-file-0"]').should('contain', 'test1.pdf');
    cy.get('[data-cy="uploaded-file-1"]').should('contain', 'test2.pdf');
  });

  it('removes file', () => {
    cy.intercept('POST', '**/api/lessons/', { fixture: 'groupsExplorePage/lessonSection/postLessonsResponse1.json'}).as('postLesson');
    const groupId = "1";
    const lessons = [
      {
          "id": 115,
          "attendances": [],
          "resources": [],
          "notes": null,
          "date": "2025-09-28T11:53:35.268678+10:00",
          "group": 1
      }
    ]
    cy.mount(<LessonsSection groupId={groupId} lessons={lessons} />)
    cy.get('[data-cy="file-input"]').selectFile('cypress/fixtures/test1.pdf', { force: true });
    cy.get('[data-cy="remove-file-0"]').click();
    cy.get('[data-cy="uploaded-file-0"]').should('not.exist');
  });

  it('shows file below', () => {
    cy.intercept('POST', '**/api/lessons/', { fixture: 'groupsExplorePage/lessonSection/postLessonsResponse1.json'}).as('postLesson');
    const groupId = "1";
    const lessons = [
      {
          "id": 115,
          "attendances": [],
          "resources": [],
          "notes": null,
          "date": "2025-09-28T11:53:35.268678+10:00",
          "group": 1
      }
    ]
    cy.mount(<LessonsSection groupId={groupId} lessons={lessons} />)
    cy.get('[data-cy="file-input"]').selectFile([
      'cypress/fixtures/test1.pdf',
      'cypress/fixtures/test2.pdf'
    ], { force: true });
    
    cy.get('[data-cy="uploaded-file-0"]').should('contain', 'test1.pdf');
    cy.get('[data-cy="uploaded-file-1"]').should('contain', 'test2.pdf');

    // Submit
    cy.get('[data-cy="newLessonFormDateInput"]').type('2024-12-15T14:30');
    cy.get('[data-cy="newLessonSubmit"]').click();

    cy.contains('test1.pdf');
    cy.contains('test2.pdf');

  });
})