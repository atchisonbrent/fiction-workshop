# Illustrated reading editions

Use this alongside `reading-editions.md` when illustrating a frozen story.
Artwork is an optional edition layer, not a rewrite of prose or canon. Keep
private passages, references, generations and receipts in the content repository.

## 1. Establish the boundary

Record the release ID and source SHA-256, allowed generation routes, cost/quota
boundary, publication destination and whether the agent may select final plates.
Verify the actual subscription/API route; a subscription name is not proof an
API request is covered. Never silently switch to a billable fallback. Respect
provider refusals; retrying a refused prompt to defeat a safeguard is not an art
revision. Do not start a service, scheduler or worker fleet for an illustration job.

Define a finite initial scene selection across the narrative, balancing ordinary
life, relationships, discovery and spectacle. Not every chapter needs a plate.
Use outlines and canon to find candidates, then read the selected frozen prose
and its earlier dependencies. State discovery coverage separately from full
prose reading. Leave unselected scenes outside this edition's acceptance claim.

## 2. Make a source-grounded visual packet

Each scene needs a stable ID, chapter, exact selected passage, insertion anchor,
and earlier passages establishing recurring visual facts. Before generation,
check the brief against the quotations—not a remembered summary of them.

Record these separately:

- **Established:** exact visible cast, names/roles, position and action, age and
  form, clothing/props explicitly present, location, time, injuries, travel mode,
  object scale and state. An open cabinet remains open on the next visit unless
  the story changes it. A companion ashore is not automatically aboard a boat.
- **Interpretation:** unspecified colors, camera, light, architecture and original
  character appearance chosen for this edition. Freeze these choices in a visual
  reference ledger without promoting them to story canon.
- **Excluded:** absent characters, abilities not yet learned, transformations not
  active, later injuries, equipment not yet introduced and simultaneous events
  occurring elsewhere. Someone speaking remotely is not physically in the room.
- **Unknown:** material details not resolved by retrieval. Retrieve more or ask;
  never manufacture a source fact to make a picture easier.

Resolve pronouns and changes within the chapter: whose shoes were removed, who
left before the sparring, who is carried, who only watches a recording. Pair a
short exact scene excerpt with the final cast/action constraints. Keep the full
chapter available as evidence, but avoid asking an image generator to choose
among multiple scenes. If the brief contradicts the source, fix the brief first.
Do not blame the model or revise an accurate picture into the invented scene.

## 3. Lock identity and continuity

Generate and inspect character references before scaling production. Capture
face/profile, hair silhouette, apparent age, proportions and relevant alternate
forms. Make a separate small-object reference when scale is easy to lose; compare
it with a hand or other known-size object. References are fallible candidates,
not proof of likeness. Explicitly exclude reference characters absent from a scene.

Choose a primary renderer for cohesion. A second provider can supply comparisons
or alternatives within the approved boundary, but an attractive outlier is not
an automatic addition. Use accepted images for recurring materials and designs;
a rejected candidate must not silently become the next identity reference.

## 4. Generate with durable receipts

Before each request, save the exact prompt/payload, source/reference hashes,
provider route, candidate ID and submission state. Afterward retain the original,
actual returned model identity, result status, local checksum and parent candidate
for edits. Do not persist credentials or signed download URLs.

Useful states are `ready`, `submitted`, `downloaded_pending_review`, `accepted`,
`rejected`, `withdrawn`, `quota_blocked` and `uncertain_submission`. Keep generation
status separate from editorial approval. Do not overwrite earlier candidates.

Parallelize independent, fully briefed scenes with distinct IDs/output paths.
Do not parallelize edits whose references are still being selected. A supervising
editor owns source interpretation, acceptance and the final edition; mechanical
workers cannot change cast, spending, publication or quality gates.

A timeout or missing download is not proof a request failed. Reconcile its saved
receipt and provider history before a retry; keep an uncertain attempt blocked.
When a provider runs out of quota, record its response, affected candidate and
resume condition. Continue on another already-approved route only if its outputs
meet the same style/identity gates. Stop when no approved route can proceed.
Never invent a reset time or call a quota checkpoint a completed edition.

## 5. Inspect, grade and revise

Load every actual candidate image. Check source continuity and anatomy before
rewarding composition. Then compare with identity references and neighboring
plates at both useful detail and small reading size.

A practical ledger uses four editorial scores out of ten: source fidelity,
identity/continuity, anatomy/readability and composition/rendering. Set a project
threshold before grading (for example, at least eight in every dimension).
Scores are subjective editorial judgments, not an objective model benchmark.

Hard failures override averages: wrong cast or moment, material source conflict,
unrecognizable lead, incorrect age/form, unusable anatomy, missing resource,
or major recurring-design/scale drift. Record the visible reason for rejection.
Prefer a targeted edit for one local defect; regenerate when composition or
identity is structurally wrong. Reinspect the entire edit for regressions.
If an unexpected composition faithfully depicts another worthwhile source moment,
record the changed selection explicitly; do not pretend it fulfilled the old brief.

## 6. Export only accepted plates

Build the existing local-image manifest from accepted IDs, not a directory glob.
Bind it to the frozen release digest. Use descriptive alt text without adding
new plot facts. Choose unique plain-paragraph anchors supported by the exporter;
quoted/footnote text may normalize differently. Smart punctuation can also change
straight apostrophes to curly ones. Inspect the actual parsed paragraph when a
unique source anchor fails; correct the manifest, never the frozen prose. Test
actual insertion and order.

Create a new edition ID. Preserve frozen prose, text-only edition identity and
previous editions. Verify all chapter prose/order, image count, EPUB image bytes
against accepted assets, resolved references, navigation and EPUBCheck. Inspect
narrow HTML rendering and the target reader when accessible. A prior reader's
success with another edition is useful evidence, not a native test of new bytes.

Deliver the private EPUB link and representative images through the chat surface's
supported attachment syntax; a bare filesystem Markdown image is not portable.
Verify remote download bytes after publication. Do not add private images to a
public tooling release. Keep a compact gallery separate from operational receipts.

## 7. Leave an honest terminal state

The production README names purpose, release, status, accepted plate count,
rejections/withdrawals, source-reading coverage, limitations, final edition and
verification receipts. A stopped run names the exact remaining scenes, unresolved
attempts, allowed resumption route and missing prerequisite. No new generation is
needed merely to discover where work stopped.

A reusable handoff includes a worked successful source/image pairing and a
rejected or withdrawn one, with the actual reason and correction. Keep those
story-specific examples private; this portable procedure defines the method.
