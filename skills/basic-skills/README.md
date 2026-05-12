---
name: basic-skills
description: Minimal demo skills that show the simplest end-to-end Domo workflows. Designed to be read in under 2 minutes and used live in demos.
---

# Basic Skills

A small, demo-friendly collection of skills that show the **simplest possible** version of common Domo workflows. Use these when you want to demonstrate Claude Code skills without the cognitive overhead of the full production playbooks under `apps/` or `orchestrator-skills/`.

## What's in here

| Skill | What it does |
| --- | --- |
| [`card-create-publish/`](card-create-publish/SKILL.md) | Scaffold a minimal Domo custom app (one card) and publish it with `domo publish`. |

## When to use these vs. the production skills

| Use this folder when... | Use `apps/` or `orchestrator-skills/` when... |
| --- | --- |
| Demoing Claude Code skills to a customer | Building a real production app |
| You want a working result in under 5 minutes | The app needs datasets, AppDB, AI, or Code Engine |
| You're teaching the skill system itself | You need themes, layout, hero metrics, navigation |

## Design rules for skills in this folder

1. **Under 100 lines of skill instructions.** If it's longer, it doesn't belong here.
2. **No optional phases.** Linear, top-to-bottom steps only.
3. **One artifact, one outcome.** Each skill produces a single, runnable thing.
4. **Inherit platform rules.** All skills here still follow `rules/core-custom-apps-rule.md` (client-side only, no SSR, etc.).
