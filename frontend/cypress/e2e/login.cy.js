const fakeJWT = (payload) => {
      const header = btoa(JSON.stringify({ alg: "HS256", typ: "JWT" }));
      const body = btoa(JSON.stringify(payload));
      const signature = "signature"; // doesn't need to verify in frontend
      return `${header}.${body}.${signature}`;
    };

describe("login process", () => {
  beforeEach(() => {
    // Clear tokens before each test
    localStorage.removeItem("authTokens");
    
  });

  it("An unauthenticated user logs on and sees the login screen", () => {
    cy.visit("/login");
    cy.contains("Sign In"); // Adjust if your LoginPage has a header/button text
  });

  it("An authenticated user logs on and doesn't see the login screen", () => {

    // Example payload
    const accessToken = fakeJWT({ username: "testuser", role: "admin", exp: Math.floor(Date.now()/1000)+3600 });
    const refreshToken = fakeJWT({ username: "testuser", type: "refresh", exp: Math.floor(Date.now()/1000)+86400 });

    localStorage.setItem(
      "authTokens",
      JSON.stringify({ access: accessToken, refresh: refreshToken, roles: ["Admin"] })
    );

    cy.visit("/");
    cy.contains("Welcome"); // Or whatever your default page shows
    cy.url().should("not.include", "/login");
  });

  it("An unauthenticated user tries to view the calendar from the menu bar and it doesn't let him", () => {
    cy.visit("/calendar");
    cy.url().should("include", "/login"); // Redirected to login
    cy.contains("Sign In");
  });

  it("An unauthenticated user logs in successfully and clicks the calendar in the menu bar and then it lets him", () => {
    cy.visit("/login");

    // Fill out login form (adjust selectors to match your LoginPage)
    cy.get('input[name="username"]').type("username");
    cy.get('input[name="password"]').type("password123");
    cy.get('button[type="submit"]').click();

    // After login, store tokens
    const accessToken = fakeJWT({ username: "testuser", role: "admin", exp: Math.floor(Date.now()/1000)+3600 });
    const refreshToken = fakeJWT({ username: "testuser", type: "refresh", exp: Math.floor(Date.now()/1000)+86400 });

    cy.window().then((win) => {
      win.localStorage.setItem(
        "authTokens",
        JSON.stringify({ access: accessToken, refresh: refreshToken, roles: ["Admin"] })
      );
    });

    // Click Calendar from the menu
    cy.contains("Groups").click();
    cy.url().should("include", "/group");
  });
});
