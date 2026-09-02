# Story model

## One model, progressive layers

Every story has a nonempty `LICENSE.md`, working `project.json`, versioned
`kernel.md`, active release contract, canon, and lineage. Resolution presets
change required artifacts, not file semantics.

| Resolution | Minimum artifacts | Added operating layer |
| --- | --- | --- |
| flash | kernel, scope budget, release contract, canon, beats | none |
| short | flash set with causal beats or scenes | payoff and continuity review |
| novella | short set plus movements, open loops, rolling summary | periodic re-outline |
| novel | novella core; additional ledgers activated by complexity | acts/movements, subplot/arc ledgers, timeline, relationship/knowledge state, retrieval packets, obligation index, global audits |

Complexity signals in `project.json` may activate a layer early. A nonlinear
2,000-word story may need a timeline; a linear 20,000-word story may not need a
relationship graph.

## Scope budget versus release contract

The mutable scope budget describes intent while drafting. The immutable release
contract records what a released version actually promised and embeds the frozen
budget used to make it.

`manuscript_status` is `planned`, `draft`, or `complete`. Only `complete` invokes
the deterministic target-word gate; exploratory work is free to grow below its
minimum until it claims completion.

Required working project concepts:

- one active release ID;
- current planning resolution and publication shape;
- target posture, not a mandatory word quota;
- reader promise;
- closure posture and revisit policy;
- complexity signals;
- divergence axes for alternatives.

## Canon statuses

- `proposed`: planning material, not true yet;
- `established`: objective within this lineage unless explicitly viewpoint-limited;
- `character_belief`: true only as a belief;
- `rumor_or_claim`: attributed assertion with uncertain truth;
- `unresolved`: deliberately undecided or ambiguous;
- `retconned`: child-lineage record superseding a named parent fact;
- `rejected_branch`: material preserved outside live canon.

Established facts, beliefs, claims, and retcons carry provenance. IDs are unique
inside one canon file/view. A child view normally retains inherited parent IDs so
provenance and retcons remain traceable across releases. Parent snapshots never
change.

Provenance is free-form while the whole text fits one reading. Once prose lives in
`working/chapters/*.md`, provenance must resolve: a chapter file stem, a heading
slug within a chapter (lowercase, punctuation stripped, spaces to hyphens), a
scene ID from `outline/scenes/`, or `kernel`. This is what makes "load only the
relevant prose" possible at novella scale without a database.

## Character evidence

Track detail only when it can constrain or enrich future writing:

- public and private goals;
- values, contradictions, and behavioral patterns;
- fears and fracture conditions;
- knowledge, suspicions, false beliefs, and secrets;
- capabilities and limitations;
- location, injuries, possessions, and commitments;
- relationship trust, power, debt, and intimacy;
- voice controls and avoided habits;
- arc pressure, not a mandatory transformation.

These fields provide evidence during review. They do not mechanically forbid
surprise, panic, hypocrisy, regression, or change.

## Event and obligation state

A beat or scene may record start state, focal character, goal, opposition, turn,
outcome, cost, and accepted state deltas. Flash fiction may use only an ID and
consequence. Never create empty fields merely to make a file look complete.

Track obligations as opened, advanced, resolved, deferred, or intentionally
abandoned. Distinguish audience knowledge from each character’s knowledge.

## Released snapshot

`release-contracts/<id>/` contains:

- `contract.json`, including the frozen scope budget and parent;
- the referenced `kernel.md` revision;
- `approved-draft.md`;
- `canon.json`;
- `manifest.json` with SHA-256 hashes of every protected file.

Released snapshots validate against their own frozen budget, never the current
working budget. A child may add or supersede facts in its lineage but cannot
rewrite the parent snapshot.
