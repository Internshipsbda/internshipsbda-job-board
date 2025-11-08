#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

const JOBS_DIR = path.join(__dirname, '../jobs');
const ARCHIVE_DIR = path.join(__dirname, '../archive');
const EXPIRY_DAYS = 30; // Jobs older than 30 days will be archived

// Ensure archive directory exists
if (!fs.existsSync(ARCHIVE_DIR)) {
  fs.mkdirSync(ARCHIVE_DIR, { recursive: true });
}

function isExpired(createdDate) {
  const created = new Date(createdDate);
  const now = new Date();
  const diffTime = Math.abs(now - created);
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  return diffDays > EXPIRY_DAYS;
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
      
      if (job.createdDate && isExpired(job.createdDate)) {
        // Move to archive
        const archivePath = path.join(ARCHIVE_DIR, file);
        fs.renameSync(filePath, archivePath);
        console.log(`✅ Archived: ${file}`);
        expiredCount++;
      } else {
        // Keep in active jobs
        activeJobs.push(job);
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
