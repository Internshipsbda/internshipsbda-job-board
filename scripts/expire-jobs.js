#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

const JOBS_DIR   = path.join(__dirname, '../jobs');
const ARCHIVE_DIR = path.join(__dirname, '../archive');

if (!fs.existsSync(ARCHIVE_DIR)) fs.mkdirSync(ARCHIVE_DIR, { recursive: true });

function isExpired(applyBy) {
  if (!applyBy) return false;
  return new Date() > new Date(applyBy);
}

function buildArchiveIndex() {
  const files = fs.readdirSync(ARCHIVE_DIR)
    .filter(f => f.endsWith('.json') && f !== 'archive.json' && !f.startsWith('_'));

  const jobs = files.map(f => {
    const raw = fs.readFileSync(path.join(ARCHIVE_DIR, f), 'utf8');
    try {
      const job = JSON.parse(raw);
      const { descriptionHtml, ...rest } = job;
      return rest;
    } catch { return null; }
  }).filter(Boolean);

  jobs.sort((a, b) => new Date(b.createdDate || 0) - new Date(a.createdDate || 0));
  fs.writeFileSync(path.join(ARCHIVE_DIR, 'archive.json'), JSON.stringify(jobs, null, 2));
  console.log(`  Rebuilt archive.json with ${jobs.length} archived jobs`);
}

function expireJobs() {
  const files = fs.readdirSync(JOBS_DIR)
    .filter(f => f.endsWith('.json') && f !== 'jobs.json' && !f.startsWith('_'));

  let expiredCount = 0;
  const activeJobs = [];

  files.forEach(file => {
    const filePath = path.join(JOBS_DIR, file);
    try {
      const job = JSON.parse(fs.readFileSync(filePath, 'utf8'));

      if (isExpired(job.applyBy)) {
        const archivePath = path.join(ARCHIVE_DIR, file);
        fs.renameSync(filePath, archivePath);
        console.log(`✅ Archived: ${file} (deadline: ${job.applyBy})`);
        expiredCount++;
      } else {
        activeJobs.push(job);
        console.log(`📌 Active: ${file} (deadline: ${job.applyBy || 'none'})`);
      }
    } catch (err) {
      console.error(`❌ Error processing ${file}:`, err.message);
    }
  });

  // Rebuild jobs/jobs.json (active only, no descriptionHtml)
  const activeIndex = activeJobs.map(({ descriptionHtml, ...rest }) => rest);
  fs.writeFileSync(path.join(JOBS_DIR, 'jobs.json'), JSON.stringify(activeIndex, null, 2));

  // Rebuild archive/archive.json (all archived jobs)
  buildArchiveIndex();

  console.log(`\n📊 Summary:`);
  console.log(`   Active jobs:   ${activeJobs.length}`);
  console.log(`   Expired today: ${expiredCount}`);
  console.log(`   jobs.json + archive.json both updated`);
}

expireJobs();
