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

    cy.contains("11 Advanced").should("exist");
    cy.contains("Tutor: Alice").should("exist");
    cy.contains("2h lesson").should("exist");

    cy.contains("12 Ext 1").should("exist");
    cy.contains("Tutor: Bob").should("exist");
    cy.contains("1h lesson").should("exist");
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
    cy.contains("Saturday 10:00 AM").should("exist");
    cy.contains("Sunday 2:00 PM").should("exist");
  });
});
