# Agentic AI Workflows for Research

A course by Simone Paci on understanding, using, and governing AI in research.

The current MVP contains an editable Quarto website and seven Reveal.js slide decks. It follows an introduction plus five core sections. Section 5 remains to be defined. The slides and exercise outlines are teaching drafts.

## Build

Install Quarto 1.10.18 and Python 3.12 or newer, then run:

```sh
quarto render site
python scripts/course-tools/validate-site.py site/_site --source site
quarto preview site --no-browser
```

On Windows, `powershell.exe -NoProfile -File scripts/course-tools/build.ps1` renders and checks the site.

## Source

- `site/`: learner pages, slides, themes, and a notes-stripping filter.
- `scripts/course-tools/`: the build command and public-output validation.
- `.github/workflows/pages.yml`: build validation on pushes and pull requests, with Pages deployment only from an explicit manual dispatch on main.

Instructor working notes, imported lecture files, unpublished research tasks, and local provenance records are maintained outside the public Git inventory. Rendered output is generated from source.

This MVP provides slide access and a course map. It does not implement learner accounts, exercise submission, unlock rules, or a discussion board.

Course anchors: [With Great Powers](https://simonepaciphd.github.io/with-great-powers/) and [Working with AI Agents](https://simonepaciphd.github.io/ai-os-public/).
