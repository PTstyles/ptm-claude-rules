# AI Engine Tab Skill

Adds an "AI Engine" explainer page to any Domo custom app. The page walks through the app's full data and AI pipeline with an interactive diagram, two AI integration cards, a prompt inspector, one interactive AI demo section (either a prompt builder or a live chat — chosen upfront), an AI/ML opportunities section, and a tech stack footer.

**Design authority:** Read `/Users/paul.mccusker/DomoApps/AI-Engine/DESIGN.md` before writing any UI code. Apply its principles: sentence case everywhere (except eyebrow labels and status pills), hairline borders for structure, `text-sm` (14px) body baseline, `font-semibold` for headings, `tabular-nums` on all numeric values, no heavy shadows, PRIMARY color used sparingly.

**Reference apps (use these as ground truth):**
- Cornerstone CU (latest, uses prompt builder): `/Users/paul.mccusker/DomoApps/cornerstone-cu-intelligence/src/views/AIEngineView.tsx`
- Innovage Clinical AI (uses live chat): `/Users/paul.mccusker/DomoApps/innovage-clinical-ai/src/views/AIEngineView.tsx`
- Midstates POS: `/Users/paul.mccusker/DomoApps/midstates-pos-app/src/views/AIArchitectureView.tsx`

---

## Step 0 — Ask which interactive AI demo to include

**Before writing any code, ask the user:**

> "For the interactive AI section, do you want a **prompt builder** (structured fields the user fills in — chips for topic, audience, format — and the app assembles the prompt) or a **live chat** (free-form conversation with the AI)? The prompt builder is better for showing how prompting works to a non-technical audience; the live chat is better when the app already has a conversational AI feature to demonstrate."

Default to **prompt builder** if the user doesn't have a preference or if the audience is non-technical. Use **live chat** only when explicitly requested or when the app already has a chat feature that should be demonstrated.

---

## What gets built

| Section | Description |
|---|---|
| Pipeline diagram | Horizontal row of 6–9 clickable `StageNode` components with `FlowArrow` connectors. Clicking a stage reveals a two-column detail panel: description + bullets (left), dark code block (right). Pre-select the most interesting/unique stage as default. |
| AI integration cards | Two cards side-by-side. Each has: icon + label + badge (trigger type), description, "Prompt contains" / "Output shape" mini-grid, numbered execution flow (5–6 steps). Always exactly two — if only one AI type exists, split into batch-prep and real-time-call. |
| Prompt inspector | Tabbed toggle (2–3 tabs). Each tab: explanation panel (left 2/5) + dark code block with macOS traffic-light dots (right 3/5). Show real prompts from the app. |
| **Interactive AI demo** (choose one) | **Prompt builder** — structured chip controls (topic, audience, format) + optional free-text field + collapsible prompt preview + Generate button + response area. See Phase 4 below. **OR** **Live chat** — sidebar with 3 suggested prompts + scrollable chat area + textarea input. See Phase 4 below. |
| AI/ML opportunities | Traditional ML opportunities specific to the app's use case and datasets. See Phase 6 below. |
| Tech stack footer | 7-column dot grid of technologies actually used in the app. |

---

## Phase 1 — Read the target app

Read these files before writing anything:

```
manifest.json                  # datasets, collections, packages, workflows mapped
src/App.tsx (or main entry)    # how views are structured, what data is loaded, nav pattern
src/lib/queries.ts             # Query SDK usage, aliases, field lists
src/hooks/use*.ts              # Data fetching hooks, AI hooks
src/components/ChatPanel.tsx   # If present: how AI is called, system prompt shape
src/components/*Panel*.tsx     # Any panel that shows AI content
vite.config.ts                 # Build format (IIFE vs ESM — matters for publishing)
index.html                     # Script tag pattern
```

**What to extract from each file:**

| File | Extract |
|---|---|
| manifest.json | Dataset aliases + IDs, collection names + schemas, package/workflow names |
| App.tsx | Nav pattern (inline header vs separate Header component), existing view type/enum, color scheme (primary hex), data loaded at mount |
| queries.ts / hooks | Query SDK vs REST fetch, which aliases, which fields selected |
| ChatPanel.tsx | AI call pattern (AIClient vs direct fetch), system prompt construction, response extraction path |
| AI-showing components | Pre-generated content (from datasets) vs on-demand AI calls |
| vite.config.ts | Whether IIFE format is already configured |

---

## Phase 2 — Map the pipeline

Every app maps to a **data source → transport → compute → AI → output** spine. Identify:

### Data sources (left end of pipeline)
- Snowflake / external DB → flag as "Pre-generated AI" candidate (Cortex likely)
- Domo datasets only → data comes from Magic ETL or connector
- AppDB → document store, stateful writes
- Code Engine packages → server-side logic
- Workflows → orchestration / multi-step triggers

### Transport layer
- `@domoinc/query` Query SDK → note which aliases and fields
- `/data/v1/alias` REST fetch → note the fields query string
- `/sql/execute` → note (and warn this ignores page filters)
- `domo.get()` / `domo.post()` → low-level Domo JS API
- `@domoinc/toolkit` AppDBClient → document read/write

