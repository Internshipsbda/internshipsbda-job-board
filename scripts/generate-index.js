#!/usr/bin/env node
const fs = require("fs");
const path = require("path");

const jobsDir = path.join(__dirname, "..", "jobs");
const indexPath = path.join(jobsDir, "jobs.json");

const today = new Date();

const jobs = fs.readdirSync(jobsDir)
  .filter(f => f.endsWith(".json") && f !== "jobs.json")
  .map(f => {
    const raw = fs.readFileSync(path.join(jobsDir, f));
    return JSON.parse(raw);
  })
  .filter(j => !j.applyBy || new Date(j.applyBy) >= today)
  .map(({ descriptionHtml, ...rest }) => rest);
  .map(({ descriptionHtml, isPaid, ...rest }) => ({ isPaid, ...rest }));


fs.writeFileSync(indexPath, JSON.stringify(jobs, null, 2));
console.log(`Wrote ${jobs.length} jobs to jobs.json`);
