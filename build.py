import os
import re
import csv
import json
import html
import math
import shutil
import hashlib
from collections import Counter, defaultdict
from datetime import datetime
from urllib.parse import quote
import xml.etree.ElementTree as ET

# ============================================================
# ADULT AI ART PROMPTS — PRODUCTION STATIC WEBSITE BUILDER
# Python 3 | Zero Dependencies | Cloudflare Pages / Workers
# ============================================================

BASE_URL = os.environ.get(
    "BASE_URL",
    "https://adult-ai-art-prompts.velvetgrid.workers.dev"
).rstrip("/")

SITE_NAME = "Adult AI Art Prompts"
NICHE_TOPIC = "AI Character Art Prompts, Anime Aesthetics & Style Parameters"
CONTACT_EMAIL = "nancympatten@gmail.com"
AFFILIATE_URL = "#affiliate-link"
AFFILIATE_CTA_TEXT = "Generate This AI Character Image Instantly (Free Credits)"
CURRENT_YEAR = datetime.utcnow().year

INPUT_FILE = "data.csv"
OUTPUT_DIR = "dist"

ITEMS_PER_PAGE = 24
RELATED_LIMIT = 8
HOMEPAGE_NEWEST_LIMIT = 30
SITEMAP_LIMIT = 45000

CSV_COLUMNS = [
    "slug",
    "title",
    "category",
    "subcategory",
    "target_keyword",
    "positive_prompt",
    "negative_prompt",
    "style_params",
    "description",
    "tags",
    "faq_q1",
    "faq_a1",
    "faq_q2",
    "faq_a2",
    "upload_date",
]

# ============================================================
# DESIGN SYSTEM
# ============================================================

CSS = r"""
:root {
    color-scheme: dark;
    --bg: #07080d;
    --card: #121521;
    --card2: #181c2b;
    --border: #282d40;
    --text: #f4f4fa;
    --muted: #a1a6bb;
    --violet: #8b5cf6;
    --cyan: #06b6d4;
    --green: #34d399;
    --radius: 16px;
}

* {
    box-sizing: border-box;
}

html {
    scroll-behavior: smooth;
}

body {
    margin: 0;
    background: var(--bg);
    color: var(--text);
    font-family: Inter, ui-sans-serif, system-ui, -apple-system,
                 BlinkMacSystemFont, "Segoe UI", sans-serif;
    line-height: 1.7;
}

a {
    color: var(--cyan);
    text-decoration: none;
}

a:hover {
    color: #67e8f9;
}

button, input, select, textarea {
    font: inherit;
}

button {
    cursor: pointer;
}

.container {
    width: min(1160px, calc(100% - 36px));
    margin: auto;
}

header {
    position: sticky;
    top: 0;
    z-index: 50;
    background: rgba(7,8,13,.94);
    border-bottom: 1px solid var(--border);
    backdrop-filter: blur(15px);
}

.nav {
    min-height: 70px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 20px;
}

.logo {
    font-weight: 900;
    font-size: 19px;
    color: white;
    letter-spacing: -.7px;
}

.logo span {
    color: var(--violet);
}

.nav-links {
    display: flex;
    gap: 20px;
    flex-wrap: wrap;
    font-size: 13px;
}

.hero {
    padding: 75px 0 55px;
    text-align: center;
    background:
        radial-gradient(ellipse at 50% 0%, rgba(139,92,246,.19), transparent 60%),
        radial-gradient(ellipse at 90% 40%, rgba(6,182,212,.08), transparent 45%);
}

.eyebrow {
    display: inline-flex;
    border: 1px solid rgba(139,92,246,.5);
    background: rgba(139,92,246,.12);
    color: #c4b5fd;
    padding: 6px 13px;
    border-radius: 30px;
    font-size: 12px;
    font-weight: 800;
    letter-spacing: 1px;
    text-transform: uppercase;
}

h1 {
    font-size: clamp(32px, 6vw, 58px);
    line-height: 1.13;
    letter-spacing: -2px;
    margin: 20px auto;
    max-width: 900px;
}

h2 {
    font-size: clamp(23px, 4vw, 32px);
    letter-spacing: -.7px;
    line-height: 1.25;
}

h3 {
    line-height: 1.35;
}

.lead {
    color: var(--muted);
    font-size: 17px;
    max-width: 750px;
    margin: 0 auto 25px;
}

.section {
    padding: 35px 0;
}

.section-head {
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 15px;
    margin-bottom: 22px;
}

.section-head h2 {
    margin: 0;
}

.grid {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 17px;
}

.card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 21px;
    transition: .2s ease;
    min-width: 0;
}

.card:hover {
    border-color: var(--violet);
    transform: translateY(-2px);
}

.card h3 {
    margin: 0 0 10px;
    font-size: 17px;
}

.card p {
    color: var(--muted);
    font-size: 14px;
}

.count {
    color: var(--cyan);
    font-size: 12px;
    font-weight: 800;
}

.pills {
    display: flex;
    flex-wrap: wrap;
    gap: 9px;
}

.pill {
    display: inline-flex;
    align-items: center;
    padding: 7px 12px;
    background: var(--card2);
    border: 1px solid var(--border);
    border-radius: 30px;
    color: #d9d9e8;
    font-size: 12px;
}

.search-wrap {
    max-width: 680px;
    margin: 25px auto;
}

.search-input {
    width: 100%;
    padding: 17px 20px;
    border-radius: 13px;
    border: 1px solid var(--border);
    background: var(--card);
    color: white;
    outline: none;
}

.search-input:focus {
    border-color: var(--violet);
    box-shadow: 0 0 0 3px rgba(139,92,246,.12);
}

.search-count {
    color: var(--muted);
    font-size: 13px;
    margin-top: 10px;
}

.prompt-card {
    margin: 22px 0;
    padding: 23px;
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
}

.prompt-card h2,
.prompt-card h3 {
    margin-top: 0;
}

.prompt-text {
    width: 100%;
    min-height: 150px;
    resize: vertical;
    background: #090b13;
    color: #e5e7eb;
    border: 1px solid var(--border);
    border-radius: 11px;
    padding: 16px;
    line-height: 1.7;
    font-size: 13px;
}

.copy-btn, .primary-btn {
    border: 0;
    background: linear-gradient(110deg, var(--violet), #6d28d9);
    color: white;
    border-radius: 9px;
    padding: 11px 17px;
    font-weight: 800;
    font-size: 13px;
    margin-top: 12px;
}

.copy-btn:hover, .primary-btn:hover {
    filter: brightness(1.15);
}

.secondary-btn {
    background: var(--card2);
    color: white;
    border: 1px solid var(--border);
    border-radius: 9px;
    padding: 9px 14px;
}

.token-count {
    color: var(--muted);
    font-size: 12px;
    float: right;
    margin-top: 13px;
}

.studio-controls {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 17px;
    margin-top: 20px;
}

.control-group {
    background: var(--card2);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 15px;
}

.control-group label {
    display: block;
    margin-bottom: 9px;
    font-weight: 800;
    font-size: 13px;
}

.control-group select {
    width: 100%;
    padding: 11px;
    background: #090b13;
    border: 1px solid var(--border);
    border-radius: 8px;
    color: white;
}

.model-card {
    border: 1px solid rgba(6,182,212,.3);
    background: rgba(6,182,212,.055);
    padding: 22px;
    border-radius: var(--radius);
    margin: 22px 0;
}

.model-card pre {
    white-space: pre-wrap;
    overflow-wrap: anywhere;
    color: #a5f3fc;
    font-size: 13px;
}

.status-badge {
    display: inline-block;
    color: #a7f3d0;
    background: rgba(52,211,153,.1);
    border: 1px solid rgba(52,211,153,.3);
    padding: 7px 12px;
    border-radius: 30px;
    font-size: 12px;
    margin: 12px 0;
}

.affiliate {
    text-align: center;
    background:
        linear-gradient(135deg, rgba(139,92,246,.2), rgba(6,182,212,.09)),
        var(--card);
    border: 1px solid rgba(139,92,246,.5);
    border-radius: var(--radius);
    padding: 30px 20px;
    margin: 25px 0;
}

.affiliate h2 {
    font-size: 23px;
}

.affiliate p {
    color: var(--muted);
}

.affiliate a {
    display: inline-block;
    margin-top: 10px;
    background: linear-gradient(110deg, var(--violet), #6d28d9);
    color: white;
    padding: 14px 20px;
    border-radius: 10px;
    font-weight: 900;
    font-size: 13px;
}

.breadcrumb {
    font-size: 12px;
    color: var(--muted);
    padding-top: 22px;
}

.faq-item {
    border-bottom: 1px solid var(--border);
    padding: 16px 0;
}

.faq-item h3 {
    font-size: 15px;
}

.faq-item p {
    color: var(--muted);
    font-size: 14px;
}

.pagination {
    display: flex;
    justify-content: center;
    align-items: center;
    flex-wrap: wrap;
    gap: 10px;
    padding: 30px 0;
}

.pagination a, .pagination span {
    padding: 9px 15px;
    border: 1px solid var(--border);
    background: var(--card);
    border-radius: 8px;
}

.pagination .active {
    background: var(--violet);
    border-color: var(--violet);
}

footer {
    border-top: 1px solid var(--border);
    margin-top: 65px;
    padding: 35px 0;
    color: var(--muted);
    font-size: 13px;
}

.footer-links {
    display: flex;
    gap: 18px;
    flex-wrap: wrap;
    margin: 15px 0;
}

.empty {
    color: var(--muted);
    text-align: center;
    padding: 30px;
    display: none;
}

.age-overlay {
    position: fixed;
    inset: 0;
    z-index: 9999;
    background: rgba(0,0,0,.96);
    display: none;
    align-items: center;
    justify-content: center;
    padding: 20px;
}

.age-box {
    width: min(460px, 100%);
    text-align: center;
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 18px;
    padding: 30px;
}

.age-box h2 {
    font-size: 28px;
}

.age-box p {
    color: var(--muted);
    font-size: 14px;
}

.age-box button {
    display: block;
    width: 100%;
    margin: 12px 0;
    padding: 13px;
    border-radius: 9px;
    border: 0;
    font-weight: 800;
}

.age-yes {
    background: var(--violet);
    color: white;
}

.age-no {
    background: var(--card2);
    color: white;
    border: 1px solid var(--border) !important;
}

.hidden {
    display: none !important;
}

.prose {
    max-width: 850px;
    color: var(--muted);
}

.prose h2, .prose h3 {
    color: white;
}

@media(max-width:800px) {
    .grid {
        grid-template-columns: repeat(2, minmax(0, 1fr));
    }
    .studio-controls {
        grid-template-columns: 1fr;
    }
}

@media(max-width:540px) {
    .grid {
        grid-template-columns: 1fr;
    }
    .hero {
        padding: 48px 0 35px;
    }
    .nav {
        padding: 12px 0;
        align-items: flex-start;
        flex-direction: column;
    }
    .nav-links {
        gap: 13px;
    }
    .prompt-card {
        padding: 15px;
    }
}
"""