### AI integrations — identify each one
| Pattern | What it is |
|---|---|
| `SNOWFLAKE.CORTEX.COMPLETE()` in SQL | Snowflake Cortex — batch, pre-generated in Snowflake |
| Dataset named `*AISummaries*` / `*AIInsights*` / `*CortexOutput*` | Pre-generated AI content loaded at fetch time |
| `AIClient.generate_text()` from `@domoinc/toolkit` | Domo AI Service Layer — real-time, uses Domo session auth. **Call signature: `generate_text(input: string)` — positional string, NOT a named object. Passing `{ systemPrompt, userPrompt, model }` causes 400 Bad Request. Combine system + user text into one string before calling.** |
| `fetch('/domo/ai/v1/text/generation', ...)` | Same Domo AI Service Layer — direct HTTP version |
| `domo.post('/domo/ai/v1/...')` | Same Domo AI service, via domo.js |
| Code Engine package call | Server-side logic — may call external LLM or Domo AI |
| Workflow trigger | May chain AI steps |

### Other notable pieces (call out in the diagram)
- AppDB collections → note the collection name and schema
- Code Engine packages → note package name and what it returns
- Workflows → note trigger and what it orchestrates
- External APIs → note domain and purpose

### Build the stage list (6–9 stages)

The pipeline always reads left-to-right: **source → transport → compute/AI → output**. Typical shapes:

**App with Snowflake + Cortex + chat:**
`Snowflake → Cortex AI → Domo Datasets → Query SDK → Context Builder → Domo AI Service → AppDB → React UI`

**App with Domo datasets + direct AI chat:**
`Domo Dataset(s) → Data API → Analytics Engine → Prompt Builder → Domo AI Service → Response Parser → UI Components`

**App with Code Engine:**
`Domo Dataset → Query SDK → Code Engine → Prompt Builder → Domo AI Service → UI`

**App with AppDB + AI:**
`AppDB Collection → Toolkit AppDBClient → Context Builder → Domo AI Service → UI`

Rules:
- Each stage needs: `id`, `label` (2–3 words), `sublabel` (tech name or endpoint), `color` (hex), `what` (1 sentence), `bullets` (4–6 items), optional `code` (real code from the app, not made up)
- Code blocks must use **real content from the app** — actual dataset IDs, actual field names, actual prompt templates, actual API paths
- The `Prompt Builder` / `Context Builder` stage always gets a code block showing the real system prompt or prompt template from the app
- The `Domo AI Service` stage always gets the request/response shape

---

## Phase 3 — Build AIEngineView.tsx

Create at `src/views/AIEngineView.tsx`.

**Install lucide-react if not present:**
```bash
npm install lucide-react
```

### Component structure (follow exactly)

```tsx
import React, { useState, useRef } from 'react';
import {
  Database, Globe, Cpu, FileText, Sparkles, Layers, Layout,
  Brain, Snowflake, BookOpen, MessageSquare, Send, Code2,
  type LucideIcon,
} from 'lucide-react';
import { AIClient } from '@domoinc/toolkit';  // only if app uses toolkit AI

// ─── Constants ────────────────────────────────────────────────────────────────
// Match the app's primary color. Examples:
//   Innovage:  const NAVY = '#1e3a5f';
//   Midstates: const RED  = '#C8102E';
//   Cornerstone: const TEAL = '#0d9488';
const PRIMARY = '<APP_PRIMARY_COLOR>';

// ─── Types ────────────────────────────────────────────────────────────────────
interface Stage { id, label, sublabel, Icon, color, what, bullets, code? }
interface ChatMessage { role: 'user'|'assistant', content: string }  // if chat exists

// ─── STAGES array ─────────────────────────────────────────────────────────────
// Built from Phase 2 analysis. 6–9 entries.
const STAGES: Stage[] = [ ... ];

// ─── AI_TYPES array ───────────────────────────────────────────────────────────
// Always exactly 2 entries.
const AI_TYPES = [ ... ];

// ─── Sub-components (copy verbatim, change PRIMARY references only) ────────────
function StageNode({ stage, isSelected, onClick }) { ... }
function FlowArrow({ color }) { ... }

// ─── Main export ──────────────────────────────────────────────────────────────
export default function AIEngineView() {
  const [selectedStage, setSelectedStage] = useState<string | null>('<most_interesting_stage_id>');
  const [promptTab, setPromptTab] = useState<0 | 1>(0);
  // Chat state only if app has AI chat:
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [chatInput, setChatInput] = useState('');
  const [chatLoading, setChatLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  ...

  return (
    <div className="flex-1 overflow-y-auto bg-slate-50">   {/* or app's bg color */}
      <div className="p-6 max-w-[1400px] mx-auto space-y-6">
        {/* 1. Page header */}
        {/* 2. Pipeline diagram card */}
        {/* 3. Two AI type cards (grid-cols-2) */}
        {/* 4. Prompt inspector card */}
        {/* 5. Live chat card (if app has chat) */}
        {/* 6. Tech stack footer */}
      </div>
    </div>
  );
}
```

### StageNode sub-component (copy verbatim)

```tsx
function StageNode({ stage, isSelected, onClick }: {
  stage: Stage; isSelected: boolean; onClick: () => void;
}) {
  return (
    <button
      onClick={onClick}
      className="flex flex-col items-center gap-2 group focus:outline-none"
      style={{ minWidth: 90 }}
    >
      <div
        className="w-14 h-14 rounded-2xl flex items-center justify-center transition-all duration-200 relative"
        style={{
          background: isSelected ? stage.color : `${stage.color}18`,
          border: `2px solid ${isSelected ? stage.color : `${stage.color}40`}`,
          boxShadow: isSelected ? `0 0 18px ${stage.color}50` : 'none',
          transform: isSelected ? 'scale(1.1)' : 'scale(1)',
        }}
      >
        <stage.Icon size={22} style={{ color: isSelected ? '#fff' : stage.color }} />
        {isSelected && (
          <div
            className="absolute -top-1 -right-1 w-3 h-3 rounded-full border-2 border-slate-50"
            style={{ background: stage.color }}
          />
        )}
      </div>
      <div className="text-center">
        <div className="text-[11px] font-semibold leading-tight"
          style={{ color: isSelected ? stage.color : '#334155' }}>
          {stage.label}
        </div>
        <div className="text-[9px] mt-0.5 text-slate-400">{stage.sublabel}</div>
      </div>
    </button>
  );
}
```

