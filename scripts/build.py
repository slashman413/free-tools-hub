#!/usr/bin/env python3
"""
free-tools-hub build script.

Takes the committed tool sources at the repo root, injects the shared
hub chrome (site header, related-tools rail, footer), rewrites canonicals
to the tools.slashmantools.us domain, and emits a deployable site into ./dist.

Also generates: hub landing page (index.html), sitemap.xml, robots.txt, 404.html.

Usage:  python3 scripts/build.py
Output: ./dist/  (deployed by GitHub Actions)
"""
import json
import os
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
BASE = "https://tools.slashmantools.us"
HUB_NAME = "Free Tools Hub"

# One analytics property (GA4) + one AdSense publisher — the same single
# property the tools already shared, so history is preserved.
GTAG = "G-MY95FHB8JG"
ADSENSE = "ca-pub-7217603696203672"
VERIFICATION = "jV8Xt5l-peRpLknp7xKYpvN8N5tCAkMctq0D-3RVyzk"

TOOLS = json.loads((ROOT / "scripts" / "tools.json").read_text(encoding="utf-8"))
TOOL_BY_NAME = {t["name"]: t for t in TOOLS}

HEAD_EXTRA = """
<meta name="google-site-verification" content="{verification}">
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={adsense}" crossorigin="anonymous"></script>
<script async src="https://www.googletagmanager.com/gtag/js?id={gtag}"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments)}}gtag('js',new Date());gtag('config','{gtag}');</script>
""".format(verification=VERIFICATION, adsense=ADSENSE, gtag=GTAG)

HEADER_HTML = """
<div class="hub-nav" style="position:sticky;top:0;z-index:9999;background:rgba(10,10,16,.93);backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px);border-bottom:1px solid rgba(255,255,255,.09)">
  <div style="max-width:960px;margin:0 auto;display:flex;align-items:center;gap:12px;padding:9px 16px;flex-wrap:wrap">
    <a href="{base}/" style="display:flex;align-items:center;gap:7px;color:#e8e8f0;text-decoration:none;font-weight:700;font-size:14.5px">&#128736;&#65039; Free Tools Hub</a>
    <span style="color:#55557a;font-size:10.5px;letter-spacing:.6px;text-transform:uppercase">17 free tools &middot; no signup</span>
    <nav style="margin-left:auto;display:flex;gap:4px;flex-wrap:wrap">
      <a href="{base}/" style="padding:5px 11px;border-radius:99px;color:#b9b9e0;text-decoration:none;font-size:12px;font-weight:600">Home</a>
      <a href="{base}/#tools" style="padding:5px 11px;border-radius:99px;color:#b9b9e0;text-decoration:none;font-size:12px;font-weight:600">All Tools</a>
      <a href="https://slashmantools.us/" style="padding:5px 11px;border-radius:99px;border:1px solid rgba(255,255,255,.12);color:#b9b9e0;text-decoration:none;font-size:12px;font-weight:600">SlashMan Tools &rarr;</a>
    </nav>
  </div>
</div>
""".format(base=BASE)

FOOTER_HTML = """
<footer class="hub-footer" style="max-width:960px;margin:30px auto 0;padding:18px 16px 8px;border-top:1px solid rgba(255,255,255,.08);text-align:center;font-size:11.5px;color:#6a6a90;line-height:2">
  <p><a href="{base}/" style="color:#8a8ab0;text-decoration:none">&#128736;&#65039; Free Tools Hub</a> &middot; free online tools &mdash; calculators, developer tools, AI tools &amp; more. Everything runs 100% in your browser; nothing is uploaded.</p>
  <p><a href="https://slashmantools.us/privacy/" style="color:#6a6a90;text-decoration:none">Privacy</a> &middot; <a href="https://slashmantools.us/terms/" style="color:#6a6a90;text-decoration:none">Terms</a> &middot; <a href="https://slashmantools.us/contact/" style="color:#6a6a90;text-decoration:none">Contact</a> &middot; &copy; 2026 SlashMan Tools</p>
</footer>
""".format(base=BASE)

