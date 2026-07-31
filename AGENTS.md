# AGENTS.md

This file provides guidance to AI coding agents when working with code in this repository.

## Repository Purpose

This is a GitHub profile repository. `README.md` is the profile page rendered on the `haesol-shin` GitHub account. `resume.yaml` is the single source of truth (SSoT) for career facts; `generate.py` regenerates README.md's fact blocks and the homepage repo's `cv.yml`/`resume.json`/`about.md` from it. There are no build steps or tests beyond running `generate.py`.

## README Structure

The README uses raw HTML (not Markdown headings) for layout control and includes:

- **Banner** — `capsule-render` waving gradient via an `<img>` tag
- **Wakatime badge** — links to the user's Wakatime profile
- **Typing SVG** — animated text via `readme-typing-svg.demolab.com`
- **Sections** — "What I'm Up To", "Projects Overview", "Papers & Research", "Awards", "Favorite Tools" (badges), "Contact Me"

Badge images use the `shields.io` `for-the-badge` style. GIF assets are referenced from the `img/` directory in this repo.

## Editing Guidelines

- Facts (career, awards, projects, education) are edited in `resume.yaml` only, then synced by running `python generate.py`. Do not hand-edit the marker blocks in README.md (`<!-- BEGIN:... --> ... <!-- END:... -->`) — they get overwritten.
- Preserve the raw-HTML structure outside the markers; mixing Markdown headings into the existing layout will break alignment.
- Badge URLs follow the pattern `https://img.shields.io/badge/<label>-<color>?style=for-the-badge&logo=<name>&logoColor=white`.
- The contact email is `haesol.me@gmail.com`.

Behavioral guidelines to reduce common LLM coding mistakes. Merge with project-specific instructions as needed.

**Tradeoff:** These guidelines bias toward caution over speed. For trivial tasks, use judgment.

## 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them - don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

## 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

## 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it - don't delete it.

When your changes create orphans:
- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: Every changed line should trace directly to the user's request.

## 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:
- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:
```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.

---

**These guidelines are working if:** fewer unnecessary changes in diffs, fewer rewrites due to overcomplication, and clarifying questions come before implementation rather than after mistakes.
