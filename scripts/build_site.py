#!/usr/bin/env python3
import csv
import html
import json
import re
import shutil
from collections import defaultdict
from datetime import date
from pathlib import Path
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse


ROOT = Path(__file__).resolve().parents[1]
EXPORT = ROOT / "nationalparkcam_export"
DIST = ROOT / "docs"
PAGES_OUT = DIST / "parks"
ASSETS_OUT = DIST / "assets"
SITE_URL = "https://national-parks.us"
NATIONALPARKCAM_SITE_URL = "https://www.nationalparkcam.com"
GOOGLE_ANALYTICS_ID = "G-6SYHNQMD41"
INFO_PAGE_SLUGS = {"about", "contact", "privacy-policy"}


SECTION_TITLES = {
    "Introduction",
    "Day Hikes",
    "Top Hikes and Climbs",
    "Hiking and Backpacking",
    "Backpacking",
    "Camping and Lodging",
    "Camping",
    "Lodging",
    "Fishing",
    "Wildlife Viewing",
    "Biking",
    "Climbing",
    "Accommodations",
    "Food & Groceries",
    "Getting Around - Transportation",
    "External Links",
    "Short History of the National Park",
}

PARK_NAMES = {
    "acadia-webcam": "Acadia National Park",
    "arches-webcam": "Arches National Park",
    "big-bend-webcam": "Big Bend National Park",
    "black-canyon-of-the-gunnison-webcam": "Black Canyon of the Gunnison National Park",
    "bryce-canyon-webcam": "Bryce Canyon National Park",
    "channel-islands-webcam": "Channel Islands National Park",
    "colorado-national-monument-webcam": "Colorado National Monument",
    "crater-lake-webcam": "Crater Lake National Park",
    "denali-webcam": "Denali National Park",
    "dinosaur-national-monument-webcam": "Dinosaur National Monument",
    "everglades-webcam": "Everglades National Park",
    "florissant-fossil-beds-national-monument-webcam": "Florissant Fossil Beds National Monument",
    "glacier-bay-webcam": "Glacier Bay National Park",
    "glacier-webcam": "Glacier National Park",
    "grand-canyon-parashant-national-monument-webcam": "Grand Canyon-Parashant National Monument",
    "grand-canyon-webcam": "Grand Canyon National Park",
    "grand-tetons-webcam": "Grand Teton National Park",
    "great-smoky-mountains-webcam": "Great Smoky Mountains National Park",
    "guadalupe-mountains-webcam": "Guadalupe Mountains National Park",
    "haleakala-webcam": "Haleakala National Park",
    "hawaii-volcanoes-webcam": "Hawaii Volcanoes National Park",
    "isle-royale-national-park-webcam": "Isle Royale National Park",
    "john-day-fossil-beds-national-monument-webcam": "John Day Fossil Beds National Monument",
    "joshua-tree-webcam": "Joshua Tree National Park",
    "katmai-webcam": "Katmai National Park",
    "kings-canyon-webcam": "Sequoia and Kings Canyon National Parks",
    "lassen-volcano-webcam": "Lassen Volcanic National Park",
    "mammoth-cave-webcam": "Mammoth Cave National Park",
    "mount-rainier-webcam": "Mount Rainier National Park",
    "new-river-gorge-webcam": "New River Gorge National Park",
    "north-cascades-webcam": "North Cascades National Park",
    "olympic-webcam": "Olympic National Park",
    "petrified-forest-webcam": "Petrified Forest National Park",
    "redwood-national-park": "Redwood National and State Parks",
    "rocky-mountain-webcam": "Rocky Mountain National Park",
    "shenandoah-webcam": "Shenandoah National Park",
    "theodore-roosevelt-webcam": "Theodore Roosevelt National Park",
    "virgin-islands-webcam": "Virgin Islands National Park",
    "wrangell-st-elias-webcam": "Wrangell-St. Elias National Park",
    "yellowstone-webcam": "Yellowstone National Park",
    "yosemite-webcam": "Yosemite National Park",
    "zion-webcam": "Zion National Park",
}

PARK_COORDS = {
    "acadia-webcam": [44.3386, -68.2733],
    "arches-webcam": [38.7331, -109.5925],
    "big-bend-webcam": [29.1275, -103.2425],
    "black-canyon-of-the-gunnison-webcam": [38.5754, -107.7416],
    "bryce-canyon-webcam": [37.593, -112.1871],
    "channel-islands-webcam": [34.0069, -119.7785],
    "colorado-national-monument-webcam": [39.0538, -108.7147],
    "crater-lake-webcam": [42.9446, -122.109],
    "denali-webcam": [63.1148, -151.1926],
    "dinosaur-national-monument-webcam": [40.4416, -109.3047],
    "everglades-webcam": [25.2866, -80.8987],
    "florissant-fossil-beds-national-monument-webcam": [38.9126, -105.2803],
    "glacier-bay-webcam": [58.6658, -136.9002],
    "glacier-webcam": [48.7596, -113.787],
    "grand-canyon-parashant-national-monument-webcam": [36.3911, -113.6877],
    "grand-canyon-webcam": [36.1069, -112.1129],
    "grand-tetons-webcam": [43.7904, -110.6818],
    "great-smoky-mountains-webcam": [35.6118, -83.4895],
    "guadalupe-mountains-webcam": [31.923, -104.87],
    "haleakala-webcam": [20.7204, -156.1552],
    "hawaii-volcanoes-webcam": [19.4194, -155.2885],
    "isle-royale-national-park-webcam": [48.011, -88.8278],
    "john-day-fossil-beds-national-monument-webcam": [44.6257, -119.8811],
    "joshua-tree-webcam": [33.8734, -115.901],
    "katmai-webcam": [58.5975, -154.6939],
    "kings-canyon-webcam": [36.8879, -118.5551],
    "lassen-volcano-webcam": [40.4977, -121.4207],
    "mammoth-cave-webcam": [37.1862, -86.1005],
    "mount-rainier-webcam": [46.8523, -121.7603],
    "new-river-gorge-webcam": [37.8683, -80.9996],
    "north-cascades-webcam": [48.7718, -121.2985],
    "olympic-webcam": [47.8021, -123.6044],
    "petrified-forest-webcam": [35.0659, -109.781],
    "redwood-national-park": [41.2132, -124.0046],
    "rocky-mountain-webcam": [40.3428, -105.6836],
    "shenandoah-webcam": [38.5339, -78.35],
    "theodore-roosevelt-webcam": [46.979, -103.5387],
    "virgin-islands-webcam": [18.3424, -64.7486],
    "wrangell-st-elias-webcam": [61.7104, -142.9857],
    "yellowstone-webcam": [44.6, -110.5],
    "yosemite-webcam": [37.8651, -119.5383],
    "zion-webcam": [37.2982, -113.0263],
}

