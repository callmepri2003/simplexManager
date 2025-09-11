import { defineConfig } from "cypress";
import dotenv from "dotenv";

dotenv.config();

export default defineConfig({
  e2e: {
    setupNodeEvents(on, config) {
      // implement node event listeners here
    },
    baseUrl: process.env.SELFBASEURL,
  },

  component: {
    devServer: {
      framework: "react",
      bundler: "vite",
    },
  },
});
