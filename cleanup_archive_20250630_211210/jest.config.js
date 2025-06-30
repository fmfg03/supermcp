module.exports = {
  transform: {
    '^.+\\.js$': 'babel-jest'
  },
  moduleFileExtensions: ["js", "mjs"],
  testEnvironment: "node",
  testMatch: ["**/*.test.js"]
};

