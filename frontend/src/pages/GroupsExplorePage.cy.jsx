import React from 'react'
import GroupsExplorePage from './GroupsExplorePage'

describe('<GroupsExplorePage />', () => {

  it('should display group information correctly', () => {
    cy.intercept('GET', '**/api/groups/**', { fixture: 'groupsExplorePage/groupResponse1.json' }).as('getGroup');
    cy.mount(<GroupsExplorePage />);
    cy.wait('@getGroup')
    // Check hero section
    cy.contains('Advanced Mathematics').should('be.visible');
    cy.contains('with Dr. Smith').should('be.visible');
    cy.contains('Monday, 10:00 AM').should('be.visible');

    // Check class details section
    cy.contains('Class Details').should('be.visible');
    cy.contains('2 hr(s)').should('be.visible');
    cy.contains('Math Fundamentals Course').should('be.visible');
  });

  it('should display lessons with notes and resources', () => {
    cy.intercept('GET', '**/api/groups/**', { fixture: 'groupsExplorePage/groupResponse1.json' }).as('getGroup');
    cy.mount(<GroupsExplorePage />);
    cy.wait('@getGroup')

    // Check lessons section exists
    cy.contains('Lessons').should('be.visible');

    // Check first lesson with content
    cy.contains('Monday 15 January 2024').should('be.visible');
    cy.contains('Today we covered quadratic equations').should('be.visible');

    // Check resources are displayed
    cy.contains('Resources').should('be.visible');
    cy.contains('Quadratic Equations Worksheet.pdf').should('be.visible');
    cy.contains('Practice Problems.docx').should('be.visible');

  });
})