**For dark-theme apps** (like Midstates with ThemeContext): replace hardcoded `'#334155'` with `c.textPrimary` and `'text-slate-400'` class with `style={{ color: c.textMuted }}`. Pass `c` as a prop.

### FlowArrow sub-component (copy verbatim)

```tsx
function FlowArrow({ color }: { color: string }) {
  return (
    <div className="flex items-center self-start mt-5 px-1 flex-shrink-0">
      <div className="h-0.5 w-5"
        style={{ background: `linear-gradient(90deg, ${color}50, ${color}20)` }} />
      <div style={{
        width: 0, height: 0,
        borderTop: '4px solid transparent',
        borderBottom: '4px solid transparent',
        borderLeft: `6px solid ${color}60`
      }} />
    </div>
  );
}
```

### Pipeline diagram card (copy structure, fill with STAGES data)

```tsx
<div className="rounded-2xl p-6 bg-white border border-slate-200 shadow-sm overflow-x-auto">
  <p className="text-[10px] uppercase tracking-widest font-semibold mb-5 text-slate-400">
    Data &amp; AI Pipeline — click any stage
  </p>

  {/* Stage row */}
  <div className="flex items-start gap-1 flex-wrap">
    {STAGES.map((stage, i) => (
      <React.Fragment key={stage.id}>
        <StageNode
          stage={stage}
          isSelected={selectedStage === stage.id}
          onClick={() => setSelectedStage(selectedStage === stage.id ? null : stage.id)}
        />
        {i < STAGES.length - 1 && <FlowArrow color={STAGES[i + 1].color} />}
      </React.Fragment>
    ))}
  </div>

  {/* Stage detail panel */}
  {selected && (
    <div className="mt-6 rounded-xl p-5 grid grid-cols-1 lg:grid-cols-2 gap-5"
      style={{ background: `${selected.color}0c`, border: `1px solid ${selected.color}28` }}>

      {/* Left: description + bullets */}
      <div className="space-y-3">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0"
            style={{ background: `${selected.color}22` }}>
            <selected.Icon size={16} style={{ color: selected.color }} />
          </div>
          <div>
            <p className="text-sm font-bold" style={{ color: selected.color }}>{selected.label}</p>
            <p className="text-[10px] text-slate-400">{selected.sublabel}</p>
          </div>
        </div>
        <p className="text-xs leading-relaxed text-slate-600">{selected.what}</p>
        <ul className="space-y-1.5">
          {selected.bullets.map((b, i) => (
            <li key={i} className="flex items-start gap-2 text-xs text-slate-600">
              <span className="w-1.5 h-1.5 rounded-full mt-1.5 flex-shrink-0"
                style={{ background: selected.color }} />
              {b}
            </li>
          ))}
        </ul>
      </div>

      {/* Right: code block (only when selected.code exists) */}
      {selected.code && (
        <div className="rounded-lg p-4 font-mono text-[10px] leading-relaxed overflow-x-auto
                        bg-slate-900 border border-slate-700">
          <div className="flex items-center gap-1.5 mb-3">
            <Code2 size={11} style={{ color: selected.color }} />
            <span className="text-[9px] uppercase tracking-wider" style={{ color: selected.color }}>
              {/* Label varies by stage: 'Example prompt', 'API shape', 'SQL', etc. */}
              {getCodeLabel(selected.id)}
            </span>
          </div>
          <pre className="whitespace-pre-wrap text-slate-300">{selected.code}</pre>
        </div>
      )}
    </div>
  )}
</div>
```

### AI type cards (copy structure, fill AI_TYPES data)

```tsx
<div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
  {AI_TYPES.map(at => (
    <div key={at.label}
      className="rounded-2xl p-5 space-y-4 bg-white border border-slate-200 shadow-sm">

      {/* Header: icon + label + badge + "available in" tags */}
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0"
            style={{ background: `${at.badgeColor}15` }}>
            <at.Icon size={18} style={{ color: at.badgeColor }} />
          </div>
          <div>
            <p className="text-sm font-bold text-slate-800">{at.label}</p>
            <span className="text-[9px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full"
              style={{ background: `${at.badgeColor}15`, color: at.badgeColor }}>
              {at.badge}
            </span>
          </div>
        </div>
        <div className="flex flex-col gap-1 items-end">
          {at.where.map(w => (
            <span key={w} className="text-[9px] px-1.5 py-0.5 rounded bg-slate-100 text-slate-500">
              {w}
            </span>
          ))}
        </div>
      </div>

      <p className="text-xs leading-relaxed text-slate-600">{at.description}</p>

      {/* Prompt/output mini-grid */}
      <div className="grid grid-cols-2 gap-3">
        <div className="rounded-lg p-3 bg-slate-50">
          <p className="text-[9px] uppercase tracking-wider font-semibold mb-1.5 text-slate-400">
            Prompt contains
          </p>
          <p className="text-xs text-slate-600">{at.promptShape}</p>
        </div>
        <div className="rounded-lg p-3 bg-slate-50">
          <p className="text-[9px] uppercase tracking-wider font-semibold mb-1.5 text-slate-400">
            Output shape
          </p>
          <p className="text-xs text-slate-600">{at.outputShape}</p>
        </div>
      </div>

      {/* Numbered execution flow */}
      <div>
        <p className="text-[9px] uppercase tracking-wider font-semibold mb-2.5 text-slate-400">
          Execution flow
        </p>
        <div className="space-y-2">
          {at.steps.map((step, i) => (
            <div key={i} className="flex items-start gap-2">
              <div className="flex-shrink-0 w-5 h-5 rounded-full flex items-center justify-center
                              text-[9px] font-bold mt-0.5 text-white"
                style={{ background: at.badgeColor }}>
                {i + 1}
              </div>
              <div className="flex-1">
                <span className="text-xs font-semibold text-slate-700">{step.label}</span>
                <span className="text-[10px] ml-1.5 text-slate-400">{step.desc}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  ))}
</div>
```

