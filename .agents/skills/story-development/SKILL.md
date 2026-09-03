---
name: story-development
description: Create and grow continuity-safe fiction across lengths.
version: 0.3.0 # x-release-please-version
author: Brent Atchison (atchisonbrent), Helion
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [fiction, creative-writing, continuity, story-development]
    related_skills: []
---

# Story Development

Develop fiction from a tiny brief through short, novella, novel, or serial form
without treating every idea as an unfinished book. One kernel, canon model, and
release lineage serve every length; longer work activates more operating
artifacts only when scope or complexity earns them.

## When to Use

Use when the user wants to:

- brainstorm, outline, draft, revise, continue, or expand fiction;
- preserve continuity, character integrity, chronology, or world rules;
- explore structurally different story possibilities;
- use artistic influences without copying or close imitation;
- resume a story already stored in the active content workspace.

Do not use for ordinary nonfiction or for line-editing text unrelated to a story
project. Do not assume a brief should become a novel.

## Prerequisites

- Define `SKILL_DIR` as notation for the absolute directory containing this
  `SKILL.md`; it is not assumed to be a pre-existing environment variable.
  Resolve every `references/`, `templates/`, and `scripts/` path from
  `SKILL_DIR`; never assume the skill is installed under a particular agent's
  configuration directory or inside the story repository.
- A story may live in any content workspace. Pass its path to the validator and
  load its files explicitly.
- Before relying on an existing story, run the following after replacing
  `<SKILL_DIR>` with the absolute directory containing this `SKILL.md`:
  `python3 <SKILL_DIR>/scripts/validate_story.py <path-to-story>`. On Windows,
  use `python` when that is the Python 3.10+ launcher.
- Treat released trees under `release-contracts/<id>/` as immutable.

## Procedure

### 1. Locate or create the story

For a new story, establish:

- a narrative kernel in `kernel.md`;
- a per-story `LICENSE.md` naming the copyright owner and terms;
- `project.json` with the current scope budget and complexity signals;
- a working release contract and canon;
- only the planning artifacts required by the current resolution.

Load `<SKILL_DIR>/references/story-model.md` for field semantics and minimum artifacts.
Completion: the story has one active working release and validates structurally.

### 2. Choose scope without forcing length

Infer a low-risk scope budget when the request makes it obvious. Ask one tight
question when flash, short, episodic, or long form would materially change the
reading experience. Word targets are budgets, not quotas.

Load `<SKILL_DIR>/references/scope-and-expansion.md` when choosing length or growing prior
material. Completion: the current budget states a reader promise and still
allows “keep it short” as a valid outcome.

### 3. Generate genuinely different possibilities

Before drafting a major direction, choose two or more divergence axes from
`project.json` (conflict source, emotional movement, information revealed,
power shift, consequence, structure, or another declared dimension). Generate
alternatives that differ structurally on those axes, not cosmetic paraphrases.
Archive rejected branches outside live canon.

Completion: every candidate can be distinguished without referring to wording.

### 4. Plan only to the earned depth

- Flash/vignette: kernel and beats.
- Short: causal beats or a small scene sequence.
- Novella: movements, near-horizon scenes, open loops, rolling summary.
- Novel/serial: keep the novella core, then activate movement hierarchy,
  subplots/arcs, timeline, relationship and knowledge state, obligation index,
  retrieval packets, and global audits as complexity requires them.

Complexity can activate a layer earlier than word count. Never manufacture acts
or scenes merely to fill a template. Completion: the near horizon is actionable
and the far horizon remains revisable.

### 5. Protect character agency

Before a consequential action, compare it with the character’s goals, knowledge,
capabilities, values, relationships, and recorded behavioral patterns. Treat
invariants and fracture conditions as evidence for review, not a rule engine.
A surprising action is welcome when pressure or transformation earns it.

Completion: the plot follows from character choices, or the deviation has
specific textual support rather than a retrospective excuse.

### 6. Draft and update state

For each beat or scene, load only relevant canon, character state, nearby prose,
open obligations, and ancestor closing contracts. Draft prose first; commit
canon and state deltas only after the passage is accepted. Discarded generations
never become facts.