RELATED_CSS = """
<style>
.hub-related{max-width:960px;margin:34px auto 0;padding:0 16px}
.hub-related-h{font-size:11px;font-weight:700;letter-spacing:1px;color:#5a5a7a;text-transform:uppercase;margin-bottom:10px}
.hub-related-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:8px}
.hub-related-grid a{display:block;padding:10px 12px;border:1px solid rgba(255,255,255,.09);border-radius:10px;background:rgba(255,255,255,.03);color:#c7c7f0;text-decoration:none;font-size:12.5px;line-height:1.45}
.hub-related-grid a:hover{background:rgba(99,102,241,.14);border-color:rgba(99,102,241,.35)}
.hub-related-all{display:inline-block;margin-top:10px;color:#a5b4fc;font-size:12.5px;text-decoration:none}
</style>
"""


def related_html(current_name: str) -> str:
    cur = TOOL_BY_NAME[current_name]
    same_cat = [t for t in TOOLS if t["cat"] == cur["cat"] and t["name"] != current_name]
    others = [t for t in TOOLS if t["cat"] != cur["cat"]]
    picks = (same_cat + others)[:6]
    cards = "".join(
        '<a href="{base}/{name}/">{icon} {title}</a>'.format(base=BASE, name=t["name"], icon=t["icon"], title=t["title"])
        for t in picks
    )
    return (
        RELATED_CSS
        + '<div class="hub-related" id="hub-related">'
        + '<div class="hub-related-h">More free tools</div>'
        + '<div class="hub-related-grid">' + cards + "</div>"
        + '<a class="hub-related-all" href="{base}/#tools">Browse all {n} tools &rarr;</a>'.format(base=BASE, n=len(TOOLS))
        + "</div>"
    )


def url_for(rel: str) -> str:
    """Map a dist-relative html file path to its canonical URL."""
    if rel == "index.html":
        return BASE + "/"
    if rel.endswith("index.html"):
        return BASE + "/" + rel[: -len("index.html")]
    return BASE + "/" + rel


def og_image_for(rel: str) -> str:
    if rel.endswith("index.html"):
        d = rel[: -len("index.html")]
        if (ROOT / d / "og.png").exists():
            return BASE + "/" + d + "og.png"
    return BASE + "/og.png"


def inject_file(src_rel: str, add_chrome: bool = True) -> None:
    src = ROOT / src_rel
    dst = DIST / src_rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    html = src.read_text(encoding="utf-8", errors="replace")

    # canonical
    html = re.sub(r'(rel="canonical" href=")[^"]*(")', r"\g<1>" + url_for(src_rel) + r"\g<2>", html, count=1)
    # og:url
    html = re.sub(r'(property="og:url" content=")[^"]*(")', r"\g<1>" + url_for(src_rel) + r"\g<2>", html, count=1)
    # og:image -> hub copy (keeps social previews on the new domain)
    html = re.sub(r'(property="og:image" content=")[^"]*(")', r"\g<1>" + og_image_for(src_rel) + r"\g<2>", html, count=1)

    if add_chrome and "<body" in html:
        # ensure analytics + verification in <head>
        if GTAG not in html:
            m = re.search(r"</head>", html)
            if m:
                html = html[: m.start()] + HEAD_EXTRA + html[m.start():]
        # sticky hub header right after <body ...>
        m = re.search(r"<body[^>]*>", html)
        if m:
            html = html[: m.end()] + "\n" + HEADER_HTML + html[m.end():]
        # related tools + footer right before </body>
        related = related_html(src_rel.split("/")[0]) if "/" in src_rel else related_html(src_rel)
        if "</body>" in html:
            html = html.replace("</body>", related + "\n" + FOOTER_HTML + "\n</body>", 1)

    dst.write_text(html, encoding="utf-8")


