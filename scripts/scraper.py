"""
Bermuda Internship Scraper
==========================
Sources:
  ✅ ILS Bermuda          — ilsbermuda.com
  ✅ BILTIR               — biltir.bm
  ✅ Butterfield Bank     — butterfieldgroup.com
  ✅ BIOS                 — bios.asu.edu
  ✅ Deloitte             — hardcoded (stable listing)
  ✅ PwC Bermuda          — pwc.com/bm
  ✅ KPMG Bermuda         — kpmg.com/bm
  ✅ EY Bermuda           — ey.com/en_bm
  ✅ Bermuda Gov Jobs     — gov.bm
  ✅ Bermuda Scholarships — bermudascholarships.com
  ✅ Bermuda Job Connect  — bermudajobconnect.com
  ⚠️  LinkedIn            — cannot be scraped (login wall + bot detection)
                            → hardcoded search link card included instead

Run manually:    python3 scraper.py
Auto-schedule:   .github/workflows/scrape.yml
"""

import requests
from bs4 import BeautifulSoup
import json, os, re
from datetime import datetime, timezone

# ── Config ────────────────────────────────────────────────────────
JOBS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "jobs")
os.makedirs(JOBS_DIR, exist_ok=True)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    )
}

# ── Helpers ───────────────────────────────────────────────────────

def slugify(text: str) -> str:
    text = text.strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    return text[:80]

def logo(domain: str) -> str:
    return f"https://logo.clearbit.com/{domain}"

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def fetch(url: str):
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        r.raise_for_status()
        return BeautifulSoup(r.text, "html.parser")
    except Exception as e:
        print(f"  ⚠ Could not fetch {url}: {e}")
        return None

def first_para(soup, keyword: str) -> str:
    if not soup:
        return ""
    for tag in soup.find_all(["h2", "h3", "h4", "strong"]):
        if keyword.lower() in tag.get_text().lower():
            p = tag.find_next("p")
            if p:
                return p.get_text(" ", strip=True)[:1000]
    return ""

def all_paras(soup, max_p=6) -> str:
    if not soup:
        return ""
    content = soup.find("main") or soup.find("article") or soup.find("body")
    if not content:
        return ""
    return " ".join(p.get_text(" ", strip=True) for p in content.find_all("p")[:max_p])[:1000]

def save_job(job: dict):
    defaults = {
        "isPaid":           True,
        "duration":         "6-8 weeks",
        "workStyle":        "In-person (on-site)",
        "fullTimePathway":  "",
        "startDate":        "",
        "endDate":          "",
        "applyBy":          "",
        "applyLink":        "",
        "createdDate":      now_iso(),
        "description":      "",
        "descriptionHtml":  "",
    }
    for k, v in defaults.items():
        job.setdefault(k, v)
    if not job["descriptionHtml"] and job["description"]:
        job["descriptionHtml"] = f"<p>{job['description']}</p>"

    path = os.path.join(JOBS_DIR, f"{job['slug']}.json")
    with open(path, "w") as f:
        json.dump(job, f, indent=2)
    print(f"  ✅ {job['slug']}.json")
    return job

# ═══════════════════════════════════════════════════════════════════
# SCRAPERS
# ═══════════════════════════════════════════════════════════════════

# ── Original sources ──────────────────────────────────────────────

def scrape_butterfield():
    print("\n🔍 Butterfield Bank...")
    url = "https://www.butterfieldgroup.com/careers/summer-internships"
    desc = all_paras(fetch(url)) or (
        "Butterfield Bank's paid Summer Internship Programme runs June–August 2026. "
        "Interns gain hands-on experience in financial services, undergo formal training, "
        "contribute to meaningful projects, and benefit from close mentoring across Banking, "
        "Compliance, Asset Management and Trust."
    )
    return save_job({
        "slug":            "Summer-Internship-Programme-butterfield-bank",
        "title":           "Summer Internship Programme 2026",
        "company":         "Butterfield Bank",
        "logo":            logo("butterfieldgroup.com"),
        "sector":          ["Banking", "Finance"],
        "location":        "City of Hamilton",
        "isPaid":          True,
        "duration":        "8-10 weeks",
        "workStyle":       "In-person (on-site)",
        "fullTimePathway": "Yes",
        "startDate":       "2026-06-01",
        "endDate":         "2026-08-31",
        "applyBy":         "2026-03-01",
        "applyLink":       url,
        "description":     desc,
        "descriptionHtml": f"<p>{desc}</p>",
    })


