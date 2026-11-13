#!/usr/bin/env python3
"""Airport Codes World - programmatic SEO static site generator.

Data source: OurAirports open data (public domain)
  https://davidmegginson.github.io/ourairports-data/
Generates pure static HTML (inline CSS, no JS framework) into dist/.

Usage:
  python3 generate.py [--base https://airport-codes-world.pages.dev]
"""
import argparse
import csv
import html
import json
import os
from collections import defaultdict

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, "data")
DIST = os.path.join(ROOT, "dist")
BRAND = "Airport Codes World"

CSS = """
:root{--blue:#0b3d91;--ink:#1a1a2e;--mut:#5a6472;--line:#dde3ea;--bg:#f6f8fb}
*{box-sizing:border-box}body{margin:0;font-family:-apple-system,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;color:var(--ink);background:#fff;line-height:1.55}
header.site{background:var(--blue);color:#fff;padding:14px 20px}header.site a{color:#fff;text-decoration:none;font-weight:700;font-size:20px}
header.site nav{margin-top:4px}header.site nav a{font-weight:400;font-size:14px;margin-right:16px;opacity:.9}
main{max-width:960px;margin:0 auto;padding:24px 20px 48px}
h1{color:var(--blue);font-size:30px;line-height:1.25;margin:8px 0 10px}h2{color:var(--blue);font-size:21px;margin:30px 0 10px;border-bottom:2px solid var(--line);padding-bottom:6px}
p.lede{font-size:17px;color:#333}
table.facts{border-collapse:collapse;width:100%;max-width:640px;background:var(--bg);border:1px solid var(--line)}
table.facts th,table.facts td{padding:8px 12px;border-bottom:1px solid var(--line);text-align:left;font-size:15px}
table.facts th{width:150px;color:var(--blue);background:#eef2f8}
table.rw{border-collapse:collapse;width:100%}table.rw th,table.rw td{padding:7px 10px;border:1px solid var(--line);font-size:14px;text-align:left}
table.rw th{background:#eef2f8;color:var(--blue)}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(210px,1fr));gap:10px;margin-top:12px}
.grid a{display:block;padding:10px 12px;border:1px solid var(--line);border-radius:8px;text-decoration:none;color:var(--ink);background:#fff}
.grid a:hover{border-color:var(--blue)}.grid a b{color:var(--blue)}
.faq div{margin:0 0 14px}.faq p{margin:2px 0 0}
.cta{margin:36px 0 8px;padding:22px;background:var(--bg);border:1px solid var(--line);border-radius:10px;text-align:center}
.cta a.btn{display:inline-block;background:var(--blue);color:#fff;padding:12px 26px;border-radius:8px;text-decoration:none;font-weight:600}
.cta p{color:var(--mut);font-size:14px}
ul.aplist{columns:2;column-gap:32px;padding-left:18px}ul.aplist li{margin:4px 0;break-inside:avoid}
footer.site{border-top:1px solid var(--line);padding:18px 20px;color:var(--mut);font-size:13px;text-align:center}
footer.site a{color:var(--blue)}
@media(max-width:640px){ul.aplist{columns:1}h1{font-size:24px}}
"""


def esc(x):
    return html.escape(str(x or "").strip(), quote=True)


def ft_to_m(ft):
    try:
        return round(float(ft) * 0.3048)
    except (TypeError, ValueError):
        return None


def load_csv(name):
    with open(os.path.join(DATA, name), encoding="utf-8") as f:
        return list(csv.DictReader(f))


