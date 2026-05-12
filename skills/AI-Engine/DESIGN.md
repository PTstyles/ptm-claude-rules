---
name: Domo Apps DESIGN.md
version: 0.1
audience: Forward Deployed Engineers, Domo
stack: Tailwind CSS v4, shadcn/ui, React, TypeScript
writing-authorities:
  - Domo house voice (primary)
  - Google Material Design UX writing best practices (tactical patterns)
  - AP Stylebook (tiebreaker for grammar, dates, numerals, capitalization)
visual-references:
  - Stripe Dashboard (KPI tile rhythm, restrained accent)
  - OpenAI Platform (form density, sentence case, breathing room)
  - Rowboat (dense data exploration, hairline structure, tabular numerals)
themes: [light, dark]
---

# Domo Apps DESIGN.md

This file teaches Claude how to design and build Domo apps the way Domo's Forward Deployed Engineering team would. It is a working contract between the FDE shipping the app and Claude generating the code.

## How to use this file

1. Drop this file at the repo root or in `.claude/DESIGN.md`. Claude reads it on every UI task.
2. Reference any token by its full path — e.g. `{colors.surface-1}`, `{typography.body}`, `{rounded.md}`. Claude resolves tokens to CSS custom properties; CSS custom properties resolve to Tailwind theme keys; Tailwind theme keys resolve to shadcn variants.
3. When Claude proposes a component, it should name the canonical primitive (`button-primary`, `kpi-tile`, `data-table`) and reference the tokens it composes from. Anything ad-hoc must be flagged as a deviation, not absorbed silently.
4. Light and dark themes are both first-class. Every component states what changes between themes; if no entry is given, the token resolves identically in both.
5. The `## Customization` section lists the small set of tokens an FDE swaps per customer engagement. Everything else stays canonical.

## Overview

Domo apps are dense, data-forward, and quiet. The canvas is white in light theme and a near-black charcoal in dark theme. Type is charcoal in light, off-white in dark. Hairline borders do most of the structural work; shadows are used sparingly and never black. Cards lift from the canvas with a one-step surface change plus a 1px border, never a heavy drop shadow. The single brand accent surfaces only on primary CTAs, key navigation states, and selected/active affordances — never as decoration or a section background.

Display type is set in **Inter** at weight 600 with measured negative letter-spacing on display sizes. Body type is the same family at weight 400. The single mono is **JetBrains Mono**, used for IDs, code snippets, and any dataset/column references rendered inside the app.

Type, spacing, radii, and color are owned by CSS custom properties at the `:root` and `[data-theme="dark"]` scopes. Tailwind extends its theme from those custom properties so utility classes resolve correctly in both themes. shadcn/ui components inherit the same custom properties through their existing variant API; Domo overrides go in `cn()` calls, not in forks of the shadcn source.

**Key Characteristics**

- White canvas in light theme (`{colors.canvas}` `oklch(0.99 0 0)`); near-black in dark (`{colors.canvas}` `oklch(0.16 0 0)`). Neither is pure white nor pure black.
- One brand accent (`{colors.brand}`) carries primary CTAs, key nav active states, and the focus ring. It never decorates.
- **Inter** at weight 600 carries display; weight 400 carries body. JetBrains Mono carries any code or ID.
- Hairline 1px borders (`{colors.hairline}`) do the heavy structural work. Shadows are tinted toward `{colors.brand}` at very low opacity, never pure black.
- Modest radii: 6–8px on buttons and inputs, 10–12px on cards, 16px reserved for hero tiles.
- Sentence case everywhere, buttons included. Uppercase is reserved for the eyebrow style and small status pill labels.
- Tabular numerals on every numeric column, KPI value, currency amount, and timestamp.
- 3-up KPI tile grids as the default dashboard rhythm; collapses to 2-up at tablet and 1-up at mobile.

## Tailwind + shadcn integration

### Theme custom properties

Domo theming lives in CSS custom properties on `:root` (light) and `[data-theme="dark"]` (dark). Tailwind v4's `@theme` directive maps those properties to utility class names. shadcn/ui's `globals.css` already follows this pattern; the Domo file extends it.

```css
@import "tailwindcss";

@theme {
  --color-canvas: var(--canvas);
  --color-surface-1: var(--surface-1);
  --color-surface-2: var(--surface-2);
  --color-hairline: var(--hairline);
  --color-hairline-soft: var(--hairline-soft);
  --color-ink: var(--ink);
  --color-ink-muted: var(--ink-muted);
  --color-ink-subtle: var(--ink-subtle);
  --color-brand: var(--brand);
  --color-brand-fg: var(--brand-fg);
  --color-ai-accent: var(--ai-accent);
  --color-success: var(--success);
  --color-warning: var(--warning);
  --color-danger: var(--danger);
  --color-info: var(--info);

  --font-sans: "Inter", ui-sans-serif, system-ui, sans-serif;
  --font-mono: "JetBrains Mono", ui-monospace, monospace;

  --radius-xs: 4px;
  --radius-sm: 6px;
  --radius-md: 8px;
  --radius-lg: 12px;
  --radius-xl: 16px;

  --shadow-sm: 0 1px 2px oklch(from var(--brand) l c h / 0.04);
  --shadow-md: 0 4px 12px oklch(from var(--brand) l c h / 0.06);
  --shadow-lg: 0 12px 32px oklch(from var(--brand) l c h / 0.08);
}

:root {
  --canvas: oklch(0.99 0 0);              /* {PLACEHOLDER: Domo light canvas} */
  --surface-1: oklch(1 0 0);              /* {PLACEHOLDER: Domo card white} */
  --surface-2: oklch(0.97 0 0);           /* {PLACEHOLDER: Domo subtle tint} */
  --hairline: oklch(0.92 0 0);            /* {PLACEHOLDER} */
  --hairline-soft: oklch(0.96 0 0);       /* {PLACEHOLDER} */
  --ink: oklch(0.18 0 0);                 /* {PLACEHOLDER: Domo charcoal} */
  --ink-muted: oklch(0.45 0 0);           /* {PLACEHOLDER} */
  --ink-subtle: oklch(0.62 0 0);          /* {PLACEHOLDER} */
  --brand: oklch(0.55 0.20 260);          /* {PLACEHOLDER: Domo primary blue} */
  --brand-fg: oklch(1 0 0);               /* text on {colors.brand} */
  --ai-accent: oklch(0.65 0.22 30);       /* {PLACEHOLDER or leave unwired} */
  --success: oklch(0.65 0.16 150);
  --warning: oklch(0.78 0.15 80);
  --danger: oklch(0.60 0.22 25);
  --info: oklch(0.65 0.15 230);
}

[data-theme="dark"] {
  --canvas: oklch(0.16 0 0);
  --surface-1: oklch(0.20 0 0);
  --surface-2: oklch(0.23 0 0);
  --hairline: oklch(0.28 0 0);
  --hairline-soft: oklch(0.24 0 0);
  --ink: oklch(0.96 0 0);
  --ink-muted: oklch(0.72 0 0);
  --ink-subtle: oklch(0.55 0 0);
  --brand: oklch(0.68 0.18 260);          /* lighter in dark for contrast */
  --brand-fg: oklch(0.16 0 0);
  --success: oklch(0.72 0.16 150);
  --warning: oklch(0.82 0.15 80);
  --danger: oklch(0.70 0.22 25);
  --info: oklch(0.72 0.15 230);
}
```

