# Scope and expansion

## Choosing length

Length follows the dramatic unit being completed:

- flash: one pressure, perception, image, reversal, or choice;
- short: one primary causal/emotional arc with a satisfying ending;
- novella: a central arc that needs several movements or sustained consequences;
- novel/serial: multiple interacting arcs, institutions, timelines, or changes
  whose value comes from accumulation.

Word targets are planning budgets. Do not inflate a complete short work to meet a
preset. “Keep it short” is a successful scope decision.

## Reader checkpoints and scope changes

For an opening installment or a work being developed with a reader, use an
optional short checkpoint in the existing decision notes or handoff. State:

- what this installment delivers now and what deliberately remains open;
- which future beats are planned, which are tentative alternatives, and which
  earlier ideas are superseded;
- two or three useful feedback questions, such as where interest increased or
  attention drifted, rather than asking only whether the reader liked it.

A checkpoint is not another mandatory template or approval ceremony. Do not
pause a requested complete work at an opening installment without the user's
agreement. An eventual length ambition does not itself authorize changing the
current deliverable. Record the source of a meaningful scope change; do not
attribute an inferred preference to the reader as an explicit instruction.

When the agreed scope changes, reconcile the current kernel, budget, contract,
and planning horizon before drafting further. Preserve the rationale in
`decisions/`; remove superseded instructions from the live plan or mark them
unambiguously inactive. Use a child release when a frozen version is affected.
An unused outline is not canon and does not obligate the story to reach its
ending. Prefer a detailed near horizon and a provisional farther direction to
an elaborate plan maintained only because it already exists.

## Expansion modes

Modes may compose and must be recorded in the child contract:

- **Deepen:** retain spine and ending; add pressure, interiority, or consequence.
- **Widen:** add POVs, factions, places, or subplots around the core event.
- **Extend:** write what precedes or follows under the same story slug.
- **Reframe:** reinterpret or restructure into a new branch.
- **Adapt:** change form, genre, POV, or audience without assuming continuity.

Cross-story shared canon and sibling-story lineage are outside the MVP boundary.

## Required expansion audit

Save the answers under `decisions/` before changing the working scope:

1. What made the shorter form satisfying on its own?
2. Which opening and closing promises must survive?
3. Which revelations depend on compression or surprise?
4. Which character choices can bear more pressure without becoming convenient?
5. Which facts are immutable, and which were viewpoint-limited beliefs?
6. What **new dramatic question** earns the additional length?
7. Does the child stand alone for readers who skipped the parent? What must it
   re-establish or re-earn?
8. Is deepening/widening better than an extension, sibling story, or no expansion?
9. Which prior plan did this audit change? If none, inspect whether the audit was
   merely performed rather than used.

The audit ends with a recommendation: keep short, expand using named modes, write
a sequel/prequel, adapt, or abandon.

## Copy-on-write process

1. Release the parent with `scripts/release_story.py`; it validates first, freezes
   the working set, writes the manifest, and revalidates. Never assemble a
   release tree by hand.
2. Create a child working contract naming the parent and expansion modes.
3. Copy relevant canon into the child working view without editing the parent;
   preserve inherited IDs and statements unless an explicit child retcon supersedes them.
4. Load ancestor closing contracts and non-negotiable constraints.
5. Record reader-reset obligations when the child must stand alone.
6. Add or supersede facts only in the child lineage.
7. Revalidate both parent and child after every structural change.

A retcon requires a child fact with `status: retconned`, `supersedes`, provenance,
and a safe `decision_ref` beneath `decisions/` explaining reason and consequences.
The superseded ID must exist in an ancestor canon. Retcon is an explicit
creative choice, not a continuity error with paperwork added afterward.

Legacy releases created before the release tool may omit `manuscript_status`.
Do not backfill their hashed contracts or add the field only to an at-rest working
contract. Leave the pair unchanged; open a child release before further work.

## Long-form operating cadence

For novella and above:

- detail the next few scenes; keep the far horizon coarse;
- update movement summaries and open loops after accepted scenes;
- audit timeline, knowledge, and relationships at movement boundaries;
- re-outline after major reversals rather than forcing obsolete plans;
- run a whole-work continuity pass near the midpoint, where drift commonly
  accumulates, and again before release.

### Multi-arc convergence and restart state

Successful local arcs do not automatically form a satisfying novel. At a major
scope change or repeated arc pattern, choose a provisional whole-work
confrontation, consequential character choice, and aftermath. Work backward:
what irreversible change does each remaining arc contribute? Keep the arc count
revisable, but do not substitute indefinite adjacent adventures for convergence.
Protect promised pleasure and genre payoff as well as continuity; a threat should
not automatically invalidate everything the characters enjoyed building.

Use existing decisions/outline/review notes for a compact restart packet, not a
new parallel canon system. Name the current approved direction and its source,
superseded alternatives, established versus proposed world rules, outstanding
mechanism tests, last accepted prose/release, next bounded dramatic unit, and
source passages required before drafting. Record actual reading coverage and
gaps. After compaction, reload that packet AND its source dependencies; remembered
summaries and a reviewer's full read do not establish the author's fresh coverage.
Update at meaningful drafting/review boundaries, not after every sentence.

When a finale depends on exceptional capabilities, test alternatives before
planting decisive clues: why ordinary solutions fail, why the exceptional one
works, its limits, and what it cannot decide morally. Do not invent incompetence
or new exceptions at payoff. Finish and review one earned unit at a time; a
multi-arc outline is not an instruction to draft the whole ending in one pass.