### Prompt inspector card (copy structure)

```tsx
<div className="rounded-2xl overflow-hidden bg-white border border-slate-200 shadow-sm">
  {/* Toolbar */}
  <div className="flex items-center justify-between px-5 py-4 border-b border-slate-200">
    <div className="flex items-center gap-2.5">
      <Code2 size={15} style={{ color: PRIMARY }} />
      <span className="text-sm font-semibold text-slate-800">Prompt Inspector</span>
      <span className="text-[9px] font-semibold px-2 py-0.5 rounded-full uppercase tracking-wider"
        style={{ background: `${PRIMARY}12`, color: PRIMARY }}>
        Live examples
      </span>
    </div>
    {/* Tab toggle */}
    <div className="flex rounded-lg overflow-hidden border border-slate-200">
      {PROMPT_TAB_LABELS.map((label, i) => (
        <button key={label} onClick={() => setPromptTab(i as 0 | 1)}
          className="px-4 py-1.5 text-xs font-medium transition-all"
          style={{
            background: promptTab === i ? PRIMARY : 'transparent',
            color: promptTab === i ? '#fff' : '#64748b',
          }}>
          {label}
        </button>
      ))}
    </div>
  </div>

  {/* Body: 2/5 explanation + 3/5 code */}
  <div className="grid grid-cols-1 lg:grid-cols-5 divide-y lg:divide-y-0 lg:divide-x divide-slate-200">
    {/* Explanation panel */}
    <div className="lg:col-span-2 p-5 space-y-4">
      <div>
        <p className="text-xs font-bold mb-1 text-slate-800">What this prompt achieves</p>
        <p className="text-xs leading-relaxed text-slate-600">
          {PROMPT_EXPLANATIONS[promptTab].description}
        </p>
      </div>
      {/* Key-value metadata rows */}
      <div className="space-y-2">
        {PROMPT_EXPLANATIONS[promptTab].meta.map(({ key, val }) => (
          <div key={key} className="flex gap-2 text-xs">
            <span className="font-semibold flex-shrink-0 w-24 text-slate-400">{key}</span>
            <span className="text-slate-600">{val}</span>
          </div>
        ))}
      </div>
      {/* "Why this service" callout box */}
      <div className="rounded-xl p-3 mt-2"
        style={{ background: `${PRIMARY}08`, border: `1px solid ${PRIMARY}20` }}>
        <div className="flex items-center gap-1.5 mb-1.5">
          <Sparkles size={11} style={{ color: PRIMARY }} />
          <span className="text-[10px] font-bold uppercase tracking-wider" style={{ color: PRIMARY }}>
            {promptTab === 0 ? 'Pre-generated (batch)' : 'Domo AI Service Layer'}
          </span>
        </div>
        <p className="text-[11px] leading-relaxed text-slate-600">
          {PROMPT_EXPLANATIONS[promptTab].callout}
        </p>
      </div>
    </div>

    {/* Code panel */}
    <div className="lg:col-span-3 p-5">
      {/* macOS traffic-light dots + filename */}
      <div className="flex items-center gap-2 mb-3">
        <div className="flex gap-1.5">
          <div className="w-2.5 h-2.5 rounded-full bg-red-400" />
          <div className="w-2.5 h-2.5 rounded-full bg-yellow-400" />
          <div className="w-2.5 h-2.5 rounded-full bg-green-400" />
        </div>
        <span className="text-[10px] text-slate-400">{PROMPT_TAB_FILENAMES[promptTab]}</span>
      </div>
      <pre className="text-[11px] leading-relaxed font-mono whitespace-pre-wrap overflow-x-auto
                      rounded-lg p-4 border text-slate-300"
        style={{ background: '#0f172a', borderColor: '#1e293b', maxHeight: '380px', overflowY: 'auto' }}>
        {PROMPT_CODE_EXAMPLES[promptTab]}
      </pre>
    </div>
  </div>
</div>
```

### Interactive AI demo — choose one based on Step 0 answer

#### Option A: Prompt builder (default)

Use the Cornerstone CU reference implementation as the template:
`/Users/paul.mccusker/DomoApps/cornerstone-cu-intelligence/src/views/AIEngineView.tsx`