def build_landing() -> str:
    cats = []
    seen = set()
    for t in TOOLS:
        if t["cat"] not in seen:
            seen.add(t["cat"])
            cats.append(t["cat"])
    cards_by_cat = ""
    for cat in cats:
        items = "".join(
            '<a class="card" href="{base}/{name}/"><div class="ic">{icon}</div><div class="t">{title}</div><div class="d">{desc}</div></a>'.format(
                base=BASE, name=t["name"], icon=t["icon"], title=t["title"], desc=t["desc"]
            )
            for t in TOOLS
            if t["cat"] == cat
        )
        cards_by_cat += (
            '<div class="cat"><span class="cat-lbl">{cat}</span><div class="grid">{items}</div></div>'.format(
                cat=cat, items=items
            )
        )
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00")
    return """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Free Tools Hub — 17 Free Online Tools (Calculators, Dev Tools, AI) | No Signup</title>
<meta name="description" content="17 free online tools in one place: calculators, compound interest, token cost, LLM VRAM, developer tools, QR codes, image compressor, PDF tools, AI prompt library, bio generator & more. No signup, no uploads, runs in your browser.">
<meta name="keywords" content="free online tools, free calculator, qr code generator, password generator, unit converter, image compressor, pdf tools, ai prompts, dev tools">
<link rel="canonical" href="{base}/">
<meta property="og:title" content="Free Tools Hub — 17 Free Online Tools">
<meta property="og:description" content="Calculators, dev tools, AI tools & more. Free, no signup, in your browser.">
<meta property="og:image" content="{base}/og.png">
<meta property="og:url" content="{base}/">
<meta property="og:site_name" content="SlashMan Tools">
<meta name="twitter:card" content="summary_large_image">
{head_extra}
<script type="application/ld+json">{{"@context":"https://schema.org","@type":"WebSite","name":"Free Tools Hub","url":"{base}/","potentialAction":{{"@type":"SearchAction","target":"{base}/#tools","query-input":"required name=search_term_string"}}}}</script>
<style>
  *{{margin:0;padding:0;box-sizing:border-box}}
  body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:#0a0a0f;color:#e8e8f0;min-height:100vh}}
  .hero{{max-width:960px;margin:0 auto;padding:56px 16px 8px;text-align:center}}
  .hero h1{{font-size:clamp(26px,5vw,40px);font-weight:800;letter-spacing:-.5px;background:linear-gradient(135deg,#a5b4fc,#f0abfc);-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:10px}}
  .hero p{{color:#8a8ab0;font-size:15px;max-width:640px;margin:0 auto;line-height:1.7}}
  .hero .badge{{display:inline-block;margin-top:16px;padding:6px 14px;border-radius:99px;background:rgba(99,102,241,.15);border:1px solid rgba(99,102,241,.35);color:#c7c7f0;font-size:12px;font-weight:600}}
  .tools{{max-width:960px;margin:0 auto;padding:36px 16px 10px}}
  .cat{{margin-bottom:34px}}
  .cat-lbl{{display:block;font-size:11px;font-weight:700;letter-spacing:1.2px;color:#5a5a7a;text-transform:uppercase;margin-bottom:12px}}
  .grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:12px}}
  .card{{display:block;background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.09);border-radius:14px;padding:16px;text-decoration:none;transition:.15s}}
  .card:hover{{background:rgba(99,102,241,.12);border-color:rgba(99,102,241,.35);transform:translateY(-2px)}}
  .card .ic{{font-size:26px;margin-bottom:8px}}
  .card .t{{color:#e8e8f0;font-weight:700;font-size:14px;margin-bottom:5px}}
  .card .d{{color:#8a8ab0;font-size:12px;line-height:1.55}}
  .hub-note{{max-width:960px;margin:0 auto;padding:10px 16px 40px;color:#55557a;font-size:11.5px;text-align:center;line-height:1.9}}
</style>
</head>
<body>
{header}
<section class="hero">
  <h1>17 free tools. One place.</h1>
  <p>Calculators, developer utilities, image &amp; PDF tools, AI prompt templates and more — every tool is 100% free, runs in your browser, and never uploads your data.</p>
  <span class="badge">&#9989; No signup &middot; No uploads &middot; Free forever</span>
</section>
<section class="tools" id="tools">
  {cards_by_cat}
</section>
<p class="hub-note">Tools formerly published as individual sites (calculators, qr-code-generator, etc.) now live here under one roof. <a href="https://slashmantools.us/" style="color:#6868a0">slashmantools.us</a> &middot; <a href="/sitemap.xml" style="color:#6868a0">Sitemap</a></p>
{footer}
</body>
</html>""".format(
        base=BASE, head_extra=HEAD_EXTRA, header=HEADER_HTML, footer=FOOTER_HTML,
        cards_by_cat=cards_by_cat, generated=now,
    )


