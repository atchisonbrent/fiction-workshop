# Fiction Workshop

A Git-backed, continuity-aware workshop for developing original fiction from
flash and short stories through novellas, novels, and serial work without
changing systems halfway through.

The repository contains:

- a portable Agent Skill for story development;
- deterministic JSON templates and a standard-library Python validator;
- tests for release integrity, lineage, canon, portability, and scope constraints;
- `small-mercy`, an original short-to-long workflow fixture.

## Requirements

- Python 3.10 or newer
- Git
- Node.js only when using the optional universal `npx skills` installer

The skill follows the open Agent Skills format used by Codex, Claude Code,
OpenCode, and Hermes Agent. The validator commands use `python3`; on Windows,
use `python` when that is the Python 3.10+ launcher on your system. The validator
and tests require no third-party Python packages.

## Install

Choose the installation scope and release channel first.

- **Stable/pinned:** install from the release tag assigned to `SKILL_VERSION` in
  the examples below. Updates stay on that tag until you explicitly install a
  newer tag.
- **Latest:** install from `atchisonbrent/fiction-workshop`. Updates follow the
  current default branch, which may contain changes newer than the latest tag.

The examples below use the current stable release. To follow latest instead,
replace the tagged URL with `atchisonbrent/fiction-workshop`.

### Install for one writing workspace

A project-local install is relative to the shell's **current directory**. Run the
command from the root of the repository or folder where you will develop stories.
For an existing project:

```text
cd /path/to/my-writing-project
SKILL_VERSION=v0.2.0 # x-release-please-version
npx skills add "https://github.com/atchisonbrent/fiction-workshop/tree/${SKILL_VERSION}/.agents/skills/story-development" \
  --skill story-development \
  --agent codex \
  --agent claude-code \
  --agent opencode \
  --agent hermes-agent
```

If you are starting from nothing, create the workspace first:

```text
mkdir my-writing-project
cd my-writing-project
git init
SKILL_VERSION=v0.2.0 # x-release-please-version
npx skills add "https://github.com/atchisonbrent/fiction-workshop/tree/${SKILL_VERSION}/.agents/skills/story-development" \
  --skill story-development \
  --agent codex \
  --agent claude-code \
  --agent opencode \
  --agent hermes-agent
```

Without `--global`, the installer creates or links skill directories beneath that
current workspace—for example `.agents/skills/story-development`, with
agent-specific links or copies such as `.claude/skills/story-development` and
`.hermes/skills/story-development`. This keeps the skill scoped to agents started
for that workspace.

### Install for your user account

Use a global install when you want the skill available across projects. In that
case, the current directory does not determine the installation location:

```text
SKILL_VERSION=v0.2.0 # x-release-please-version
npx skills add "https://github.com/atchisonbrent/fiction-workshop/tree/${SKILL_VERSION}/.agents/skills/story-development" \
  --skill story-development \
  --agent codex \
  --agent claude-code \
  --agent opencode \
  --agent hermes-agent \
  --global
```

The installer then uses each agent's user-level skill directory. Update a
project-local installation from that project's root with:

```text
npx skills update --project story-development
```

Update a global installation from anywhere with:

```text
npx skills update --global story-development
```

For a latest-channel installation, those commands fetch current default-branch
content. For a pinned installation, they refresh the same recorded tag. To move
to a later release, rerun the matching `skills add` command after changing
`SKILL_VERSION` to the desired release tag. The project's `skills-lock.json`
records the selected tag and content hash; commit that lock file when the writing
workspace is shared so collaborators use the same source.

The installer includes the complete skill—references, templates, and validator.
Start a new agent session after installation. Invoke it explicitly as
`$story-development` in Codex, `/story-development` in Claude Code, or ask any
supported agent naturally to develop a story.

## Clone and develop

```text
git clone https://github.com/atchisonbrent/fiction-workshop.git
cd fiction-workshop
python3 -m unittest discover -s tests -v
python3 .agents/skills/story-development/scripts/validate_story.py examples/small-mercy
```

Codex, OpenCode, and a trusted Hermes checkout discover the checked-in
`.agents/skills/story-development` directly. For Hermes, trust the checkout once
with `hermes skills trust`; Claude Code and any agent version that does not scan
`.agents/skills` directly should use the installer above so it receives the skill
in its own supported directory.

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

- `.agents/skills/story-development/` — procedure, references, templates, and validator.
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
2. Copy the JSON templates from `.agents/skills/story-development/templates/`.
3. Add a per-story `LICENSE.md` naming the copyright owner and terms; adapt the
   notice pattern described in `examples/LICENSE.md`.
4. Add `kernel.md`, `project.json`, working contract/canon, and only the planning
   artifacts required by the chosen resolution.
5. Validate the story before committing it.

See `.agents/skills/story-development/references/story-model.md` and
`docs/architecture.md` for the complete model.

## Validation

```text
python3 -m unittest discover -s tests -v
python3 .agents/skills/story-development/scripts/validate_story.py examples/small-mercy
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

## Releases

This repository uses [Release Please](https://github.com/googleapis/release-please)
to release eagerly from Conventional Commits on `main`. For every release-worthy
push, the workflow tests `main`, generates a release PR, checks out and tests that
generated version change, auto-merges it, then creates the matching `vX.Y.Z` tag
and GitHub Release in the same run. No package registry is involved.

To roll back a published release, delete the GitHub Release and tag, then restore
the manifest, version files, and changelog to one consistent prior version before
pushing again. Do not hand-edit the transient Release Please PR; fix the source
commit on `main` and let automation regenerate it.

## Current boundary

This version deliberately has no database, vector retrieval, daemon, UI,
story-publication pipeline, shared universe across story slugs, or autonomous
multi-agent runtime. Repository version tags and GitHub Releases are handled by
the software release workflow above. Add omitted story-system machinery only
after real stories demonstrate the need.
