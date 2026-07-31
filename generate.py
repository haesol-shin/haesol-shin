#!/usr/bin/env python3
"""
generate.py — Regenerate README.md, cv.yml, and resume.json from resume.yaml.

resume.yaml is the single source of truth (SSoT). This script never reads
from or writes to any other file as a source of facts.

Homepage directory resolution order:
    1. --homepage-dir CLI argument
    2. HAESOL_HOMEPAGE_DIR environment variable
    One of the two is required — there is no implicit path guessing.

Usage:
    python generate.py --homepage-dir PATH [--dry-run]
    HAESOL_HOMEPAGE_DIR=PATH python generate.py [--dry-run]

Outputs:
    haesol-shin/README.md                                (marker blocks only)
    haesol-shin.github.io/_data/cv.yml                    (fully regenerated)
    haesol-shin.github.io/assets/json/resume.json         (fully regenerated)
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

import yaml

SCRIPT_DIR = Path(__file__).resolve().parent
RESUME_YAML = SCRIPT_DIR / "resume.yaml"
README_PATH = SCRIPT_DIR / "README.md"

MARKER_RE_TEMPLATE = r"(<!--\s*BEGIN:{name}\s*-->)(.*?)(<!--\s*END:{name}\s*-->)"


def resolve_homepage_dir(cli_arg):
    """Resolution order: --homepage-dir > HAESOL_HOMEPAGE_DIR env var.
    Returns (path, source_label) for logging, or (None, None) if neither is set."""
    if cli_arg is not None:
        return cli_arg, "--homepage-dir"
    env_val = os.environ.get("HAESOL_HOMEPAGE_DIR")
    if env_val:
        return Path(env_val), "HAESOL_HOMEPAGE_DIR env var"
    return None, None


def load_resume():
    with open(RESUME_YAML, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def _award_sort_key(award):
    """Sort by full date descending; entries without an explicit `date` sort
    to the end of their year (most conservative — no false precision)."""
    date = award.get("date") or f"{award['year']}-12"
    return date


def in_channel(entry, channel):
    """Return True if `entry` should be shown in `channel`.
    Default (no `channels` key) is to show everywhere."""
    channels = entry.get("channels")
    if not channels:
        return True
    return channel in channels


# ----------------------------------------------------------------------------
# README.md — marker-block replacement only. Everything outside markers
# (banner, typing SVG, badges, GIFs) is left untouched.
# ----------------------------------------------------------------------------

def render_readme_up_to(data):
    lines = ['<ul>']
    for exp in data.get("research_experience", []):
        if not in_channel(exp, "readme"):
            continue
        lab_url = "https://sites.google.com/view/cnudolab/home"
        lines.append(
            f'  <li>Researching {exp.get("topic", "")} at '
            f'<a href="{lab_url}">DO Lab</a> ({exp.get("advisor", "")}).</li>'
        )
    for exp in data.get("open_source_experience", []):
        if not in_channel(exp, "readme"):
            continue
        if exp["id"] == "exp-thisisthepy":
            lines.append(
                '  <li>Core developer of '
                '<a href="https://github.com/thisisthepy/PyREPL">PyREPL</a> and '
                '<a href="https://github.com/thisisthepy/toolchain">toolchain</a> at the '
                '<a href="https://github.com/thisisthepy">Thisisthepy Group</a>.</li>'
            )
    edu = data.get("education", [{}])[0]
    lines.append(
        f'  <li>Pursuing a Bachelor\'s Degree in AI at {edu.get("institution", "")} '
        f'(expected {_format_month_year(edu.get("end", ""))}).</li>'
    )
    lines.append('</ul>')
    return "\n".join(lines)


def render_readme_projects(data):
    lines = ['<ul>']
    projects = [p for p in data.get("projects", []) if in_channel(p, "readme")]
    projects.sort(key=lambda p: p.get("importance", 999))
    for p in projects:
        lines.append(
            f'  <li><a href="{p["url"]}">{p["name"]}</a>: {p["description"].rstrip(".")}</li>'
        )
    lines.append('</ul>')
    return "\n".join(lines)


def render_readme_research(data):
    lines = ['<ul>']
    for exp in data.get("research_experience", []):
        if not in_channel(exp, "readme"):
            continue
        lines.append(f'  <li>Conducting research on {exp.get("topic", "")} at DO Lab.</li>')
    lines.append('</ul>')
    return "\n".join(lines)


def render_readme_awards(data):
    lines = ['<ul>']
    awards = [a for a in data.get("awards", []) if in_channel(a, "readme")]
    awards.sort(key=_award_sort_key, reverse=True)
    for award in awards:
        lines.append(f'  <li>{award["event"]} — {award["title"]} ({award["org"]})</li>')
    lines.append('</ul>')
    return "\n".join(lines)


def render_readme_contact(data):
    email = data["basics"]["email"]
    linkedin = data["basics"]["links"]["linkedin"]
    return (
        '<div align="left">\n'
        f'  <a href="mailto:{email}">\n'
        '    <img src="https://img.shields.io/badge/gmail-EA4335?style=for-the-badge&amp;logo=gmail&amp;logoColor=white" alt="Gmail">\n'
        '  </a>\n'
        f'  <a href="{linkedin}" target="_blank">\n'
        '    <img src="https://img.shields.io/badge/linkedin-0077B5?style=for-the-badge&amp;logo=linkedin&amp;logoColor=white" alt="LinkedIn">\n'
        '  </a>\n'
        '</div>'
    )


README_SECTIONS = {
    "up-to": render_readme_up_to,
    "projects": render_readme_projects,
    "research": render_readme_research,
    "awards": render_readme_awards,
    "contact": render_readme_contact,
}


def update_readme(data, dry_run=False):
    text = README_PATH.read_text(encoding="utf-8")
    original_text = text
    updated_sections = []
    missing_sections = []

    for name, render_fn in README_SECTIONS.items():
        pattern = re.compile(MARKER_RE_TEMPLATE.format(name=re.escape(name)), re.DOTALL)
        match = pattern.search(text)
        if not match:
            missing_sections.append(name)
            continue
        new_body = "\n" + render_fn(data) + "\n"
        text = pattern.sub(lambda m, b=new_body: m.group(1) + b + m.group(3), text, count=1)
        updated_sections.append(name)

    for name in missing_sections:
        print(f"  WARNING: marker pair for '{name}' not found in README.md — skipped.")

    if text != original_text and not dry_run:
        README_PATH.write_text(text, encoding="utf-8")

    return updated_sections, missing_sections


# ----------------------------------------------------------------------------
# about.md (homepage) — marker-block replacement only. The prose intro above
# the marker is hand-written and left untouched.
# ----------------------------------------------------------------------------

def render_about_facts(data):
    lines = []

    lines.append("### Research Interests")
    lines.append("")
    for interest in data["basics"].get("research_interests", []):
        lines.append(f"- {interest}")
    lines.append("")

    lines.append("### Education")
    lines.append("")
    for edu in data.get("education", []):
        if not in_channel(edu, "homepage"):
            continue
        status = " (expected)" if edu.get("status") == "expected" else ""
        lines.append(f"- **{edu['degree'].replace('B.S. —', 'B.S. in').strip()}**, {edu['institution']}  ")
        lines.append(f"  {_date_range(edu['start'], edu['end'])}{status}")
    lines.append("")

    lines.append("### Research Experience")
    lines.append("")
    for exp in data.get("research_experience", []):
        if not in_channel(exp, "homepage"):
            continue
        lines.append(f"- **{exp['role']}**, DO Lab  ")
        lines.append(f"  {_date_range(exp['start'], exp['end'])}")

    return "\n".join(lines)


def update_about_md(data, homepage_dir, dry_run=False):
    about_path = homepage_dir / "_pages" / "about.md"
    if not about_path.exists():
        return False, "about.md not found"

    text = about_path.read_text(encoding="utf-8")
    pattern = re.compile(MARKER_RE_TEMPLATE.format(name="facts"), re.DOTALL)
    match = pattern.search(text)
    if not match:
        return False, "marker pair for 'facts' not found in about.md"

    new_body = "\n" + render_about_facts(data) + "\n"
    new_text = pattern.sub(lambda m: m.group(1) + new_body + m.group(3), text, count=1)

    if new_text != text and not dry_run:
        about_path.write_text(new_text, encoding="utf-8")

    return True, None


# ----------------------------------------------------------------------------
# cv.yml — al-folio time_table format, fully regenerated (safe: this file is
# generated-only, never hand-edited).
# ----------------------------------------------------------------------------

def _format_month_year(ym):
    """'2026-03' -> 'Mar. 2026'; 'present' -> 'Present'."""
    if not ym or ym.lower() == "present":
        return "Present"
    months = ["Jan.", "Feb.", "Mar.", "Apr.", "May.", "Jun.",
              "Jul.", "Aug.", "Sep.", "Oct.", "Nov.", "Dec."]
    try:
        year, month = ym.split("-")
        return f"{months[int(month) - 1]} {year}"
    except (ValueError, IndexError):
        return ym


def _date_range(start, end):
    s = _format_month_year(start)
    e = _format_month_year(end)
    if e == "Present":
        return f"{s} - Present"
    return f"{s} - {e}"


def build_cv_yml(data):
    """NOTE: al-folio's cv.liquid layout ignores this file entirely whenever
    `_config.yml`'s `jekyll_get_json` loads `site.data.resume` (which it does
    here, from assets/json/resume.json). This function is kept for parity /
    fallback in case that config is ever removed, but the live /cv page
    currently renders from build_resume_json(), not this function."""
    cv = []

    # General information
    basics = data["basics"]
    cv.append({
        "title": "General Information",
        "type": "map",
        "contents": [
            {"name": "Full Name", "value": basics["name_en"]},
            {"name": "Email", "value": basics["email"]},
            {"name": "Website", "value": basics["links"]["homepage"]},
        ],
    })

    # Education
    edu_contents = []
    for edu in data.get("education", []):
        status = " (expected)" if edu.get("status") == "expected" else ""
        edu_contents.append({
            "title": edu["degree"],
            "institution": edu["institution"],
            "year": _date_range(edu["start"], edu["end"]) + status,
        })
    cv.append({"title": "Education", "type": "time_table", "contents": edu_contents})

    # Research experience
    research_contents = []
    for exp in data.get("research_experience", []):
        if not in_channel(exp, "homepage"):
            continue
        research_contents.append({
            "title": exp["role"],
            "institution": exp["org"],
            "year": _date_range(exp["start"], exp["end"]),
            "description": [b["text"].strip() for b in exp.get("bullets", [])],
        })
    if research_contents:
        cv.append({"title": "Research Experience", "type": "time_table", "contents": research_contents})

    # Selected projects
    project_contents = []
    projects = [p for p in data.get("projects", []) if in_channel(p, "homepage")]
    projects.sort(key=lambda p: p.get("importance", 999))
    for p in projects:
        project_contents.append({
            "title": p["name"],
            "institution": p["description"],
            "year": "Research Software" if p.get("category") == "research" else "Software",
            "description": [p["url"]],
        })
    if project_contents:
        cv.append({"title": "Selected Projects", "type": "time_table", "contents": project_contents})

    # Awards
    award_contents = []
    awards = [a for a in data.get("awards", []) if in_channel(a, "homepage")]
    awards.sort(key=_award_sort_key, reverse=True)
    for award in awards:
        award_contents.append({
            "title": award["title"],
            "institution": award["event"],
            "year": award["year"],
        })
    if award_contents:
        cv.append({"title": "Awards", "type": "time_table", "contents": award_contents})

    return cv


# ----------------------------------------------------------------------------
# resume.json — JSON Resume standard schema, fully regenerated.
# ----------------------------------------------------------------------------

def build_resume_json(data):
    basics = data["basics"]

    profiles = [
        {"network": "GitHub", "username": "haesol-shin", "url": basics["links"]["github"]},
        {"network": "LinkedIn", "username": "haesol-shin", "url": basics["links"]["linkedin"]},
    ]

    education = []
    for edu in data.get("education", []):
        education.append({
            "institution": edu["institution"],
            "area": edu["degree"].split("—")[-1].strip(),
            "studyType": edu["degree"].split("—")[0].strip(),
            "startDate": f"{edu['start']}-01",
            "endDate": f"{edu['end']}-01",
        })

    work = []
    for exp in data.get("research_experience", []):
        work.append({
            "name": exp["org"],
            "position": exp["role"],
            "startDate": f"{exp['start']}-01",
            "endDate": "Present" if exp["end"] == "present" else f"{exp['end']}-01",
            "summary": exp.get("topic", ""),
            "highlights": [b["text"].strip() for b in exp.get("bullets", [])],
        })
    for exp in data.get("open_source_experience", []):
        work.append({
            "name": exp["org"],
            "position": exp["role"],
            "startDate": f"{exp['start']}-01",
            "endDate": "Present" if exp["end"] == "present" else f"{exp['end']}-01",
            "highlights": [b["text"].strip() for b in exp.get("bullets", [])],
        })

    projects = []
    for p in data.get("projects", []):
        projects.append({
            "name": p["name"],
            "summary": p["description"],
            "url": p["url"],
        })

    awards = []
    sorted_awards = sorted(data.get("awards", []), key=_award_sort_key, reverse=True)
    for a in sorted_awards:
        awards.append({
            "title": a["title"],
            "date": str(a["year"]),
            "awarder": a["event"],
            "summary": a.get("org", ""),
        })

    skills = []
    sk = data.get("skills", {})
    if sk.get("languages"):
        skills.append({"name": "Languages", "keywords": sk["languages"]})
    if sk.get("frameworks"):
        skills.append({"name": "Frameworks", "keywords": sk["frameworks"]})
    if sk.get("tools"):
        skills.append({"name": "Tools", "keywords": sk["tools"]})
    if sk.get("interests"):
        skills.append({"name": "Interests", "keywords": sk["interests"]})

    return {
        "basics": {
            "name": basics["name_en"],
            "label": data["research_experience"][0]["role"] if data.get("research_experience") else "",
            "email": basics["email"],
            "summary": basics["summary"].strip(),
            "location": {
                "city": basics["location"]["city"],
                "countryCode": "KR",
                "region": basics["location"]["country"],
            },
            "profiles": profiles,
        },
        "education": education,
        "work": work,
        "projects": projects,
        "awards": awards,
        "skills": skills,
    }


# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--homepage-dir", type=Path, default=None,
                         help="Path to haesol-shin.github.io checkout "
                              "(or set HAESOL_HOMEPAGE_DIR env var instead)")
    parser.add_argument("--dry-run", action="store_true",
                         help="Print what would change without writing files")
    args = parser.parse_args()

    if not RESUME_YAML.exists():
        print(f"ERROR: {RESUME_YAML} not found.")
        sys.exit(1)

    data = load_resume()
    n_exp = len(data.get("research_experience", [])) + len(data.get("open_source_experience", []))
    n_awards = len(data.get("awards", []))
    n_projects = len(data.get("projects", []))
    print(f"Parsed resume.yaml ({n_exp} experience entries, {n_awards} awards, {n_projects} projects)")

    # README.md
    updated, missing = update_readme(data, dry_run=args.dry_run)
    for name in updated:
        verb = "Would update" if args.dry_run else "Updated"
        print(f"  {verb} README.md <!-- BEGIN:{name} --> block")

    # cv.yml / resume.json (homepage)
    homepage_dir, homepage_dir_source = resolve_homepage_dir(args.homepage_dir)
    if homepage_dir is None:
        print("ERROR: homepage directory not specified. Pass --homepage-dir PATH "
              "or set the HAESOL_HOMEPAGE_DIR environment variable.")
        verb = "would still be applied" if args.dry_run else "were still applied"
        print(f"(README.md updates above, if any, {verb}.)")
        sys.exit(1)
    print(f"Homepage dir: {homepage_dir} (source: {homepage_dir_source})")
    cv_yml_path = homepage_dir / "_data" / "cv.yml"
    resume_json_path = homepage_dir / "assets" / "json" / "resume.json"

    if homepage_dir.exists():
        cv_data = build_cv_yml(data)
        resume_data = build_resume_json(data)

        if args.dry_run:
            print(f"  Would rewrite {cv_yml_path}")
            print(f"  Would rewrite {resume_json_path}")
        else:
            cv_yml_path.parent.mkdir(parents=True, exist_ok=True)
            with open(cv_yml_path, "w", encoding="utf-8") as f:
                f.write("# GENERATED FROM haesol-shin/resume.yaml via generate.py — DO NOT EDIT DIRECTLY\n")
                yaml.dump(cv_data, f, allow_unicode=True, sort_keys=False, default_flow_style=False)
            print(f"  Rewrote {cv_yml_path}")

            resume_json_path.parent.mkdir(parents=True, exist_ok=True)
            with open(resume_json_path, "w", encoding="utf-8") as f:
                json.dump(resume_data, f, indent=2, ensure_ascii=False)
                f.write("\n")
            print(f"  Rewrote {resume_json_path}")

        about_ok, about_err = update_about_md(data, homepage_dir, dry_run=args.dry_run)
        if about_ok:
            verb = "Would update" if args.dry_run else "Updated"
            print(f"  {verb} about.md <!-- BEGIN:facts --> block")
        else:
            print(f"  WARNING: {about_err} — skipped about.md")
    else:
        print(f"  WARNING: homepage dir not found ({homepage_dir}) — skipped cv.yml/resume.json/about.md")

    print("  NOTE: HaesolShin_Resume.docx is not auto-generated — update it manually against resume.yaml")

    total = len(updated) + (3 if homepage_dir.exists() else 0)
    verb = "would be updated" if args.dry_run else "updated"
    print(f"Done: {total} file(s) {verb}")


if __name__ == "__main__":
    main()
