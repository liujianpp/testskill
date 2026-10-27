/** @type {import('jest').Config} */
module.exports = {
  testMatch: ['<rootDir>/miniprogram/tests/**/*.spec.js'],
  testTimeout: 60000,
  maxWorkers: 1,
  setupFilesAfterEnv: ['<rootDir>/jest.setup.js'],
  reporters: ['default'],
};
