"""
Bermuda Internship Scraper
==========================
Scrapes internship listings and outputs:

  jobs/<slug>.json     — one file per listing (used by detail.html)
  jobs/jobs.json       — flat array of all jobs (used by job-board.html)

Run manually:    python3 scraper.py
Auto-schedule:   see .github/workflows/scrape.yml
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

def save_job(job: dict):
    """Fill defaults, ensure descriptionHtml exists, then write <slug>.json."""
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

    # Fall back: wrap plain description in <p> if no HTML provided
    if not job["descriptionHtml"] and job["description"]:
        job["descriptionHtml"] = f"<p>{job['description']}</p>"

    path = os.path.join(JOBS_DIR, f"{job['slug']}.json")
    with open(path, "w") as f:
        json.dump(job, f, indent=2)
    print(f"  ✅ {job['slug']}.json")
    return job

# ── Scrapers ──────────────────────────────────────────────────────

def scrape_butterfield():
    print("\n🔍 Butterfield Bank...")
    url = "https://www.butterfieldgroup.com/careers/summer-internships"
    soup = fetch(url)
    desc = ""
    if soup:
        content = soup.find("main") or soup.find("body")
        if content:
            desc = " ".join(p.get_text(" ", strip=True) for p in content.find_all("p")[:6])[:1000]
    desc = desc or (
        "Butterfield Bank's paid Summer Internship Programme runs June–August 2026. "
        "Interns gain hands-on experience in financial services, undergo formal training, "
        "contribute to meaningful projects, and benefit from close mentoring relationships "
        "with experienced professionals across Banking, Compliance, Asset Management and Trust."
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
                "running 6–8 weeks. Interns work within the integrated financial services regulator for Bermuda.",
        },
        {
            "slug":    "Captive-Insurance-Internship-marsh-bermuda",
            "title":   "Captive Insurance Internship 2026",
            "company": "Marsh Management Services Bermuda",
            "logo":    logo("marsh.com"),
            "sector":  ["Insurance", "Risk Management"],
            "applyBy": "2026-01-09",
            "description": first_para(soup, "Marsh") or
                "Interns work directly with advisors on accounting, regulatory compliance and "
                "administrative functions for a portfolio of captive insurance companies. 6–8 weeks, summer 2026.",
        },
        {
            "slug":    "ILS-Investment-Internship-hiscox",
            "title":   "ILS Investment Internship 2026",
            "company": "Hiscox ILS",
            "logo":    logo("hiscox.com"),
            "sector":  ["Insurance", "Investments"],
            "description": first_para(soup, "Hiscox") or
                "Join Hiscox ILS in their Bermuda offices as part of the Bermuda College partnership. "
                "6–8 week summer internship focused on insurance-linked investment strategies.",
        },
        {
            "slug":    "Reinsurance-Internship-price-forbes-bermuda",
            "title":   "Rotational (Re)Insurance Internship 2026",
            "company": "Price Forbes Bermuda",
            "logo":    logo("priceforbes.com"),
            "sector":  ["Reinsurance", "Capital Markets"],
            "description": first_para(soup, "Price Forbes") or
                "A rotational internship across Insurance, Reinsurance, and Capital Markets Advisory. "
                "Interns are fully integrated into teams and gain first-hand exposure to global client broking.",
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
            "slug":    "Actuarial-Finance-Intern-global-atlantic",
            "title":   "Actuarial / Finance Summer Intern 2026",
            "company": "Global Atlantic",
            "logo":    logo("globalatlantic.com"),
            "sector":  ["Actuarial", "Finance", "Reinsurance"],
            "applyLink": "http://www.globalatlantic.com/careers/internships/7200347",
            "description": first_para(soup, "Global Atlantic") or
                "Work with the Actuarial or Finance team at Global Atlantic's Bermuda office, "
                "gaining experience in reinsurance. Open to students in actuarial science, math, stats or finance.",
        },
        {
            "slug":    "Life-Reinsurance-Intern-pacific-life-re",
            "title":   "Life Reinsurance Summer Intern 2026",
            "company": "Pacific Life Re",
            "logo":    logo("pacificlifere.com"),
            "sector":  ["Actuarial", "Reinsurance"],
            "applyLink": url,
            "description": first_para(soup, "Pacific Life") or
                "6th annual BILTIR Summer Internship with Pacific Life Re in Bermuda. "
                "For students pursuing Actuarial Science, Mathematics or Finance. Bermudian or PRC holders.",
        },
        {
            "slug":    "Risk-Finance-Intern-catalina-holdings",
            "title":   "Risk & Finance Summer Intern 2026",
            "company": "Catalina Holdings",
            "logo":    logo("catalinare.com"),
            "sector":  ["Finance", "Risk", "Reinsurance"],
            "applyLink": url,
            "description": first_para(soup, "Catalina") or
                "Hands-on experience across Risk, Compliance, Legal, Actuarial, Treasury and Finance. "
                "Includes a presentation to the business. Open to Bermuda and PRC holders.",
        },
        {
            "slug":    "Actuarial-Intern-wilton-re",
            "title":   "Actuarial Summer Intern 2026",
            "company": "Wilton Re",
            "logo":    logo("wiltonre.com"),
            "sector":  ["Actuarial", "Reinsurance"],
            "applyLink": url,
            "description": first_para(soup, "Wilton") or
                "Summer internship with Wilton Re Bermuda including Lunch & Learn sessions with "
                "other BILTIR programme interns. For students in maths, actuarial science or related degree.",
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
    soup = fetch(url)
    desc = ""
    if soup:
        content = soup.find("main") or soup.find("article") or soup.find("body")
        if content:
            desc = " ".join(p.get_text(" ", strip=True) for p in content.find_all("p")[:5])[:1000]
    desc = desc or (
        "Paid summer research fellowships for Bermudian students aged 18+, working alongside "
        "ASU BIOS scientists in field and laboratory settings. Full-time, 4–8 weeks. "
        "Session 1: June 8–July 29. Session 2: June 29–August 21, 2026. Academic credit available."
    )
    return save_job({
        "slug":            "Bermuda-Program-Summer-Research-bios",
        "title":           "Bermuda Program – Summer Research Fellowship 2026",
        "company":         "BIOS (Bermuda Institute of Ocean Sciences)",
        "logo":            logo("bios.edu"),
        "sector":          ["Science", "Marine Research"],
        "location":        "St. George's",
        "isPaid":          True,
        "duration":        "4-8 weeks",
        "workStyle":       "In-person (on-site)",
        "startDate":       "2026-06-08",
        "endDate":         "2026-08-21",
        "applyLink":       url,
        "description":     desc,
        "descriptionHtml": f"<p>{desc}</p>",
    })


# ── jobs.json builder ─────────────────────────────────────────────

def build_jobs_json():
    """
    Merge all individual <slug>.json files into jobs/jobs.json.
    Output is a FLAT ARRAY — exactly what job-board.html's fetch() expects.
    Sorted newest-first by createdDate.
    """
    all_jobs = []
    for fname in sorted(os.listdir(JOBS_DIR)):
        if fname.endswith(".json") and fname != "jobs.json":
            with open(os.path.join(JOBS_DIR, fname)) as f:
                all_jobs.append(json.load(f))

    # Sort newest first (matches default sort in job-board.html)
    all_jobs.sort(key=lambda j: j.get("createdDate", ""), reverse=True)

    with open(os.path.join(JOBS_DIR, "jobs.json"), "w") as f:
        json.dump(all_jobs, f, indent=2)

    print(f"\n📦 jobs/jobs.json → {len(all_jobs)} listings")


# ── Main ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    scrape_butterfield()
    scrape_deloitte()
    scrape_ils_bermuda()
    scrape_biltir()
    scrape_bios()
    build_jobs_json()
    print("\n✅ Done!")
