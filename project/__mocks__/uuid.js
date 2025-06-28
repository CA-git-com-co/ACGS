/**
 * Mock implementation of uuid package for Jest tests
 */

// Simple mock implementation that generates predictable UUIDs for testing
let counter = 0;

const v1 = () => {
  counter++;
  return `00000000-0000-1000-8000-${counter.toString().padStart(12, '0')}`;
};

const v4 = () => {
  counter++;
  return `${counter.toString().padStart(8, '0')}-0000-4000-8000-000000000000`;
};

const validate = uuid => {
  const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
  return uuidRegex.test(uuid);
};

const version = uuid => {
  if (!validate(uuid)) return null;
  return parseInt(uuid.charAt(14), 16);
};

module.exports = {
  v1,
  v4,
  validate,
  version,
};

// Also export as default for ES module compatibility
module.exports.default = {
  v1,
  v4,
  validate,
  version,
};
