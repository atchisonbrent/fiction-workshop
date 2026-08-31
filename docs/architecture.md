# Architecture

## One model across lengths

The workshop treats length as a mutable scope budget rather than a permanent
story type. Flash fiction, short stories, novellas, novels, and serials share one
kernel, canon model, release lineage, and obligation model. Greater length or
complexity activates more planning and review artifacts instead of requiring a
migration to a second system.

## Working state and releases

A story has mutable working state and zero or more immutable releases.

Working state includes:

- `project.json` and the active scope budget;
- `kernel.md`;
- `working/release-contract.json`;
- `working/canon.json`;
- scope-appropriate outlines, summaries, chapters, and ledgers.

A released tree freezes:

- the release contract and scope budget;
- the relevant kernel;
- approved prose;
- canon state;
- a SHA-256 manifest covering protected files.

Expansion is copy-on-write. A child release may deepen, widen, extend, reframe,
or adapt an earlier work, but it never edits the released parent.

## Progressive artifacts

- **Flash:** kernel, budget, working contract/canon, and beats.
- **Short:** the flash set plus causal beats or scene cards.
- **Novella:** movement outline, open-loop ledger, and rolling summary.
- **Novel or serial:** add hierarchy, subplot and character-arc ledgers,
  timelines, relationship/knowledge state, retrieval packets, and scheduled
  global audits as complexity requires.

These are defaults rather than quotas. Complexity may activate a layer early,
and a deliberately brief story is not an unfinished long work.

## Canon and character agency

Facts carry explicit statuses and provenance so proposals, beliefs, rumors,
established events, retcons, and rejected branches cannot silently collapse into
one another. Character behavior is reviewed against goals, knowledge, values,
capabilities, relationships, and earned fracture conditions; the outline does
not get to conscript a character into implausible behavior.

## Voice and influence

The procedure, project voice, narrator, point-of-view perception, character
voices, temporary influence cards, and editorial roles remain separate. Artistic
influence is represented through abstract craft dimensions, never copied text,
signature imitation, or a permanent global writer persona.

## Publication boundary

The repository contains reusable tooling and one curated original example only.
Personal fiction lives in a separate content repository. Code and procedural
material use the root MIT license; example prose has explicit per-example
copyright terms. The validator requires every validated story directory to carry
its own `LICENSE.md`, making the licensing boundary part of structural validation
rather than a README promise.

## Deliberate omissions

The initial architecture has no database, embeddings, service process, custom
interface, story-publication automation, or autonomous agent runtime. Git,
Markdown, JSON, and deterministic validation are enough until demonstrated scale
requires more machinery. Repository version tags and GitHub Releases are handled
separately by the software release workflow documented in `README.md`.
