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
    cy.get('[data-cy="newLessonSubmit"]').click();
    cy.contains('Sunday 15 December 2024');
  })
})