> Replace each `{PLACEHOLDER}` value with the locked Domo brand value before shipping. The structure is final; only the values need filling.

### shadcn override pattern

shadcn components are imported as-is, never forked. Domo customization lives in `cn()` extensions and is named after the canonical primitive.

```tsx
import { Button as ShadcnButton } from "@/components/ui/button";
import { cn } from "@/lib/utils";

export function Button({ className, variant = "primary", ...props }) {
  return (
    <ShadcnButton
      className={cn(
        // base — applies to every Domo button
        "font-medium tracking-tight transition-colors duration-150 ease-out",
        "focus-visible:ring-2 focus-visible:ring-brand focus-visible:ring-offset-2",
        // variants
        variant === "primary" && "bg-ink text-canvas hover:bg-ink/90",
        variant === "secondary" && "bg-surface-1 text-ink border border-hairline hover:bg-surface-2",
        variant === "tertiary" && "bg-transparent text-ink hover:bg-surface-2",
        variant === "destructive" && "bg-danger text-white hover:bg-danger/90",
        variant === "ai" && "bg-ai-accent text-white hover:bg-ai-accent/90",
        className
      )}
      {...props}
    />
  );
}
```

### Token resolution rules

- Always reference tokens via Tailwind utility classes (`bg-surface-1`, `text-ink-muted`) rather than CSS variables directly. This keeps theming consistent and IntelliSense useful.
- Never use Tailwind's built-in palette (`bg-gray-100`, `text-blue-600`). Those bypass the theme.
- Never hardcode hex values inside components. If a value is missing from the theme, add it to the theme first.

### shadcn workflow

The shadcn/ui project ships a Claude skill that gives AI assistants project-aware context. Install it on day one of every FDE engagement:

```bash
pnpm dlx skills add shadcn/ui
```

The skill activates when a `components.json` file is present in the repo and runs `shadcn info --json` on every interaction to inject project configuration into Claude's context — framework, Tailwind version, aliases, base library (`radix` or `base`), icon library, installed components, and resolved file paths. This is what stops Claude from importing `@/components/ui/button` when the project uses `@/ui/button`, or generating `radix`-flavored APIs in a project on the `base` library, or both.

**Conventions that follow from the skill:**