# ============================================================
# CLIENT JAVASCRIPT
# ============================================================

JS = r"""
(function(){
    "use strict";

    // Evergreen browser-year engine.
    function updateLiveYear(){
        var year = new Date().getFullYear();

        document.querySelectorAll(".live-year").forEach(function(el){
            el.textContent = year;
        });

        var month = new Date().toLocaleString("en-US",{month:"long"});

        document.querySelectorAll(".model-freshness").forEach(function(el){
            el.textContent =
                "Updated Model Weights & Prompts • " + month + " " + year;
        });
    }

    updateLiveYear();

    // Age verification.
    var overlay = document.getElementById("ageOverlay");

    if(overlay){
        try {
            var verified = localStorage.getItem("adultArtAgeVerified");

            if(verified !== "yes"){
                overlay.style.display = "flex";
            }
        } catch(e) {
            overlay.style.display = "flex";
        }

        var yes = document.getElementById("ageYes");
        var no = document.getElementById("ageNo");

        if(yes){
            yes.addEventListener("click",function(){
                try {
                    localStorage.setItem("adultArtAgeVerified","yes");
                } catch(e) {}

                overlay.style.display = "none";
            });
        }

        if(no){
            no.addEventListener("click",function(){
                document.body.innerHTML =
                    '<main class="container section"><h1>Access restricted</h1><p>This website is intended for adults aged 18 or older.</p></main>';
            });
        }
    }

    // Copy functionality.
    document.querySelectorAll("[data-copy-target]").forEach(function(btn){
        btn.addEventListener("click",async function(){
            var target = document.getElementById(
                btn.getAttribute("data-copy-target")
            );

            if(!target) return;

            var text = target.value || target.textContent || "";

            try {
                if(navigator.clipboard && window.isSecureContext){
                    await navigator.clipboard.writeText(text);
                } else {
                    target.focus();
                    target.select();
                    var copied = document.execCommand("copy");
                    if(!copied) throw new Error("Copy failed");
                }

                var original = btn.textContent;
                btn.textContent = "Copied!";

                setTimeout(function(){
                    btn.textContent = original;
                },1600);

            } catch(e) {
                btn.textContent = "Select and copy manually";
                target.focus();
                target.select();
            }
        });
    });

    // Prompt token counter.
    var positive = document.getElementById("positivePrompt");
    var counter = document.getElementById("tokenCounter");

    function countTokens(value){
        return value.trim() ? value.trim().split(/\s+/).length : 0;
    }

    function updateCounter(){
        if(positive && counter){
            counter.textContent = countTokens(positive.value) + " words";
        }
    }

    if(positive){
        positive.addEventListener("input",updateCounter);
        updateCounter();
    }

    // Interactive style and lighting modifier.
    var ratio = document.getElementById("aspectRatio");
    var lighting = document.getElementById("lightingStyle");
    var positiveOriginal = positive ? positive.value : "";

    function updatePrompt(){
        if(!positive) return;

        var additions = [];

        if(ratio && ratio.value){
            additions.push(ratio.value);
        }

        if(lighting && lighting.value){
            additions.push(lighting.value);
        }

        positive.value = positiveOriginal;

        if(additions.length){
            positive.value += ", " + additions.join(", ");
        }

        updateCounter();
    }

    if(ratio) ratio.addEventListener("change",updatePrompt);
    if(lighting) lighting.addEventListener("change",updatePrompt);

    // Instant homepage search.
    var search = document.getElementById("promptSearch");
    var results = document.getElementById("searchResults");
    var searchCount = document.getElementById("searchCount");

    if(search && results){
        var cards = Array.from(
            results.querySelectorAll("[data-searchable]")
        );

        search.addEventListener("input",function(){
            var query = search.value.toLowerCase().trim();
            var visible = 0;

            cards.forEach(function(card){
                var content =
                    (card.getAttribute("data-searchable") || "").toLowerCase();

                var match = !query || content.includes(query);

                card.style.display = match ? "" : "none";

                if(match) visible++;
            });

            if(searchCount){
                searchCount.textContent =
                    visible + " prompt" + (visible === 1 ? "" : "s") +
                    " found";
            }

            var empty = document.getElementById("searchEmpty");

            if(empty){
                empty.style.display = visible ? "none" : "block";
            }
        });
    }
})();
"""

# ============================================================
# HELPERS
# ============================================================

def esc(value):
    return html.escape(str(value or ""), quote=True)


def clean_text(value):
    return str(value or "").strip()


def slugify(value):
    value = clean_text(value).lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = value.strip("-")
    return value or "untitled"


def safe_slug(value):
    value = slugify(value)
    return value[:120]


def parse_tags(value):
    if isinstance(value, list):
        return [clean_text(x) for x in value if clean_text(x)]

    value = clean_text(value)

    if not value:
        return []

    # Supports comma-separated, pipe-separated and semicolon-separated tags.
    parts = re.split(r"[,;|]", value)

    result = []
    seen = set()

    for part in parts:
        tag = clean_text(part)

        if tag and tag.lower() not in seen:
            result.append(tag)
            seen.add(tag.lower())

    return result


