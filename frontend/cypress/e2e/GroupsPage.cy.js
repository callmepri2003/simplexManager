describe("GroupsPage", () => {
  beforeEach(() => {
    cy.loginFakeJWT();
    // intercept the API call and return fixture data
    cy.intercept("GET", "/api/groups/", { fixture: "groups.json" }).as("getGroups");
    cy.visit("/groups"); // adjust route to match your app
  });

  it("shows loading initially", () => {
    cy.contains("Loading groups...").should("exist");
  });

  it("renders the correct number of Group cards", () => {
    cy.wait("@getGroups");
    cy.get(".groupsCardContainerIndividual").should("have.length", 2);
  });

  it("renders course, tutor, and lesson info correctly", () => {
    cy.wait("@getGroups");

    cy.contains("Junior Maths").should("exist");
    cy.contains("Tutor: Pri").should("exist");
    cy.contains("2h lesson").should("exist");
  });

  it("renders buttons inside each card", () => {
    cy.wait("@getGroups");
    cy.get(".groupsCardContainerIndividual")
      .first()
      .within(() => {
        cy.contains("Explore").should("exist");
        cy.contains("Start Lesson").should("exist");
      });
  });

  it("renders weekly_time", () => {
    cy.wait("@getGroups");
    cy.contains("Monday, 6:00 AM").should("exist");
  });
});
