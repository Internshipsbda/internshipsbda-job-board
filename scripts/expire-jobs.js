#!/usr/bin/env node
const fs = require("fs");
const path = require("path");

const jobsDir = path.join(__dirname, "..", "jobs");
const archiveDir = path.join(__dirname, "..", "archive");
if (!fs.existsSync(archiveDir)) fs.mkdirSync(archiveDir);

const today = new Date();

fs.readdirSync(jobsDir)
  .filter(f => f.endsWith(".json") && f !== "jobs.json")
  .forEach(f => {
    const full = path.join(jobsDir, f);
    const job = JSON.parse(fs.readFileSync(full));
    if (job.applyBy && new Date(job.applyBy) < today) {
      const dest = path.join(archiveDir, f);
      fs.renameSync(full, dest);
      console.log(`Archived ${f}`);
    }
  });

// Refresh index after archiving
require("./generate-index");