def scrape_deloitte():
    print("\n🔍 Deloitte Bermuda...")
    desc = (
        "Deloitte's Exclusive Experience Program (DEEP) — work on real client projects, "
        "receive mentorship from senior professionals, and collaborate with interns from "
        "Deloitte's global network. You will analyze data, prepare work papers, conduct "
        "industry research, and participate in developing innovative client solutions. "
        "Open to Bermudian students only."
    )
    return save_job({
        "slug":            "DEEP-Summer-Internship-deloitte-bermuda",
        "title":           "DEEP Summer Internship 2026",
        "company":         "Deloitte Bermuda",
        "logo":            logo("deloitte.com"),
        "sector":          ["Accounting", "Consulting", "Finance"],
        "location":        "City of Hamilton",
        "isPaid":          True,
        "duration":        "8 weeks",
        "workStyle":       "In-person (on-site)",
        "fullTimePathway": "Yes",
        "applyLink":       "https://jobs.accaglobal.com/job/13822386/bermudian-students-only-2026-co-op-internships/",
        "description":     desc,
        "descriptionHtml": f"<p>{desc}</p>",
    })


def scrape_ils_bermuda():
    print("\n🔍 ILS Bermuda...")
    url = "https://ilsbermuda.com/education-initiative"
    soup = fetch(url)
    listings = [
        {
            "slug":    "ILS-Internship-bermuda-monetary-authority",
            "title":   "ILS & Long-term Business Internship 2026",
            "company": "Bermuda Monetary Authority",
            "logo":    logo("bma.bm"),
            "sector":  ["Insurance", "Regulation", "Finance"],
            "applyBy": "2025-12-31",
            "description": first_para(soup, "Monetary Authority") or
                "The BMA offers two summer 2026 internship tracks — ILS and Long-term Business — "
                "running 6–8 weeks within Bermuda's integrated financial services regulator.",
        },
        {
            "slug":    "Captive-Insurance-Internship-marsh-bermuda",
            "title":   "Captive Insurance Internship 2026",
            "company": "Marsh Management Services Bermuda",
            "logo":    logo("marsh.com"),
            "sector":  ["Insurance", "Risk Management"],
            "applyBy": "2026-01-09",
            "description": first_para(soup, "Marsh") or
                "Interns work on accounting, regulatory compliance and admin for a portfolio of "
                "captive insurance companies. 6–8 weeks, summer 2026.",
        },
        {
            "slug":    "ILS-Investment-Internship-hiscox",
            "title":   "ILS Investment Internship 2026",
            "company": "Hiscox ILS",
            "logo":    logo("hiscox.com"),
            "sector":  ["Insurance", "Investments"],
            "description": first_para(soup, "Hiscox") or
                "Join Hiscox ILS in their Bermuda offices through the Bermuda College partnership. "
                "6–8 week summer internship in insurance-linked investment strategies.",
        },
        {
            "slug":    "Reinsurance-Internship-price-forbes-bermuda",
            "title":   "Rotational (Re)Insurance Internship 2026",
            "company": "Price Forbes Bermuda",
            "logo":    logo("priceforbes.com"),
            "sector":  ["Reinsurance", "Capital Markets"],
            "description": first_para(soup, "Price Forbes") or
                "Rotational internship across Insurance, Reinsurance, and Capital Markets Advisory "
                "with full team integration and exposure to global client broking.",
        },
    ]
    results = []
    for item in listings:
        item.setdefault("location", "City of Hamilton")
        item.setdefault("applyLink", url)
        results.append(save_job(item))
    return results


