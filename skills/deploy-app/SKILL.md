---
name: deploy-app
description: After `domo publish` returns a design ID, create an App Studio app + page that hosts the published custom app as a full-page card. Use whenever the user has just published a pro-code app and wants it hosted in App Studio without building metrics/dashboards around it. Skip when the user wants a full analytics dashboard with native cards (use `app-studio-build` instead).
---

# Deploy Published App to App Studio

One-step deploy: takes a Domo published design ID and produces a clean App Studio app whose only contents are that pro-code card, sized to fill the page.

## When to use

- User just ran `domo publish` and got a design ID back
- User says "deploy this to App Studio", "wrap this in an App Studio page", "host this app", or similar
- User wants their pro-code app accessible at an App Studio URL with optional LEFT nav

## When NOT to use

- User wants metrics, KPIs, or native cards alongside the pro-code app → use `app-studio-build`
- User wants the card on an *existing* App Studio page → just call `create_procode_card` (snippet below) directly

## Inputs you need before running

| Input | How to get it | Required |
|-------|---------------|----------|
| `design_id` | UUID printed by `domo publish` (`Design can be found at .../assetlibrary?designId=…`) | ✅ |
| `app_title` | What the App Studio app should be called | ✅ |
| `instance` | e.g. `domo-paul-mccusker.domo.com` | ✅ |
| `developer_token` | `DDCI…` token for the instance | ✅ |
| `dataset_mappings` | List of `{alias, dataSetId}` if the published app's `manifest.json` declares dataset aliases | only if app uses datasets |

If the user's `manifest.json` has `datasetsMapping`, the same aliases must appear in `dataset_mappings` here — otherwise the card will load with no data.

## Run

```bash
python3 deploy_app.py \
  --design-id ab4935ae-0ec2-4f51-ba0e-003f77a327f4 \
  --title "My App" \
  --instance domo-paul-mccusker.domo.com \
  --token DDCI...
```

With dataset mappings:

```bash
python3 deploy_app.py \
  --design-id ab4935ae-0ec2-4f51-ba0e-003f77a327f4 \
  --title "My App" \
  --instance domo-paul-mccusker.domo.com \
  --token DDCI... \
  --mapping loans=1165f255-4776-4455-a262-7c77b2f6850c \
  --mapping alerts=4d8c706c-363a-41a0-8630-0245411a44fe
```

Output:
```
✓ App created: 302225920
✓ Card created: 307121958
✓ Layout: full-page
App URL: https://domo-paul-mccusker.domo.com/app/302225920
```

The script lives at [deploy_app.py](deploy_app.py) in this same directory — copy it next to your project or run it in place.

## What the script does

1. **Create app** — `POST /api/content/v1/dataapps` with title/description, captures `dataAppId` + `landingViewId`.
2. **Configure shell** — sets `navOrientation: LEFT`, hides Domo navigation/title/logo for a clean wrapper.
3. **Create pro-code card**:
   - `POST /domoapps/apps/v2/contexts` with `{designId, mapping}` — gets `contextId`
   - `POST /domoapps/apps/v2?fullpage=false&pageId={pid}&cardTitle={enc}` with `{contextId, id: contextId}` — Domo creates the card on the landing page
   - `GET /api/content/v1/pages/{pid}/cards` — find the new card by title to get its ID
4. **Apply full-page layout** — `GET /api/content/v4/pages/{pid}/layouts`, position the card at `(0, 0, 60, 94)` with all chrome hidden (`hideTitle/hideBorder/hideMargins/fitToFrame` all true), then write-lock + PUT + delete-lock the layout.

## Common gotchas

- **Thumbnail required at publish time.** If `domo publish` warned that a thumbnail was missing, the card-creation step here will fail with `DA0087: Design … is missing a thumbnail`. Add `thumbnail.png` (300×300) to the design's `dist/` and re-publish *to the same design ID* before running this skill.
- **Don't pass `dsId`** in mappings — the field is `dataSetId` (camelCase, capital S).
- **`fields: []` is required** in each mapping entry even when not aliasing columns; omitting it triggers `Cannot read properties of undefined (reading 'map')` at card load time.
- **`domoapps/apps/v2` returns no card ID** — the script sleeps 2s then GETs the page's cards and matches by title. If the title isn't unique on the page, it returns the first match — pass a unique `--title`.
- **Layout write-lock dance is not optional.** Skipping the `PUT /writelock` → `PUT /layouts/{lid}` → `DELETE /writelock` sequence either silently no-ops or 409s. The script handles all three.

## Verifying

After the script prints the App URL, open it. The published app should fill the page with no surrounding chrome. If you see the card title bar, border, or margins, the layout's `hideTitle/hideBorder/hideMargins/fitToFrame` flags didn't apply — re-run the script (it's idempotent at the layout level once the card exists).