Key pieces to copy and adapt:
- `AGENT_TOPICS`, `AGENT_AUDIENCES`, `AGENT_FORMATS` constants — replace with app-specific options
- `agentPrompt` useMemo — adapt the template text to match the app's domain and persona
- `sendAgent()` function — adapt the system prompt and userPrompt to match the topic/format/audience pattern

> **`AIClient.generate_text()` call signature warning:** The first argument must be a plain string — `generate_text(inputString)`. Passing a named object like `{ systemPrompt, userPrompt, model }` causes a `400 Bad Request`. Combine everything into one string before calling. Response body is at `response?.body?.choices?.[0]?.output` (toolkit wraps in `.body`).
> ```ts
> const input = `${agentPrompt}\n\nGenerate the ${agentFormat.toLowerCase()} about ${agentTopic.toLowerCase()}.`;
> const response = await AIClient.generate_text(input);
> const body = response?.body ?? response?.data ?? response;
> const answer = body?.choices?.[0]?.output ?? body?.output ?? 'Unable to generate a response.';
> ```
- The JSX section with: header bar (PRIMARY background), 3-column chip controls, extra context input, collapsible prompt preview, Generate button, response area

**Adapting to a new app:**
1. Replace `AGENT_TOPICS` with 4 topics relevant to this app's data (e.g. for a fuel management app: Fuel consumption · Inventory levels · Driver behavior · Cost analysis)
2. Replace `AGENT_AUDIENCES` with roles relevant to this app's users (e.g. Fleet manager · Operations director · Finance team · Field supervisor)
3. Keep `AGENT_FORMATS` the same — Short summary · Bullet points · Action plan · One sentence are universal
4. Adapt the `agentPrompt` useMemo template to reference the app's actual name and context
5. Replace "Conexus CU" and "4 Texas credit unions" references with the app's context

#### Option B: Live chat (only when user explicitly requests it)

```tsx
<div className="rounded-2xl overflow-hidden bg-white border border-slate-200 shadow-sm">
  {/* Header bar — uses PRIMARY color as background */}
  <div className="flex items-center gap-3 px-5 py-4 border-b border-slate-200"
    style={{ background: PRIMARY }}>
    <div className="flex h-7 w-7 items-center justify-center rounded-full bg-white/20
                    text-xs font-bold text-white">AI</div>
    <div>
      <p className="text-sm font-semibold text-white">{CHAT_TITLE} — Live Demo</p>
      <p className="text-[10px] text-white/60">
        Powered by Domo AI Service Layer · AIClient.generate_text()
      </p>
    </div>
    <div className="ml-auto flex items-center gap-1.5">
      <div className="w-1.5 h-1.5 rounded-full bg-green-400 animate-pulse" />
      <span className="text-[10px] text-white/60">Connected</span>
    </div>
  </div>

  <div className="grid grid-cols-1 lg:grid-cols-4">
    {/* Suggested prompts sidebar */}
    <div className="lg:col-span-1 p-4 border-b lg:border-b-0 lg:border-r border-slate-200 bg-slate-50">
      <p className="text-[9px] uppercase tracking-wider font-semibold text-slate-400 mb-3">
        Try a query
      </p>
      <div className="space-y-2">
        {SUGGESTED_PROMPTS.map(p => (
          <button key={p} onClick={() => sendChat(p)} disabled={chatLoading}
            className="w-full text-left text-xs px-3 py-2.5 rounded-lg border border-slate-200
                       bg-white text-slate-600 hover:border-blue-300 hover:text-blue-700
                       transition-colors disabled:opacity-50">
            {p}
          </button>
        ))}
      </div>
      {/* Context note box */}
      <div className="mt-4 rounded-lg p-3 text-[10px] leading-relaxed"
        style={{ background: `${PRIMARY}08`, color: '#475569' }}>
        <strong className="block mb-1" style={{ color: PRIMARY }}>Demo context</strong>
        {CHAT_CONTEXT_NOTE}
      </div>
    </div>

    {/* Chat area */}
    <div className="lg:col-span-3 flex flex-col" style={{ height: 340 }}>
      <div className="flex-1 overflow-y-auto p-4 space-y-3 bg-slate-50">
        {chatMessages.length === 0 && (
          <p className="text-center text-xs text-slate-400 pt-6">
            Select a suggested prompt or type a question — this calls the live Domo AI Service.
          </p>
        )}
        {chatMessages.map((m, i) => (
          <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[80%] rounded-2xl px-3 py-2.5 text-sm leading-relaxed ${
              m.role === 'user'
                ? 'text-white rounded-br-sm'
                : 'bg-white border border-slate-200 text-slate-700 rounded-bl-sm shadow-sm'
            }`} style={m.role === 'user' ? { background: PRIMARY } : {}}>
              {m.content}
            </div>
          </div>
        ))}
        {chatLoading && (
          <div className="flex justify-start">
            <div className="rounded-2xl rounded-bl-sm border border-slate-200 bg-white px-4 py-2.5 shadow-sm">
              <div className="flex gap-1">
                {[0, 1, 2].map(i => (
                  <span key={i} className="h-1.5 w-1.5 rounded-full bg-slate-300 animate-bounce"
                    style={{ animationDelay: `${i * 0.15}s` }} />
                ))}
              </div>
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>
      {/* Input bar */}
      <div className="border-t border-slate-200 bg-white px-3 py-2.5 flex items-end gap-2">
        <textarea value={chatInput} onChange={e => setChatInput(e.target.value)}
          onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendChat(chatInput); }}}
          placeholder="Ask a question…" rows={1}
          className="flex-1 resize-none rounded-lg border border-slate-200 px-3 py-2 text-sm
                     outline-none focus:border-blue-400 leading-tight" />
        <button onClick={() => sendChat(chatInput)} disabled={!chatInput.trim() || chatLoading}
          className="rounded-lg px-3 py-2 text-sm text-white transition-opacity
                     disabled:opacity-40 hover:opacity-90 flex items-center gap-1.5"
          style={{ background: PRIMARY }}>
          <Send size={13} />
        </button>
      </div>
    </div>
  </div>