PAGE_SOURCE_EMBEDS = {
    "https://video-monitoring.com/everglades/royalpalm/": {
        "kind": "image",
        "url": "https://video-monitoring.com/everglades/royalpalm/sstn/s1.jpg",
    },
    "https://www.nps.gov/media/webcam/view.htm?id=81B46712-1DD8-B71B-0B4B99EDA0AE3CFC": {
        "kind": "image",
        "url": "https://www.nps.gov/webcams-glba/BartlettDock.jpg",
    },
    "https://www.nps.gov/media/webcam/view.htm?id=81B4672D-1DD8-B71B-0B04336F55ECDD47": {
        "kind": "image",
        "url": "https://www.nps.gov/webcams-glba/LowerBay.jpg",
    },
    "https://www.nps.gov/media/webcam/view.htm?id=81B46B99-1DD8-B71B-0B124A40CC3384CE": {
        "kind": "image",
        "url": "https://www.nps.gov/webcams-shen/bvc2.jpg",
    },
    "https://www.nps.gov/media/webcam/view.htm?id=51F606E1-BAF1-472B-2BC7D21ED4CDA08E": {
        "kind": "image",
        "url": "https://www.nps.gov/webcams-wrst/KennecottNorth.jpg",
    },
    "https://www.nps.gov/media/webcam/view.htm?id=5224B014-CBDE-5E14-DEF34EBF65E78E88": {
        "kind": "image",
        "url": "https://www.nps.gov/webcams-wrst/KennecottSouth.jpg",
    },
    "https://www.nps.gov/media/webcam/view.htm?id=F91F11B2-C421-28C4-16C717FF1FF2CB72": {
        "kind": "image",
        "url": "https://www.nps.gov/webcams-wrst/HQVC.jpg",
    },
    "https://www.nps.gov/media/webcam/view.htm?id=B28D5845-C504-BBA5-17748BFF1C6CC716": {
        "kind": "image",
        "url": "https://cdn.pixelcaster.com/public.pixelcaster.com/snapshots/yosemite-turtleback/latest.jpg",
        "status": "Current webcam image",
        "description": "Located on a dome near the Wawona Tunnel, this webcam provides a view of Yosemite Valley.",
    },
    "https://www.nps.gov/media/webcam/view.htm?id=1148077C-F06F-CD3A-969692F6BC0481AC": {
        "kind": "image",
        "url": "https://cdn.pixelcaster.com/public.pixelcaster.com/snapshots/yosemite-sentinel/latest.jpg",
        "status": "Current webcam image",
        "description": "This webcam looks across Yosemite's high country toward Half Dome and the surrounding peaks.",
    },
    "https://www.nps.gov/media/webcam/view.htm?id=EAA24FCD-BC0D-C360-19BF30B462D0ACE8": {
        "kind": "image",
        "url": "https://cdn.pixelcaster.com/public.pixelcaster.com/snapshots/yosemite-halfdome/latest.jpg",
        "status": "Current webcam image",
        "description": "This webcam shows Half Dome and the surrounding Yosemite Valley landscape.",
    },
    "https://www.nps.gov/media/webcam/view.htm?id=3E81EC42-BB62-0A59-E30ABB8F1646322E": {
        "kind": "image",
        "url": "https://cdn.pixelcaster.com/public.pixelcaster.com/snapshots/yosemite-yosfalls/latest.jpg",
        "status": "Current webcam image",
        "description": "This webcam shows the upper section of Yosemite Falls.",
    },
}


def clean_site_text(text):
    nps_attribution = "(" + "U.S. National " + "Park Service" + ")"
    text = text.replace(f" {nps_attribution}", "")
    text = text.replace(nps_attribution, "")
    text = re.sub(r"(?:&lt;|<)\s*br\s*/?\s*(?:&gt;|>)", " ", text, flags=re.IGNORECASE)
    text = re.sub(r"\s+", " ", text).strip()
    repeated_park_name = re.compile(
        r"^(.+?\b(?:National Park(?: & Preserve)?|National Parks(?: & Preserve)?|National and State Parks))\s+\1\b"
    )
    while repeated_park_name.search(text):
        text = repeated_park_name.sub(r"\1", text, count=1)
    return text


def clean_title(title):
    title = title.replace("Liv e", "Live").replace("Glacie r", "Glacier")
    title = title.replace("G rand", "Grand").replace("Gr eat", "Great")
    title = title.replace("G uadalupe", "Guadalupe").replace("H awaii", "Hawaii")
    title = title.replace("Y osemite", "Yosemite")
    return clean_site_text(title)


def decode_url(url):
    parsed = urlparse(url)
    if parsed.netloc == "www.google.com" and parsed.path == "/url":
        q = parse_qs(parsed.query).get("q")
        if q:
            return q[0]
    return url


def portable_embed_url(url):
    parsed = urlparse(url)
    if parsed.netloc in {"www.youtube.com", "youtube.com"} and parsed.path.startswith("/embed/"):
        allowed = {
            key: value
            for key, value in parse_qs(parsed.query).items()
            if key
            not in {
                "embed_config",
                "errorlinks",
            }
        }
        query = urlencode(allowed, doseq=True)
        return urlunparse((parsed.scheme, parsed.netloc, parsed.path, "", query, ""))
    return url


def page_href(row):
    if row["slug"] == "national-park-webcam-home":
        return "index.html"
    return f"parks/{row['slug']}.html"


def nationalparkcam_park_url(slug):
    return f"{NATIONALPARKCAM_SITE_URL}/parks/{slug}.html"


def sitemap_loc(row):
    if row["slug"] == "national-park-webcam-home":
        return f"{SITE_URL}/"
    if row["slug"] in INFO_PAGE_SLUGS:
        return f"{SITE_URL}/{row['slug']}.html"
    return f"{SITE_URL}/parks/{row['slug']}.html"


def build_sitemap(pages):
    lastmod = date.today().isoformat()
    urls = "\n".join(
        "\n".join(
            [
                "  <url>",
                f"    <loc>{html.escape(sitemap_loc(page))}</loc>",
                f"    <lastmod>{lastmod}</lastmod>",
                "  </url>",
            ]
        )
        for page in pages
    )
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{urls}
</urlset>
"""


def build_robots_txt():
    return f"""User-agent: *