def parse_date(value):
    value = clean_text(value)

    if not value:
        return datetime(CURRENT_YEAR, 1, 1)

    formats = [
        "%Y-%m-%d",
        "%Y/%m/%d",
        "%d-%m-%Y",
        "%m/%d/%Y",
        "%Y-%m-%d %H:%M:%S",
    ]

    for fmt in formats:
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            pass

    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).replace(
            tzinfo=None
        )
    except ValueError:
        return datetime(CURRENT_YEAR, 1, 1)


def write_file(path, content):
    os.makedirs(os.path.dirname(path) or OUTPUT_DIR, exist_ok=True)

    with open(path, "w", encoding="utf-8", newline="") as file:
        file.write(content)


def canonical(path=""):
    return BASE_URL + "/" + path.lstrip("/")


def json_script(data):
    return json.dumps(
        data,
        ensure_ascii=False,
        separators=(",", ":")
    ).replace("</", "<\\/")


def relative_art(item):
    return "../" * item.get("_depth", 0) + "art/" + item["slug"] + ".html"


def item_url(item):
    return canonical("art/" + item["slug"] + ".html")


def safe_json_text(value):
    return clean_text(value).replace("\x00", "")


def unique_slug(value, used):
    base = safe_slug(value)
    result = base
    number = 2

    while result in used:
        result = base + "-" + str(number)
        number += 1

    used.add(result)
    return result


# ============================================================
# CSV READER
# ============================================================