</div>
```

**sendChat function (adapt system prompt to the app):**

```tsx
async function sendChat(text: string) {
  if (!text.trim() || chatLoading) return;
  setChatMessages(m => [...m, { role: 'user', content: text }]);
  setChatInput('');
  setChatLoading(true);
  setTimeout(() => bottomRef.current?.scrollIntoView({ behavior: 'smooth' }), 50);

  try {
    // Build a COMPACT demo context — not the full app context, just enough to answer
    // the suggested prompts accurately. Real data names, not placeholders.
    const systemPrompt = `You are a [ROLE] for [APP_NAME]. [BRIEF_CONTEXT_2_SENTENCES].
Respond concisely and [TONE — clinically / analytically / etc.].`;

    const response = await AIClient.generate_text(`${systemPrompt}\n\nUser: ${text}`);
    const body = response?.body ?? response?.data ?? response;  // toolkit wraps in .body
    const answer: string = body?.choices?.[0]?.output ?? body?.output ?? 'Unable to generate a response.';
    setChatMessages(m => [...m, { role: 'assistant', content: answer }]);
  } catch {
    setChatMessages(m => [...m, { role: 'assistant', content: 'Sorry, the AI service is unavailable right now.' }]);
  } finally {
    setChatLoading(false);
    setTimeout(() => bottomRef.current?.scrollIntoView({ behavior: 'smooth' }), 50);
  }
}
```

**If the app uses direct fetch instead of AIClient:**
```tsx
const res = await fetch('/domo/ai/v1/text/generation', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ input: `${systemPrompt}\n\nUser: ${text}` }),
});
const data = await res.json();
const answer = data?.choices?.[0]?.output ?? 'Unable to generate a response.';
```

### Tech stack footer (copy, fill with real technologies)

```tsx
<div className="rounded-2xl p-5 grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-7 gap-4
                bg-white border border-slate-200 shadow-sm">
  {[
    { label: 'React + Vite',  sub: 'App framework',    color: '#61dafb' },
    { label: 'TypeScript',    sub: 'Type safety',      color: '#3b82f6' },
    { label: 'Tailwind CSS',  sub: 'Styling',          color: '#06b6d4' },
    // Add/replace based on actual tech in the app:
    { label: 'Snowflake',     sub: 'Data warehouse',   color: '#29b5e8' },  // if Snowflake
    { label: 'Cortex AI',     sub: 'Batch LLM',        color: '#8b5cf6' },  // if Cortex
    { label: 'Domo AI Layer', sub: 'Real-time chat',   color: PRIMARY    },  // always
    { label: 'AppDB',         sub: 'Document store',   color: '#ef4444' },  // if AppDB
    { label: 'Code Engine',   sub: 'Server logic',     color: '#f59e0b' },  // if Code Engine
    { label: 'Recharts',      sub: 'Visualization',    color: '#8b5cf6' },  // if Recharts
  ].map(({ label, sub, color }) => (
    <div key={label} className="flex flex-col items-center text-center gap-1.5">
      <div className="w-2 h-2 rounded-full" style={{ background: color }} />
      <span className="text-xs font-semibold text-slate-700">{label}</span>
      <span className="text-[10px] text-slate-400">{sub}</span>
    </div>
  ))}