def scrape_biltir():
    print("\n🔍 BILTIR...")
    url = "https://biltir.bm/2024-summer-intern-opportunities"
    soup = fetch(url)
    listings = [
        {
            "slug":      "Actuarial-Finance-Intern-global-atlantic",
            "title":     "Actuarial / Finance Summer Intern 2026",
            "company":   "Global Atlantic",
            "logo":      logo("globalatlantic.com"),
            "sector":    ["Actuarial", "Finance", "Reinsurance"],
            "applyLink": "http://www.globalatlantic.com/careers/internships/7200347",
            "description": first_para(soup, "Global Atlantic") or
                "Work with the Actuarial or Finance team at Global Atlantic's Bermuda office. "
                "Open to students in actuarial science, math, statistics or finance.",
        },
        {
            "slug":      "Life-Reinsurance-Intern-pacific-life-re",
            "title":     "Life Reinsurance Summer Intern 2026",
            "company":   "Pacific Life Re",
            "logo":      logo("pacificlifere.com"),
            "sector":    ["Actuarial", "Reinsurance"],
            "applyLink": url,
            "description": first_para(soup, "Pacific Life") or
                "6th annual BILTIR Summer Internship with Pacific Life Re. For students pursuing "
                "Actuarial Science, Mathematics or Finance. Bermudian or PRC holders only.",
        },
        {
            "slug":      "Risk-Finance-Intern-catalina-holdings",
            "title":     "Risk & Finance Summer Intern 2026",
            "company":   "Catalina Holdings",
            "logo":      logo("catalinare.com"),
            "sector":    ["Finance", "Risk", "Reinsurance"],
            "applyLink": url,
            "description": first_para(soup, "Catalina") or
                "Experience across Risk, Compliance, Legal, Actuarial, Treasury and Finance, "
                "including a presentation to the business. Open to Bermuda and PRC holders.",
        },
        {
            "slug":      "Actuarial-Intern-wilton-re",
            "title":     "Actuarial Summer Intern 2026",
            "company":   "Wilton Re",
            "logo":      logo("wiltonre.com"),
            "sector":    ["Actuarial", "Reinsurance"],
            "applyLink": url,
            "description": first_para(soup, "Wilton") or
                "Summer internship with Wilton Re Bermuda with Lunch & Learn sessions alongside "
                "other BILTIR programme interns. For maths or actuarial science students.",
        },
    ]
    results = []
    for item in listings:
        item.setdefault("location", "City of Hamilton")
        results.append(save_job(item))
    return results


def scrape_bios():
    print("\n🔍 BIOS...")
    url = "https://bios.asu.edu/education/bermuda-program"
    desc = all_paras(fetch(url)) or (
        "Paid summer research fellowships for Bermudian students aged 18+, working alongside "
        "ASU BIOS scientists in field and lab settings. Full-time, 4–8 weeks. "
        "Session 1: June 8–July 29. Session 2: June 29–August 21, 2026."
    )
    return save_job({
        "slug":      "Bermuda-Program-Summer-Research-bios",
        "title":     "Bermuda Program – Summer Research Fellowship 2026",
        "company":   "BIOS (Bermuda Institute of Ocean Sciences)",
        "logo":      logo("bios.edu"),
        "sector":    ["Science", "Marine Research"],
        "location":  "St. George's",
        "duration":  "4-8 weeks",
        "startDate": "2026-06-08",
        "endDate":   "2026-08-21",
        "applyLink": url,
        "description":     desc,
        "descriptionHtml": f"<p>{desc}</p>",
    })


# ── New sources ───────────────────────────────────────────────────

