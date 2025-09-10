Cypress.Commands.add("loginFakeJWT", () => {
  const fakeJWT = (payload) => {
    const header = btoa(JSON.stringify({ alg: "HS256", typ: "JWT" }));
    const body = btoa(JSON.stringify(payload));
    const signature = "signature"; // frontend doesn't verify
    return `${header}.${body}.${signature}`;
  };

  const accessToken = fakeJWT({
    username: "testuser",
    role: "admin",
    exp: Math.floor(Date.now() / 1000) + 3600, // 1 hour
  });

  const refreshToken = fakeJWT({
    username: "testuser",
    type: "refresh",
    exp: Math.floor(Date.now() / 1000) + 86400, // 24 hours
  });

  localStorage.setItem(
    "authTokens",
    JSON.stringify({ access: accessToken, refresh: refreshToken, roles: ["Admin"] })
  );
});
