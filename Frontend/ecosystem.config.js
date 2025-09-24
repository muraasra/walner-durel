module.exports = {
  apps: [{
    name: "walner-frontend",
    script: ".output/server/index.mjs",
    watch: false,
    env: {
      "NODE_ENV": "production",
      "PORT": 3000
    },
    exp_backoff_restart_delay: 100
  }]
} 