def scrape_pwc_bermuda():
    print("\n🔍 PwC Bermuda...")
    url = "https://www.pwc.com/bm/en/careers/student-programs.html"
    soup = fetch(url)
    desc = all_paras(soup) or (
        "PwC Bermuda's student internship programme offers hands-on experience across Audit, "
        "Tax and Advisory services. Interns work alongside experienced professionals on real "
        "client engagements. Strong candidates may receive full-time offers upon graduation."
    )
    return save_job({
        "slug":            "Summer-Internship-pwc-bermuda",
        "title":           "Student Internship Programme 2026",
        "company":         "PwC Bermuda",
        "logo":            logo("pwc.com"),
        "sector":          ["Accounting", "Audit", "Consulting"],
        "location":        "City of Hamilton",
        "isPaid":          True,
        "duration":        "8-10 weeks",
        "workStyle":       "In-person (on-site)",
        "fullTimePathway": "Yes",
        "applyLink":       url,
        "description":     desc,
        "descriptionHtml": f"<p>{desc}</p>",
    })


def scrape_kpmg_bermuda():
    print("\n🔍 KPMG Bermuda...")
    url = "https://kpmg.com/bm/en/home/careers.html"
    soup = fetch(url)
    desc = all_paras(soup) or (
        "KPMG Bermuda offers summer internships across Audit, Tax and Advisory. "
        "Interns gain exposure to Bermuda's international business sector, working on "
        "real engagements with a globally connected team of professionals."
    )
    return save_job({
        "slug":            "Summer-Internship-kpmg-bermuda",
        "title":           "Summer Internship 2026",
        "company":         "KPMG Bermuda",
        "logo":            logo("kpmg.com"),
        "sector":          ["Accounting", "Audit", "Tax"],
        "location":        "City of Hamilton",
        "isPaid":          True,
        "duration":        "8 weeks",
        "workStyle":       "In-person (on-site)",
        "fullTimePathway": "Yes",
        "applyLink":       url,
        "description":     desc,
        "descriptionHtml": f"<p>{desc}</p>",
    })


def scrape_ey_bermuda():
    print("\n🔍 EY Bermuda...")
    url = "https://www.ey.com/en_bm/careers"
    soup = fetch(url)
    desc = all_paras(soup) or (
        "EY Bermuda's internship programme places students within Assurance, Tax and "
        "Consulting teams. Interns work on client projects in Bermuda's international "
        "business and insurance sectors, with mentorship from senior EY professionals."
    )
    return save_job({
        "slug":            "Summer-Internship-ey-bermuda",
        "title":           "Summer Internship 2026",
        "company":         "EY Bermuda",
        "logo":            logo("ey.com"),
        "sector":          ["Accounting", "Assurance", "Tax"],
        "location":        "City of Hamilton",
        "isPaid":          True,
        "duration":        "8 weeks",
        "workStyle":       "In-person (on-site)",
        "fullTimePathway": "Yes",
        "applyLink":       url,
        "description":     desc,
        "descriptionHtml": f"<p>{desc}</p>",
    })