- Install components via `shadcn add` rather than copy-pasting source files. The CLI keeps `components.json` in sync, which is the source of truth the skill reads.
- Run `shadcn diff` periodically to surface upstream component updates worth reviewing.
- `components.json` itself is canonical — don't hand-edit aliases, base library, or icon library; re-run `shadcn init` instead.
- Use shadcn's canonical composition primitives where they exist:
  - `Field` / `FieldGroup` for form fields and their label/helper/error trio (referenced in Component #14).
  - `ToggleGroup` for option sets and segmented controls (referenced in Component #6, segmented variant).
  - `ButtonGroup` for related buttons sharing a border (toolbar controls, paginators).
  - `Empty` for the empty-state primitive (referenced in Component #9).
  - `Spinner` for the indeterminate loading primitive (referenced in Component #10).
  - `Item` for list rows that need a consistent row scaffold.
  - `Kbd` for inline keyboard shortcut hints.
- Reach for shadcn's MCP server when the project pulls from a custom registry (e.g., a Domo internal registry of pre-themed components shared across customer engagements). Configure once in the project; AI assistants can then search, browse, and install registry components programmatically.

## Colors

> All values are placeholders and OKLCH-encoded for predictable lightness behavior across themes. Replace placeholder values with locked Domo brand values; do not change token names.

### Brand & Accent

- `{colors.brand}` — Primary brand color. Surfaces only on primary CTAs, key nav active states, the focus ring, and small inline emphasis. Never as a section background or decorative fill.
- `{colors.brand-fg}` — Text color on `{colors.brand}` backgrounds.
- `{colors.ai-accent}` — Reserved for AI-product surfaces (chat composer send button, agent action chips, "powered by AI" badges). If Domo does not have an AI-product accent, leave this token defined but unused; do not delete it.

### Surface

- `{colors.canvas}` — Default page background. White in light, near-black in dark.
- `{colors.surface-1}` — Cards, modals, dropdowns, the elevated surface that lifts from canvas.
- `{colors.surface-2}` — Subtle tinted strip — alternating table rows, inline callouts, sidebar background, hovered surface state.
- `{colors.hairline}` — 1px structural borders on cards, inputs, table cells.
- `{colors.hairline-soft}` — Even softer dividers between FAQ rows, list items, and footer columns.

### Text

- `{colors.ink}` — Primary text. Headlines, body, button labels.
- `{colors.ink-muted}` — Secondary text. Field labels, helper text, secondary table columns.
- `{colors.ink-subtle}` — Tertiary text. Captions, timestamps, footnotes, disabled labels (paired with `aria-disabled`).

### Semantic

- `{colors.success}` — Positive state. Success toasts, "live" indicators, positive deltas in KPIs.
- `{colors.warning}` — Caution state. Warning banners, "paused" indicators.
- `{colors.danger}` — Destructive or error state. Form validation errors, destructive CTAs, error toasts.
- `{colors.info}` — Informational state. Info banners, neutral notifications.

### Dataviz Palette

The dataviz palette lives separately from the brand palette. It is consumed by chart wrappers (`chart-card`) and never bleeds into application chrome. Palette structure:

| Token | Use |
|---|---|
| `{dataviz.series-1}` through `{dataviz.series-8}` | Categorical series colors, ordered for legibility on white and on dark canvas. |
| `{dataviz.sequential-min}` / `{dataviz.sequential-max}` | Endpoints for sequential heatmaps and choropleths. |
| `{dataviz.diverging-low}` / `{dataviz.diverging-mid}` / `{dataviz.diverging-high}` | Diverging scale anchors. |

> Decide categorical series colors after locking `{colors.brand}`; series-1 should be `{colors.brand}` so the most prominent line in any single-series chart matches the app's accent.

## Typography

### Font Family

- **`var(--font-sans)`** — The customer's brand sans-serif. Carries display, body, eyebrow, and button. Weight 400 for body, 500 for emphasis, 600 for display, 700 reserved for marketing surfaces. When the customer brand font isn't yet locked, fall back to a system font stack (`ui-sans-serif, system-ui, -apple-system, sans-serif`) — not Inter, Roboto, or Poppins, which are the AI defaults this file is designed to push back against.
- **`var(--font-mono)`** — The customer's brand mono, or a system mono fallback (`ui-monospace, SFMono-Regular, Menlo, monospace`). Used for IDs, code snippets, dataset names, column references, SQL.

### Hierarchy

| Token | Size | Weight | Line Height | Letter Spacing | Tailwind Use |
|---|---|---|---|---|---|
| `{typography.display-xl}` | 48px | 600 | 1.10 | -0.02em | `text-5xl font-semibold tracking-tight` |
| `{typography.display-lg}` | 36px | 600 | 1.15 | -0.02em | `text-4xl font-semibold tracking-tight` |
| `{typography.display-md}` | 28px | 600 | 1.20 | -0.015em | `text-3xl font-semibold tracking-tight` |
| `{typography.headline}` | 22px | 600 | 1.25 | -0.01em | `text-[22px] font-semibold` |
| `{typography.title}` | 18px | 600 | 1.30 | -0.005em | `text-lg font-semibold` |
| `{typography.subhead}` | 16px | 500 | 1.40 | 0 | `text-base font-medium` |
| `{typography.body}` | 14px | 400 | 1.50 | 0 | `text-sm` |
| `{typography.body-sm}` | 13px | 400 | 1.50 | 0 | `text-[13px]` |
| `{typography.caption}` | 12px | 400 | 1.40 | 0 | `text-xs` |
| `{typography.button}` | 13px | 500 | 1.20 | 0 | `text-[13px] font-medium` |
| `{typography.eyebrow}` | 12px | 500 | 1.30 | 0.04em | `text-xs font-medium tracking-wider uppercase` |
| `{typography.kpi-value}` | 28px | 600 | 1.10 | -0.015em | `text-3xl font-semibold tabular-nums` |
| `{typography.mono}` | 13px | 400 | 1.50 | 0 | `font-mono text-[13px]` |

### Principles

- **14px is the body baseline.** Domo apps run dense; 14px keeps tables and forms compact without sacrificing readability.
- **Weight 600 carries display.** Most modern sans-serifs at 600 read as confident without crossing into bold; verify that the customer brand font ships a 600 weight before locking it in.
- **Negative letter-spacing scales with size.** `-0.02em` at display sizes, `-0.005em` at title, `0` on body.
- **Tabular numerals are mandatory** in: KPI values, table number columns, currency, percentages, timestamps, durations. Apply `font-variant-numeric: tabular-nums` (Tailwind `tabular-nums`).
- **Sentence case for all UI strings**, including buttons. Uppercase is reserved for the eyebrow style and small status pill labels.
- **Eyebrow uses the only legitimate uppercase pattern** — 12px / 500 / `tracking-wider`. Never use uppercase for any other purpose.

## Layout

### Spacing System

- **Base unit**: 4px (Tailwind native).
- **Tokens**: `{spacing.0}` 0 · `{spacing.1}` 4px · `{spacing.2}` 8px · `{spacing.3}` 12px · `{spacing.4}` 16px · `{spacing.5}` 20px · `{spacing.6}` 24px · `{spacing.8}` 32px · `{spacing.10}` 40px · `{spacing.12}` 48px · `{spacing.16}` 64px · `{spacing.section}` 96px.
- Card interior padding: `{spacing.5}` 20px on KPI tiles, `{spacing.6}` 24px on standard cards, `{spacing.8}` 32px on hero tiles.
- Button padding: 8px vertical · 14px horizontal (default) · 10px / 18px (large) · 6px / 10px (compact).
- Form field padding: 8px vertical · 12px horizontal.
- Table cell padding: 12px vertical · 16px horizontal (default density) · 8px / 12px (compact density).

### Grid & Container

- Max content width: 1440px on dashboards, 1280px on focused workflows (settings, single-record views), 720px on reading-heavy surfaces.
- Page gutter: 32px desktop, 24px tablet, 16px mobile.
- KPI tile grid: 4-up at desktop-XL, 3-up at desktop, 2-up at tablet, 1-up at mobile.
- Standard card grid: 3-up at desktop, 2-up at tablet, 1-up at mobile.
- Sidebar width: 240px expanded, 56px collapsed (icon-only).
- Topbar height: 56px.

### Whitespace Philosophy

Domo apps are dense by design — customers come for data, not airy marketing. Density without crowding comes from:

1. Hairline borders separating regions, not large gaps.
2. Generous interior padding inside cards (24px), small gaps between cards (16px).
3. Section breaks of `{spacing.12}` 48px on dashboards, never `{spacing.section}` 96px (that's a marketing rhythm).

## Elevation & Depth

| Level | Treatment | Use |
|---|---|---|
| 0 (flat) | No shadow, no border | Body type, page headings, sidebar items |
| 1 (hairline lift) | `{colors.surface-1}` + 1px `{colors.hairline}` border | Default for cards, KPI tiles, chart cards, tables |
| 2 (soft float) | Level 1 + `var(--shadow-sm)` | Hovered cards, dropdown menus, popovers |
| 3 (deep float) | `{colors.surface-1}` + `var(--shadow-md)`, no border | Modals, dialogs, command palettes |
| 4 (overlay) | `{colors.surface-1}` + `var(--shadow-lg)` over a 50% `{colors.canvas}` scrim | Confirmation dialogs, destructive flows |

Shadows are tinted toward `{colors.brand}` at very low opacity, never pure black. This keeps depth feeling on-brand and prevents the "gray haze" of generic shadow stacks.

## Shapes

### Border Radius Scale

| Token | Value | Use |
|---|---|---|
| `{rounded.xs}` | 4px | Chips, status pills (when not pill-rounded), small badges |
| `{rounded.sm}` | 6px | Inline tags, table cell highlights |
| `{rounded.md}` | 8px | Buttons, form inputs, dropdown items |
| `{rounded.lg}` | 12px | Cards, KPI tiles, chart cards, modals |
| `{rounded.xl}` | 16px | Hero tiles, oversized illustration cards |
| `{rounded.pill}` | 9999px | Status pills, segmented controls, avatar groups |
| `{rounded.full}` | 9999px | Avatars, single-character icon buttons |

Square corners are not used. Pill-rounded CTAs are not used.

## Components

The 15 canonical FDE primitives. Each entry states the shadcn primitive it extends, the tokens it composes from, and what changes between light and dark themes.

### 1. Button — `button-primary`, `button-secondary`, `button-tertiary`, `button-destructive`, `button-ai`

Extends shadcn `<Button>`. Five variants, three sizes (`sm`, `default`, `lg`).

- **Primary**: `bg-ink text-canvas`, sentence case label, `font-medium`, `rounded-md`. Hover: `bg-ink/90`. Active: `scale-[0.98]`.
- **Secondary**: `bg-surface-1 text-ink border border-hairline`, sentence case, `rounded-md`. Hover: `bg-surface-2`.
- **Tertiary**: `bg-transparent text-ink`, sentence case, `rounded-md`. Hover: `bg-surface-2`.
- **Destructive**: `bg-danger text-white`, sentence case, `rounded-md`. Hover: `bg-danger/90`.
- **AI**: `bg-ai-accent text-white`, sentence case, `rounded-md`. Hover: `bg-ai-accent/90`. Reserved for AI-product CTAs only.

All variants share: `transition-colors duration-150 ease-out`, `focus-visible:ring-2 focus-visible:ring-brand focus-visible:ring-offset-2`, disabled `opacity-50 pointer-events-none`.

### 2. Input + Textarea + Select — `text-input`, `textarea`, `select`

Extends shadcn `<Input>`, `<Textarea>`, `<Select>`. Common shape:

- `bg-surface-1 text-ink placeholder:text-ink-subtle border border-hairline rounded-md`
- Padding 8px / 12px (input/select); 12px (textarea).
- Focus: `ring-2 ring-brand ring-offset-1 border-brand`.
- Error: `border-danger ring-danger` when paired with an error message below.
- Disabled: `bg-surface-2 text-ink-subtle cursor-not-allowed`.
- Always paired with a `<Label>` and optional `<HelperText>` (see Form Layout).

### 3. Card — `card`, `kpi-tile`, `chart-card`

Extends shadcn `<Card>`. Three variants:

- **Card** (default): `bg-surface-1 border border-hairline rounded-lg p-6`. Title `{typography.title}`, body `{typography.body}`.
- **KPI tile**: `bg-surface-1 border border-hairline rounded-lg p-5`. Eyebrow label `{typography.eyebrow text-ink-muted}` on top, value `{typography.kpi-value} tabular-nums` center, optional delta chip `{colors.success}` or `{colors.danger}` bottom.
- **Chart card**: `bg-surface-1 border border-hairline rounded-lg p-6`. Includes header row (title + filter button + period selector), 240–320px chart body, optional footer with legend.

Hover state on interactive cards: `hover:shadow-sm hover:border-hairline-soft transition-shadow duration-200 ease-out`. Static cards do not animate on hover.

### 4. Data Table — `data-table`

Extends shadcn `<Table>` with TanStack Table for sorting/pagination/selection.

- Header row: `bg-surface-2 text-ink-muted text-xs font-medium uppercase tracking-wider border-b border-hairline`.
- Body row: `border-b border-hairline-soft`. Hover: `bg-surface-2`. Selected: `bg-brand/5`.
- Cells: `py-3 px-4 text-sm`. Numeric columns get `text-right tabular-nums`.
- Sort caret: `lucide-react` `<ChevronUp />` / `<ChevronDown />` at 14px, `text-ink-subtle` default, `text-ink` when active.
- Pagination footer: 12px row, count left, page controls right.
- Empty state: full-bleed empty-state component (see #9), not an empty `<tbody>`.

### 5. Filter Bar — `filter-bar`, `filter-chip`

Horizontal strip of segmented filter chips above a table or chart card.

- Container: `flex flex-wrap gap-2 items-center py-3`.
- Chip default: `bg-surface-1 border border-hairline text-ink-muted rounded-pill px-3 py-1 text-sm`. Hover: `bg-surface-2`.
- Chip active: `bg-ink text-canvas border-ink`.
- "Clear filters" link: `text-brand text-sm underline-offset-2 hover:underline`, only visible when at least one chip is active.

### 6. Tabs — `tabs`

Extends shadcn `<Tabs>`. Two variants:

- **Underline tabs** (default for in-page navigation): tab text `text-ink-muted`, active `text-ink border-b-2 border-brand`. Inactive hover `text-ink`.
- **Segmented tabs** (for view-switching, e.g. Day / Week / Month): use shadcn `<ToggleGroup>` with the `single` type. Container `bg-surface-2 rounded-md p-1`. Each `<ToggleGroupItem>` `text-ink-muted px-3 py-1.5 rounded-sm`. Selected state `data-[state=on]:bg-surface-1 data-[state=on]:text-ink data-[state=on]:shadow-sm`.

### 7. Modal — `modal`, `dialog`

Extends shadcn `<Dialog>`. `bg-surface-1 rounded-lg border border-hairline shadow-md`, max-width 480px (default), 640px (form), 800px (data preview). Header `{typography.title}` + close button (`lucide-react` `<X />`). Footer right-aligned action buttons; primary CTA rightmost.

### 8. Toast — `toast`

Extends shadcn `<Sonner>` or `<Toast>`. `bg-surface-1 border border-hairline rounded-md shadow-md p-4`, max-width 400px, anchored bottom-right. Variants by left-edge accent color: success `border-l-4 border-l-success`, warning `border-l-4 border-l-warning`, error `border-l-4 border-l-danger`, info `border-l-4 border-l-info`. Auto-dismiss 5s; sticky if action button is present.

### 9. Empty State — `empty-state`

Extends shadcn `<Empty>`. Used when a table, list, or chart has no data — never a blank region.

- Composition: `<Empty>` → `<EmptyHeader>` (icon + title + description) → optional `<EmptyContent>` (CTA).
- Container: `flex flex-col items-center justify-center text-center py-12 px-6`.
- Icon: 40px `lucide-react` icon, `text-ink-subtle`, inside `<EmptyMedia variant="icon">`.
- Title: `<EmptyTitle>` styled `{typography.title}` `text-ink`.
- Description: `<EmptyDescription>` styled `{typography.body}` `text-ink-muted`, max-width 320px, 1–2 sentences.
- Optional CTA: `<button-secondary>` inside `<EmptyContent>`.

### 10. Loading State — `skeleton`, `spinner`

Two patterns. Default to skeleton; spinner only for indeterminate sub-second waits.

- **Skeleton**: extends shadcn `<Skeleton>`. `bg-surface-2 rounded-md animate-pulse`. Match the dimensions of the content it replaces. Stagger animations across a list with 100ms delays.
- **Spinner**: extends shadcn `<Spinner>` (or `lucide-react` `<Loader2 />` with `animate-spin` if Spinner isn't installed). Sized to context (16px inline, 20px in buttons, 24px standalone).

### 11. Tooltip + Popover — `tooltip`, `popover`

- **Tooltip**: extends shadcn `<Tooltip>`. `bg-ink text-canvas text-xs rounded-sm px-2 py-1`. 200ms open delay, instant close. Use only for icon-button labels and brief clarifications, never for primary content.
- **Popover**: extends shadcn `<Popover>`. `bg-surface-1 border border-hairline rounded-md shadow-md p-4`, max-width 320px. Use for richer disclosure (filters, mini-forms, info cards).

### 12. Dropdown Menu — `dropdown-menu`

Extends shadcn `<DropdownMenu>`. Trigger: any button; common as a kebab `<MoreHorizontal />` icon button. Menu: `bg-surface-1 border border-hairline rounded-md shadow-md p-1`. Item: `text-sm text-ink rounded-sm px-3 py-1.5 hover:bg-surface-2`. Destructive item: `text-danger`. Separator: `border-t border-hairline-soft my-1`.

### 13. Navigation — `sidebar`, `topbar`

- **Sidebar**: 240px wide, `bg-surface-2 border-r border-hairline`. Section header `{typography.eyebrow} text-ink-subtle px-4 pt-6 pb-2`. Nav item: `flex items-center gap-3 px-4 py-2 rounded-sm text-sm text-ink-muted hover:bg-surface-1 hover:text-ink`. Active: `bg-surface-1 text-ink border-l-2 border-brand`. Collapsed (56px): icon-only, tooltip on hover.
- **Topbar**: 56px tall, `bg-canvas border-b border-hairline px-6`. Left: app/workspace switcher. Center: optional global search (max-width 480px). Right: notifications bell, settings cog, user avatar — all 32px icon buttons with 8px gap.

### 14. Form Layout — `form-field`, `form-label`, `form-helper`, `form-error`

Extends shadcn `<Field>` and `<FieldGroup>`. Standard vertical form rhythm: labels above fields, helper text below, error replaces helper on validation failure.

- Composition: wrap related fields in a `<FieldGroup>`; each field is a `<Field>` containing `<FieldLabel>`, the input, and `<FieldDescription>` (or `<FieldError>`).
- Field container: `flex flex-col gap-1.5`.
- Label (`<FieldLabel>`): `{typography.body-sm} font-medium text-ink`. Required asterisk: `text-danger ml-0.5`.
- Helper (`<FieldDescription>`): `{typography.caption} text-ink-muted`.
- Error (`<FieldError>`): `{typography.caption} text-danger`. Field input gets `border-danger ring-danger`.
- Field-to-field gap (inside `<FieldGroup>`): `space-y-4`.
- Section gap: `space-y-8` with optional `{typography.title}` section header above. Use `<FieldSeparator>` between major sections within a single form.

### 15. Chart Wrapper — `chart-card` body

The `chart-card` (#3) contains the chart; this entry covers the chart body itself, regardless of charting library (recharts, visx, Domo's own).

- Chart canvas: 240px tall (KPI sparkline), 320px (standard), 480px (focused). Width fills container.
- Gridlines: 1px `{colors.hairline-soft}` horizontal, no vertical gridlines.
- Axis labels: `{typography.caption} text-ink-subtle tabular-nums`.
- Tooltip on hover: 8px `{colors.surface-1}` card with hairline border, shadow-sm, tabular-nums values, `{typography.caption}` for labels.
- Series colors: `{dataviz.series-1}` through `{dataviz.series-8}` in order. Single-series defaults to `{colors.brand}`.
- Empty: replaced by `empty-state` (#9), never a blank canvas.

## Polish Details

These are the small, mechanical rules that make Domo apps feel built, not assembled. Adapted from Jakub Krehel's "Details that make interfaces feel better." Each rule is enforceable — Claude should apply them by default.

### Optical alignment

- Icons paired with text are not pixel-centered; they are **optically centered**. For most `lucide-react` icons at 16px, this means a -1px translate-y. Use `relative top-px` or `-mt-px` per the icon family.
- Single-character buttons (e.g. close `X`) need a 1–2px nudge to read centered. Test in a real screenshot; eyeballing the bounding box lies.
- Numeric values in KPI tiles align to the **baseline of the value**, not the center of the tile. Eyebrow above, delta below — both baseline-anchored to the value.

### Hover and active feedback

- Every interactive surface has a hover state. Cards: `shadow-sm` lift. Buttons: `bg-{token}/90`. Rows: `bg-surface-2`.
- Buttons get a 2% scale-down on press: `active:scale-[0.98] transition-transform duration-75`. Apply to primary, secondary, tertiary, destructive, AI.
- Transitions are short and ease-out, never linear: `transition-colors duration-150 ease-out`. Color and shadow only — never `transition-all`.

### Tabular numerals

- Apply `tabular-nums` (Tailwind utility, maps to `font-variant-numeric: tabular-nums`) to every number that sits in a column or compares to another number across rows. KPI values, currency, percentages, durations, timestamps, table number columns.
- Most modern sans-serifs ship with tabular figures via the `tnum` OpenType feature; verify with the customer's brand font and fall back to a font with locked tabular figures if it doesn't.
- Counters and badges that show a single number do not need tabular-nums.

### Borders and shadows

- Borders carry structure; shadows carry float. Cards default to border-only (level 1). Add shadow only when the card lifts (hover, modal, popover).
- Shadows are tinted toward `{colors.brand}` at very low opacity (already encoded in `var(--shadow-sm/md/lg)`). Black shadows are forbidden.
- Stacked shadows beat single deep shadows. `var(--shadow-md)` is `0 4px 12px brand/0.06`, not `0 8px 24px black/0.15`.

### Image and avatar treatment

- Images and avatars get a 1px inset shadow to define their edge against the canvas: `box-shadow: inset 0 0 0 1px oklch(from currentColor l c h / 0.08)`. Prevents the "floating sticker" look on light backgrounds.
- Avatars are `{rounded.full}` and use 32px (compact), 40px (default), 64px (profile).
- Logo tiles use `{rounded.sm}` with the same 1px inset shadow.

### Font smoothing

- Apply `-webkit-font-smoothing: antialiased; -moz-osx-font-smoothing: grayscale;` globally on `body`. Most sans-serifs render heavy without it on macOS.
- Do not apply `font-smoothing` to dark text on dark backgrounds or vice versa — the difference becomes visible.

### Stagger animations

- Lists of 5+ items animate in with a 30–60ms stagger. Use `framer-motion` with `delay: i * 0.04` or CSS `animation-delay: calc(var(--i) * 40ms)`.
- Above 12 items, drop the stagger and fade the entire list together (300ms ease-out).
- Stagger is reserved for first-render. List re-orders animate via FLIP, not stagger.

### Focus rings

- Focus ring is `ring-2 ring-brand ring-offset-2`, with `ring-offset-color` matching the surface (`canvas` on body, `surface-1` inside cards).
- Use `focus-visible:` (keyboard focus only), not `focus:`. Mouse clicks should not draw the ring.

### Disabled states

- `opacity-50 pointer-events-none` on the disabled element, plus `aria-disabled="true"` for screen readers.
- Disabled buttons keep their original color but at 50% opacity. Do not gray them out — gray reads as a different color, not as disabled.

### Loading and empty are not edge cases

- Every list, table, or chart that fetches data has explicit `loading`, `empty`, and `error` states. None of these are afterthoughts; they are designed surfaces.
- Loading: skeleton, never a centered spinner over an empty container.
- Empty: full empty-state component (#9), never a blank region.
- Error: inline alert at the top of the container, optional retry CTA.

## UX Writing

Domo's house voice is the primary authority. Material Design provides tactical patterns when the house voice is silent. AP Style is the tiebreaker for grammar, dates, numerals, and capitalization.

### Voice (from `domo-ui-writing` skill)

- **Sentence case** for everything, buttons included. Uppercase is reserved for eyebrow labels and small status pills.
- **"People" not "users"** when referring to humans. Reserve "user" for technical contexts (user ID, user account).
- **Contractions on**: "you're," "we'll," "can't," "don't." More natural, fewer characters.
- **Positive framing**: "Save changes" not "Don't lose your work." "We couldn't connect" not "Connection failed."
- **No exclamations**: never. Even in success messages.
- **No Oxford comma**: "apples, oranges and pears" — Domo style, also AP style.
- **No jargon**: avoid "leverage," "synergize," "utilize." Say "use." Avoid "feature-rich" and "robust" anywhere a customer can see.

### Tactical patterns (from Material Design)

- **Button vocabulary** (use the same word for the same action across the entire app):
  - Confirm an action that completes a flow: `Done`
  - Save a form: `Save`
  - Apply filters or settings without closing: `Apply`
  - Cancel a flow: `Cancel`
  - Acknowledge an info dialog: `Got it`
  - Continue to next step: `Next`
  - Go back: `Back`
  - Delete with confirmation: `Delete` (destructive variant)
- **Errors describe the problem, then the fix.** "We couldn't reach the dataset. Check the connection settings and try again."
- **Empty states tell people what to do next.** "No reports yet. Create your first report to get started." Never just "No results."
- **Progressive disclosure**: hide advanced options until needed. A `Show advanced` link beats a wall of fields.
- **Truncate with ellipsis only when length is unpredictable** (filenames, dataset names, customer names). Always offer the full value on hover (tooltip) or click (popover).
- **Glyph and punctuation**:
  - Use the actual ellipsis character `…`, not three periods.
  - Use proper apostrophes `'` and quotes `" "`, not straight `'` `"`.
  - Use en-dash `–` for ranges (Q1–Q4), em-dash `—` sparingly for parenthetical breaks.
  - Use a non-breaking space before units: `12 GB` (not `12 GB` that wraps).

### AP Style fallbacks

- **Numerals**: spell out one through nine; use figures for 10 and above. Always use figures with units (`5 GB`, `3%`).
- **Percent**: use `%` in tables, KPIs, and any numeric context. Spell out "percent" in body prose only.
- **Dates**: `Mar. 14, 2026` or `Mar 14` in tight contexts. Months: spell out March through July; abbreviate the rest.
- **Times**: `9 a.m.` (lowercase, periods, space). Use 12-hour clock with `a.m./p.m.`, not 24-hour, unless the data demands it.
- **State abbreviations**: AP-style two-letter postal abbreviations in addresses (`Salt Lake City, Utah` in prose; `Salt Lake City, UT` in data).
- **Headlines and titles**: sentence case (Domo convention overrides AP's title case).
- **Job titles**: lowercase except when before a name (`product manager Jane Doe` becomes `Product Manager Jane Doe`).
- **Currency**: `$1,250.00` for USD; ISO codes for non-USD (`MYR 1,250.00`, `EUR 1,250.00`). Always include thousands separators.

### Glossary of canonical strings

Use the exact wording below in the exact context. Variations break recognition.

| Action | String |
|---|---|
| Primary save | `Save` |
| Cancel | `Cancel` |
| Confirm done | `Done` |
| Apply filters | `Apply` |
| Acknowledge info | `Got it` |
| Continue forward | `Next` |
| Go back | `Back` |
| Delete | `Delete` |
| Empty state header (no data) | `No [thing] yet` |
| Empty state header (no results) | `No matches found` |
| Loading | (no string — skeleton or spinner only) |
| Generic error | `Something went wrong. Try again or contact support.` |
| Connection error | `We couldn't reach [service]. Check the connection and try again.` |
| Validation, required field | `This field is required.` |
| Validation, invalid format | `Enter a valid [thing].` |

## Accessibility

WCAG 2.1 AA is the floor, not the goal. These defaults bake compliance into every primitive.

- **Color contrast**: every text/background pair in this file meets AA (4.5:1 for body, 3:1 for large text and UI components). The OKLCH-encoded tokens are tuned to maintain contrast in both themes; do not change lightness values without re-checking.
- **Focus**: every interactive element has a visible `focus-visible` ring (`ring-2 ring-brand ring-offset-2`). Never set `outline: none` without replacing the indicator.
- **Touch targets**: 40px minimum height on touch surfaces; 32px is permitted on desktop-only dense table actions.
- **Keyboard**: every interaction is keyboard-reachable. Modals trap focus; `Escape` closes; tabs navigate.
- **Screen readers**: every icon-only button has an `aria-label`. Every form field has a programmatically associated `<Label>`. Live regions (`aria-live="polite"`) announce toast notifications.
- **Motion**: respect `prefers-reduced-motion`. Disable transforms and stagger when the user opts out; keep color transitions (they aren't motion).
- **Color is never the only signal**: validation errors get an icon and an error message, not just a red border. Status pills get an icon or text, not just a dot.

## Do's and Don'ts

### Do

- Use the canonical primitive names from `## Components` when generating code (e.g. `kpi-tile`, `chart-card`, `data-table`).
- Lift cards from canvas with hairline borders first, shadows second.
- Apply `tabular-nums` to every numeric column, KPI value, and timestamp.
- Use sentence case everywhere, buttons included.
- Use the glossary's exact wording for save, cancel, done, apply.
- Compose colors via Tailwind utilities (`bg-surface-1`, `text-ink-muted`), never raw hex.
- Define every component's loading, empty, and error states alongside its happy path.
- Test every text/background pair for AA contrast before shipping.

### Don't

The Don'ts are organized by where the drift comes from. They hold regardless of which customer brand the app is themed to.

#### Visual anti-patterns (the AI defaults)

These are what AI generates by reflex when nothing pushed back. None of them are right for a customer app, regardless of which customer.

- Don't ship purple gradients — especially the `linear-gradient(135deg, #667eea 0%, #764ba2 100%)` indigo-to-violet that AI reaches for first.
- Don't use mesh gradients or "aurora" blob backgrounds — those swirly multi-color blurry shapes behind hero sections. Trend-flavored, ages fast.
- Don't use glassmorphism — frosted-blur translucent panels with `backdrop-filter`. Works for one card on a hero; ruinous as a system.
- Don't use neon glow on dark surfaces (`box-shadow: 0 0 20px <bright>`). Cyberpunk theater.
- Don't default to Inter, Roboto, or Poppins as the brand font. They're the AI fallbacks. Use the customer's actual brand font; the system font stack is a better placeholder than these defaults.
- Don't use generic palette blues (`#3B82F6`, `#2563EB`, `#1E40AF`) as primary. Tailwind's `blue-500` is the AI default for "this is a button." Always reference `{colors.brand}`.
- Don't ship 3D floating objects, isometric illustrations, or retro-wave grids. None survive a year.
- Don't use heavy bevel, emboss, or skeuomorphic shadows. Reads as 2008.

#### The lazy defaults

These are what an underbaked design ships when nobody pushed back on the easy choices.

- Don't use Tailwind's built-in palette (`bg-gray-100`, `text-blue-600`).
- Don't use pure black for text (`text-black`) or pure white for canvas (`bg-white`). Use `text-ink` and `bg-canvas`. The ink token is intentionally near-black with a slight warmth; the canvas token is intentionally not pure white.
- Don't use pure white text in dark theme either. The dark-theme `ink` token is intentionally not `#fff`.
- Don't use black drop shadows at `rgba(0,0,0,0.15)` or higher. Shadows are tinted toward `{colors.brand}` at low opacity (already encoded in `var(--shadow-sm/md/lg)`).
- Don't `rounded-full` every button. Pill is reserved for status pills and segmented controls.
- Don't use square corners (`rounded-none`) on cards. Use the radius scale.
- Don't use 96px section breaks on app pages — that's marketing rhythm. App pages live at 32–48px breaks.
- Don't use ALL CAPS outside the eyebrow style and small status pills.
- Don't add `transition-all`. Be explicit about which properties animate.
- Don't use linear easing. Default to `ease-out` for entrances, `ease-in-out` for transitions.
- Don't put `cursor: pointer` on non-interactive elements — it suggests clickability that doesn't exist.
- Don't ship a blank state for an empty list or chart. Use the `empty-state` component.
- Don't copy-paste shadcn component source files into the repo. Install via `shadcn add` so `components.json` stays in sync with what's actually installed.

#### Data display

- Don't center numbers in numeric table columns. Numeric columns are right-aligned with `tabular-nums`.
- Don't use pie charts with 6+ slices. Convert to a horizontal bar.
- Don't use donut charts where a single number tells the same story.
- Don't ship 3D charts. Ever. They distort the data.
- Don't ship charts without axis labels. "Trust me, this line is going up" isn't a chart.
- Don't use stacked bars when totals matter. Use grouped bars or surface the totals explicitly.
- Don't auto-scale Y-axes without a zero baseline unless deviation from a baseline is the explicit story. Auto-scaling makes tiny changes look huge.
- Don't put two charts side-by-side with different y-axis scales. The eye compares them anyway and gets fooled.
- Don't promote dataviz palette colors to chrome. They live inside chart bodies only.

#### Copy

- Don't use Title Case in body copy or buttons. Sentence case applies everywhere except eyebrows and status pills.
- Don't put exclamation marks in product copy.
- Don't use "Oops!" "Whoops!" "Yikes!" in error messages. Customers don't want kid-energy when something just broke.
- Don't use emoji as functional icons in serious flows (billing, security, errors, transactions). Decorative emoji in a friendly internal tool is fine — context-dependent.
- Don't write link text like "Click here" or "Read more." Link text describes its destination.
- Don't use 24-hour time when the customer's locale uses 12-hour. Default to 12-hour for US/Canada.
- Don't ship Lorem ipsum to any state that can render to production — empty states, skeletons, and loading placeholders all need real copy from day one.
- Don't ship a bare "Something went wrong" without a follow-up sentence describing the fix.
- Don't use "user" when "people" works.
- Don't use the AI accent (`{colors.ai-accent}`) on non-AI surfaces.

#### Interaction

- Don't ship hover states that only change color. Add a second affordance — shadow, border weight, scale, or underline.
- Don't put primary content inside tooltips. Tooltips are clarifications, not essential reading.
- Don't ship auto-advancing carousels. They pull focus, distract, and rarely respect reduced-motion.
- Don't trigger a modal from inside a modal. Use a multi-step modal or a side sheet.
- Don't put a spinner over content that's partly loaded. Use skeletons for the unfetched parts; let what's loaded stay visible.

#### Accessibility

- Don't `outline: none` without replacing the focus indicator with a `focus-visible` ring.
- Don't ship animation without a `prefers-reduced-motion` guard.
- Don't make a tooltip the only way a screen reader hears a button's label. Icon buttons need an `aria-label`.
- Don't use color as the only signal. Validation errors get an icon and a message; status pills get an icon or text, not just a dot.
- Don't ship text/background pairs below AA contrast (4.5:1 body, 3:1 UI components and large text).

## Responsive Behavior

### Breakpoints (Tailwind defaults)

| Name | Width | Key Changes |
|---|---|---|
| Desktop-XL (`xl`) | 1280px+ | Default desktop layout, KPI 4-up, sidebar expanded |
| Desktop (`lg`) | 1024–1279px | KPI 3-up, sidebar expanded |
| Tablet (`md`) | 768–1023px | KPI 2-up, sidebar collapses to icon-only |
| Mobile (`sm`) | 640–767px | KPI 1-up, sidebar hides behind hamburger, topbar height 56px maintained |
| Mobile (default) | < 640px | Single column, dense table becomes card list |

### Touch targets

- 40px minimum on all touch-reachable interactive elements.
- Increase padding, do not increase font size, to reach 40px.

### Collapsing strategy

- **Sidebar**: 240px → 56px icon-only at `md`, hamburger overlay below `sm`.
- **KPI grid**: 4-up → 3-up → 2-up → 1-up across breakpoints.
- **Data table**: at `sm` and below, transform into a card list — one card per row, label/value pairs stacked.
- **Filter bar**: chips wrap; "Clear filters" stays right-aligned.
- **Chart card**: chart canvas reduces from 320px to 240px tall at `sm`.

### Image behavior

- Charts maintain aspect ratio; never distort.
- Logos and avatars maintain fixed pixel sizes; do not scale with viewport.

## Customization

The five tokens below are the per-engagement levers FDEs can swap. Everything else stays canonical.

| Token | What it controls | Customer override frequency |
|---|---|---|
| `{colors.brand}` | Primary CTA, active nav, focus ring, single-series chart color | Every engagement |
| `{colors.brand-fg}` | Text on `{colors.brand}` backgrounds | Every engagement |
| `--font-sans` | Display and body family | Occasional (when customer mandates a brand font) |
| `{dataviz.series-1..8}` | Categorical chart colors | Occasional (when customer has a locked dataviz palette) |
| Logo asset | Topbar wordmark | Every engagement |

To customize:

1. Update the five tokens in `globals.css` (light + dark blocks).
2. Drop the customer logo at `/public/logo.svg` (light) and `/public/logo-dark.svg` (dark).
3. Re-run `npx @google/design.md lint DESIGN.md` to confirm structural integrity.
4. Diff the rendered theme against AA contrast targets; adjust lightness if `{colors.brand}` fails contrast on `{colors.surface-1}`.

Do not edit anything outside this list per engagement. Cross-customer drift is the failure mode this file exists to prevent.

### Locking the customer font is the first task on every engagement

The repo's demo files use Inter as a visual placeholder so the demos render coherently before any engagement starts. Inter is **not** the recommended brand font — it's the AI default this file is designed to push back against (see "Visual anti-patterns" under Don'ts).

On day one of a new engagement:

1. Get the customer's brand font name and licensing terms. Confirm the foundry, the variants licensed (display, body, mono), and whether web embedding is in scope.
2. Update `--font-sans` and `--font-mono` in `globals.css`. If the customer doesn't have a brand font, use the system stack documented in the Typography section — not Inter.
3. Verify the chosen font ships a 600 weight (used for display) and tabular figures via the `tnum` OpenType feature. If either is missing, escalate before locking.
4. Re-render every demo page and check that line-heights and tracking from the Typography Hierarchy table still read correctly with the new font. Negative letter-spacing values are tuned for geometric sans-serifs; serif or humanist fonts may need the values relaxed.

Demos that ship with Inter past the first week of an engagement are a sign the customer brand font got blocked somewhere. Surface it and unblock.

## Iteration Guide

1. Focus on ONE component at a time and reference it by its `components:` token name.
2. When introducing a new section, decide first whether it sits on `{colors.canvas}` (default) or lifts onto a `{colors.surface-1}` card.
3. Default body to `{typography.body}` 14px / weight 400.
4. Run `npx @google/design.md lint DESIGN.md` after edits.
5. Add new variants as separate component entries; do not overload an existing variant.
6. Treat `{colors.ai-accent}` as a product accent, not a decoration.
7. Verify the component's loading, empty, and error states alongside the happy path.
8. Verify AA contrast on both light and dark before merging.

## Known Gaps

- **Dataviz palette values** are not locked. Categorical series-1 should equal `{colors.brand}`; the remaining seven need to be selected for legibility on both themes and for color-blind safety.
- **AI accent** (`{colors.ai-accent}`) is defined but unwired. If Domo standardizes an AI-product accent, populate the token and add a "When to use AI accent" subsection under Components.
- **Marketing surfaces** (Domo.com pages, customer-facing landing) are out of scope for this file. A separate `MARKETING-DESIGN.md` should cover marketing typography (likely heavier display weights), section rhythms (96px), and illustration guidance.
- **Email templates** are out of scope. Email constraints (table layouts, restricted CSS) merit a separate file.
- **Iconography**: the file defaults to `lucide-react`. If Domo has a proprietary icon library, swap the import pattern but keep the size and stroke-weight conventions.
- **Internationalization**: string lengths in non-English locales can break the dense layouts. Pad cell widths defensively when shipping i18n surfaces.