def page_shell(title, desc, canonical, body, credit=None):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<meta name="google-site-verification" content="EwewxoN21MFdlTRASb3oiE-m4zHqA8t4nOPOCKThuDc">
<link rel="canonical" href="{esc(canonical)}">
<style>{CSS}</style>
</head>
<body>
<header class="site"><a href="/">{BRAND}</a><nav><a href="/">Home</a><a href="/pricing/">Data API</a></nav></header>
<main>
{body}
</main>
<footer class="site">{credit or f"Data: OurAirports (public domain)."} {BRAND} is an independent reference site.</footer>
</body>
</html>
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="https://airport-codes-world.pages.dev")
    args = ap.parse_args()
    base = args.base.rstrip("/")

    countries = {r["code"]: r["name"] for r in load_csv("countries.csv")}
    regions = {r["code"]: r["name"] for r in load_csv("regions.csv")}

    runways_by_ident = defaultdict(list)
    for rw in load_csv("runways.csv"):
        if rw["closed"] == "1":
            continue
        runways_by_ident[rw["airport_ident"]].append(rw)

    airports = [
        r for r in load_csv("airports.csv")
        if r["type"] in ("large_airport", "medium_airport") and r["iata_code"].strip()
    ]
    airports.sort(key=lambda r: (r["iata_code"]))
    by_country = defaultdict(list)
    by_region = defaultdict(list)
    for a in airports:
        by_country[a["iso_country"]].append(a)
        by_region[a["iso_region"]].append(a)

    urls = ["/", "/pricing/"]
    os.makedirs(DIST, exist_ok=True)

    def write(path, content):
        full = os.path.join(DIST, path.lstrip("/"), "index.html") if path != "/" \
            else os.path.join(DIST, "index.html")
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w", encoding="utf-8") as f:
            f.write(content)

    # ---------- airport pages ----------
    for a in airports:
        iata = a["iata_code"].strip()
        slug = iata.lower()
        city = a["municipality"].strip()
        name = a["name"].strip()
        ctry_code = a["iso_country"].strip()
        ctry = countries.get(ctry_code, ctry_code)
        region = regions.get(a["iso_region"].strip(), "")
        icao = a["icao_code"].strip()
        elev = a["elevation_ft"].strip()
        lat, lon = a["latitude_deg"].strip(), a["longitude_deg"].strip()
        atype = "Large airport" if a["type"] == "large_airport" else "Medium airport"
        loc = ", ".join(x for x in [city, region, ctry] if x)
        canon = f"{base}/airport/{slug}/"
        urls.append(f"/airport/{slug}/")

        if city and not name.lower().startswith(city.lower()):
            h1 = f"{city} {name} (IATA: {iata})"
        else:
            h1 = f"{name} (IATA: {iata})"
        summary = f"{name} is an airport located in {loc}. Its IATA code is {iata}"
        if icao:
            summary += f" and its ICAO code is {icao}"
        summary += "."
        title = f"{name} ({iata}) Airport Code & Facts | {BRAND}"
        desc = summary + " Quick facts, runway details, elevation, coordinates and nearby airports."

        facts = [("IATA code", iata)]
        if icao:
            facts.append(("ICAO code", icao))
        if city:
            facts.append(("City", city))
        if region:
            facts.append(("State / Region", region))
        facts.append(("Country", ctry))
        if elev:
            facts.append(("Elevation", f"{int(float(elev)):,} ft ({ft_to_m(elev):,} m)"))
        if lat and lon:
            facts.append(("Coordinates", f"{float(lat):.4f}, {float(lon):.4f}"))
        facts.append(("Type", atype))
        if a["home_link"].strip():
            facts.append(("Official website",
                          f'<a href="{esc(a["home_link"])}" rel="nofollow noopener" target="_blank">{esc(a["home_link"])}</a>'))
        facts_html = "\n".join(
            f"<tr><th>{esc(k)}</th><td>{v if k == 'Official website' else esc(v)}</td></tr>"
            for k, v in facts
        )

        # Runways
        rw_html = ""
        rws = runways_by_ident.get(a["ident"], [])
        if rws:
            rows = []
            for rw in rws:
                pair = "/".join(x for x in [rw["le_ident"].strip(), rw["he_ident"].strip()] if x)
                ln = rw["length_ft"].strip()
                ln_txt = f"{int(float(ln)):,} ft ({ft_to_m(ln):,} m)" if ln else "—"
                rows.append(
                    f"<tr><td>{esc(pair) or '—'}</td><td>{ln_txt}</td><td>{esc(rw['surface']) or '—'}</td></tr>")
            rw_html = ("<h2>Runways</h2>\n<table class=\"rw\"><tr><th>Runway</th>"
                       "<th>Length</th><th>Surface</th></tr>\n" + "\n".join(rows) + "\n</table>")

        # FAQ
        faqs = [
            (f"What is the airport code for {name}?",
             f"The IATA airport code for {name} is {iata}" + (f" and its ICAO code is {icao}." if icao else ".")),
            (f"Where is {iata} airport located?",
             f"{iata} ({name}) is located in {loc}."),
        ]
        if elev:
            faqs.append((f"What is the elevation of {name}?",
                         f"{name} sits at an elevation of {int(float(elev)):,} feet ({ft_to_m(elev):,} meters) above sea level."))
        else:
            faqs.append((f"What type of airport is {name}?",
                         f"{name} is classified as a {atype.lower()} serving {loc}."))
        faq_html = "\n".join(
            f"<div><b>{esc(q)}</b><p>{esc(ans)}</p></div>" for q, ans in faqs)
        faq_ld = {
            "@context": "https://schema.org", "@type": "FAQPage",
            "mainEntity": [{"@type": "Question", "name": q,
                            "acceptedAnswer": {"@type": "Answer", "text": ans}} for q, ans in faqs],
        }

        # Nearby airports: same region, large first, up to 12
        peers = [p for p in by_region.get(a["iso_region"], []) if p["ident"] != a["ident"]]
        peers.sort(key=lambda p: (0 if p["type"] == "large_airport" else 1, p["name"]))
        near = peers[:12]
        near_html = ""
        if near:
            cards = "\n".join(
                f'<a href="/airport/{p["iata_code"].strip().lower()}/"><b>{esc(p["iata_code"])}</b> — '
                f'{esc(p["name"])}<br><small>{esc(p["municipality"] or ctry)}</small></a>'
                for p in near)
            near_html = f"<h2>Nearby airports</h2>\n<div class=\"grid\">\n{cards}\n</div>"

        cta_city = city or ctry
        body = f"""<h1>{esc(h1)}</h1>
<p class="lede">{esc(summary)}</p>
<h2>Quick facts</h2>
<table class="facts">
{facts_html}
</table>
{rw_html}
<h2>Frequently asked questions</h2>
<div class="faq">
{faq_html}
</div>
<script type="application/ld+json">{json.dumps(faq_ld, ensure_ascii=False)}</script>
{near_html}
<!-- TODO-AFFILIATE: replace the placeholder href below with a real flight affiliate link once a program is approved. Do NOT invent one. -->
<div class="cta"><a class="btn" href="#">Search flights to {esc(cta_city)}</a>
<p>Planning a trip to {esc(cta_city)}? Compare flight options for {esc(iata)}.</p>
<p>Need this data in bulk? See our <a href="/pricing/">Airport Data API</a>.</p></div>"""
        write(f"/airport/{slug}/", page_shell(title, desc, canon, body))

    # ---------- country pages (>=5 airports) ----------
    country_pages = {c: lst for c, lst in by_country.items() if len(lst) >= 5}
    for code, lst in sorted(country_pages.items()):
        cname = countries.get(code, code)
        lst_sorted = sorted(lst, key=lambda r: (0 if r["type"] == "large_airport" else 1, r["name"]))
        items = "\n".join(
            f'<li><a href="/airport/{a["iata_code"].strip().lower()}/"><b>{esc(a["iata_code"])}</b> — '
            f'{esc(a["name"])}</a>{(" (" + esc(a["municipality"]) + ")") if a["municipality"].strip() else ""}</li>'
            for a in lst_sorted)
        body = (f"<h1>Airport codes in {esc(cname)}</h1>\n"
                f"<p class=\"lede\">{len(lst_sorted)} airports in {esc(cname)} with IATA codes, "
                f"including large and medium airports.</p>\n"
                f"<ul class=\"aplist\">\n{items}\n</ul>")
        write(f"/country/{code.lower()}/",
              page_shell(f"Airport Codes in {cname} — Full List | {BRAND}",
                         f"Complete list of {len(lst_sorted)} airport IATA codes in {cname}: names, cities, runways and facts.",
                         f"{base}/country/{code.lower()}/", body))
        urls.append(f"/country/{code.lower()}/")

    # ---------- airline pages (data: OpenFlights airlines.dat, ODbL) ----------
    # Filter: active ("Y") AND a valid 2-char IATA code. See data/SOURCES.md.
    import re
    NULLS = {"", "\\N", "N/A", "-"}

    def clean(v):
        v = (v or "").strip()
        return "" if v in NULLS else v

    name_to_code = {v: k for k, v in countries.items()}
    airlines_by_iata = defaultdict(list)
    with open(os.path.join(DATA, "airlines.dat"), encoding="utf-8") as f:
        for row in csv.reader(f):
            if len(row) < 8 or row[7].strip() != "Y":
                continue
            iata = row[3].strip().upper()
            if not re.fullmatch(r"[A-Z0-9]{2}", iata):
                continue
            airlines_by_iata[iata].append({
                "name": clean(row[1]), "alias": clean(row[2]), "iata": iata,
                "icao": clean(row[4]), "callsign": clean(row[5]),
                "country": clean(row[6]),
            })
    n_airlines = sum(len(v) for v in airlines_by_iata.values())
    AIRLINE_CREDIT = ('Data: <a href="https://openflights.org/data.php" rel="nofollow noopener" '
                      'target="_blank">OpenFlights</a> (Open Database License).')

    def airline_more_links(al):
        links = ['<a href="/airlines/"><b>ALL</b> — All airline codes</a>',
                 '<a href="/"><b>Home</b> — Airport codes</a>']
        cc = name_to_code.get(al["country"])
        if cc and cc in country_pages:
            links.append(f'<a href="/country/{cc.lower()}/"><b>{esc(al["country"])}</b> — '
                         f'Airport codes in {esc(al["country"])}</a>')
        return ('<h2>More codes</h2>\n<div class="grid">\n' + "\n".join(links) + "\n</div>")

    for code in sorted(airlines_by_iata):
        als = sorted(airlines_by_iata[code], key=lambda a: a["name"])
        slug = code.lower()
        canon = f"{base}/airline/{slug}/"
        urls.append(f"/airline/{slug}/")
        single = len(als) == 1
        a0 = als[0]

        if single:
            title = f"{a0['name']} ({code}) Airline Code, ICAO & Callsign | {BRAND}"
            summary = (f"{a0['name']} is an airline based in {a0['country']}. "
                       f"Its IATA code is {code}") if a0["country"] else \
                      (f"{a0['name']} is an airline. Its IATA code is {code}")
            if a0["icao"]:
                summary += f" and its ICAO code is {a0['icao']}"
            summary += "."
            h1 = f"{a0['name']} (IATA: {code})"
        else:
            names = ", ".join(a["name"] for a in als)
            title = f"Airline Code {code} — Which Airline Is It? | {BRAND}"
            summary = (f"The IATA code {code} is shared by {len(als)} airlines: {names}. "
                       f"IATA occasionally assigns the same two-letter code to more than one carrier.")
            h1 = f"Airline code {code}"
        desc = summary + " Quick facts: IATA and ICAO codes, callsign and country of registration."

        sections = []
        faqs = []
        if single:
            faqs.append((f"Which airline has the IATA code {code}?",
                         f"The IATA code {code} belongs to {a0['name']}"
                         + (f", based in {a0['country']}." if a0["country"] else ".")))
        else:
            faqs.append((f"Which airlines use the IATA code {code}?",
                         f"The IATA code {code} is shared by {len(als)} airlines: "
                         + ", ".join(a["name"] for a in als) + "."))
        for al in als:
            facts = [("IATA code", al["iata"])]
            if al["icao"]:
                facts.append(("ICAO code", al["icao"]))
            facts.append(("Airline", al["name"]))
            if al["alias"]:
                facts.append(("Also known as", al["alias"]))
            if al["callsign"]:
                facts.append(("Callsign", al["callsign"]))
            if al["country"]:
                facts.append(("Country", al["country"]))
            facts_html = "\n".join(
                f"<tr><th>{esc(k)}</th><td>{esc(v)}</td></tr>" for k, v in facts)
            head = "" if single else f"<h2>{esc(al['name'])}</h2>\n"
            sections.append(head + "<table class=\"facts\">\n" + facts_html + "\n</table>")
            if al["icao"]:
                faqs.append((f"What is the ICAO code for {al['name']}?",
                             f"The ICAO code for {al['name']} is {al['icao']} "
                             f"(IATA code {code})."))
            if al["callsign"]:
                faqs.append((f"What is the callsign of {al['name']}?",
                             f"The radio callsign of {al['name']} is \"{al['callsign']}\"."))
            if al["country"]:
                faqs.append((f"Where is {al['name']} based?",
                             f"{al['name']} is based in {al['country']}."))
        faq_html = "\n".join(
            f"<div><b>{esc(q)}</b><p>{esc(ans)}</p></div>" for q, ans in faqs)
        faq_ld = {
            "@context": "https://schema.org", "@type": "FAQPage",
            "mainEntity": [{"@type": "Question", "name": q,
                            "acceptedAnswer": {"@type": "Answer", "text": ans}} for q, ans in faqs],
        }
        body = f"""<h1>{esc(h1)}</h1>
<p class="lede">{esc(summary)}</p>
<h2>Quick facts</h2>
{chr(10).join(sections)}
<h2>Frequently asked questions</h2>
<div class="faq">
{faq_html}
</div>
<script type="application/ld+json">{json.dumps(faq_ld, ensure_ascii=False)}</script>
{airline_more_links(a0)}"""
        write(f"/airline/{slug}/",
              page_shell(title, desc, canon, body, credit=AIRLINE_CREDIT))

    # ---------- airlines index ----------
    idx_items = []
    for code in sorted(airlines_by_iata):
        for al in sorted(airlines_by_iata[code], key=lambda a: a["name"]):
            idx_items.append(
                f'<li><a href="/airline/{code.lower()}/"><b>{esc(code)}</b> — {esc(al["name"])}</a>'
                + (f' ({esc(al["country"])})' if al["country"] else "") + "</li>")
    idx_body = (f"<h1>Airline Codes — IATA Codes by Airline</h1>\n"
                f"<p class=\"lede\">{n_airlines:,} active airlines and their two-letter IATA codes, "
                f"covering {len(airlines_by_iata):,} unique codes, with ICAO codes, callsigns and "
                f"countries. Some IATA codes are shared by more than one carrier.</p>\n"
                f"<ul class=\"aplist\">\n" + "\n".join(idx_items) + "\n</ul>\n"
                f"<p>Looking for an airport instead? Browse <a href=\"/\">airport codes</a>.</p>")
    write("/airlines/", page_shell(
        f"Airline IATA Codes — Full List of {len(airlines_by_iata):,} Codes | {BRAND}",
        f"Complete list of {n_airlines:,} active airlines with IATA codes: ICAO codes, callsigns and countries.",
        f"{base}/airlines/", idx_body, credit=AIRLINE_CREDIT))
    urls.append("/airlines/")

    # ---------- homepage ----------
    top = sorted([a for a in airports if a["type"] == "large_airport"],
                 key=lambda r: r["name"])[:60]
    top_cards = "\n".join(
        f'<a href="/airport/{a["iata_code"].strip().lower()}/"><b>{esc(a["iata_code"])}</b> — '
        f'{esc(a["name"])}<br><small>{esc(a["municipality"])}, {esc(countries.get(a["iso_country"], a["iso_country"]))}</small></a>'
        for a in top)
    country_links = "\n".join(
        f'<a href="/country/{c.lower()}/">{esc(countries.get(c, c))} ({len(country_pages[c])})</a>'
        for c in sorted(country_pages, key=lambda c: countries.get(c, c)))
    home_body = f"""<h1>{BRAND} — Every Airport Code, Explained</h1>
<p class="lede">Look up any airport by its IATA code: location, ICAO code, elevation, coordinates,
runways and nearby airports. Covering {len(airports):,} large and medium airports worldwide.</p>
<h2>Popular airports</h2>
<div class="grid">
{top_cards}
</div>
<h2>Browse by country</h2>
<div class="grid">
{country_links}
</div>"""
    write("/", page_shell(f"{BRAND} — Airport IATA Codes, Facts & Runways",
                          f"Search {len(airports):,} airport IATA codes worldwide: quick facts, runways, elevation, coordinates and nearby airports.",
                          base + "/", home_body))

    # ---------- pricing placeholder ----------
    pricing_body = """<h1>Airport Data API — Coming Soon</h1>
<p class="lede">The same airport dataset behind this site — IATA/ICAO codes, coordinates,
elevations and runway data for thousands of airports — will soon be available as a simple API.</p>
<h2>Get notified</h2>
<!-- TODO: form is a placeholder only, not wired to any backend yet. -->
<form method="post" action="#" onsubmit="return false;">
<label>Email address<br><input type="email" name="email" placeholder="you@example.com" style="padding:10px;width:280px;max-width:100%"></label>
<button type="submit" style="padding:10px 18px;background:#0b3d91;color:#fff;border:0;border-radius:6px">Notify me</button>
</form>
<p>Planned tiers: a free tier for small projects and paid tiers for commercial use. Details at launch.</p>"""
    write("/pricing/", page_shell(f"Airport Data API — Coming Soon | {BRAND}",
                                   "Bulk airport data API with IATA/ICAO codes, coordinates and runways. Coming soon — join the waitlist.",
                                   base + "/pricing/", pricing_body))

    # ---------- sitemap + robots ----------
    sm = ['<?xml version="1.0" encoding="UTF-8"?>',
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u in urls:
        sm.append(f"<url><loc>{base}{u}</loc></url>")
    sm.append("</urlset>")
    with open(os.path.join(DIST, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write("\n".join(sm))
    with open(os.path.join(DIST, "robots.txt"), "w", encoding="utf-8") as f:
        f.write(f"User-agent: *\nAllow: /\nSitemap: {base}/sitemap.xml\n")

    print(f"airports={len(airports)} countries={len(country_pages)} "
          f"airlines={n_airlines} airline_codes={len(airlines_by_iata)} pages={len(urls)} base={base}")


if __name__ == "__main__":
    main()
