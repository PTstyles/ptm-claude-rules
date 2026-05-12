# Process Summary: Building Themed Domo App Studio Apps with Pro-Code Components

## What Gets Built

A single prompt produces a complete, production-grade Domo demo consisting of:

- **(~4-7) raw source datasets** in a star schema (fact + dimension tables), generated and uploaded to Domo
- **A Magic ETL dataflow** that joins/transforms the star schema into 3 denormalized output datasets
- **Multi-page App Studio app** with left-nav navigation (3-5 pages), powered by the ETL output datasets
- Per-page **pro-code banner** (CSS gradient + branded text, rendered in iframe)
- Per-page **pro-code chart** (React + Recharts `ComposedChart` or `BarChart`, rendered in iframe)
- Native Domo cards (KPI single-value, tables) mixed with pro-code cards
- Page filters that interact with native app studio and pro code components
- Page variables that interact with native app studio and pro code components
- Full theme application (colors, fonts, card styles, navigation chrome)
- **Pitch deck** (HTML slides → PDF) with branded cover, architecture diagrams, and dashboard showcase
- **Demo video** (30s, 1920x1080 MP4 via Playwright) capturing the real deployed App Studio app — page navigation, scrolling, live data
- Automated screenshots via Playwright for visual validation
- See [https://modocorp.domo.com/app-studio/396231467/pages/1942764543](https://modocorp.domo.com/app-studio/396231467/pages/1942764543) for classic baseline example of components, layout and content (theme and color palettes can vary).

## Skills Used (from `~/.agents/skills/`)


| Skill                   | Path                                              | Purpose                                                                                                                                                                                                                                                                                                |
| ----------------------- | ------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `domo-data-generator`   | `~/.agents/skills/domo-data-generator/SKILL.md`   | Generate realistic sample datasets — YAML catalog definitions, entity pools, rolling dates. Creates datasets and uploads to Domo.                                                                                                                                                                      |
| `magic-etl`             | `~/.agents/skills/magic-etl/SKILL.md`             | Create Magic ETL dataflows programmatically — DAG-based JSON definitions, input/transform/output node wiring, join operations, execution via API or Java CLI.                                                                                                                                          |
| `pb-apps-initial-build` | `~/.agents/skills/pb-apps-initial-build/SKILL.md` | Build orchestration for App Studio apps — phases 0-9 from manifest through publish. Phase 2b references pro-code chart defaults.                                                                                                                                                                       |
| `app-studio`            | `~/.agents/skills/app-studio/SKILL.md`            | App Studio REST API — app creation, view/page management, layout templates, card placement, navigation config, theme PUT endpoint. Contains the verified Domo icon catalog (133 names).                                                                                                                |
| `app-studio-pro-code`   | `~/.agents/skills/app-studio-pro-code/SKILL.md`   | Pro-code card embedding — decision routing (native vs pro-code), `domo publish` → context API → card instance creation, banner/chart CSS/JS patterns, font-family mapping table, theme color inheritance warnings, DEFAULT VISUALIZATION STRATEGY (ComposedChart on main page, BarChart on sub-pages). |
| `domo-app-theme`        | `~/.agents/skills/domo-app-theme/SKILL.md`        | Theme system — DESIGN.md format, color slot mapping (c1-c59), font slot mapping (f1-f8), card style presets (ca1-ca8), importable Theme JSON structure. Houses 31+ theme DESIGN.md files in `themes/` subdirectory.                                                                                    |
| `html-deck`             | `~/.agents/skills/html-deck/SKILL.md`             | HTML slide deck → PDF pipeline — slide anatomy, content patterns (tables, flow diagrams, card grids, info boxes), print-safe CSS, Puppeteer PDF conversion. Uses `domo-theme.md` for Domo-branded styling.                                                                                             |
| `app-studio-demo-capture` | `~/.agents/skills/app-studio-demo-capture/SKILL.md` | Playwright-based demo video capture of deployed App Studio apps — authenticates, navigates pages, scrolls, records the real production UI (left-nav, native cards, pro-code iframes, applied theme, live data). Produces polished MP4 walkthrough of the actual app. |
| `publish`               | `~/.agents/skills/publish/SKILL.md`               | `domo publish` CLI — dist workflow, first-publish ID handling.                                                                                                                                                                                                                                         |
| `manifest`              | `~/.agents/skills/manifest/SKILL.md`              | manifest.json configuration — dataset aliases, collections, Code Engine packages.                                                                                                                                                                                                                      |


## Build Process (per app)

### Step 1 — Generate Sample Data

Using `domo-data-generator`, create (~4-7) raw source datasets in a **star schema** appropriate for the industry vertical:

- **3 fact tables** (transactional/event data — 500-2000+ rows each)
- **4 dimension tables** (lookup/reference data — entities, categories, regions, etc.)

Create YAML catalog definitions if they don't exist, generate the data, and upload all datasets to Domo. Column names should use `snake_case` and include foreign key `_id` columns linking facts to dimensions.

### Step 2 — Create & Execute Magic ETL Dataflow

Using `magic-etl`, create a Magic ETL dataflow that joins the star schema into **3 denormalized output datasets** ready for app consumption:

- Each output joins 1 fact table to its relevant dimensions via left joins
- Add `SelectValues` steps to keep only columns needed by the app
- Execute the dataflow after creation and confirm output datasets are populated

The **output datasets** power the App Studio app and pro-code charts — NOT the raw source tables.

### Step 3 — Create App Studio App

```python
POST /api/content/v1/dataapps  →  {"title": "App Name"}
# Returns appId, landingViewId
```

### Step 4 — Create Additional Pages

```python
POST /api/content/v1/dataapps/{appId}/views  →  {"title": "Page Name"}
# Repeat for each sub-page; rename landingView title via PUT
```

### Step 5 — Apply Theme

```python
GET /api/content/v1/dataapps/{appId}/theme  →  theme JSON
# Modify colors (c1-c59, c56=page bg, c58/c59=text), fonts (f1-f8), 
# cards (ca1 for charts, ca8 for banners), navigation (bg, active, hover, 
# linkFontColor, titleFontColor, showShadow, icons)
PUT /api/content/v1/dataapps/{appId}/theme  →  modified theme
```

**Critical theme fields**: `c56` = page background (must be set explicitly, separate from `c1`). `c58` = primary text color (FONT tag). `c59` = secondary text (FONT tag). `c60` = AUTOMATIC_COLOR — never rely on it for dark themes. Navigation uses `background`, `activeBackground`, `hoverBackground`, `titleFontColor`, `linkFontColor`, `showShadow`.

### Step 6 — Build & Publish Pro-Code Components

For each page, create two pro-code apps:

1. **Banner** — HTML/CSS gradient with branded text (no dataset needed)
2. **Chart** — React + Recharts via esm.sh import maps (no build step)

```
# File structure per component:
banner-overview/
  index.html    # loads ryuu.js, app.css, app.js
  app.css       # gradient bg, brand text, pattern overlay
  app.js        # (empty or minimal for banners)
  manifest.json # {"name":"...", "size":{...}, "mapping":[]}

chart-overview/
  index.html    # import map: react@18.2.0, recharts@2.12.7 from esm.sh
  app.css       # chart container, tooltip, legend, loading states
  app.js        # React.createElement (no JSX), ComposedChart/BarChart
  manifest.json # dataset alias mapping
```

**Colors and fonts in pro-code are HARDCODED** — they do NOT inherit from the App Studio theme. Every `app.css` and `app.js` must use hex values matching the DESIGN.md palette. If the theme changes, all pro-code components must be updated and republished.

```bash
cd banner-overview && domo publish   # creates designId
cd chart-overview && domo publish    # creates designId
```

### Step 7 — Create Card Instances from Published Designs

```python
# Context API uses ROOT DOMAIN, not /api/ prefix
DOMO = f"https://{instance}.domo.com"

# Step 5a: Create context
POST {DOMO}/domoapps/apps/v2/contexts  →  {"designId": ..., "mapping": [...]}

# Step 5b: Create card on page
POST {DOMO}/domoapps/apps/v2?fullpage=false&pageId={pageId}&cardTitle={title}
     →  {"contextId": ctx_id, "id": ctx_id}

# Step 5c: Find numeric card ID
GET /api/content/v1/pages/{pageId}/cards  →  find by title
```

### Step 8 — Assemble Layout

```python
GET /api/content/v4/pages/{pageId}/layouts  →  layout JSON
PUT .../writelock  # acquire lock

# Build template: HEADER(banner) at y=0, SPACER, CARD(chart) below, 
# native cards in grid. Each entry needs: contentKey, x, y, width, height, 
# type ("CARD"|"HEADER"|"SPACER"), virtualAppendix, virtual, children
# Canvas items: children=[]  |  Appendix items: children=None

PUT /api/content/v4/pages/layouts/{layoutId}  →  modified layout
DELETE .../writelock  # release lock
```

**Content entry properties for pro-code cards**:

```python
{"hideTitle": True, "hideSummary": True, "hideDescription": True, 
 "hideFooter": True, "hideBorder": True/False, "hideMargins": True/False, 
 "fitToFrame": True, "style": {"sourceId": "ca8"}}  # ca8 for banners, ca1 for charts
```

### Step 9 — Configure Navigation

```python
# Navigation is part of the theme PUT — set per-page icons using ONLY 
# verified Domo icon names (NOT Material Design names)
# Proven icons: analytics, store, dataflow, certified, stethoscope, 
#   notebook, people, pricetag, warehouse, badge, benchmark, etc.
# Full catalog of 133 verified names in app-studio/SKILL.md
```

### Step 10 — Screenshot & Validate

```bash
node screenshot.js app {appId} '{"Overview":"{pageId1}","Sales":"{pageId2}"}' ./screenshots/
```

### Step 11 — Generate Pitch Deck

Using `html-deck` skill with the Domo theme (`domo-theme.md`):

1. Create 8-10 HTML slides — cover, problem statement, solution overview, architecture/data flow diagram, dashboard showcase, ROI/value metrics, implementation timeline, closing CTA
2. Run the Puppeteer converter script to produce a retina-quality PDF

** see /Users/cassidy.hilton/Cursor Projects/CobraML for context on how to approach the deck build, if needed (ensure /Users/cassidy.hilton/Cursor Projects/CobraML/Sample Assets/Template.pdf is used as template baseline skeleton). 

### Step 12 — Capture Demo Video

Using `app-studio-demo-capture` Playwright pipeline:

1. The App Studio app must be fully deployed (all pages, cards, theme, data) from Steps 3-9
2. Authenticate a headless Playwright browser using the Domo session from `domo login`
3. Navigate through all pages, scroll content, and record a polished walkthrough video of the real production app — left-nav, native cards, pro-code iframes, applied theme, live data
4. Post-process with ffmpeg if needed and produce the final MP4

## Default Pro-Code Chart Patterns

### Main/Overview Page — Multi-Line ComposedChart

- Solid line = Actuals (`COLORS.primary`)
- Solid lighter line = Plan/Prior Period (`COLORS.secondary`)
- Dashed line = Forecast (`COLORS.secondary`, `strokeDasharray: '4 3'`)
- `Area` = Confidence band (gradient fill, MAE upper/lower)
- `ReferenceLine` = "Today" (dashed vertical)
- Day/Week/Month `<select>` toggle with `aggregateData()` function
- Confidence band toggle button
- Custom `ChartTooltip` component
- Manual footer legend (hide Recharts built-in)

### Sub-Pages — Time-Based BarChart

- Same date x-axis, same aggregation toggle
- `Bar` with `radius: [2,2,0,0]`, `maxBarSize: 40`
- Same tooltip, legend, "Today" line patterns

## Key Bugs & Fixes (Lessons Encoded in Skills)

1. `**c56` must be set explicitly** — page background is separate from `c1`
2. **Navigation icons must use Domo-native names** — Material Design names silently fail
3. `**HOME` page must be first** in navigation order
4. **Layout entries require `type` and `children` fields** — omitting causes 400 errors
5. **Pro-code iframe colors are NOT inherited** — must hardcode + republish on theme change
6. **Font family must match** across theme JSON and pro-code CSS `font-family` stacks
7. `**ca8` banner cards** need `backgroundColor` matching page bg, `padding:0`, `borderRadius:0` for frameless look
8. **Context API uses root domain** (`/domoapps/...`), NOT `/api/domoapps/...`
9. `**chartColorPalette` cannot be changed** from DOMO to CUSTOM type via PUT API
10. **Unsupported theme properties** (`activeLinkFontColor`, `activeColor`, `borderWidth` on cards, `dropShadow`/`dropShadowColor`) cause 400 errors — must be removed

## Theme System Architecture

3-layer system: **DESIGN.md** (single source of truth for AI) → **Theme JSON** (importable into App Studio) → **Pro-Code CSS/JS** (hardcoded values from DESIGN.md). 31+ themes across light/dark modes, multiple font families, and categories (punk, shades, green/forest, charcoal, corporate). Browse available themes in `~/.agents/skills/domo-app-theme/themes/`.

## End-to-End Deliverables Checklist


| #   | Deliverable                      | Verification                |
| --- | -------------------------------- | --------------------------- |
| 1   | ~7 raw datasets uploaded to Domo | Visible in Data Center      |
| 2   | Magic ETL dataflow executed      | 3 output datasets populated |
| 3   | Pro-code apps published          | Design IDs recorded         |
| 4   | App Studio app live              | Viewable at URL on instance |
| 5   | Pitch deck PDF generated         | File on disk                |
| 6   | Demo video MP4 rendered          | File on disk                |


