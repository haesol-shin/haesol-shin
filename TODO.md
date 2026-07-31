# TODO — Personal Branding Follow-ups

> Tracks work deferred during the 2026-07-31 SSoT setup (`resume.yaml` + `generate.py`). Update `resume.yaml` first for any fact change, then come back here to check things off.

## Open decisions

- [ ] **Open-source contributions on homepage** — Gajae Code (gjc) contribution is in `resume.yaml` (`open_source_contributions`, tagged `channels: [resume, homepage]`) but nothing renders it yet. Options discussed: (1) new custom section on `/cv` (requires editing `_layouts/cv.liquid` + `_includes/resume/*.liquid` — al-folio template change), (2) fold into the `work` array (fast, but blurs "core dev" vs "one-off contribution"), (3) leave homepage out, keep GitHub README only. Decide direction, then extend `generate.py`'s `build_resume_json()` accordingly.
- [ ] **University-internal awards (7-8 entries)** — currently excluded from `resume.yaml` awards entirely (README/resume/homepage all skip them). Decide: individually listed (channels: [resume] only) vs. summarized as one line ("Multiple intramural awards, 2024-2026") vs. left out permanently.
- [ ] **LG Aimers 8th Cohort status** — "participant" vs "completed" not yet confirmed. `resume.yaml`'s `training` list is currently empty pending this.

## Manual sync required

- [ ] **`HaesolShin_Resume.docx`** — not auto-generated (Word formatting). Re-check against `resume.yaml` after any SSoT change and update by hand.

## Cleanup (not urgent)

- [ ] **`haesol-shin/.omc/`** — old agent session artifacts (drafts, plans, research) from the pre-`resume.yaml` branding attempt. Superseded. Decide: delete, or keep as historical reference (currently untracked, not committed).
- [ ] **`haesol-shin/CLAUDE.md`** — still references the old `haesol.research@gmail.com` contact email in its guidelines. Update or fold into this repo's own docs.

## Later (explicitly deferred, larger scope)

- [ ] **al-folio redesign** — current site reads as "template-y," not custom/professional enough. Reference points discussed: junho.io (dynamic/personal-brand feel) vs. shanggdlk.github.io (clean/academic-static feel). Direction leaned toward staying on Jekyll/al-folio and doing a full CSS/layout pass rather than a from-scratch rebuild — not yet started.
- [ ] **Blog** — user wants profile (research + dev) and blog (also research + dev) as separate content types. Leaning toward keeping them integrated in one al-folio site (it already has `_pages/blog.md`) rather than splitting into a separate site/repo, but not finalized.
