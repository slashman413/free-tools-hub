# 🛠️ Free Tools Hub

One deployable site consolidating **17 previously-separate static tool sites** into a
single domain: **[https://tools.slashmantools.us](https://tools.slashmantools.us)**

| # | Tool | Old site | New URL |
|---|------|----------|---------|
| 1 | Free Online Calculators | `slashmantools.us/calculators/` | `/calculators/` |
| 2 | Color Picker & Palette | `slashmantools.us/color-tools/` | `/color-tools/` |
| 3 | PDF Tools | `slashmantools.us/pdf-tools/` | `/pdf-tools/` |
| 4 | QR Code Generator | `slashmantools.us/qr-code-generator/` | `/qr-code-generator/` |
| 5 | Word & Character Counter | `slashmantools.us/word-counter/` | `/word-counter/` |
| 6 | Unit Converter | `slashmantools.us/unit-converter/` | `/unit-converter/` |
| 7 | Developer Tools | `slashmantools.us/dev-tools/` | `/dev-tools/` |
| 8 | JSON Formatter & Regex Tester | `slashmantools.us/json-regex-devtools/` | `/json-regex-devtools/` |
| 9 | Password Generator | `slashmantools.us/password-generator/` | `/password-generator/` |
| 10 | Token & API Cost Calculator | `slashmantools.us/token-cost-calculator/` | `/token-cost-calculator/` |
| 11 | LLM VRAM Calculator | `slashmantools.us/llm-calc/` | `/llm-calc/` |
| 12 | Image Compressor & Resizer | `slashmantools.us/image-compressor/` | `/image-compressor/` |
| 13 | AI Image Size Calculator | `slashmantools.us/ai-image-size-calculator/` | `/ai-image-size-calculator/` |
| 14 | AI Bio Generator | `slashmantools.us/bio-generator/` | `/bio-generator/` |
| 15 | Compound Interest Calculator | `slashmantools.us/compound-calculator/` | `/compound-calculator/` |
| 16 | Pomodoro Focus Timer | `slashmantools.us/pomodoro-focus-timer/` | `/pomodoro-focus-timer/` |
| 17 | AI Prompt Templates Library | `slashmantools.us/ai-prompt-library/` | `/ai-prompt-library/` |

All old URLs keep the same path on the new domain — **only the host changes**
(`slashmantools.us/<tool>/` → `tools.slashmantools.us/<tool>/`).

## What the hub gives us

- **One domain, one sitemap** (`/sitemap.xml`, 120 URLs incl. deep pages) — SEO
  authority concentrates instead of splitting 17 ways.
- **Shared chrome everywhere** — sticky site header, per-tool *related tools* rail,
  and a shared footer are injected by `scripts/build.py` into every page, so every
  tool cross-links every other tool.
- **One analytics + AdSense property** — all pages use GA4 `G-MY95FHB8JG` and
  AdSense `ca-pub-7217603696203672` (the same single property the tools already
  shared, so history is preserved).
- **One build/deploy pipeline** — GitHub Actions (`.github/workflows/deploy.yml`)
  runs the build and deploys to Pages.

## Repo layout

```
index.html                     hub landing (generated)
tools.json                     registry: name / title / desc / icon / category
scripts/build.py               injects chrome, rewrites canonicals, emits ./dist
<tool>/index.html              committed tool sources (monorepo = source of truth)
.github/workflows/deploy.yml   build + Pages deploy
sitemap.xml · robots.txt · 404.html · CNAME · ads.txt   (generated / static)
```

## Redirects from archived source repos

The 16 source repos + `ai-prompt-library` were archived (read-only) after the hub
went live. Their Pages sites still answer at the old URLs with a canonical +
meta-refresh consolidation page pointing at the hub (GitHub Pages cannot emit
HTTP 301s from static files, so this is the equivalent soft redirect).

See `docs/redirect-map.md` for the full map.

## Build & deploy

```bash
python3 scripts/build.py   # -> dist/
```

Push to `main` → workflow builds and deploys to https://tools.slashmantools.us
