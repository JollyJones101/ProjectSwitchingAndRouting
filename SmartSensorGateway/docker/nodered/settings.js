module.exports = {
  flowFile: 'flows.json',
  credentialSecret: false,
  httpNodeRoot: '/red',
  userDir: '/data',
  uiPort: process.env.PORT || 1880,
  logging: {
    console: {
      level: 'info'
    }
  }
};
