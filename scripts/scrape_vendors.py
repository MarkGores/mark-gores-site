#!/usr/bin/env python3
"""Scrape the MNRET vendor list into src/data/vendors.json.

Fetches https://www.mnrealestateteamvendors.com/ (one static page, all
vendors inline), parses category sections and vendor rows, drops the
realtor-facing categories, and writes JSON for the /vendors page.

Runs on Python stdlib only so the monthly GitHub Action needs no installs.
Fails loudly (nonzero exit, no file written) if the page shape changes or
counts drop below sanity thresholds, so a broken scrape never deploys.
"""

import html as htmlmod
import json
import re
import sys
import urllib.request
from datetime import date, datetime, timezone
from pathlib import Path

SOURCE_URL = "https://www.mnrealestateteamvendors.com/"
OUT_PATH = Path(__file__).resolve().parent.parent / "src" / "data" / "vendors.json"

# Categories aimed at agents, landlords, or commercial work, not at a
# homeowner, buyer, or seller. Everything NOT listed here is kept, so a new
# MNRET category shows up automatically instead of silently disappearing.
EXCLUDED_CATEGORIES = {
    "ACH Company",
    "Apparel",
    "Background Checks",
    "Business Broker",
    # Second-tier cuts (July 2026): lifestyle-only or too niche for a
    # homeowner/buyer/seller referral page.
    "Child Proofing",
    "Dog Walker",
    "Elevator Contractor",
    "Feng Shui",
    "Financial Planning",
    "Home Theater-Audio",
    "Property Management",
    "Spancrete Garage Floors",
    "Tiny-Homes",
    "TV Mounting",
    "Business Cards",
    "Closing Gifts",
    "Commercial Appraiser",
    "Commercial Inspector",
    "Commercial Landscaper",
    "Commercial Lender",
    "Commercial Solar Panel",
    "Commercial-HVAC",
    "Evictions",
    "HeadShots",
    "Marketing",
    "Measuring Services",
    "Name Tags",
    "Postcards",
    "Print Marketing",
    "Professional Photos - Virtual Tours",
    "Promotional Items",
    "Sign/Post Installation",
    "Signs",
    "Social Media/Website Design",
    "Transaction Management",
}

# A wrong page today should not be able to wipe the list. The live page has
# 171 categories and 570 vendors as of July 2026.
MIN_CATEGORIES = 100
MIN_VENDORS = 350

CATEGORY_RE = re.compile(r'<h3[^>]*>\s*<a name="([^"]+)">')
VENDOR_RE = re.compile(
    r'<div class="col-sm-3 dpad">\s*(?P<name>.*?)\s*</div>\s*'
    r'<div class="col-sm-2 dpad">\s*(?P<contact>.*?)\s*</div>.*?'
    r'<a href="tel:[^"]*">\s*(?P<phone>.*?)\s*</a>.*?'
    r'<a href="mailto:(?P<email>[^"]*)">.*?'
    r'<a href="(?P<website>[^"]*)"[^>]*target="_blank">.*?'
    r'<div class="col-sm-12 dpad">\s*(?P<notes>.*?)\s*</div>',
    re.S,
)


def strip_dashes(text):
    """Site rule: no em/en dashes anywhere, including scraped vendor notes."""
    text = re.sub("[ \\t]+[\\u2013\\u2014][ \\t]+", ", ", text)  # spaced dash -> comma
    text = text.replace("–", "-")  # bare en dash -> hyphen (ranges)
    text = text.replace("—", ", ")  # bare em dash -> comma
    return text


def clean(text):
    text = htmlmod.unescape(text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub("[\\u00a0\\u2002\\u2003\\u2009]", " ", text)
    text = strip_dashes(text)
    return re.sub(r"[ \t]+", " ", text).strip()


def clean_multiline(text):
    text = htmlmod.unescape(text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub("[\\u00a0\\u2002\\u2003\\u2009]", " ", text)
    text = strip_dashes(text)
    lines = [re.sub(r"[ \t]+", " ", ln).strip() for ln in text.splitlines()]
    return "\n".join(ln for ln in lines if ln)


def clean_url(url):
    url = re.sub(r"\s+", "", url)
    if url in ("", "http://", "https://"):
        return ""
    return url


def main():
    req = urllib.request.Request(SOURCE_URL, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        page = resp.read().decode("utf-8", errors="replace")

    # Split the page into category sections at each h3 anchor.
    matches = list(CATEGORY_RE.finditer(page))
    if len(matches) < MIN_CATEGORIES:
        sys.exit(
            f"FAIL: only {len(matches)} categories found (expected >= "
            f"{MIN_CATEGORIES}). Page structure probably changed; not writing."
        )

    categories = []
    total_vendors = 0
    for i, m in enumerate(matches):
        name = clean(m.group(1))
        end = matches[i + 1].start() if i + 1 < len(matches) else len(page)
        section = page[m.end() : end]
        vendors = []
        for vm in VENDOR_RE.finditer(section):
            company = clean(vm.group("name"))
            if not company:
                continue
            vendors.append(
                {
                    "company": company,
                    "contact": clean(vm.group("contact")),
                    "phone": clean(vm.group("phone")),
                    "email": clean(vm.group("email")),
                    "website": clean_url(vm.group("website")),
                    "notes": clean_multiline(vm.group("notes")),
                }
            )
        total_vendors += len(vendors)
        if name in EXCLUDED_CATEGORIES or not vendors:
            continue
        categories.append({"category": name, "vendors": vendors})

    if total_vendors < MIN_VENDORS:
        sys.exit(
            f"FAIL: only {total_vendors} vendors parsed (expected >= "
            f"{MIN_VENDORS}). Parser probably broken; not writing."
        )

    out = {
        "source": SOURCE_URL,
        "scrapedAt": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "scrapedOn": date.today().isoformat(),
        "categoryCount": len(categories),
        "vendorCount": sum(len(c["vendors"]) for c in categories),
        "categories": categories,
    }
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n")
    print(
        f"OK: {out['categoryCount']} categories, {out['vendorCount']} vendors "
        f"({len(matches) - out['categoryCount']} categories excluded/empty) -> {OUT_PATH}"
    )


if __name__ == "__main__":
    main()