def scrape_bermuda_gov():
    print("\n🔍 Bermuda Government Jobs...")
    url = "https://www.gov.bm/jobs"
    soup = fetch(url)
    listings = []

    if soup:
        # Gov site lists job postings in various formats — try common patterns
        for item in soup.select("article, .views-row, .job-listing, li.job"):
            title_tag = item.find(["h2", "h3", "h4", "a"])
            if not title_tag:
                continue
            title = title_tag.get_text(strip=True)
            if not any(kw in title.lower() for kw in ["intern", "cadet", "trainee", "student", "apprentice"]):
                continue
            link_tag = item.find("a", href=True)
            link = link_tag["href"] if link_tag else url
            if link.startswith("/"):
                link = "https://www.gov.bm" + link
            desc_tag = item.find("p")
            desc = desc_tag.get_text(" ", strip=True)[:500] if desc_tag else ""
            listings.append(save_job({
                "slug":      slugify(f"{title}-bermuda-government"),
                "title":     title,
                "company":   "Bermuda Government",
                "logo":      logo("gov.bm"),
                "sector":    ["Government", "Public Sector"],
                "location":  "City of Hamilton",
                "applyLink": link,
                "description":     desc or f"Internship/trainee opportunity with the Bermuda Government. See listing for full details.",
                "descriptionHtml": f"<p>{desc}</p>" if desc else "<p>See listing for full details.</p>",
            }))

    if not listings:
        # Fallback: link card pointing to gov jobs board
        listings.append(save_job({
            "slug":            "internships-bermuda-government-jobs",
            "title":           "Student & Internship Opportunities",
            "company":         "Bermuda Government",
            "logo":            logo("gov.bm"),
            "sector":          ["Government", "Public Sector"],
            "location":        "Bermuda",
            "applyLink":       url,
            "description":     "The Bermuda Government regularly posts internship, cadet and student placements across various ministries. Visit the Government Jobs portal for current openings.",
            "descriptionHtml": "<p>The Bermuda Government regularly posts internship, cadet and student placements across various ministries. Visit the Government Jobs portal for current openings.</p>",
        }))

    return listings


def scrape_bermuda_scholarships():
    print("\n🔍 Bermuda Scholarships...")
    url = "https://www.bermudascholarships.com"
    soup = fetch(url)
    listings = []

    if soup:
        # Look for internship/work experience listings
        for item in soup.select("article, .listing, .post, .entry"):
            title_tag = item.find(["h2", "h3", "h4"])
            if not title_tag:
                continue
            title = title_tag.get_text(strip=True)
            if not any(kw in title.lower() for kw in ["intern", "work experience", "placement", "summer"]):
                continue
            link_tag = item.find("a", href=True)
            link = link_tag["href"] if link_tag else url
            if link.startswith("/"):
                link = "https://www.bermudascholarships.com" + link
            desc_tag = item.find("p")
            desc = desc_tag.get_text(" ", strip=True)[:500] if desc_tag else ""
            listings.append(save_job({
                "slug":      slugify(f"{title}-bermuda-scholarships"),
                "title":     title,
                "company":   "Bermuda Scholarships",
                "logo":      logo("bermudascholarships.com"),
                "sector":    ["Education", "General"],
                "location":  "Bermuda",
                "applyLink": link,
                "description":     desc or "See listing on Bermuda Scholarships for full details.",
                "descriptionHtml": f"<p>{desc}</p>" if desc else "<p>See listing for full details.</p>",
            }))

    if not listings:
        listings.append(save_job({
            "slug":            "internships-bermuda-scholarships-portal",
            "title":           "Internship & Work Experience Listings",
            "company":         "Bermuda Scholarships",
            "logo":            logo("bermudascholarships.com"),
            "sector":          ["Education", "General"],
            "location":        "Bermuda",
            "applyLink":       url,
            "description":     "Bermuda Scholarships lists internship and work experience opportunities alongside scholarship information for Bermudian students.",
            "descriptionHtml": "<p>Bermuda Scholarships lists internship and work experience opportunities alongside scholarship information for Bermudian students.</p>",
        }))

    return listings