</div>
```

---

## Phase 4 — Build AI/ML opportunities section

Add a section below the live chat card that highlights traditional ML opportunities specific to this app's use case and datasets. This section is **always included** — it shows what is possible beyond the generative AI already in the app.

### Step 1 — Identify the ML opportunity space from the data

Based on what datasets the app has, map each field group to the ML category most likely to benefit from it:

| Data available | ML categories to consider |
|---|---|
| Labeled historical outcomes (defaults, churn, conversions) | Supervised learning (classification, regression) |
| Transaction / event sequences over time | Time series & forecasting |
| Customer profile fields (demographics, products owned, behavior) | Unsupervised segmentation, recommendation systems |
| Free text fields (notes, reviews, descriptions) | NLP sentiment, classification |
| Images, documents, PDFs | Computer vision / OCR |
| Duplicate or fuzzy-match problems | Unsupervised entity resolution |

### Step 2 — Write 4–6 specific opportunities

Each opportunity must be **grounded in the actual app data** — real field names, real dataset aliases, real business outcomes. Never write generic examples. Structure:

```ts
interface MLItem {
  name: string;          // "Loan default prediction" — sentence case, specific
  description: string;   // 2–3 sentences: what model, what data features, why it matters for this app
  signals: string[];     // actual FIELD_NAMES from the app's datasets
  dataset: string;       // alias name(s), e.g. "loanPortfolio" or "memberSummary + householdSummary"
  value: string;         // one sentence business impact
}
```

**Categories to cover (pick the 4 most relevant for the app):**

- **Supervised learning** — classification or regression on labeled outcomes
  - Examples: default/churn prediction, fraud scoring, demand forecasting, diagnosis
  - Fields to look for: any historical outcome column, boolean flags, score columns

- **Unsupervised learning** — clustering, anomaly detection, entity resolution
  - Examples: behavioral micro-segmentation, duplicate detection, outlier flagging
  - Fields to look for: demographics, behavioral metrics, multiple overlapping ID columns

- **Time series & forecasting** — ARIMA, LSTM, Prophet on timestamped data
  - Examples: demand forecasting, delinquency early warning, inventory prediction
  - Fields to look for: date/month columns, running totals, trend metrics

- **Recommendation systems** — collaborative filtering, matrix factorization
  - Examples: product cross-sell, content recommendations, next-best-action
  - Fields to look for: binary ownership flags, purchase history, interaction events

- **NLP (classical)** — sentiment, classification, entity extraction
  - Examples: ticket routing, review sentiment, document classification
  - Fields to look for: text/notes/description columns, free-text feedback

### Step 3 — Component structure

```tsx
const ML_OPPORTUNITIES: MLCategory[] = [
  {
    category: 'Supervised learning',  // sentence case for display; the pill uses uppercase via CSS
    categoryColor: '#3b82f6',
    items: [
      {
        name: 'Loan default prediction',
        description: '...',           // specific to this app's data and use case
        signals: ['ACTUAL_FIELD_NAME', 'ANOTHER_FIELD'],   // real field names
        dataset: 'loanPortfolio',
        value: 'One sentence business impact.',
      },
      // ...
    ],
  },
  // 3 more categories...
];
```

**Section layout (copy from Cornerstone CU reference):**
- Section eyebrow: `text-[10px] font-medium tracking-wider uppercase text-slate-400`
- Section title: `text-sm font-semibold text-slate-800`
- Category divider: colored `h-px` lines flanking a pill badge, colored by category
- Cards: `rounded-xl bg-white border border-slate-200 shadow-sm p-5`
  - Name: `text-sm font-semibold text-slate-800`
  - Dataset badge: `font-mono text-[9px] bg-slate-100 text-slate-500`
  - Description: `text-xs leading-relaxed text-slate-600`
  - "Data signals" eyebrow + `font-mono` colored pills for each field name
  - Value callout: tinted box with `TrendingUp` icon in category color
- 2-column grid for categories with 2 items; single-item categories get one card + filler placeholder

---

## Phase 5 — Wire navigation in App.tsx

> Previously Phase 4 — renumbered to make room for the ML opportunities phase above.

### Pattern A: App has a separate Header component (midstates pattern)

The Header component receives `activeView` + `onViewChange` props and renders tabs. Add the AI Engine tab to the existing tab array inside Header.tsx:

```tsx
// In Header.tsx — find the TABS / nav items array and append:
{ id: 'ai-engine', label: 'AI Engine', Icon: Cpu }

// In App.tsx — add to the view render block:
<div style={{ display: activeView === 'ai-engine' ? 'block' : 'none' }}>
  <AIEngineView />
</div>
```

### Pattern B: App has inline header in App.tsx (innovage pattern)

Add state, import icons, add tab nav inside the header JSX, mount the view with display:none:

```tsx
// 1. Add to imports
import AIEngineView from './views/AIEngineView';
import { Sparkles, <ExistingViewIcon> } from 'lucide-react';

// 2. Add state
const [activeView, setActiveView] = useState<AppView>('main');  // or whatever existing default

// 3. Add tab array inside the component (before return)
const TABS = [
  { id: 'main' as AppView,       label: 'Dashboard',  Icon: LayoutDashboard },
  { id: 'ai-engine' as AppView,  label: 'AI Engine',  Icon: Sparkles },
];

// 4. Inside the header element — add nav
<nav className="flex gap-1">
  {TABS.map(tab => (
    <button key={tab.id} onClick={() => setActiveView(tab.id)}
      className="flex items-center gap-1.5 px-4 py-1.5 rounded-lg text-sm font-medium transition-all"
      style={{
        background: activeView === tab.id ? 'rgba(255,255,255,0.2)' : 'transparent',
        color: activeView === tab.id ? '#fff' : 'rgba(191,219,254,0.8)',
      }}>
      <tab.Icon size={14} />
      {tab.label}
    </button>
  ))}
</nav>

// 5. Wrap existing main content:
<div className="flex flex-1 overflow-hidden"
  style={{ display: activeView === 'main' ? 'flex' : 'none' }}>
  {/* existing content */}
</div>

// 6. Mount AI Engine view:
<div className="flex flex-1 overflow-hidden"
  style={{ display: activeView === 'ai-engine' ? 'flex' : 'none' }}>
  <AIEngineView />
</div>
```

**Critical:** Always use `display: none` / `display: flex` toggling — never `&&` or ternary unmounting. This preserves any AI state (chat history, generated insights) when the user switches tabs.

**Also critical:** Any toolbar elements that are dashboard-specific (search bars, filter dropdowns, stats bars) should be conditionally hidden when on the AI Engine tab:
```tsx
style={{ display: activeView === 'dashboard' ? '' : 'none' }}
// or
{activeView === 'dashboard' && <div>stats bar</div>}
```

---

## Phase 6 — Build and publish

### Check build format

modocorp.domo.com requires IIFE format. domo-paul-mccusker.domo.com works with default ESM.

**If publishing to modocorp and vite.config.ts is NOT already IIFE:**

```ts
// vite.config.ts
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [
    react(),
    {
      name: 'no-module-type',
      transformIndexHtml: {
        order: 'post',
        handler: (html) => html
          .replace(/ type="module"/g, '')
          .replace(/ crossorigin/g, '')
          .replace(/<script src=/g, '<script defer src='),
      },
    },
  ],
  base: './',
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    rollupOptions: {
      output: {
        format: 'iife',
        entryFileNames: 'assets/[name]-[hash].js',
      },
    },
  },
});
```

**Verify the built index.html has `defer` and no `type="module"`:**
```bash
cat dist/index.html
```

### Publish steps

```bash
# Build
npm run build