When prose is split into `working/chapters/*.md`, every established fact's
`provenance` must name a chapter file stem (`03-six-red-marks`), a scene ID, or
`kernel`. Prefer scene IDs when a fact needs finer or rename-stable location.
Facts inherited unchanged from an ancestor release keep their original
provenance even when it predates this rule.

Regenerate `working/manuscript.md` by sorting chapter paths lexicographically
(use zero-padded numeric prefixes), stripping trailing newlines from each file,
joining them with exactly `\n\n---\n\n`, and appending one final newline. The
validator rejects a stale aggregate.

Completion: accepted prose and state agree, and every new established fact has
provenance that resolves to real text.

### 7. Review in separate passes

Load `<SKILL_DIR>/references/editorial-rubrics.md`. Run only the lenses activated by scope
and complexity: causality/time, character, world/facts, obligation/payoff, POV
and tone, pacing/necessity, prose, and freshness/imitation risk. Findings cite
both conflicting passages or the exact obligation they concern.

Completion: blockers are repaired or explicitly accepted; editorial opinion is
not misreported as deterministic validation.

### 8. Release, then expand by copy-on-write

Release with the tool, never by hand:

```text
python3 <SKILL_DIR>/scripts/release_story.py <path-to-story> [--dry-run]
```

It requires a valid story whose working contract declares
`manuscript_status: complete`, freezes the kernel, canon, prose (assembled from
chapters when present), and contract with the current scope budget, writes the
manifest, and re-validates. It refuses to touch an existing release tree.

While the working set still points at a released ID, its kernel and canon must
stay byte-identical to the release, its contract must equal the released contract
apart from `status` and `frozen_scope_budget`, and its prose must be text-identical
to the approved draft. The validator treats drift as editing a released story.
To keep writing, open a child: new `release_id`, `parent_release_id` naming the
release, `active_release_id` updated to match.

Never edit a released parent to make a child fit. Save an expansion audit under
`decisions/`, choose one or more modes (deepen, widen, extend, reframe, adapt),
and create a child working release. Load every ancestor’s closing contract and
non-negotiable constraints. A retcon lives in the child lineage and names the
superseded fact; the parent snapshot remains unchanged.

Completion: the parent still passes its manifest and frozen-budget validation,
and the audit identifies the new dramatic question that earns the added length.

### 9. Apply voice and influence deliberately

Load `<SKILL_DIR>/references/influence-and-voice.md`. Use craft dimensions and transformed
influence cards, never copied passages, signature-phrase mimicry, or “write
exactly like” instructions. Keep narrator, POV, character, and source-universe
voices separate.

Completion: the prose has a project-specific voice and no named influence is
being impersonated.

## Genre adapters

Load `<SKILL_DIR>/references/genre-adapters.md` only when a genre creates special state or
fairness obligations, such as clues in mystery, consent and relationship turns
in romance, threat rules in horror, or technology costs in science fiction.
Adapters add checks; they do not impose one universal plot structure.

## Pitfalls

- **Accidental novelization:** more backstory is not a new dramatic question.
- **Checklist prose:** state tracking supports fiction; it must not appear as
  explanatory dialogue or defensive narration.
- **Canon leakage:** proposed and rejected ideas are not established facts.
- **Parent mutation:** Git history does not excuse changing released snapshots.
- **Style Lego:** too many influence cards produce a mosaic, not a voice.
- **Long-context complacency:** context capacity is not reliable state tracking.
- **LLM judge theater:** semantic reviews cite evidence and remain fallible.

## Verification

Run:

```text
python3 <SKILL_DIR>/scripts/validate_story.py <path-to-story>
```

Before claiming completion, verify:

- the active working set has a nonempty, non-symlinked `LICENSE.md` and satisfies
  its own scope and complexity requirements;
- every released tree matches its manifest and frozen budget;
- a working set that reuses a released ID has identical kernel, canon, contract
  semantics, and prose as described above;
- a child’s parent exists and remains unchanged;
- canon fact IDs are unique within each canon view; inherited facts may retain
  their IDs across parent and child views, and required statuses carry provenance;
- the requested form is complete on its own terms rather than merely longer.