def load_data():
    if not os.path.isfile(INPUT_FILE):
        raise FileNotFoundError(
            "data.csv was not found. Place data.csv beside build.py."
        )

    rows = []
    used_slugs = set()

    with open(
        INPUT_FILE,
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as file:

        reader = csv.DictReader(file)

        if reader.fieldnames is None:
            raise ValueError("data.csv has no header row.")

        missing = [
            col for col in CSV_COLUMNS
            if col not in reader.fieldnames
        ]

        if missing:
            raise ValueError(
                "Missing required CSV columns: " + ", ".join(missing)
            )

        for line_number, raw in enumerate(reader, start=2):
            if not raw or not any(clean_text(v) for v in raw.values()):
                continue

            row = {
                key: clean_text(raw.get(key, ""))
                for key in CSV_COLUMNS
            }

            if not row["title"]:
                print("Skipping row", line_number, "- missing title.")
                continue

            if not row["category"]:
                row["category"] = "Uncategorized"

            if not row["subcategory"]:
                row["subcategory"] = "General"

            row["tags_list"] = parse_tags(row["tags"])

            row["slug"] = unique_slug(
                row["slug"] or row["title"],
                used_slugs
            )

            row["_date"] = parse_date(row["upload_date"])
            row["_timestamp"] = row["_date"].timestamp()

            row["_category_slug"] = slugify(row["category"])
            row["_subcategory_slug"] = slugify(row["subcategory"])

            row["_tag_slugs"] = list(dict.fromkeys(
                slugify(tag) for tag in row["tags_list"]
            ))

            if not row["positive_prompt"]:
                row["positive_prompt"] = row["title"]

            if not row["negative_prompt"]:
                row["negative_prompt"] = (
                    "low quality, blurry, distorted anatomy, "
                    "extra fingers, malformed hands, artifacts, "
                    "watermark, text, duplicate limbs"
                )

            if not row["style_params"]:
                row["style_params"] = (
                    "Recommended settings: Choose a compatible model, "
                    "start with 25-35 sampling steps, CFG 5-8, "
                    "and adjust resolution according to your generator."
                )

            rows.append(row)

    if not rows:
        raise ValueError("No valid prompt rows were found in data.csv.")

    # Deterministic newest-first ordering.
    rows.sort(
        key=lambda item: (
            item["_timestamp"],
            item["title"].lower()
        ),
        reverse=True
    )

    return rows


# ============================================================
# COMMON HTML COMPONENTS
# ============================================================

def header_html(depth=0):
    prefix = "../" * depth

    return f"""
<header>
    <div class="container nav">
        <a class="logo" href="{prefix}index.html">
            VELVET<span>GRID</span> / ART PROMPTS
        </a>
        <nav class="nav-links">
            <a href="{prefix}index.html">Home</a>
            <a href="{prefix}index.html#categories">Categories</a>
            <a href="{prefix}index.html#latest">Latest Prompts</a>
            <a href="{prefix}dmca.html">DMCA</a>
        </nav>
    </div>
</header>
<!-- AD_SLOT_TOP_BANNER -->
"""


def footer_html(depth=0):
    prefix = "../" * depth

    return f"""
<footer>
    <div class="container">
        <strong>{esc(SITE_NAME)}</strong>

        <p>
            Explore creative AI character art prompts, anime aesthetics,
            composition ideas and model parameter guides.
        </p>

        <div class="footer-links">
            <a href="{prefix}index.html">Home</a>
            <a href="{prefix}dmca.html">DMCA Policy</a>
            <a href="{prefix}2257.html">18 U.S.C. 2257 Statement</a>
            <a href="mailto:{esc(CONTACT_EMAIL)}">Contact</a>
        </div>

        <p>
            © <span class="live-year">{CURRENT_YEAR}</span>
            {esc(SITE_NAME)}. All rights reserved.
        </p>

        <p>
            This website is an independent creative resource.
            External AI tools have their own policies and terms.
        </p>

        <section class="network-footer" aria-labelledby="network-footer-title">
            <h3 id="network-footer-title">Explore Our Interactive Network</h3>
            <div class="footer-links">
                <a href="https://ai-girlfriend-prompts.velvetgrid.workers.dev/">AI Girlfriend Prompts</a>
                <a href="https://couples-intimacy-games.velvetgrid.workers.dev/">Couples Intimacy Games</a>
                <a href="https://fantasy-roleplay-hub.velvetgrid.workers.dev/">Fantasy Roleplay Hub</a>
                <a href="https://character-persona-hub.velvetgrid.workers.dev/">Character Persona Hub</a>
                <a href="https://flirty-chat-openers.velvetgrid.workers.dev/">Flirty Chat Openers</a>
                <a href="https://midnight-audio-stories.velvetgrid.workers.dev/">Midnight Audio Stories</a>
                <a href="https://spicy-party-games.velvetgrid.workers.dev/">Spicy Party Games</a>
                <a href="https://intimacy-quiz-hub.velvetgrid.workers.dev/">Intimacy Quiz Hub</a>
                <a href="https://couples-bucket-list.velvetgrid.workers.dev/">Couples Bucket List</a>
                <a href="https://adult-ai-art-prompts.velvetgrid.workers.dev/">Adult AI Art Prompts</a>
            </div>
        </section>
    </div>
</footer>
<!-- AD_SLOT_STICKY_FOOTER -->
"""


def age_modal():
    return """
<div class="age-overlay" id="ageOverlay" role="dialog"
     aria-modal="true" aria-labelledby="ageTitle">
    <div class="age-box">
        <div class="eyebrow">Adults only</div>
        <h2 id="ageTitle">18+ Age Verification</h2>
        <p>
            This website is intended for adults aged 18 or older.
            Some creative prompts may explore mature artistic themes.
            By continuing, you confirm that you meet the minimum age
            requirement applicable in your location.
        </p>
        <button class="age-yes" id="ageYes">
            I am 18 or older — Continue
        </button>
        <button class="age-no" id="ageNo">
            I am under 18 — Exit
        </button>
        <p>Age verification is stored locally in your browser.</p>
    </div>
</div>
"""


def meta_tags(title, description, url, page_type="website"):
    title = esc(title[:65])
    description = esc(description[:160])
    url = esc(url)

    return f"""
<title>{title}</title>
<meta name="description" content="{description}">
<meta name="robots" content="index,follow,max-image-preview:large">
<meta name="google-site-verification" content="Ee2L9A2G2nVVNtBt7HiplcBJf1nSen-Rcz4sNqLuAdc" />
<meta name="msvalidate.01" content="4573069C62AEC27DA4F08DC57760BAD4" />
<meta name="rating" content="RTA-5042-1996-1400-1577-RTA" />
<link rel="canonical" href="{url}">
<meta property="og:type" content="{esc(page_type)}">
<meta property="og:site_name" content="{esc(SITE_NAME)}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{description}">
<meta property="og:url" content="{url}">
<meta name="twitter:card" content="summary">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{description}">
<meta name="theme-color" content="#07080d">
"""


def document(
    title,
    description,
    path,
    body,
    depth=0,
    extra_head="",
    page_type="website"
):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
{meta_tags(title, description, canonical(path), page_type)}
<link rel="stylesheet" href="{('../' * depth)}assets/style.css">
{extra_head}
<script defer src="{('../' * depth)}assets/app.js"></script>
</head>
<body>
{header_html(depth)}
<main>
{body}
</main>
{footer_html(depth)}
{age_modal()}
</body>
</html>
"""


# ============================================================
# PROMPT CARD COMPONENT
# ============================================================

def prompt_card(item):
    searchable = " ".join([
        item["title"],
        item["target_keyword"],
        item["category"],
        item["subcategory"],
        " ".join(item["tags_list"]),
    ])

    tag_html = "".join(
        '<span class="pill">' + esc(tag) + '</span>'
        for tag in item["tags_list"][:3]
    )

    return f"""
<article class="card" data-searchable="{esc(searchable)}">
    <div class="count">{esc(item["category"])}</div>
    <h3>
        <a href="{item_url(item)}">{esc(item["title"])}</a>
    </h3>
    <p>{esc(item["description"][:145])}</p>
    <div class="pills">{tag_html}</div>
    <p>
        <a href="{item_url(item)}">Explore Prompt →</a>
    </p>
</article>
"""


# ============================================================
# HOMEPAGE
# ============================================================

def build_homepage(rows):
    category_groups = defaultdict(list)
    subcategory_groups = defaultdict(list)
    tag_groups = defaultdict(list)

    for item in rows:
        category_groups[item["_category_slug"]].append(item)
        subcategory_groups[item["_subcategory_slug"]].append(item)

        for tag_slug in item["_tag_slugs"]:
            tag_groups[tag_slug].append(item)

    # One unique card per category.
    categories = sorted(
        category_groups.items(),
        key=lambda x: (-len(x[1]), x[0])
    )

    category_html = ""

    for cat_slug, items in categories:
        name = items[0]["category"]

        category_html += f"""
<div class="card">
    <h3>
        <a href="category/{esc(cat_slug)}/page-1.html">
            {esc(name)}
        </a>
    </h3>
    <span class="count">{len(items)} AI art prompts</span>
    <p>Explore creative {esc(name.lower())} prompt collections.</p>
</div>
"""

    subcategory_html = ""

    for sub_slug, items in sorted(
        subcategory_groups.items(),
        key=lambda x: (-len(x[1]), x[0])
    ):
        name = items[0]["subcategory"]

        subcategory_html += f"""
<a class="pill"
   href="topic/{quote(sub_slug)}.html">
   {esc(name)} · {len(items)}
</a>
"""

    tag_html = ""

    for tag_slug, items in sorted(
        tag_groups.items(),
        key=lambda x: (-len(x[1]), x[0])
    ):
        name = next(
            (
                tag for item in items
                for tag in item["tags_list"]
                if slugify(tag) == tag_slug
            ),
            tag_slug
        )

        tag_html += f"""
<a class="pill" href="tag/{quote(tag_slug)}.html">
    #{esc(name)} ({len(items)})
</a>
"""

    newest = rows[:HOMEPAGE_NEWEST_LIMIT]

    newest_html = "".join(prompt_card(item) for item in newest)

    body = f"""
<section class="hero">
    <div class="container">
        <div class="eyebrow">
            AI Art Prompt Library · <span class="live-year">{CURRENT_YEAR}</span>
        </div>

        <h1>
            Discover Your Next
            <span style="color:#a78bfa">AI Character Art</span>
            Masterpiece
        </h1>

        <p class="lead">
            Explore curated AI character art prompts, anime aesthetics,
            creative lighting combinations, composition techniques,
            and practical model settings.
        </p>

        <div class="search-wrap">
            <input
                id="promptSearch"
                class="search-input"
                type="search"
                placeholder="Search prompts, characters, styles and tags..."
                aria-label="Search AI art prompts"
            >
            <div id="searchCount" class="search-count">
                Search our creative prompt collection.
            </div>
        </div>

        <div class="pills" style="justify-content:center">
            <span class="pill">{len(rows)} Curated Prompts</span>
            <span class="pill">{len(categories)} Categories</span>
            <span class="pill">{len(subcategory_groups)} Topics</span>
            <span class="pill">18+ Audience</span>
        </div>
    </div>
</section>

<div class="container">

    <section class="section" id="categories">
        <div class="section-head">
            <h2>Browse AI Art Prompt Categories</h2>
            <span class="count">{len(categories)} Unique Categories</span>
        </div>

        <div class="grid">
            {category_html}
        </div>
    </section>

    <section class="section">
        <div class="section-head">
            <h2>Explore Subcategories</h2>
        </div>
        <div class="pills">
            {subcategory_html}
        </div>
    </section>

    <section class="section">
        <div class="section-head">
            <h2>Discover Popular Tags</h2>
        </div>
        <div class="pills">
            {tag_html}
        </div>
    </section>

    <!-- AD_SLOT_MID_CONTENT -->

    <section class="section" id="latest">
        <div class="section-head">
            <h2>Latest AI Art Prompts</h2>
            <span class="count">30 Newest Entries</span>
        </div>

        <div class="grid" id="searchResults">
            {newest_html}
        </div>

        <div class="empty" id="searchEmpty">
            No matching prompts found. Try another search.
        </div>
    </section>

    <section class="section">
        <div class="card">
            <h2>Welcome to the AI Art Prompt Studio</h2>
            <p>
                Find structured creative prompts, experiment with
                aspect ratios, explore lighting directions and
                discover practical image-generation parameters.
                Each prompt includes positive and negative prompt
                fields designed to make creative experimentation
                easier.
            </p>
            <p>
                Results vary according to the model, sampler,
                platform, and generation settings you choose.
            </p>
        </div>
    </section>
</div>
"""

    write_file(
        os.path.join(OUTPUT_DIR, "index.html"),
        document(
            SITE_NAME + " | AI Character Art Prompts",
            "Discover curated AI character art prompts, anime aesthetics, "
            "lighting styles, model settings and creative prompt guides.",
            "",
            body
        )
    )


# ============================================================
# DETAIL PAGE — AI ART PROMPT STUDIO
# ============================================================

def related_items(current, rows):
    current_tags = set(current["_tag_slugs"])

    scored = []

    for item in rows:
        if item["slug"] == current["slug"]:
            continue

        score = 0

        if item["_subcategory_slug"] == current["_subcategory_slug"]:
            score += 10

        if item["_category_slug"] == current["_category_slug"]:
            score += 4

        shared = current_tags.intersection(set(item["_tag_slugs"]))
        score += len(shared) * 3

        if score > 0:
            scored.append((score, item["_timestamp"], item))

    scored.sort(
        key=lambda x: (x[0], x[1]),
        reverse=True
    )

    selected = [entry[2] for entry in scored[:RELATED_LIMIT]]

    if len(selected) < RELATED_LIMIT:
        selected_slugs = {x["slug"] for x in selected}
        selected_slugs.add(current["slug"])

        for item in rows:
            if item["slug"] not in selected_slugs:
                selected.append(item)
                selected_slugs.add(item["slug"])

            if len(selected) >= RELATED_LIMIT:
                break

    return selected


def howto_schema(item):
    return {
        "@context": "https://schema.org",
        "@type": "HowTo",
        "name": "How to use " + item["title"] + " AI art prompts",
        "description": (
            "A practical guide to using positive and negative prompts "
            "in an AI image generation application."
        ),
        "step": [
            {
                "@type": "HowToStep",
                "name": "Open an AI image generator",
                "text": (
                    "Choose an image generation tool and open its "
                    "text-to-image interface."
                )
            },
            {
                "@type": "HowToStep",
                "name": "Copy the positive prompt",
                "text": (
                    "Copy the positive prompt and paste it into "
                    "the main prompt input."
                )
            },
            {
                "@type": "HowToStep",
                "name": "Configure the negative prompt",
                "text": (
                    "Copy the negative prompt into the negative "
                    "prompt field if your generator supports it."
                )
            },
            {
                "@type": "HowToStep",
                "name": "Adjust model settings",
                "text": (
                    "Review the suggested model and sampler settings. "
                    "Adjust aspect ratio, steps and guidance according "
                    "to your chosen generator."
                )
            },
            {
                "@type": "HowToStep",
                "name": "Generate and refine",
                "text": (
                    "Generate an image, review the result and refine "
                    "the prompt or parameters as needed."
                )
            }
        ]
    }


def article_schema(item, url):
    return {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": item["title"],
        "description": item["description"][:300],
        "keywords": ", ".join(
            [item["target_keyword"]] + item["tags_list"]
        ),
        "datePublished": item["_date"].strftime("%Y-%m-%d"),
        "dateModified": datetime.utcnow().strftime("%Y-%m-%d"),
        "mainEntityOfPage": {
            "@type": "WebPage",
            "@id": url
        },
        "author": {
            "@type": "Organization",
            "name": SITE_NAME
        },
        "publisher": {
            "@type": "Organization",
            "name": SITE_NAME
        }
    }


def breadcrumb_schema(item):
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": 1,
                "name": "Home",
                "item": canonical("")
            },
            {
                "@type": "ListItem",
                "position": 2,
                "name": item["category"],
                "item": canonical(
                    "category/" + item["_category_slug"] + "/page-1.html"
                )
            },
            {
                "@type": "ListItem",
                "position": 3,
                "name": item["title"],
                "item": item_url(item)
            }
        ]
    }


def faq_schema(item):
    questions = []

    for q_key, a_key in [
        ("faq_q1", "faq_a1"),
        ("faq_q2", "faq_a2")
    ]:
        question = item[q_key]
        answer = item[a_key]

        if question and answer:
            questions.append({
                "@type": "Question",
                "name": question,
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": answer
                }
            })

    if not questions:
        return None

    return {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": questions
    }


def build_detail_page(item, rows):
    title = item["title"]

    description = (
        item["description"]
        or "Explore this AI art prompt and customize its image generation settings."
    )

    url = item_url(item)

    schemas = [
        howto_schema(item),
        article_schema(item, url),
        breadcrumb_schema(item)
    ]

    faq = faq_schema(item)

    if faq:
        schemas.append(faq)

    schema_html = "\n".join(
        '<script type="application/ld+json">' +
        json_script(schema) +
        '</script>'
        for schema in schemas
    )

    tags = "".join(
        f'<a class="pill" href="../tag/{quote(slugify(tag))}.html">'
        f'#{esc(tag)}</a>'
        for tag in item["tags_list"]
    )

    related = related_items(item, rows)

    related_html = "".join(
        prompt_card(other) for other in related
    )

    faq_html = ""

    for q, a in [
        (item["faq_q1"], item["faq_a1"]),
        (item["faq_q2"], item["faq_a2"])
    ]:
        if q and a:
            faq_html += f"""
<div class="faq-item">
    <h3>{esc(q)}</h3>
    <p>{esc(a)}</p>
</div>
"""

    if not faq_html:
        faq_html = """
<div class="faq-item">
    <h3>Can I customize this AI art prompt?</h3>
    <p>
        Yes. You can modify the positive prompt, negative prompt,
        aspect ratio and lighting choices to experiment with
        different visual results.
    </p>
</div>
<div class="faq-item">
    <h3>Which AI image generator should I use?</h3>
    <p>
        Choose a compatible image generator that supports your
        preferred prompt syntax and generation parameters.
    </p>
</div>
"""

    positive = item["positive_prompt"]
    negative = item["negative_prompt"]

    body = f"""
<div class="container">

    <div class="breadcrumb">
        <a href="../index.html">Home</a> /
        <a href="../category/{esc(item["_category_slug"])}/page-1.html">
            {esc(item["category"])}
        </a> /
        {esc(title)}
    </div>

    <section class="section">
        <div class="eyebrow">{esc(item["category"])}</div>

        <h1>{esc(title)}</h1>

        <p class="lead" style="margin-left:0">
            {esc(description)}
        </p>

        <div class="pills">
            <span class="pill">{esc(item["subcategory"])}</span>
            <span class="pill">AI Character Art</span>
            <span class="pill">18+ Audience</span>
        </div>

        <div class="status-badge model-freshness">
            Updated Model Weights & Prompts •
            {datetime.utcnow().strftime("%B %Y")}
        </div>
    </section>

    <section class="prompt-card">
        <h2>Interactive AI Art Prompt Studio</h2>

        <p style="color:var(--muted)">
            Customize the composition, lighting and aspect ratio
            before copying your final prompt.
        </p>

        <div class="studio-controls">
            <div class="control-group">
                <label for="aspectRatio">Aspect Ratio</label>
                <select id="aspectRatio">
                    <option value="">Original Prompt Settings</option>
                    <option value="portrait composition, aspect ratio 2:3">
                        2:3 Portrait
                    </option>
                    <option value="cinematic widescreen composition, aspect ratio 16:9">
                        16:9 Cinematic
                    </option>
                    <option value="square composition, aspect ratio 1:1">
                        1:1 Avatar
                    </option>
                    <option value="vertical composition, aspect ratio 9:16">
                        9:16 Vertical
                    </option>
                    <option value="landscape composition, aspect ratio 4:3">
                        4:3 Landscape
                    </option>
                </select>
            </div>

            <div class="control-group">
                <label for="lightingStyle">Lighting Style</label>
                <select id="lightingStyle">
                    <option value="">Original Lighting</option>
                    <option value="neon cyberpunk lighting, vibrant magenta and cyan glow">
                        Neon Cyberpunk
                    </option>
                    <option value="soft golden hour lighting, warm sunlight">
                        Soft Golden Hour
                    </option>
                    <option value="moody candlelight, dramatic warm shadows">
                        Moody Candlelight
                    </option>
                    <option value="cinematic volumetric lighting, atmospheric haze">
                        Cinematic Volumetric
                    </option>
                    <option value="soft diffused studio lighting">
                        Soft Studio Lighting
                    </option>
                    <option value="dramatic rim lighting, deep contrast">
                        Dramatic Rim Lighting
                    </option>
                    <option value="moonlight illumination, cool blue tones">
                        Moonlight
                    </option>
                </select>
            </div>
        </div>

        <div style="margin-top:25px">
            <h3>Positive Prompt Box</h3>

            <textarea
                id="positivePrompt"
                class="prompt-text"
                spellcheck="false"
                aria-label="Positive AI art prompt"
            >{esc(positive)}</textarea>

            <span class="token-count" id="tokenCounter">0 words</span>

            <button
                class="copy-btn"
                data-copy-target="positivePrompt"
                type="button"
            >
                Copy Positive Prompt
            </button>
        </div>

        <div style="margin-top:30px">
            <h3>Negative Prompt Box</h3>

            <textarea
                id="negativePrompt"
                class="prompt-text"
                spellcheck="false"
                aria-label="Negative AI art prompt"
            >{esc(negative)}</textarea>

            <button
                class="copy-btn"
                data-copy-target="negativePrompt"
                type="button"
            >
                Copy Negative Prompt
            </button>
        </div>
    </section>

    <section class="model-card">
        <h2>Recommended Model & Sampler Settings</h2>

        <pre>{esc(item["style_params"])}</pre>

        <p style="color:var(--muted);font-size:12px">
            These settings are suggestions, not universal requirements.
            Different models and image-generation platforms may interpret
            parameters differently.
        </p>
    </section>

    <!-- AD_SLOT_MID_CONTENT -->

    <section class="affiliate">
        <div class="eyebrow">Creative AI Toolkit</div>

        <h2>Bring Your AI Character Concept to Life</h2>

        <p>
            Experiment with your customized prompt using an AI
            image-generation platform.
        </p>

        <a
            href="{esc(AFFILIATE_URL)}"
            target="_blank"
            rel="nofollow sponsored noopener"
        >
            {esc(AFFILIATE_CTA_TEXT)} →
        </a>

        <p style="font-size:11px">
            Affiliate disclosure: We may earn a commission from
            qualifying purchases or referrals at no additional cost
            to you.
        </p>
    </section>

    <section class="section prose">
        <h2>About This AI Art Prompt</h2>

        <p>{esc(description)}</p>

        <h3>Creative Prompt Details</h3>

        <p>
            Category: {esc(item["category"])}.
            Subcategory: {esc(item["subcategory"])}.
            Target keyword: {esc(item["target_keyword"])}.
        </p>

        <p>
            Use the interactive prompt studio to explore different
            lighting and composition options. Review the generated
            results and adjust the wording to match the capabilities
            of your preferred model.
        </p>

        <h3>Prompt Tags</h3>

        <div class="pills">{tags}</div>
    </section>

    <section class="section">
        <h2>Frequently Asked Questions</h2>
        {faq_html}
    </section>

    <section class="section">
        <div class="section-head">
            <h2>Related AI Art Prompts</h2>
            <span class="count">8 Recommendations</span>
        </div>

        <div class="grid">
            {related_html}
        </div>
    </section>

    <section class="section">
        <h2>Explore More</h2>
        <div class="pills">
            <a class="pill"
               href="../category/{esc(item["_category_slug"])}/page-1.html">
                More {esc(item["category"])}
            </a>

            <a class="pill"
               href="../topic/{esc(item["_subcategory_slug"])}.html">
                {esc(item["subcategory"])}
            </a>

            <a class="pill" href="../index.html">
                All AI Art Prompts
            </a>
        </div>
    </section>
</div>
"""

    html_output = document(
        title + " | AI Art Prompt Studio",
        description,
        "art/" + item["slug"] + ".html",
        body,
        depth=1,
        extra_head=schema_html,
        page_type="article"
    )

    write_file(
        os.path.join(OUTPUT_DIR, "art", item["slug"] + ".html"),
        html_output
    )


# ============================================================
# GENERIC COLLECTION HUBS
# ============================================================

def build_collection_page(
    title,
    description,
    path,
    items,
    current_page=1,
    total_pages=1,
    hub_type="category"
):
    cards = "".join(prompt_card(item) for item in items)

    previous_link = ""
    next_link = ""

    if hub_type == "category":
        base = os.path.dirname(path)

        if current_page > 1:
            previous_link = (
                f'<a href="{base}/page-{current_page - 1}.html">'
                '← Previous</a>'
            )

        if current_page < total_pages:
            next_link = (
                f'<a href="{base}/page-{current_page + 1}.html">'
                'Next →</a>'
            )

    else:
        if current_page > 1:
            previous_link = '<span>Previous</span>'

        if current_page < total_pages:
            next_link = '<span>Next</span>'

    page_numbers = ""

    if total_pages > 1:
        for page in range(1, total_pages + 1):
            if page == current_page:
                page_numbers += (
                    f'<span class="active">{page}</span>'
                )
            elif hub_type == "category":
                base = os.path.dirname(path)
                page_numbers += (
                    f'<a href="{base}/page-{page}.html">{page}</a>'
                )

    body = f"""
<div class="container">
    <section class="section">
        <div class="breadcrumb">
            <a href="../index.html">Home</a> / Collections
        </div>

        <div class="eyebrow">AI Art Prompt Collection</div>

        <h1>{esc(title)}</h1>

        <p class="lead" style="margin-left:0">
            {esc(description)}
        </p>

        <p class="count">
            {len(items)} prompts on this page
        </p>
    </section>

    <section class="section">
        <div class="grid">
            {cards}
        </div>

        <div class="pagination">
            {previous_link}
            {page_numbers}
            {next_link}
        </div>
    </section>
</div>
"""

    extra_head = ""

    if hub_type == "category":
        if current_page > 1:
            extra_head += (
                '<link rel="prev" href="' +
                esc(canonical(
                    os.path.dirname(path) +
                    "/page-" + str(current_page - 1) + ".html"
                )) + '">'
            )

        if current_page < total_pages:
            extra_head += (
                '<link rel="next" href="' +
                esc(canonical(
                    os.path.dirname(path) +
                    "/page-" + str(current_page + 1) + ".html"
                )) + '">'
            )

    html_output = document(
        title + " | " + SITE_NAME,
        description,
        path,
        body,
        depth=1 if path.count("/") == 1 else 2,
        extra_head=extra_head
    )

    write_file(
        os.path.join(OUTPUT_DIR, path),
        html_output
    )


def build_category_hubs(rows):
    groups = defaultdict(list)

    for item in rows:
        groups[item["_category_slug"]].append(item)

    for cat_slug, items in groups.items():
        category_name = items[0]["category"]

        total_pages = max(
            1,
            math.ceil(len(items) / ITEMS_PER_PAGE)
        )

        for page in range(1, total_pages + 1):
            start = (page - 1) * ITEMS_PER_PAGE
            page_items = items[start:start + ITEMS_PER_PAGE]

            path = (
                "category/" + cat_slug +
                "/page-" + str(page) + ".html"
            )

            title = category_name

            if page > 1:
                title += " - Page " + str(page)

            description = (
                f"Browse {len(items)} curated AI art prompts "
                f"in the {category_name} category. "
                "Explore creative styles, characters and image "
                "generation settings."
            )

            build_collection_page(
                title,
                description,
                path,
                page_items,
                page,
                total_pages,
                "category"
            )


def build_subcategory_hubs(rows):
    groups = defaultdict(list)

    for item in rows:
        groups[item["_subcategory_slug"]].append(item)

    for sub_slug, items in groups.items():
        name = items[0]["subcategory"]

        path = "topic/" + sub_slug + ".html"

        description = (
            f"Discover AI art prompts in the {name} topic. "
            f"Explore {len(items)} curated prompt ideas, "
            "creative styles and model settings."
        )

        build_collection_page(
            name + " AI Art Prompts",
            description,
            path,
            items,
            1,
            1,
            "topic"
        )


def build_tag_hubs(rows):
    groups = defaultdict(list)
    tag_names = {}

    for item in rows:
        for tag in item["tags_list"]:
            tag_slug = slugify(tag)

            groups[tag_slug].append(item)
            tag_names.setdefault(tag_slug, tag)

    for tag_slug, items in groups.items():
        tag_name = tag_names[tag_slug]

        path = "tag/" + tag_slug + ".html"

        description = (
            f"Explore {len(items)} AI art prompts tagged "
            f"{tag_name}. Discover related creative ideas "
            "and prompt techniques."
        )

        build_collection_page(
            "#" + tag_name + " AI Art Prompts",
            description,
            path,
            items,
            1,
            1,
            "tag"
        )


# ============================================================
# LEGAL AND POLICY PAGES
# ============================================================

def build_legal_pages():
    dmca_body = f"""
<div class="container section">
    <div class="eyebrow">Website Policy</div>
    <h1>DMCA Copyright Policy</h1>

    <div class="prose">
        <p>
            {esc(SITE_NAME)} respects intellectual property rights
            and expects website visitors and contributors to do
            the same.
        </p>

        <h2>Copyright Complaints</h2>

        <p>
            If you believe that material available on this website
            infringes your copyright, you may submit a written
            notification containing the following information:
        </p>

        <ul>
            <li>Identification of the copyrighted work.</li>
            <li>Identification of the material you believe is infringing.</li>
            <li>The specific URL or location of the material.</li>
            <li>Your name and contact information.</li>
            <li>A statement of good-faith belief that the use is unauthorized.</li>
            <li>A statement that the information is accurate and that you
                are authorized to act on behalf of the copyright owner.</li>
            <li>Your physical or electronic signature.</li>
        </ul>

        <h2>Submit a Notice</h2>

        <p>
            Contact:
            <a href="mailto:{esc(CONTACT_EMAIL)}">
                {esc(CONTACT_EMAIL)}
            </a>
        </p>

        <h2>Review and Response</h2>

        <p>
            We will review sufficiently detailed notices and take
            appropriate action where warranted. We may request
            additional information when necessary.
        </p>

        <p>
            This policy does not constitute legal advice.
        </p>
    </div>
</div>
"""

    write_file(
        os.path.join(OUTPUT_DIR, "dmca.html"),
        document(
            "DMCA Copyright Policy",
            "Copyright complaint and DMCA policy for " + SITE_NAME + ".",
            "dmca.html",
            dmca_body
        )
    )

    section_2257 = f"""
<div class="container section">
    <div class="eyebrow">Compliance Information</div>

    <h1>18 U.S.C. § 2257 Statement</h1>

    <div class="prose">
        <p>
            {esc(SITE_NAME)} is an AI art prompt resource.
            The website publishes text-based creative prompts,
            descriptions, artistic ideas and model parameter
            suggestions.
        </p>

        <h2>Nature of Website Content</h2>

        <p>
            This website is not intended to host or distribute
            actual sexually explicit photographic or video
            depictions of individuals. Its primary content consists
            of text-based creative material and AI image prompt
            instructions.
        </p>

        <h2>Record-Keeping Notice</h2>

        <p>
            To the extent any content or activity becomes subject
            to applicable record-keeping or labeling requirements
            under 18 U.S.C. §§ 2257 and 2257A or related regulations,
            the website operator will evaluate its obligations
            and comply with applicable law.
        </p>

        <h2>Contact</h2>

        <p>
            Compliance inquiries:
            <a href="mailto:{esc(CONTACT_EMAIL)}">
                {esc(CONTACT_EMAIL)}
            </a>
        </p>

        <p>
            This statement is informational and does not replace
            a legal review of the website's actual content,
            operations or jurisdictional obligations.
        </p>
    </div>
</div>
"""

    write_file(
        os.path.join(OUTPUT_DIR, "2257.html"),
        document(
            "18 U.S.C. 2257 Statement",
            "Compliance and record-keeping information for " + SITE_NAME + ".",
            "2257.html",
            section_2257
        )
    )


# ============================================================
# SITEMAP XML + XSL
# ============================================================

def build_sitemaps(rows, extra_paths):
    """
    Build a mandatory sitemap index and URL-set files from the completed
    output directory so all generated HTML pages are included automatically.
    """
    if not os.path.isdir(OUTPUT_DIR):
        raise RuntimeError(
            "Sitemap generation failed: output directory does not exist."
        )

    html_paths = []
    for root, dirs, files in os.walk(OUTPUT_DIR):
        dirs[:] = sorted(
            directory for directory in dirs
            if directory not in {".git", "__pycache__"}
        )
        for filename in files:
            if filename.lower().endswith(".html"):
                absolute_path = os.path.join(root, filename)
                relative_path = os.path.relpath(
                    absolute_path, OUTPUT_DIR
                ).replace(os.sep, "/")
                html_paths.append(relative_path)

    if "index.html" not in html_paths:
        raise RuntimeError(
            "Sitemap generation failed: dist/index.html is missing."
        )

    ordered_paths = sorted(set(html_paths))
    urls = [canonical(path) for path in ordered_paths]
    if not urls:
        raise RuntimeError(
            "Sitemap generation failed: no HTML URLs were discovered."
        )

    today = datetime.utcnow().strftime("%Y-%m-%d")

    def url_entry(url):
        return (
            "    <url>\n"
            "        <loc>" + esc(url) + "</loc>\n"
            "        <lastmod>" + today + "</lastmod>\n"
            "    </url>"
        )

    # Keep below the protocol maximum of 50,000 URLs per sitemap.
    chunk_size = min(max(int(SITEMAP_LIMIT), 1), 50000)
    chunks = [
        urls[index:index + chunk_size]
        for index in range(0, len(urls), chunk_size)
    ]
    sitemap_refs = []

    for index, chunk in enumerate(chunks, start=1):
        filename = "sitemap-" + str(index) + ".xml"
        sitemap_refs.append(
            "    <sitemap>\n"
            "        <loc>" + esc(canonical(filename)) + "</loc>\n"
            "        <lastmod>" + today + "</lastmod>\n"
            "    </sitemap>"
        )
        xml_content = (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<?xml-stylesheet type="text/xsl" href="sitemap.xsl"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            + "\n".join(url_entry(url) for url in chunk)
            + "\n</urlset>\n"
        )
        write_file(os.path.join(OUTPUT_DIR, filename), xml_content)

    sitemap_index = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<?xml-stylesheet type="text/xsl" href="sitemap.xsl"?>\n'
        '<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(sitemap_refs)
        + "\n</sitemapindex>\n"
    )
    sitemap_path = os.path.join(OUTPUT_DIR, "sitemap.xml")
    write_file(sitemap_path, sitemap_index)

    xsl = r"""<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0"
 xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
 xmlns:s="http://www.sitemaps.org/schemas/sitemap/0.9">
<xsl:output method="html" encoding="UTF-8" indent="yes"/>
<xsl:template match="/">
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>XML Sitemap | VelvetGrid</title>
<style>
*{box-sizing:border-box}
body{margin:0;padding:40px 20px;background:#07080d;color:#f4f4fa;font-family:system-ui,sans-serif}
main{max-width:1000px;margin:auto}
h1{color:#a78bfa}
p{color:#a1a6bb}
table{width:100%;border-collapse:collapse;background:#121521;border-radius:12px;overflow:hidden;margin:20px 0}
th,td{padding:14px;border-bottom:1px solid #282d40;text-align:left;overflow-wrap:anywhere}
th{color:#67e8f9}
a{color:#06b6d4}
tr:hover{background:#181c2b}
</style>
</head>
<body>
<main>
<h1>VelvetGrid XML Sitemap</h1>
<p>Generated website URLs for search engine discovery.</p>
<xsl:if test="s:urlset">
<table>
<thead><tr><th>URL</th><th>Last Modified</th></tr></thead>
<tbody>
<xsl:for-each select="s:urlset/s:url">
<tr><td><a href="{s:loc}"><xsl:value-of select="s:loc"/></a></td><td><xsl:value-of select="s:lastmod"/></td></tr>
</xsl:for-each>
</tbody>
</table>
</xsl:if>
<xsl:if test="s:sitemapindex">
<table>
<thead><tr><th>Sitemap</th><th>Last Modified</th></tr></thead>
<tbody>
<xsl:for-each select="s:sitemapindex/s:sitemap">
<tr><td><a href="{s:loc}"><xsl:value-of select="s:loc"/></a></td><td><xsl:value-of select="s:lastmod"/></td></tr>
</xsl:for-each>
</tbody>
</table>
</xsl:if>
</main>
</body>
</html>
</xsl:template>
</xsl:stylesheet>
"""
    write_file(os.path.join(OUTPUT_DIR, "sitemap.xsl"), xsl)

    # Mandatory validation gate: parse index and every referenced URL set.
    if not os.path.isfile(sitemap_path) or os.path.getsize(sitemap_path) == 0:
        raise RuntimeError(
            "Sitemap validation failed: dist/sitemap.xml is missing or empty."
        )

    namespace = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    try:
        index_root = ET.parse(sitemap_path).getroot()
    except ET.ParseError as error:
        raise RuntimeError(
            "Sitemap validation failed: sitemap.xml is invalid XML: " + str(error)
        )

    expected_index = "{http://www.sitemaps.org/schemas/sitemap/0.9}sitemapindex"
    if index_root.tag != expected_index:
        raise RuntimeError(
            "Sitemap validation failed: sitemap.xml is not a sitemap index."
        )

    references = index_root.findall("sm:sitemap/sm:loc", namespace)
    if not references:
        raise RuntimeError(
            "Sitemap validation failed: sitemap index has no sitemap references."
        )

    indexed_count = 0
    for reference in references:
        sitemap_url = clean_text(reference.text)
        sitemap_filename = sitemap_url.rsplit("/", 1)[-1]
        sitemap_file = os.path.join(OUTPUT_DIR, sitemap_filename)
        if not os.path.isfile(sitemap_file):
            raise RuntimeError(
                "Sitemap validation failed: referenced file is missing: "
                + sitemap_filename
            )
        try:
            urlset_root = ET.parse(sitemap_file).getroot()
        except ET.ParseError as error:
            raise RuntimeError(
                "Sitemap validation failed in " + sitemap_filename + ": "
                + str(error)
            )
        expected_urlset = "{http://www.sitemaps.org/schemas/sitemap/0.9}urlset"
        if urlset_root.tag != expected_urlset:
            raise RuntimeError(
                "Sitemap validation failed: " + sitemap_filename
                + " is not a URL set."
            )
        entries = urlset_root.findall("sm:url/sm:loc", namespace)
        if len(entries) > 50000:
            raise RuntimeError(
                "Sitemap validation failed: " + sitemap_filename
                + " exceeds the 50,000 URL limit."
            )
        indexed_count += len(entries)

    if indexed_count != len(urls):
        raise RuntimeError(
            "Sitemap validation failed: expected " + str(len(urls))
            + " URLs but found " + str(indexed_count) + "."
        )

    print(
        "Sitemap validated:", len(urls), "HTML URLs across",
        len(references), "sitemap file(s)."
    )


# ============================================================
# ROBOTS.TXT
# ============================================================

def build_robots():
    content = f"""User-agent: *
Allow: /

Disallow: /assets/

Sitemap: {canonical("sitemap.xml")}
"""

    write_file(
        os.path.join(OUTPUT_DIR, "robots.txt"),
        content
    )


# ============================================================
# CLOUDFLARE PAGES CONFIGURATION
# ============================================================

def build_cloudflare_files():
    # Static asset headers and cache configuration.
    headers = """/*
  X-Content-Type-Options: nosniff
  Referrer-Policy: strict-origin-when-cross-origin
  Permissions-Policy: camera=(), microphone=(), geolocation=()
  X-Frame-Options: SAMEORIGIN

/assets/*
  Cache-Control: public, max-age=31536000, immutable

/*.html
  Cache-Control: public, max-age=3600, stale-while-revalidate=86400

/sitemap*.xml
  Content-Type: application/xml; charset=utf-8

/sitemap.xsl
  Content-Type: application/xslt+xml; charset=utf-8
"""

    write_file(
        os.path.join(OUTPUT_DIR, "_headers"),
        headers
    )

    # Cloudflare Pages does not require a custom runtime for this site.
    # No Worker backend, database, or external package is required.

    write_file(
        os.path.join(OUTPUT_DIR, "_redirects"),
        ""
    )


# ============================================================
# BUILD MANIFEST
# ============================================================

def build_manifest(rows):
    manifest = {
        "site_name": SITE_NAME,
        "base_url": BASE_URL,
        "niche_topic": NICHE_TOPIC,
        "generated_year": CURRENT_YEAR,
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "python_version_required": "3.x",
        "dependencies": [],
        "total_prompts": len(rows),
        "items_per_category_page": ITEMS_PER_PAGE,
        "features": [
            "Responsive dark mode",
            "Client-side prompt search",
            "Positive prompt copy",
            "Negative prompt copy",
            "Interactive style modifier",
            "Dynamic browser year",
            "Dynamic model freshness badge",
            "Age verification",
            "Category hubs",
            "Subcategory hubs",
            "Tag hubs",
            "Related prompt recommendations",
            "JSON-LD structured data",
            "Mandatory validated XML sitemap index and URL sets",
            "Cloudflare Pages headers"
        ]
    }

    write_file(
        os.path.join(OUTPUT_DIR, "build-manifest.json"),
        json.dumps(manifest, indent=2, ensure_ascii=False)
    )


# ============================================================
# MAIN BUILD PIPELINE
# ============================================================

def main():
    print("=" * 65)
    print(" ADULT AI ART PROMPTS — STATIC SITE BUILDER")
    print("=" * 65)

    print("\n[1/10] Loading CSV data...")

    rows = load_data()

    print("Loaded prompts:", len(rows))

    if os.path.isdir(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("\n[2/10] Building static assets...")

    os.makedirs(
        os.path.join(OUTPUT_DIR, "assets"),
        exist_ok=True
    )

    write_file(
        os.path.join(OUTPUT_DIR, "assets", "style.css"),
        CSS
    )

    write_file(
        os.path.join(OUTPUT_DIR, "assets", "app.js"),
        JS
    )

    print("\n[3/10] Building homepage...")

    build_homepage(rows)

    print("\n[4/10] Building individual AI art pages...")

    for index, item in enumerate(rows, start=1):
        build_detail_page(item, rows)

        if index % 50 == 0:
            print("Generated detail pages:", index)

    print("Total detail pages:", len(rows))

    print("\n[5/10] Building category hubs...")

    build_category_hubs(rows)

    print("\n[6/10] Building subcategory hubs...")

    build_subcategory_hubs(rows)

    print("\n[7/10] Building tag hubs...")

    build_tag_hubs(rows)

    print("\n[8/10] Building policy pages...")

    build_legal_pages()

    print("\n[9/10] Building SEO infrastructure...")

    extra_paths = [
        "dmca.html",
        "2257.html",
        "robots.txt",
    ]

    category_slugs = {
        item["_category_slug"] for item in rows
    }

    for cat_slug in category_slugs:
        items = [
            item for item in rows
            if item["_category_slug"] == cat_slug
        ]

        pages = max(
            1,
            math.ceil(len(items) / ITEMS_PER_PAGE)
        )

        for page in range(1, pages + 1):
            extra_paths.append(
                f"category/{cat_slug}/page-{page}.html"
            )

    for sub_slug in {
        item["_subcategory_slug"] for item in rows
    }:
        extra_paths.append("topic/" + sub_slug + ".html")

    for tag_slug in {
        tag for item in rows for tag in item["_tag_slugs"]
    }:
        extra_paths.append("tag/" + tag_slug + ".html")

    build_sitemaps(rows, extra_paths)

    # Mandatory build gate: never report success without a valid sitemap.
    required_sitemap = os.path.join(OUTPUT_DIR, "sitemap.xml")
    if not os.path.isfile(required_sitemap) or os.path.getsize(required_sitemap) == 0:
        raise RuntimeError(
            "BUILD FAILED: mandatory dist/sitemap.xml is missing or empty."
        )

    build_robots()

    print("\n[10/10] Building Cloudflare configuration...")

    build_cloudflare_files()

    build_manifest(rows)

    # Count generated HTML documents.
    html_count = 0

    for root, dirs, files in os.walk(OUTPUT_DIR):
        html_count += sum(
            1 for filename in files
            if filename.endswith(".html")
        )

    print("\n" + "=" * 65)
    print(" BUILD COMPLETED SUCCESSFULLY")
    print("=" * 65)

    print("Website:", SITE_NAME)
    print("Base URL:", BASE_URL)
    print("Prompts:", len(rows))
    print("HTML pages:", html_count)
    print("Output directory:", os.path.abspath(OUTPUT_DIR))

    print("\nGenerated structure:")
    print("dist/")
    print("├── index.html")
    print("├── art/")
    print("├── category/")
    print("├── topic/")
    print("├── tag/")
    print("├── assets/")
    print("├── sitemap.xml")
    print("├── sitemap-1.xml")
    print("├── sitemap.xsl")
    print("├── robots.txt")
    print("├── dmca.html")
    print("├── 2257.html")
    print("├── _headers")
    print("├── _redirects")
    print("└── build-manifest.json")

    print("\nDeployment:")
    print("1. Upload the contents of dist/ to Cloudflare Pages.")
    print("2. Configure your custom domain or Workers hostname.")
    print("3. Submit sitemap.xml to Google Search Console.")
    print("4. Verify affiliate URLs and legal information.")
    print("5. Review age-verification and content compliance.")

    print("\nNote:")
    print(
        "Evergreen year updates are client-side. "
        "SEO freshness dates are generated during each build. "
        "Schedule periodic rebuilds to refresh server-rendered metadata."
    )

    print(
        "No static website can guarantee immunity from search-engine "
        "penalties, hosting restrictions, or legal requirements."
    )

    print("=" * 65)


if __name__ == "__main__":
    main()