# Login (full hostname, not shortname)
domo login -i modocorp.domo.com -t <token>
# or
domo login -i domo-paul-mccusker.domo.com -t <token>

# Publish from dist (NEVER from project root)
cd dist && domo publish
```

Tokens are in `/Users/paul.mccusker/DomoApps/.domo-credentials` and in the memory file `reference_domo_credentials.md`.

---

## Stage color palette

Use distinct colors per stage — no two adjacent stages should share the same hue:

| Stage type | Recommended color |
|---|---|
| External data warehouse (Snowflake, Redshift) | `#29b5e8` (Snowflake blue) |
| Batch AI / pre-generation (Cortex, Magic ETL AI) | `#8b5cf6` (violet) |
| Domo Datasets / connector | `#3b82f6` (blue) |
| Data API / REST fetch | `#8b5cf6` (purple) |
| Query SDK | `#f59e0b` (amber) |
| Analytics Engine / client compute | `#f59e0b` (amber) |
| Prompt Builder / Context Builder | `#10b981` (green) |
| Domo AI Service Layer | App primary color (for emphasis) |
| Code Engine | `#f97316` (orange) |
| AppDB | `#ef4444` (red) |
| Response Parser | `#06b6d4` (cyan) |
| UI Components | `#64748b` (slate) |

---

## AI type card data shape

```ts
const AI_TYPES = [
  {
    label: string,           // "Pre-generated Clinical AI" / "Batch Cortex Analysis"
    badge: string,           // "Snowflake Cortex · Batch nightly" / "Auto-loads on open"
    badgeColor: string,      // hex — green (#10b981) for auto, red/primary for on-demand
    Icon: LucideIcon,        // Snowflake / Clock for batch; MessageSquare / Sparkles for real-time
    description: string,     // 2–3 sentences explaining when/why it fires and what it produces
    promptShape: string,     // 1 sentence: what data goes INTO the prompt
    outputShape: string,     // 1 sentence: what comes OUT (shape, structure, length)
    where: string[],         // UI locations where this AI type is visible (e.g. "Patient Drawer header")
    steps: { label: string; desc: string }[],  // 5–6 numbered execution steps
  },
  // second entry...
];
```

**Common "two AI types" splits:**
- Batch (Cortex/ETL, fires nightly) + Real-time (chat, fires on user message)
- Auto-loads on view open (daily briefing) + On-demand click (generate analysis)
- Pre-loaded from dataset + Interactive query (typed question)
- Code Engine (server-side with LLM) + Domo AI Service (in-app chat)

---

## Common stage code block labels

Pick the right label for the `code` block header based on the stage:

| Stage id | Code label |
|---|---|
| `snowflake` / external DB | `'Schema'` |
| `cortex` / batch AI | `'Cortex SQL'` |
| `datasets` / manifest | `'manifest.json'` |
| `querysdk` / dataapi | `'Query pattern'` |
| `context` / `prompt` | `'Example prompt'` |
| `ailayer` / `ai` | `'API shape'` |
| `appdb` | `'AppDB usage'` |
| `codeengine` | `'Contract / invocation'` |
| `parser` | `'Parse logic'` |

---

## Checklist before marking done

- [ ] **Step 0 completed** — asked user whether to use prompt builder or live chat; decision recorded
- [ ] `npm install lucide-react` if not already in package.json
- [ ] Read `DESIGN.md` before writing UI — apply sentence case, hairline borders, `text-sm` body baseline, `tabular-nums` on metrics, no heavy shadows
- [ ] All stage `code` blocks contain **real content from the app** (real IDs, real field names, real prompt text) — never invented placeholders
- [ ] `selectedStage` initial value set to the most interesting/unique stage (usually the AI or prompt stage)
- [ ] Two AI type cards cover all AI integrations in the app — nothing omitted
- [ ] Prompt inspector shows the **actual** prompts used in the app, copied from ChatPanel or wherever they're built
- [ ] **Prompt builder** (if chosen): `AGENT_TOPICS`, `AGENT_AUDIENCES`, `AGENT_FORMATS` are app-specific; `agentPrompt` template references the app's name and domain; collapsible preview updates live
- [ ] **Live chat** (if chosen): system prompt in `sendChat` gives enough real context to answer the 3 suggested prompts; use `display:none` so chat history persists on tab switch
- [ ] AI/ML opportunities section included — 4–6 items grounded in real field names and dataset aliases from this app
- [ ] Each ML opportunity card has: name, description (2–3 sentences, specific to this app), `signals` (real field names), `dataset` alias, and value callout
- [ ] Navigation uses `display: none` toggling (not conditional rendering)
- [ ] Any header-level UI only shown on the dashboard tab is hidden on the AI Engine tab
- [ ] Build succeeds with no TypeScript errors
- [ ] If modocorp target: vite.config.ts uses IIFE format, `dist/index.html` has `defer` and no `type="module"`
- [ ] Published from `cd dist && domo publish` (never from project root)