def scrape_bermuda_job_connect():
    print("\n🔍 Bermuda Job Connect...")
    url = "https://www.bermudajobconnect.com"
    soup = fetch(url)
    listings = []

    if soup:
        for item in soup.select("article, .job-listing, .job-post, .views-row, li.job"):
            title_tag = item.find(["h2", "h3", "h4", "a"])
            if not title_tag:
                continue
            title = title_tag.get_text(strip=True)
            if not any(kw in title.lower() for kw in ["intern", "student", "trainee", "summer", "graduate", "entry"]):
                continue
            link_tag = item.find("a", href=True)
            link = link_tag["href"] if link_tag else url
            if link.startswith("/"):
                link = "https://www.bermudajobconnect.com" + link
            company_tag = item.find(class_=re.compile(r"company|employer|org", re.I))
            company = company_tag.get_text(strip=True) if company_tag else "Various"
            desc_tag = item.find("p")
            desc = desc_tag.get_text(" ", strip=True)[:500] if desc_tag else ""
            listings.append(save_job({
                "slug":      slugify(f"{title}-{company}-bjc"),
                "title":     title,
                "company":   company,
                "logo":      logo("bermudajobconnect.com"),
                "sector":    ["General"],
                "location":  "Bermuda",
                "applyLink": link,
                "description":     desc or "See full listing on Bermuda Job Connect.",
                "descriptionHtml": f"<p>{desc}</p>" if desc else "<p>See full listing on Bermuda Job Connect.</p>",
            }))

    if not listings:
        listings.append(save_job({
            "slug":            "internships-bermuda-job-connect",
            "title":           "Internship & Entry-Level Listings",
            "company":         "Bermuda Job Connect",
            "logo":            logo("bermudajobconnect.com"),
            "sector":          ["General"],
            "location":        "Bermuda",
            "applyLink":       url,
            "description":     "Bermuda Job Connect aggregates local job and internship postings across all sectors. Visit the site and filter by internship or entry-level for current openings.",
            "descriptionHtml": "<p>Bermuda Job Connect aggregates local job and internship postings across all sectors. Visit the site and filter by internship or entry-level for current openings.</p>",
        }))

    return listings


def scrape_linkedin_card():
    """
    LinkedIn blocks scrapers. Instead we add a link card pointing to
    a pre-filtered LinkedIn job search for Bermuda internships.
    """
    print("\n⚠️  LinkedIn — adding search link card (scraping not possible)...")
    search_url = "https://www.linkedin.com/jobs/search/?keywords=internship&location=Bermuda"
    return save_job({
        "slug":            "internships-search-linkedin-bermuda",
        "title":           "Search Internships on LinkedIn",
        "company":         "LinkedIn",
        "logo":            logo("linkedin.com"),
        "sector":          ["General"],
        "location":        "Bermuda",
        "isPaid":          True,
        "applyLink":       search_url,
        "description":     "LinkedIn cannot be scraped automatically. Click 'Read More' to go directly to a pre-filtered LinkedIn job search for internships in Bermuda.",
        "descriptionHtml": "<p>LinkedIn cannot be scraped automatically. Click the button below to go directly to a pre-filtered LinkedIn job search for internships in Bermuda.</p>",
    })


# ── jobs.json builder ─────────────────────────────────────────────

def build_jobs_json():
    """
    Merge all <slug>.json files into jobs/jobs.json as a FLAT ARRAY
    — exactly what job-board.html's fetch() expects.
    Sorted newest-first by createdDate.
    """
    all_jobs = []
    for fname in sorted(os.listdir(JOBS_DIR)):
        if fname.endswith(".json") and fname != "jobs.json":
            with open(os.path.join(JOBS_DIR, fname)) as f:
                all_jobs.append(json.load(f))

    all_jobs.sort(key=lambda j: j.get("createdDate", ""), reverse=True)

    with open(os.path.join(JOBS_DIR, "jobs.json"), "w") as f:
        json.dump(all_jobs, f, indent=2)

    print(f"\n📦 jobs/jobs.json → {len(all_jobs)} listings")


# ── Main ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Original sources
    scrape_butterfield()
    scrape_deloitte()
    scrape_ils_bermuda()
    scrape_biltir()
    scrape_bios()

    # New sources
    scrape_pwc_bermuda()
    scrape_kpmg_bermuda()
    scrape_ey_bermuda()
    scrape_bermuda_gov()
    scrape_bermuda_scholarships()
    scrape_bermuda_job_connect()
    scrape_linkedin_card()

    build_jobs_json()
    print("\n✅ Done!")
