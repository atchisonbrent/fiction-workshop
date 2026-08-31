# Fiction Workshop

A Git-backed, continuity-aware workshop for developing original fiction from
flash and short stories through novellas, novels, and serial work without
changing systems halfway through.

The repository contains:

- a project-local Hermes skill for story development;
- deterministic JSON templates and a standard-library Python validator;
- tests for release integrity, lineage, canon, and scope constraints;
- `small-mercy`, an original short-to-long workflow fixture.

## Requirements

- Python 3.10 or newer
- Git
- [Hermes Agent](https://hermes-agent.nousresearch.com/docs) when using the
  project-local writing skill

The validator and tests do not require third-party Python packages.

## Quick start

```text
git clone https://github.com/atchisonbrent/fiction-workshop.git
cd fiction-workshop
python3 -m unittest discover -s tests -v
python3 .hermes/skills/story-development/scripts/validate_story.py examples/small-mercy
```

To use the project-local skill, trust this checkout once:

```text
hermes skills trust
```

Then start a Hermes session from the repository and invoke
`/story-development`, or ask naturally to develop an original story.

## Story model

Every story uses the same:

- narrative kernel;
- mutable working scope budget;
- immutable release contracts;
- provenance-bearing canon facts;
- parent/child lineage;
- reader promises and unresolved obligations.

Longer work activates more operating artifacts—movement outlines, open-loop and
subplot ledgers, rolling summaries, timelines, and global audits. It does not
migrate to a second schema.

## Repository layout

- `.hermes/skills/story-development/` — procedure, references, templates, and validator.
- `examples/small-mercy/` — one complete original project used as a public validator and workflow fixture.
- `tests/` — deterministic validator tests.

Personal story projects live in a separate content repository or directory and
use the same internal `working/`, `release-contracts/`, `outline/`, `decisions/`,
and `style/` layout. Cloning this tooling repository does not download Brent's
private works.

When a story uses chapter files, `working/manuscript.md` is the aggregate sharing
copy assembled in chapter order. A released `approved-draft.md` is the immutable
sharing copy for that release.

## Create a story

1. Create a story directory in your own content repository or workspace.
2. Copy the JSON templates from `.hermes/skills/story-development/templates/`.
3. Add a per-story `LICENSE.md` naming the copyright owner and terms; adapt the
   notice pattern described in `examples/LICENSE.md`.
4. Add `kernel.md`, `project.json`, working contract/canon, and only the planning
   artifacts required by the chosen resolution.
5. Validate the story before committing it.

See `.hermes/skills/story-development/references/story-model.md` and
`docs/architecture.md` for the complete model.

## Validation

```text
python3 -m unittest discover -s tests -v
python3 .hermes/skills/story-development/scripts/validate_story.py examples/small-mercy
```

The validator checks structural fields and types, required planning artifacts,
payoff ledgers, canon provenance, release lineage, safe paths, immutable
manifests, story ownership markers, and configured manuscript word budgets.
It does **not** prove literary quality, emotional truth, or every semantic
continuity claim.

## Publication boundary

This repository ships **tooling plus one curated original example**. Personal
story projects—including original works—belong in a separate content repository
so consumers do not download them with the tool. Never commit derivative fan
works, copied source text, confidential drafts, credentials, or private model
and review-session logs here. See `CONTRIBUTING.md`.

## Licensing

Code, templates, and eligible workshop documentation are MIT licensed. Original
story prose and story-specific creative assets are not covered by MIT and remain
copyrighted by their author. See `LICENSES.md` and `examples/LICENSE.md`.

## Current boundary

This version deliberately has no database, vector retrieval, daemon, UI,
publishing pipeline, shared universe across story slugs, or autonomous
multi-agent runtime. Add those only after real stories demonstrate the need.
