import React from 'react'
import LessonHistoryTimeline from './LessonHistoryTimeline'

describe('<LessonHistoryTimeline />', () => {
  it('renders logically', () => {
    cy.fixture('lessonHistoryTimeline/lessons1.json').then((lesson1)=>{
      cy.mount(<LessonHistoryTimeline lessons = {lesson1}/>)

      cy.get('[data-cy="student1"]').should('exist');

      // If they're present it should be green
      cy.get('[data-cy="student1"]').should('have.class', 'bg-success');

      // If they're not present it should be blue
      cy.get('[data-cy="student2"]').should('have.class', 'bg-primary');

    })
  })

  it('toggles colour on click', () => {
    cy.fixture('lessonHistoryTimeline/lessons1.json').then((lesson1)=>{

      cy.mount(<LessonHistoryTimeline lessons = {lesson1}/>)

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
})