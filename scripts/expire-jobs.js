#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

const JOBS_DIR = path.join(__dirname, '../jobs');
const ARCHIVE_DIR = path.join(__dirname, '../archive');

// Ensure archive directory exists
if (!fs.existsSync(ARCHIVE_DIR)) {
  fs.mkdirSync(ARCHIVE_DIR, { recursive: true });
}

function isExpired(applicationDeadline) {
  if (!applicationDeadline) {
    // If no deadline specified, don't expire
    return false;
  }
  
  const deadline = new Date(applicationDeadline);
  const now = new Date();
  
  // Check if deadline has passed
  return now > deadline;
}

function expireJobs() {
  const files = fs.readdirSync(JOBS_DIR).filter(f => f.endsWith('.json') && f !== 'jobs.json');
  
  let expiredCount = 0;
  let activeJobs = [];

  files.forEach(file => {
    const filePath = path.join(JOBS_DIR, file);
    const content = fs.readFileSync(filePath, 'utf8');
    
    try {
      const job = JSON.parse(content);
      
      if (job.applicationDeadline && isExpired(job.applicationDeadline)) {
        // Move to archive
        const archivePath = path.join(ARCHIVE_DIR, file);
        fs.renameSync(filePath, archivePath);
        console.log(`✅ Archived: ${file} (deadline: ${job.applicationDeadline})`);
        expiredCount++;
      } else {
        // Keep in active jobs
        activeJobs.push(job);
        if (job.applicationDeadline) {
          console.log(`📌 Active: ${file} (deadline: ${job.applicationDeadline})`);
        } else {
          console.log(`📌 Active: ${file} (no deadline set)`);
        }
      }
    } catch (err) {
      console.error(`❌ Error processing ${file}:`, err.message);
    }
  });

  // Rebuild jobs.json index with only active jobs
  const jobsIndex = activeJobs.map(job => {
    const { descriptionHtml, ...jobWithoutHtml } = job;
    return jobWithoutHtml;
  });

  fs.writeFileSync(
    path.join(JOBS_DIR, 'jobs.json'),
    JSON.stringify(jobsIndex, null, 2)
  );

  console.log(`\n📊 Summary:`);
  console.log(`   Active jobs: ${activeJobs.length}`);
  console.log(`   Expired jobs: ${expiredCount}`);
  console.log(`   Updated jobs.json index`);
}

// Run the script
expireJobs();