Allow: /
Sitemap: {SITE_URL}/sitemap.xml
"""


def rel_from_page(target, page_slug):
    if page_slug == "national-park-webcam-home":
        return target
    if target.startswith("parks/"):
        return target.split("/", 1)[1]
    return f"../{target}"


def load_pages():
    pages = []
    with (EXPORT / "index.csv").open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            row = dict(row)
            row["title"] = clean_title(row["title"])
            row["line_count"] = int(row["line_count"])
            row["link_count"] = int(row["link_count"])
            row["image_count"] = int(row["image_count"])
            row["embed_count"] = int(row.get("embed_count") or 0)
            if row["slug"] in PARK_NAMES:
                row["title"] = f"{PARK_NAMES[row['slug']]} Webcams"
            pages.append(row)
    return pages


def load_resources():
    resources = defaultdict(list)
    with (EXPORT / "resources.csv").open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            row = dict(row)
            row["page"] = clean_title(row["page"])
            row["url"] = portable_embed_url(decode_url(row["url"]))
            resources[row["page_url"]].append(row)
    return resources


def load_webcam_sources():
    path = EXPORT / "webcam_sources.csv"
    sources = defaultdict(list)
    if not path.exists():
        return sources
    with path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            replacement = PAGE_SOURCE_EMBEDS.get(row["url"])
            if replacement:
                row.update(replacement)
                row["status"] = row["status"].replace("page", "embed")
            sources[row["slug"]].append(dict(row))
    return sources


def parse_markdown(path):
    lines = path.read_text(encoding="utf-8").splitlines()
    title = lines[0].lstrip("# ").strip()
    source = ""
    body = []
    in_resource = False
    for line in lines[1:]:
        if line.startswith("Source:"):
            source = line.replace("Source:", "", 1).strip()
            continue
        if line.startswith("## Images") or line.startswith("## Embeds") or line.startswith("## Links"):
            in_resource = True
        if in_resource:
            continue
        text = line.strip()
        if text:
            body.append(clean_site_text(text))
    return clean_title(title), source, body


def display_title(page, parsed_title):
    if page["slug"] in PARK_NAMES:
        return f"{PARK_NAMES[page['slug']]} Webcams"
    return parsed_title


def first_image(resources):
    candidates = []
    for item in resources:
        if item["type"] != "image":
            continue
        url = item["url"]
        label = item["label"].lower()
        if "email" in label or "sociallinks" in url or "sheets_32dp" in url:
            continue
        candidates.append(url)
    return candidates[0] if candidates else ""


def clean_summary_text(text):
    text = html.unescape(text)
    text = re.sub(r"<\s*br\s*/?\s*>", " ", text, flags=re.IGNORECASE)
    return clean_site_text(text)


def official_nps_summary(resources, fallback_title, fallback_description=""):
    for item in resources:
        if item["type"] != "link":
            continue
        parsed = urlparse(item["url"])
        if not parsed.netloc.endswith("nps.gov"):
            continue
        if not parsed.path.endswith("/index.htm"):
            continue
        label = clean_title(item["label"])
        title = clean_summary_text(fallback_title)
        description = clean_summary_text(fallback_description)
        marker = "(" + "U.S. National " + "Park Service" + ")"
        if marker in label:
            title_part, description_part = label.split(marker, 1)
            title = clean_summary_text(title_part)
            description = clean_summary_text(description_part) or clean_summary_text(fallback_description)
        return {
            "url": item["url"],
            "title": title,
            "description": description,
        }
    return {
        "url": "",
        "title": clean_summary_text(fallback_title),
        "description": clean_summary_text(fallback_description),
    }


def intro_from_body(body):
    for line in body:
        if len(line) > 90 and not line.startswith("Image:"):
            return line
    return body[0] if body else ""


def is_internal_nav_link(url, page_urls):
    parsed = urlparse(url)
    if parsed.netloc != "www.nationalparkcam.com":
        return False
    normalized = f"{parsed.scheme}://{parsed.netloc}{parsed.path.rstrip('/')}"
    return normalized in page_urls


def resource_groups(resources, page_urls):
    links, embeds, images = [], [], []
    seen = set()
    for item in resources:
        url = item["url"]
        label = clean_title(item["label"]).strip() or item["type"].title()
        key = (item["type"], label, url)
        if key in seen:
            continue
        seen.add(key)
        if item["type"] == "link":
            if is_internal_nav_link(url, page_urls):
                continue
            if url.startswith("mailto:"):
                continue
            links.append({**item, "label": label})
        elif item["type"] == "embed":
            embeds.append({**item, "label": label})
        elif item["type"] == "image":
            if "email" in label.lower() or "sociallinks" in url or "sheets_32dp" in url:
                continue
            images.append({**item, "label": label})
    return links, embeds, images


def is_map_embed(embed):
    return "maps-api-ssl.google.com" in embed["url"]


def rendered_embed_count(embeds):
    return sum(1 for embed in embeds if "youtube.com/embed/" in embed["url"])


def first_webcam_image(webcam_sources):
    for source in webcam_sources:
        if source.get("kind") == "image" and source.get("url") and "nps.gov" in source["url"]:
            return source["url"]
    for source in webcam_sources:
        if source.get("kind") == "image" and source.get("url"):
            return source["url"]
    return ""


def section_has_body(section):
    return any(not line.startswith("Image:") for line in section["paragraphs"])


def inline_link_candidates(links):
    grouped = {}
    candidates = []

    def add_candidate(label, url):
        label = clean_title(label).strip().rstrip(".")
        if not label or url.startswith("mailto:"):
            return
        if label.startswith(("http://", "https://")):
            return
        if len(label) > 80:
            return
        if label not in grouped:
            grouped[label] = {"label": label, "urls": []}
            candidates.append(grouped[label])
        grouped[label]["urls"].append(url)

    for link in links:
        label = clean_title(link["label"]).strip()
        url = link["url"]
        if label.lower() == "bike":
            add_candidate("Bike riding", url)
            add_candidate("Biking", url)
            continue
        add_candidate(label, url)
        if "wikipedia.org" in url:
            for alias in ("Wikipedia website", "Wikipedia site", "Wikipedia page", "Wikipedia", "wikipedia website", "wikipedia site", "wikipedia page", "wikipedia"):
                add_candidate(alias, url)

            parsed_name = urlparse(url).path.rsplit("/", 1)[-1].replace("_", " ")
            parsed_name = re.sub(r"%[0-9A-Fa-f]{2}", "", parsed_name).strip()
            if parsed_name:
                short_name = re.sub(r"\s+National\s+Park.*$", "", parsed_name).strip()
                if short_name:
                    add_candidate(f"{short_name} Wikipedia website", url)
                    add_candidate(f"{short_name} Wikipedia site", url)
    candidates.sort(key=lambda item: len(item["label"]), reverse=True)
    return candidates


def linked_paragraph(line, inline_links=None):
    inline_links = inline_links or []
    escaped = html.escape(line)
    for link in inline_links:
        if not link["urls"]:
            continue
        label = html.escape(link["label"])
        pattern = re.compile(rf"(?<![\w/]){re.escape(label)}(?![\w/])", flags=re.IGNORECASE)
        if not pattern.search(escaped):
            continue

        url = html.escape(link["urls"].pop(0))
        parts = re.split(r"(<a\b[^>]*>.*?</a>)", escaped, flags=re.IGNORECASE)
        replaced = False
        for index, part in enumerate(parts):
            if replaced or part.lower().startswith("<a "):
                continue
            if pattern.search(part):
                parts[index] = pattern.sub(
                    lambda match: f'<a href="{url}" target="_blank" rel="noopener">{match.group(0)}</a>',
                    part,
                    count=1,
                )
                replaced = True
        if replaced:
            escaped = "".join(parts)
        else:
            link["urls"].insert(0, html.unescape(url))
    return escaped


def inline_formatting(rendered):
    return re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", rendered)


BOLD_LEAD_LABELS = {
    "Camping",
    "Hotel/Lodge",
    "Restaurants",
    "Grocery Stores",
    "Food and groceries",
    "Food and Groceries",
    "Riding the River",
    "Biking",
}

BOLD_LEAD_STOPWORDS = {
    "A",
    "All",
    "Also",
    "For",
    "Here",
    "However",
    "If",
    "In",
    "It",
    "Please",
    "The",
    "There",
    "These",
    "This",
    "Visitors",
    "We",
}


def title_like_words(text):
    words = text.replace("&", " ").split()
    if not words:
        return False
    title_words = 0
    for word in words:
        stripped = word.strip(".,:;()[]")
        if not stripped or stripped.lower() in {"and", "of", "the", "to", "at", "from"}:
            continue
        if stripped[0].isupper() or stripped[0].isdigit():
            title_words += 1
        else:
            return False
    return title_words > 0


def detect_bold_lead(line):
    for label in sorted(BOLD_LEAD_LABELS, key=len, reverse=True):
        if line.startswith(label + " "):
            return label

    first_word = line.split(" ", 1)[0].strip(".,:;")
    if first_word in BOLD_LEAD_STOPWORDS:
        return ""

    for marker in (" This ", " The campground ", " The trail ", " The lodge "):
        if marker in line:
            lead = line.split(marker, 1)[0].strip()
            if 1 <= len(lead.split()) <= 7 and title_like_words(lead):
                return lead

    match = re.match(
        r"^(.{2,70}?)(?=\s+(?:is|are|has|have|offers|provides|takes|runs|allows|will|can|:)\b)",
        line,
    )
    if match:
        lead = match.group(1).strip()
        if 1 <= len(lead.split()) <= 7 and title_like_words(lead):
            return lead
    return ""


def bold_lead_text(rendered, line):
    if rendered.startswith("<strong>"):
        return rendered

    anchor = re.match(r"^(<a\b[^>]*>.*?</a>)(\s*)", rendered, flags=re.IGNORECASE)
    if anchor:
        return f"<strong>{anchor.group(1)}</strong>{anchor.group(2)}{rendered[anchor.end():]}"

    lead = detect_bold_lead(line)
    if not lead:
        return rendered

    escaped_lead = html.escape(lead)
    if rendered.startswith(escaped_lead):
        return f"<strong>{escaped_lead}</strong>{rendered[len(escaped_lead):]}"
    return rendered


def text_to_html(body, inline_links=None):
    inline_links = inline_links or []
    sections = []
    current = {"title": "", "paragraphs": []}
    for line in body:
        if line.startswith("Image:"):
            continue
        if line in SECTION_TITLES or (len(line) <= 46 and not line.endswith((".", ",")) and len(line.split()) <= 7):
            if current["title"] or section_has_body(current):
                sections.append(current)
            current = {"title": line, "paragraphs": []}
        else:
            current["paragraphs"].append(line)
    if current["title"] or section_has_body(current):
        sections.append(current)

    out = []
    for section in sections:
        if not section_has_body(section):
            continue
        heading = f"<h2>{inline_formatting(html.escape(section['title']))}</h2>" if section["title"] else ""
        paragraphs = "".join(
            f"<p>{bold_lead_text(inline_formatting(linked_paragraph(line, inline_links)), line)}</p>"
            for line in section["paragraphs"]
        )
        out.append(f'<section class="content-section">{heading}{paragraphs}</section>')
    return "\n".join(out)


def youtube_id(url):
    match = re.search(r"/embed/([^?&/]+)", url)
    return match.group(1) if match else ""


def is_webcam_heading(line):
    normalized = re.sub(r"\s+", " ", line.lower())
    return "webcam" in normalized or "web cam" in normalized or "web c am" in normalized


def webcam_caption_lines(body):
    try:
        intro_index = body.index("Introduction")
    except ValueError:
        return []
    start = next((index + 1 for index, line in enumerate(body[:intro_index]) if is_webcam_heading(line)), -1)
    if start < 0:
        return []
    captions = []
    for line in body[start:intro_index]:
        if not is_webcam_heading(line) and len(line) <= 180:
            captions.append(line)
    return captions


def strip_webcam_caption_block(body):
    captions = webcam_caption_lines(body)
    if not captions:
        return body
    intro_index = body.index("Introduction")
    start = next((index for index, line in enumerate(body[:intro_index]) if is_webcam_heading(line)), -1)
    if start < 0:
        return body
    return body[:start] + body[intro_index:]


def strip_body_lead_for_page(page_slug, body):
    if page_slug in {"big-bend-webcam", "grand-tetons-webcam", "lassen-volcano-webcam", "mammoth-cave-webcam", "mount-rainier-webcam", "new-river-gorge-webcam", "north-cascades-webcam", "olympic-webcam", "petrified-forest-webcam", "redwood-national-park", "rocky-mountain-webcam", "shenandoah-webcam", "theodore-roosevelt-webcam", "virgin-islands-webcam", "wrangell-st-elias-webcam", "yellowstone-webcam"} and body and "Introduction" in body:
        if body[0] == "Introduction":
            return body
        return body[1:]
    return body


def caption_for_label(label, captions):
    label_key = re.sub(r"[^a-z0-9]+", " ", html.unescape(label).lower())
    best_index = -1
    best_score = 0
    for index, caption in enumerate(captions):
        caption_key = re.sub(r"[^a-z0-9]+", " ", caption.lower())
        words = {word for word in caption_key.split() if len(word) > 3}
        score = sum(1 for word in words if word in label_key)
        if score > best_score:
            best_index = index
            best_score = score
    if best_index < 0 or best_score == 0:
        return ""
    caption = captions.pop(best_index)
    if " - " in caption:
        prefix, detail = caption.split(" - ", 1)
        if prefix.lower() in html.unescape(label).lower():
            return detail
    return caption


def webcam_description(source, captions):
    description = source.get("description", "").strip()
    if not description:
        description = caption_for_label(source.get("title", ""), captions)
    if description and description != source.get("status", ""):
        return f"<p>{html.escape(description)}</p>"
    return ""


def youtube_video_id(url):
    match = re.search(r"youtube\.com/embed/([^?&#/]+)", html.unescape(url))
    return match.group(1) if match else ""


def render_video_frame(src, title):
    video_id = youtube_video_id(src)
    if not video_id:
        return f'<div class="embed-frame"><iframe src="{src}" title="{title}" loading="lazy" allowfullscreen></iframe></div>'
    thumbnail = html.escape(f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg")
    thumbnail_alt = html.escape(f"{html.unescape(title)} video thumbnail")
    srcdoc = html.escape(
        f"""
        <style>
          body {{ margin: 0; }}
          a {{ display: grid; place-items: center; position: relative; height: 100vh; overflow: hidden; background: #111; color: white; text-decoration: none; }}
          img {{ width: 100%; height: 100%; object-fit: cover; }}
          span {{ position: absolute; display: grid; place-items: center; width: 68px; height: 48px; border-radius: 8px; background: rgba(0,0,0,.74); }}
          span::before {{ content: ""; width: 0; height: 0; margin-left: 4px; border-top: 11px solid transparent; border-bottom: 11px solid transparent; border-left: 18px solid white; }}
        </style>
        <a href="{html.unescape(src)}" aria-label="Play {html.unescape(title)}">
          <img src="{thumbnail}" alt="{thumbnail_alt}">
          <span></span>
        </a>
        """,
        quote=True,
    )
    return f'<div class="embed-frame"><iframe src="{src}" srcdoc="{srcdoc}" title="{title}" loading="lazy" allowfullscreen></iframe></div>'


def render_webcam_source_cards(webcam_sources, captions=None, page_slug=""):
    captions = captions or []
    cards = []
    nationalparkcam_url = html.escape(nationalparkcam_park_url(page_slug)) if page_slug else ""
    nationalparkcam_link = (
        f'<a class="source-link" href="{nationalparkcam_url}" target="_blank" rel="noopener">View this webcam on NationalParkCam.com</a>'
        if nationalparkcam_url
        else ""
    )
    for source in webcam_sources:
        title = html.escape(source["title"])
        url = html.escape(source["url"])
        page_url = html.escape(source["page_url"])
        provider = html.escape(source["provider"])
        status = html.escape(source["status"])
        description = webcam_description(source, captions)
        kind = source.get("kind")
        if kind == "iframe":
            cards.append(
                f"""
                <article class="embed-card video-card">
                  {render_video_frame(url, title)}
                  <div class="embed-meta"><span>{provider}</span><strong>{title}</strong><p>{status}</p>{description}{nationalparkcam_link}</div>
                </article>
                """
            )
        elif kind == "page":
            cards.append(
                f"""
                <article class="embed-card video-card webcam-page-card">
                  <div class="embed-frame"><iframe src="{url}" title="{title}" loading="lazy" allowfullscreen></iframe></div>
                  <div class="embed-meta"><span>{provider}</span><strong>{title}</strong><p>{status}</p>{description}{nationalparkcam_link}</div>
                </article>
                """
            )
        elif kind == "inactive":
            cards.append(
                f"""
                <article class="embed-card webcam-unavailable-card">
                  <div class="webcam-unavailable-media" role="img" aria-label="{title} is temporarily unavailable">
                    <span>Webcam temporarily unavailable</span>
                  </div>
                  <div class="embed-meta"><span>{provider}</span><strong>{title}</strong><p>{status}</p>{description}{nationalparkcam_link}</div>
                </article>
                """
            )
        else:
            cards.append(
                f"""
                <article class="embed-card webcam-image-card">
                  <div class="webcam-image-media" data-full-src="{url}" data-title="{title}" data-nationalparkcam-url="{nationalparkcam_url}">
                    <img src="{url}" data-refresh-src="{url}" alt="{title}" loading="lazy" onerror="this.closest('.webcam-image-card').classList.add('image-missing'); this.remove();">
                  </div>
                  <div class="embed-meta"><span>{provider}</span><strong>{title}</strong><p>{status}</p>{description}{nationalparkcam_link}</div>
                </article>
                """
            )
    return cards


def render_park_map_card(page_slug):
    coords = PARK_COORDS.get(page_slug)
    if not coords:
        return ""
    lat, lng = coords
    return f"""
                <article class="embed-card">
                  <div class="embed-frame map park-location-map" data-park-map data-lat="{lat}" data-lng="{lng}"></div>
                  <div class="embed-meta"><strong>Park location</strong></div>
                </article>
                """


def render_embed_cards(embeds, webcam_sources=None, captions=None, page_slug=""):
    webcam_sources = webcam_sources or []
    captions = list(captions or [])
    cards = []
    missing = []
    has_map = False
    for embed in embeds:
        url = embed["url"]
        raw_label = embed["label"]
        label = html.escape(raw_label)
        if "youtube.com/embed/" in url:
            src = html.escape(url)
            caption = caption_for_label(raw_label, captions)
            caption_html = f"<p>{html.escape(caption)}</p>" if caption else ""
            cards.append(
                f"""
                <article class="embed-card video-card">
                  {render_video_frame(src, label)}
                  <div class="embed-meta"><span>Live video</span><strong>{html.escape(clean_embed_label(raw_label))}</strong>{caption_html}</div>
                </article>
                """
            )
        elif "maps-api-ssl.google.com" in url:
            has_map = True
        elif url.startswith("google-sites-frame:"):
            missing.append((label, html.escape(url.replace("google-sites-frame:", ""))))
    if has_map:
        cards.append(render_park_map_card(page_slug))
    cards.extend(render_webcam_source_cards(webcam_sources, captions, page_slug))
    return "\n".join(cards)


def render_link_list(links):
    useful = links[:28]
    items = []
    for link in useful:
        items.append(
            f'<li><a href="{html.escape(link["url"])}" target="_blank" rel="noopener">{html.escape(link["label"])}</a></li>'
        )
    return "\n".join(items)


def clean_embed_label(label):
    return label.replace("YouTube Video, ", "").strip()


def popular_streams(resources_by_url, pages):
    preferred = [
        "katmai-webcam",
        "yellowstone-webcam",
        "yosemite-webcam",
        "grand-tetons-webcam",
    ]
    by_slug = {page["slug"]: page for page in pages}
    streams = []
    for slug in preferred:
        page = by_slug.get(slug)
        if not page:
            continue
        for item in resources_by_url[page["url"]]:
            if item["type"] == "embed" and "youtube.com/embed/" in item["url"]:
                streams.append(
                    {
                        "park": short_name(page["title"]),
                        "label": clean_embed_label(clean_title(item["label"])),
                        "url": item["url"],
                        "href": nationalparkcam_park_url(page["slug"]),
                    }
                )
                break
    return streams


def render_popular_streams(streams):
    cards = []
    for stream in streams[:4]:
        video_id = youtube_id(stream["url"])
        thumbnail = f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg" if video_id else ""
        alt_text = f"{stream['park']} {stream['label']} video thumbnail"
        image = (
            f'<img src="{html.escape(thumbnail)}" alt="{html.escape(alt_text)}" loading="eager" onerror="this.closest(\'.hero-stream-card\').classList.add(\'image-missing\'); this.remove();">'
            if thumbnail
            else ""
        )
        cards.append(
            f"""
            <article class="hero-stream-card">
              <a href="{html.escape(stream['href'])}" target="_blank" rel="noopener">
                <div class="hero-stream-thumb">{image}<span class="play-badge">Live</span></div>
                <span>{html.escape(stream['park'])}</span>
                <strong>{html.escape(stream['label'])}</strong>
              </a>
            </article>
            """
        )
    return "\n".join(cards)


def render_nav(pages, current_slug, depth):
    prefix = "" if depth == 0 else "../"
    links = [
        f'<a href="{prefix}index.html">Home</a>',
        f'<a href="{prefix}index.html#parks">Parks</a>',
    ]
    if current_slug not in {"national-park-webcam-home", "resources"}:
        current = next((p for p in pages if p["slug"] == current_slug), None)
        if current:
            links.append(f'<a aria-current="page" href="{prefix}parks/{current["slug"]}.html">{html.escape(short_name(current["title"]))}</a>')
    return "\n".join(links)


def short_name(title):
    title = title.replace("National and State Parks Webcams", "")
    title = title.replace("National Parks Webcams", "")
    title = title.replace("National Park Webcams", "")
    title = title.replace("National Park", "")
    title = title.replace("Webcams", "")
    return re.sub(r"\s+", " ", title).strip(" -.") or title


def hero_intro(title, intro):
    park_name = title.replace(" Webcams", "").strip()
    if intro.startswith(f"{park_name} "):
        return intro[len(park_name):].strip()
    return intro


def related_park_links(current_page, pages, count=4):
    current_coords = PARK_COORDS.get(current_page["slug"])
    if not current_coords:
        return ""
    related = []
    for page in pages:
        coords = PARK_COORDS.get(page["slug"])
        if not coords or page["slug"] == current_page["slug"]:
            continue
        distance = (coords[0] - current_coords[0]) ** 2 + (coords[1] - current_coords[1]) ** 2
        related.append((distance, page))
    related.sort(key=lambda item: item[0])
    cards = []
    for _, page in related[:count]:
        title = short_name(page["title"])
        cards.append(
            f"""
            <a class="related-park-card" href="{html.escape(nationalparkcam_park_url(page['slug']))}" target="_blank" rel="noopener">
              <span>{html.escape(title)}</span>
              <strong>View on NationalParkCam.com</strong>
            </a>
            """
        )
    if not cards:
        return ""
    return f"""
    <section class="related-parks-section" aria-labelledby="related-parks-heading">
      <div class="section-heading">
        <div><span class="eyebrow">Nearby parks</span><h2 id="related-parks-heading">Related Park Links</h2></div>
      </div>
      <div class="related-park-grid">{''.join(cards)}</div>
    </section>
"""


def structured_data(title, page_slug, description, canonical_url):
    if page_slug == "national-park-webcam-home":
        graph = [
            {
                "@context": "https://schema.org",
                "@type": "WebSite",
                "name": "National Parks Webcams",
                "url": canonical_url,
                "description": description,
            }
        ]
    else:
        graph = [
            {
                "@context": "https://schema.org",
                "@type": "WebPage",
                "name": title,
                "url": canonical_url,
                "description": description,
                "isPartOf": {
                    "@type": "WebSite",
                    "name": "National Parks Webcams",
                    "url": SITE_URL,
                },
            },
            {
                "@context": "https://schema.org",
                "@type": "BreadcrumbList",
                "itemListElement": [
                    {
                        "@type": "ListItem",
                        "position": 1,
                        "name": "Home",
                        "item": SITE_URL,
                    },
                    {
                        "@type": "ListItem",
                        "position": 2,
                        "name": title,
                        "item": canonical_url,
                    },
                ],
            },
        ]
    return json.dumps(graph, ensure_ascii=False)


def seo_page_title(title, page_slug):
    if page_slug == "national-park-webcam-home":
        return "National Parks Webcams | Live Park Cams, Weather & Maps"
    if page_slug in INFO_PAGE_SLUGS:
        return f"{title} | National Parks Webcams"
    return f"{short_name(title)} Webcams | Live Cams, Weather & Maps"


def google_analytics_tag():
    measurement_id = html.escape(GOOGLE_ANALYTICS_ID)
    return f"""  <!-- Google tag (gtag.js) -->
  <script async src="https://www.googletagmanager.com/gtag/js?id={measurement_id}"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){{dataLayer.push(arguments);}}
    gtag('js', new Date());

    gtag('config', '{measurement_id}');
  </script>"""


def page_shell(title, body, page_slug, pages, description, image="", depth=0):
    prefix = "" if depth == 0 else "../"
    image_meta = f'<meta property="og:image" content="{html.escape(image)}">' if image else ""
    twitter_image_meta = f'<meta name="twitter:image" content="{html.escape(image)}">' if image else ""
    if page_slug == "national-park-webcam-home":
        canonical_url = SITE_URL
    elif page_slug in INFO_PAGE_SLUGS:
        canonical_url = f"{SITE_URL}/{page_slug}.html"
    else:
        canonical_url = f"{SITE_URL}/parks/{page_slug}.html"
    seo_title = seo_page_title(title, page_slug)
    json_ld = structured_data(title, page_slug, description, canonical_url).replace("</", "<\\/")
    data_attrs = f' data-page-slug="{html.escape(page_slug)}" data-page-title="{html.escape(title)}" data-page-depth="{depth}"'
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(seo_title)}</title>
  <meta name="description" content="{html.escape(description[:155])}">
  <meta property="og:title" content="{html.escape(seo_title)}">
  <meta property="og:description" content="{html.escape(description[:180])}">
  <meta property="og:type" content="website">
  <meta property="og:url" content="{html.escape(canonical_url)}">
  {image_meta}
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{html.escape(seo_title)}">
  <meta name="twitter:description" content="{html.escape(description[:180])}">
  <meta name="twitter:url" content="{html.escape(canonical_url)}">
  {twitter_image_meta}
  <link rel="canonical" href="{html.escape(canonical_url)}">
  <script type="application/ld+json">{json_ld}</script>
{google_analytics_tag()}
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
  <link rel="stylesheet" href="{prefix}assets/styles.css">
</head>
<body{data_attrs}>
  <header class="site-header">
    <a class="brand" href="{prefix}index.html" aria-label="National Parks Webcams home">
      <img class="brand-logo" src="{prefix}assets/npsLogo.png" alt="National Park Cam logo">
    </a>
    <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="site-nav">Menu</button>
    <div class="header-nav-group">
      <nav class="recent-parks" id="recent-parks" aria-label="Recently viewed parks"></nav>
      <nav class="site-nav" id="site-nav">{render_nav(pages, page_slug, depth)}</nav>
    </div>
  </header>
  {body}
  <section class="footer-contact" aria-label="Contact">
    <p>For questions or comments, email <a href="mailto:npcam012@gmail.com">npcam012@gmail.com</a></p>
    <nav class="footer-links" aria-label="Site information">
      <a href="{prefix}about.html">About</a>
      <a href="{prefix}contact.html">Contact</a>
      <a href="{prefix}privacy-policy.html">Privacy Policy</a>
    </nav>
  </section>
  <footer class="site-footer"></footer>
  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
  <script src="{prefix}assets/app.js?v=20260505-gtcr"></script>
</body>
</html>
"""


def build_home(pages, content_by_url, resources_by_url, webcam_sources_by_slug):
    home = next(p for p in pages if p["slug"] == "national-park-webcam-home")
    park_pages = [p for p in pages if p["slug"] != "national-park-webcam-home"]
    cards = []
    for page in park_pages:
        parsed_title, _, body = content_by_url[page["url"]]
        title = display_title(page, parsed_title)
        res = resources_by_url[page["url"]]
        links, embeds, images = resource_groups(res, {p["url"].rstrip("/") for p in pages})
        cam_count = rendered_embed_count(embeds) + len(webcam_sources_by_slug.get(page["slug"], []))
        intro = intro_from_body(body)
        nps = official_nps_summary(res, PARK_NAMES.get(page["slug"], short_name(title)), intro)
        map_count = max(0, len(embeds) - rendered_embed_count(embeds))
        nps_link = (
            f'<a class="official-link" href="{html.escape(nps["url"])}" target="_blank" rel="noopener">Official NPS page</a>'
            if nps["url"]
            else ""
        )
        cards.append(
            f"""
            <article class="park-card" data-title="{html.escape(title.lower())}">
              <a href="{html.escape(nationalparkcam_park_url(page['slug']))}" target="_blank" rel="noopener" aria-label="Open {html.escape(title)} on NationalParkCam.com">
                <div class="park-card-body">
                  <h2>{html.escape(nps["title"])}</h2>
                  <p>{html.escape(nps["description"])}</p>
                  <strong class="card-action">View live cams on NationalParkCam.com</strong>
                </div>
              </a>
              {nps_link}
            </article>
            """
        )
    _, _, home_body = content_by_url[home["url"]]
    hero_source = next((p for p in park_pages if p["slug"] == "glacier-webcam"), park_pages[0])
    hero_image = first_image(resources_by_url[hero_source["url"]]) or first_image(resources_by_url[home["url"]])
    description = intro_from_body(home_body)
    page_urls = {p["url"].rstrip("/") for p in pages}
    hero_streams = popular_streams(resources_by_url, park_pages)
    map_points = []
    for page in park_pages:
        links, embeds, _ = resource_groups(resources_by_url[page["url"]], page_urls)
        cam_count = rendered_embed_count(embeds) + len(webcam_sources_by_slug.get(page["slug"], []))
        coords = PARK_COORDS.get(page["slug"])
        if not coords:
            continue
        map_points.append(
            {
                "slug": page["slug"],
                "title": short_name(page["title"]),
                "fullTitle": page["title"],
                "href": nationalparkcam_park_url(page["slug"]),
                "lat": coords[0],
                "lng": coords[1],
                "cams": cam_count,
                "embeds": len(embeds),
                "links": len(links),
            }
        )
    map_json = html.escape(json.dumps(map_points), quote=False)
    body = f"""
  <main>
    <section class="home-hero">
      <div class="hero-copy">
        <span class="eyebrow">Live views, hikes, camping, lodging, and park notes</span>
        <h1>National Parks Webcams</h1>
        <p>{html.escape(description)}</p>
        <div class="hero-actions">
          <a class="button primary" href="#parks">Find live cams</a>
        </div>
      </div>
      <div class="hero-streams" aria-label="Popular live streams">
        {render_popular_streams(hero_streams)}
      </div>
    </section>
    <section class="park-browser" id="parks">
      <div class="section-heading">
        <div>
          <span class="eyebrow">Browse by location</span>
          <h2>Live Cam Map</h2>
        </div>
        <label class="search-box">
          <span>Search</span>
          <input type="search" id="park-search" placeholder="Yellowstone, Acadia, Zion...">
        </label>
      </div>
      <div class="map-explorer">
        <div id="webcam-map" class="webcam-map" aria-label="Interactive national park webcam map"></div>
        <aside class="map-side">
          <span class="eyebrow">Featured live cams</span>
          <h3 id="map-active-title">Select a park</h3>
          <p id="map-active-meta">Choose a marker or a park below to jump straight to its webcam page.</p>
          <a id="map-active-link" class="button primary" href="#parks" target="_blank" rel="noopener">Open park cams</a>
          <div class="map-list" id="map-list"></div>
        </aside>
      </div>
      <script type="application/json" id="park-map-data">{map_json}</script>
      <div class="section-heading park-grid-heading">
        <div>
          <span class="eyebrow">All webcam pages</span>
          <h2>Park Directory</h2>
        </div>
      </div>
      <div class="park-grid" id="park-grid">{''.join(cards)}</div>
    </section>
  </main>
"""
    return page_shell("National Parks Webcams", body, home["slug"], pages, description, hero_image, 0)


def build_park_page(page, pages, content, resources, page_urls, webcam_sources):
    parsed_title, source, body = content
    title = display_title(page, parsed_title)
    links, embeds, images = resource_groups(resources, page_urls)
    cam_count = rendered_embed_count(embeds) + len(webcam_sources)
    map_count = max(0, len(embeds) - rendered_embed_count(embeds))
    intro = intro_from_body(body)
    captions = webcam_caption_lines(body)
    article_body = strip_body_lead_for_page(page["slug"], strip_webcam_caption_block(body))
    nps = official_nps_summary(resources, PARK_NAMES.get(page["slug"], short_name(title)), intro)
    planning_url = nps["url"] or (links[0]["url"] if links else source)
    nationalparkcam_url = nationalparkcam_park_url(page["slug"])
    coords = PARK_COORDS.get(page["slug"], ["", ""])
    weather_attrs = f'data-lat="{coords[0]}" data-lng="{coords[1]}"' if coords[0] != "" else ""
    cam_notice = ""
    if page["slug"] == "black-canyon-of-the-gunnison-webcam":
        cam_notice = '<p class="section-note">The Black Canyon webcams are currently inactive. The park map remains available below.</p>'
    body_html = f"""
  <main>
    <section class="page-hero">
      <div class="page-hero-copy">
        <a class="back-link" href="../index.html">All parks</a>
        <h1>{html.escape(title)}</h1>
        <p>{html.escape(hero_intro(title, intro))}</p>
        <div class="page-actions">
          <a class="button primary" href="{html.escape(nationalparkcam_url)}" target="_blank" rel="noopener">View webcams on NationalParkCam.com</a>
          <a class="button" href="{html.escape(planning_url)}" target="_blank" rel="noopener">Visit park website</a>
        </div>
      </div>
    </section>
    <section class="resource-section live-first" id="live-cams">
      <div class="section-heading">
        <div><h2>Live Cams & Maps</h2></div>
      </div>
      {cam_notice}
      <div class="embed-grid">{render_embed_cards(embeds, webcam_sources, captions, page["slug"])}</div>
    </section>
    <section class="weather-section" {weather_attrs}>
      <div class="section-heading">
        <div><h2>Weather</h2></div>
      </div>
      <div class="weather-layout">
        <article class="weather-card">
          <h3>Next 12 hours</h3>
          <div class="hourly-weather" data-weather-hourly>Loading hourly forecast...</div>
        </article>
        <article class="weather-card">
          <h3>7 day outlook</h3>
          <div class="daily-weather" data-weather-daily>Loading forecast...</div>
        </article>
      </div>
    </section>
    <div class="page-layout">
      <article class="page-content">{text_to_html(article_body, inline_link_candidates(links))}</article>
    </div>
    {related_park_links(page, pages)}
  </main>
"""
    return page_shell(title, body_html, page["slug"], pages, intro, first_image(resources), 1)


def build_info_page(slug, title, description, sections, pages):
    section_html = []
    for heading, paragraphs in sections:
        section_html.append(f'<section class="content-section"><h2>{html.escape(heading)}</h2>')
        for paragraph in paragraphs:
            section_html.append(f"<p>{paragraph}</p>")
        section_html.append("</section>")
    body_html = f"""
  <main>
    <section class="park-hero">
      <a class="back-link" href="index.html">Home</a>
      <div class="park-hero-grid">
        <div>
          <span class="eyebrow">National Parks Webcams</span>
          <h1>{html.escape(title)}</h1>
          <p>{html.escape(description)}</p>
        </div>
      </div>
    </section>
    <div class="page-layout">
      <article class="page-content">{''.join(section_html)}</article>
    </div>
  </main>
"""
    return page_shell(title, body_html, slug, pages, description, "", 0)


def info_pages():
    email = '<a href="mailto:npcam012@gmail.com">npcam012@gmail.com</a>'
    return [
        {
            "slug": "about",
            "title": "About National Parks Webcams",
            "description": "Learn about National Parks Webcams, an independent guide to official park webcams, maps, weather, and visitor planning resources.",
            "sections": [
                (
                    "Our Purpose",
                    [
                        "National Parks Webcams is an independent visitor guide that helps people find official park webcams, maps, weather, and planning resources in one place.",
                        "The goal is simple: make it easier to check current conditions, explore park views, and plan better visits to national parks and national monuments.",
                    ],
                ),
                (
                    "Sources",
                    [
                        "Whenever possible, this site links to official National Park Service pages, official webcam sources, Recreation.gov, and other public agency resources.",
                        "National Parks Webcams is not affiliated with, endorsed by, or operated by the National Park Service.",
                    ],
                ),
            ],
        },
        {
            "slug": "contact",
            "title": "Contact National Parks Webcams",
            "description": "Contact National Parks Webcams about broken webcam links, incorrect park information, suggestions, or general questions.",
            "sections": [
                (
                    "Email",
                    [
                        f"For questions, corrections, broken webcam links, or suggestions, email {email}.",
                        "Please note that this is an independent website. For official park rules, closures, reservations, permits, or emergency information, contact the National Park Service or the relevant public land agency directly.",
                    ],
                ),
            ],
        },
        {
            "slug": "privacy-policy",
            "title": "Privacy Policy",
            "description": "Privacy Policy for National Parks Webcams, including Google Analytics, cookies, third-party services, and contact information.",
            "sections": [
                (
                    "Overview",
                    [
                        "National Parks Webcams does not directly create user accounts, collect form submissions, sell personal information, or process payments.",
                        "This site is a public visitor guide. It may collect limited technical information through third-party services used for analytics, performance, security, advertising, or embedded content.",
                    ],
                ),
                (
                    "Google Analytics",
                    [
                        "This site uses Google Analytics to understand general traffic patterns, popular pages, referring websites, approximate location, device type, and similar usage information.",
                        "Google Analytics may use cookies or similar technologies to collect and process this information. The data helps improve the site and understand how visitors use it.",
                    ],
                ),
                (
                    "Cookies",
                    [
                        "National Parks Webcams does not currently provide user accounts or site-specific preference settings that require first-party cookies.",
                        "Third-party services, including Google Analytics and any future advertising services such as Google AdSense, may use cookies or similar technologies to measure traffic, prevent abuse, personalize services, or measure advertising performance.",
                    ],
                ),
                (
                    "Managing Cookies",
                    [
                        "Visitors can manage, block, or delete cookies through their browser settings. Most browsers allow you to block cookies, delete existing cookies, or receive a warning before cookies are stored.",
                        'Visitors can also manage Google ad personalization through <a href="https://adssettings.google.com/" target="_blank" rel="noopener">Google Ad Settings</a> and learn how Google uses information from sites and apps at <a href="https://policies.google.com/technologies/partner-sites" target="_blank" rel="noopener">Google Partner Sites</a>.',
                    ],
                ),
                (
                    "Third-Party Links and Embeds",
                    [
                        "This site links to third-party websites such as National Park Service pages, Recreation.gov, YouTube, map providers, webcam providers, and other public resources.",
                        "Those third-party websites and embedded services may have their own privacy practices and cookie policies. National Parks Webcams is not responsible for the privacy practices of those external websites.",
                    ],
                ),
                (
                    "Contact",
                    [
                        f"For privacy questions or site questions, email {email}.",
                    ],
                ),
            ],
        },
    ]


def main():
    pages = load_pages()
    resources_by_url = load_resources()
    webcam_sources_by_slug = load_webcam_sources()
    page_urls = {p["url"].rstrip("/") for p in pages}
    content_by_url = {}
    for page in pages:
        content_by_url[page["url"]] = parse_markdown(EXPORT / page["markdown"])

    if DIST.exists():
        shutil.rmtree(DIST)
    PAGES_OUT.mkdir(parents=True)
    ASSETS_OUT.mkdir(parents=True)
    shutil.copy(ROOT / "assets" / "styles.css", ASSETS_OUT / "styles.css")
    shutil.copy(ROOT / "assets" / "app.js", ASSETS_OUT / "app.js")
    shutil.copy(ROOT / "assets" / "npsLogo.png", ASSETS_OUT / "npsLogo.png")

    (DIST / "index.html").write_text(build_home(pages, content_by_url, resources_by_url, webcam_sources_by_slug), encoding="utf-8")
    info = info_pages()
    sitemap_pages = pages + [{"slug": item["slug"]} for item in info]
    (DIST / "CNAME").write_text("national-parks.us\n", encoding="utf-8")
    (DIST / "sitemap.xml").write_text(build_sitemap(sitemap_pages), encoding="utf-8")
    (DIST / "robots.txt").write_text(build_robots_txt(), encoding="utf-8")
    for item in info:
        (DIST / f"{item['slug']}.html").write_text(
            build_info_page(item["slug"], item["title"], item["description"], item["sections"], pages),
            encoding="utf-8",
        )
    for page in pages:
        if page["slug"] == "national-park-webcam-home":
            continue
        html_out = build_park_page(
            page,
            pages,
            content_by_url[page["url"]],
            resources_by_url[page["url"]],
            page_urls,
            webcam_sources_by_slug.get(page["slug"], []),
        )
        (PAGES_OUT / f"{page['slug']}.html").write_text(html_out, encoding="utf-8")
    print(f"Built {len(pages)} pages into {DIST}")


if __name__ == "__main__":
    main()