def build_sitemap() -> str:
    urls = [BASE + "/"]
    # tool index pages
    for t in TOOLS:
        urls.append(BASE + "/" + t["name"] + "/")
    # deep SEO pages: llm-calc models + bio-generator posts (+ any other non-index html)
    for dp, dn, fn in os.walk(DIST):
        dn[:] = [d for d in dn if d != "assets"]
        for f in sorted(fn):
            if not f.endswith(".html"):
                continue
            rel = os.path.relpath(os.path.join(dp, f), DIST).replace(os.sep, "/")
            if rel in ("404.html",) or rel.endswith(("embed.html", "privacy.html")):
                continue
            if not rel.endswith("index.html") and not rel.startswith("_"):
                urls.append(url_for(rel))
    urls = sorted(set(urls))
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    body = "".join(
        "  <url><loc>{u}</loc><lastmod>{d}</lastmod><changefreq>monthly</changefreq><priority>0.8</priority></url>\n".format(u=u, d=now)
        for u in urls
    )
    return '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + body + "</urlset>\n"


def build_404() -> str:
    return """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>404 — Free Tools Hub</title>
<link rel="canonical" href="{base}/404.html">
<style>
  body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:#0a0a0f;color:#e8e8f0;min-height:100vh;display:flex;align-items:center;justify-content:center;text-align:center}}
  .box{{max-width:480px;padding:20px}}
  h1{{font-size:64px;margin-bottom:8px;background:linear-gradient(135deg,#a5b4fc,#f0abfc);-webkit-background-clip:text;-webkit-text-fill-color:transparent}}
  p{{color:#8a8ab0;margin-bottom:22px;line-height:1.7}}
  a{{display:inline-block;padding:10px 22px;border-radius:99px;background:rgba(99,102,241,.2);border:1px solid rgba(99,102,241,.4);color:#c7c7f0;text-decoration:none;font-weight:600;font-size:14px}}
</style>
</head>
<body>
<div class="box">
  <h1>404</h1>
  <p>This tool page doesn't exist (yet). All 17 free tools live on the hub home page.</p>
  <a href="{base}/">&#128736;&#65039; Back to Free Tools Hub</a>
</div>
</body>
</html>""".format(base=BASE)


def main() -> None:
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir(parents=True)

    # 1. copy everything from repo root (sources) -> dist
    for item in sorted(ROOT.iterdir()):
        if item.name in (".git", "dist", "scripts", ".github", ".gitignore", "README.md", "CNAME", "ads.txt"):
            continue
        dst = DIST / item.name
        if item.is_dir():
            shutil.copytree(item, dst)
        else:
            shutil.copy2(item, dst)

    # 2. inject chrome into every html page
    injected = 0
    for dp, dn, fn in os.walk(DIST):
        dn[:] = [d for d in dn if d not in ("assets",)]
        for f in sorted(fn):
            if not f.endswith(".html"):
                continue
            rel = os.path.relpath(os.path.join(dp, f), DIST).replace(os.sep, "/")
            if rel.startswith("404") or f == "embed.html" or f == "privacy.html":
                continue
            inject_file(rel, add_chrome=True)
            injected += 1

    # 3. hub-level files
    (DIST / "index.html").write_text(build_landing(), encoding="utf-8")
    (DIST / "sitemap.xml").write_text(build_sitemap(), encoding="utf-8")
    (DIST / "robots.txt").write_text("User-agent: *\nAllow: /\nSitemap: " + BASE + "/sitemap.xml\n", encoding="utf-8")
    (DIST / "404.html").write_text(build_404(), encoding="utf-8")
    (DIST / "CNAME").write_text("tools.slashmantools.us\n", encoding="utf-8")
    if (ROOT / "ads.txt").exists():
        shutil.copy2(ROOT / "ads.txt", DIST / "ads.txt")

    print("built dist/ — {} pages with hub chrome injected".format(injected))
    n_html = sum(1 for dp, dn, fn in os.walk(DIST) for f in fn if f.endswith(".html"))
    print("total html in dist: {}".format(n_html))


if __name__ == "__main__":
    main()
