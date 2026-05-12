---
name: card-create-publish
description: Scaffold a minimal single-card Domo custom app and publish it with the Domo CLI. Use when the user asks for the simplest possible "create and publish a card" demo. Skip when the user wants datasets, charts, App Studio integration, or anything beyond a single static card — use orchestrator-skills/basic-app-build instead.
---

# Card Create & Publish (Basic)

The simplest end-to-end Domo custom app: scaffold one HTML card, publish it, save the design ID. No datasets, no AppDB, no charts. Designed for live demos.

## When to use

- Live demo of "create and publish a Domo card with one prompt"
- Sanity-checking that `domo` CLI auth works on a new machine
- Teaching the skill system without the full app-build playbook

**Skip** if the user wants a real app with data — route to `orchestrator-skills/basic-app-build/SKILL.md`.

## What you'll produce

A folder with four files:

```
my-card/
├── manifest.json      # App metadata (Domo reads this on publish)
├── thumbnail.png      # 300x300 thumbnail (required by Domo)
├── index.html         # The single card UI
└── domo.js            # Domo runtime (loaded by index.html)
```

## Steps

### 1. Confirm the app name and target folder

Ask the user for:
- **App name** (e.g., "Hello Domo Card") — used in `manifest.json`
- **Folder name** (e.g., `hello-domo-card`) — kebab-case, will be created under `/Users/paul.mccusker/DomoApps/`

If they don't specify, default folder = kebab-case of the app name.

### 2. Create `manifest.json`

```json
{
  "name": "Hello Domo Card",
  "version": "1.0.0",
  "fullpage": false,
  "size": { "width": 4, "height": 3 },
  "datasetsMapping": [],
  "collections": [],
  "workflowMapping": [],
  "packagesMapping": []
}
```

Notes:
- **Do not** set `id` on first publish — Domo generates it.
- `fullpage: false` keeps it as a normal card. Set `true` only if the user wants a full-page app.
- Empty `datasetsMapping` is fine — this card doesn't read any data.

### 3. Create `index.html`

Keep it intentionally tiny. Show the user that custom apps are just static HTML.

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>Hello Domo</title>
  <script src="domo.js"></script>
  <style>
    body {
      margin: 0;
      font-family: "Open Sans", system-ui, sans-serif;
      display: flex;
      align-items: center;
      justify-content: center;
      height: 100vh;
      background: #f4f6f9;
    }
    .card {
      padding: 32px 48px;
      background: white;
      border: 1px solid #e2e6ee;
      text-align: center;
    }
    h1 { margin: 0 0 8px; color: #2563BE; font-size: 28px; }
    p  { margin: 0; color: #4a5568; }
  </style>
</head>
<body>
  <div class="card">
    <h1>Hello, Domo!</h1>
    <p>This card was created and published by Claude Code.</p>
  </div>
</body>
</html>
```

**Critical:** the `<script src="domo.js"></script>` tag is required even on apps that don't call `domo.get()`. Without it, `window.domo` is never injected and any future code that touches it will silently fail. (See `feedback_domo_js_script_tag.md`.)

### 4. Add `domo.js` and `thumbnail.png`

- **`domo.js`**: copy from any existing app in `/Users/paul.mccusker/DomoApps/` (e.g., `lone-star-parts/public/domo.js`). It's the Domo runtime — same file across all apps.
- **`thumbnail.png`**: 300x300 PNG. Generate one with Python/Pillow if needed:
  ```python
  from PIL import Image
  Image.new("RGB", (300, 300), "#2563BE").save("thumbnail.png")
  ```

Without `thumbnail.png`, `domo publish` returns `DA0087` and refuses to publish.

### 5. Publish

```bash
cd /Users/paul.mccusker/DomoApps/<folder-name>
domo login -i domo-paul-mccusker.domo.com -t <developer-token>
domo publish
```

Login token lives in memory: see `reference_domo_credentials.md`.

`domo publish` will print a **design ID** like:
```
Successfully published design 9f5ee91e-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

### 6. Save the design ID back into `manifest.json`

After the **first** publish, Domo writes an `id` field into the dist `manifest.json`. Copy that `id` back into your source `manifest.json`:

```json
{
  "name": "Hello Domo Card",
  "id": "9f5ee91e-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "version": "1.0.0",
  ...
}
```

**Why this matters:** if you skip this, every future `domo publish` creates a brand new app instead of updating the existing one. You'll end up with five "Hello Domo" apps in your asset library.

### 7. Confirm to the user

Print:
- Design ID
- Direct URL: `https://domo-paul-mccusker.domo.com/page/0?kpiEdit=<design-id>` (or instruct them to add the card to a page)

## Gotchas

| Gotcha | Symptom | Fix |
| --- | --- | --- |
| Missing `<script src="domo.js"></script>` | `window.domo is undefined` later | Add the tag, even on no-data cards |
| Missing `thumbnail.png` | `domo publish` fails with DA0087 | Drop a 300x300 PNG next to manifest.json |
| Forgot to copy `id` back | New app on every publish | Copy `id` from dist manifest after first publish |
| Wrong login host | `401 Unauthorized` on publish | Use full hostname `domo-paul-mccusker.domo.com`, not just `domo-paul-mccusker` |

## Bigger version of this skill

When the user is ready for the real thing, route to:
- `orchestrator-skills/basic-app-build/SKILL.md` — full app build with datasets, charts, and App Studio
- `apps/manifest/SKILL.md` — full manifest reference
- `apps/publish/SKILL.md` — full publish reference
