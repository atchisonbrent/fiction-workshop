# Independent editorial review

Use at a meaningful draft or arc boundary, or when the author is stuck on a
specific problem. This is a portable handoff procedure, not a requirement to
launch a panel of agents. Model/provider choice, authorization, privacy, budget,
and tool restrictions belong to the host environment.

## Default: point the reviewer at the work

Give the reviewer a short brief, a stable manuscript location, permission to read
that scope, and two or three relevant lenses. Let it navigate and read the text
itself through the host's approved read-only tools or broker. Do not make the
writer hand-select excerpts or reconstruct the book in a briefing packet when
the original is accessible. A typical request is:

```text
Read the complete manuscript at <path>, revision <snapshot>.
Assess reader engagement, character/relationship movement, and continuity.
Cite exact passages, report what you could not read, and distinguish taste
from contradiction. Diagnose; do not rewrite or consult author planning notes.
```

This reference supplies optional detail for choosing those lenses and interpreting
results. It is not a mandatory form to fill before every review. Use attachments
when direct reading is unavailable; use targeted context for a genuinely narrow
question. Prefer automatically recorded file/range receipts to manual preparation.

## Choose the job before choosing the lens

Editing terminology varies. State the actual deliverable instead of merely
asking for an "editor". Work from large decisions to small ones:

1. **Reader-response pass:** what experience does the prose actually create?
   Record specific engagement, confusion, surprise, drag, and emotional payoff.
   Do not diagnose or prescribe immediately. An LLM's simulated reaction is not
   a human beta reader's experience.
2. **Developmental pass:** diagnose arc, causality, pacing, agency, relationship
   movement, and the promise made by the opening. A coherent story may still be
   dull; a quiet or ambiguous scene is not defective because it lacks action.
3. **Continuity pass:** verify chronology, staging, knowledge, capabilities,
   objects, names, and setup/payoff against the actual prose. Use state documents
   as indexes and check their provenance, not as proof the prose communicates it.
4. **Line/copy pass:** after structural choices settle, inspect voice, subtext,
   rhythm, repetition, clarity, and mechanical consistency. Preserve deliberate
   irregularity. Proofread the reading edition after layout/export separately.

For a short or uncomplicated work, these can be labeled sections of one call.
They are separate analytical tasks, not independent reviewers. For a complicated
arc, choose a whole-arc developmental review and a separate continuity pass
when the additional cost is justified. Target line work to actual trouble spots;
do not pay to polish a scene likely to be removed. A chapter-only review cannot
certify an entire arc.

This order is a useful default, not an assembly line: discovery during a line
edit can reopen structure. Professional guidance places copyediting after
structural/stylistic work, while practitioners differ on service boundaries and
when developmental line edits help.[1][2]

## Protect the reviewer's independence

Distinguish **isolation** (fresh context), **model independence** (a different
model), and **human perspective** (an actual reader). None guarantees the others.
Several personas on one model do not become independent votes.

For an unprimed reader-response pass, provide the manuscript and a short,
non-spoiling audience/genre brief. Withhold the author's self-review, preferred
interpretation, previous verdicts, planned sequels, and explanations of what
"works". Do not conceal reader-facing information that would accompany the book.
For an intent-aware developmental or continuity pass, provide relevant contracts,
style/canon records, accepted ambiguities, and user requirements, distinctly
labeled as notes rather than story. Plans and rejected branches are not canon.

A single call with notes at the bottom is **not blind**: the model can attend to
all supplied text. A full-arc reader-response call also knows the ending. It can
analyze likely reading experience but cannot demonstrate real first-time surprise.
If a genuinely sequential experiment matters, withhold later chapters until
reactions are recorded; label it a different, explicitly authorized task.

Tell the reviewer what must remain intact, not what verdict to reach. "The hero
is physically invulnerable" protects a premise; "the restraint is beautifully
handled" primes praise. Frozen releases are immutable, but flaws in an opening
remain reviewable: propose changes only in an authorized child revision. Keep
**review scope** separate from **permission to edit**.

Human beta-reader practice supports both targeted questions and unprompted
responses; neither is universally best. Reader testimony identifies an experience,
whereas editorial expertise offers a diagnosis. Keep those categories separate.[3]

## Select lenses, not a universal scorecard

Start with the stage-appropriate [default selection](editorial-rubrics.md#default-lens-selection),
then use the detailed questions in [editorial-rubrics.md](editorial-rubrics.md).
Activate only the lenses that serve the story:

| Lens | Useful question | Evidence to return |
| --- | --- | --- |
| Reader promise and closure | What does the opening teach us to anticipate, and what actually pays it off? | Opening/ending anchors; unresolved promise versus deliberate openness |
| Scene function and pacing | Do adjacent scenes repeat the same emotional lesson? Where does attention change? | Two or more scenes and their distinct or repeated functions |
| Characterization and agency | Do choices arise from different wants, blind spots and pressures? | Decision, preceding pressure, later behavior |
| Emotional credibility and relationships | Do responses and changes in trust or closeness follow from lived experience? | Preceding experience, response and later behavior; acknowledge alternative readings rather than prescribe one emotional timetable |
| Knowledge and revelation | Who knows, suspects, misbelieves, or conceals what, and how did it reach them? | Establishing passage, transmission or inference, later use |
| Timeline and physical staging | Can people, objects and events occupy these positions in this order? | Both anchors, explicit assumptions, calculation if needed |
| World and capability | Are constraints stable without inventing an off-switch for convenience? | Established rule and apparent exception, including viewpoint uncertainty |
| Voice, dialogue and subtext | Are speakers distinguishable beyond names? Does narration explain what action already conveys? | Contrasting passages; identify the mechanism, not a generic "AI tell" label |
| Humor and wonder | Does the joke arise from this situation/person, or interrupt it? Does scale feel lived rather than advertised? | Setup, turn, target, timing; preserve examples that work |
| Freshness and thematic restraint | Are motifs developing, or do different scenes repeat familiar conclusions? | Repeated mechanism and a meaningful variation or counterexample |
| Line/copy and reader edition | Is the language intentionally shaped and consistently rendered? | Exact sentence or rendered location, plus the relevant style decision |

This table is a workshop synthesis of the existing rubrics, not a validated
psychometric scale. Do not average "humor 8/10" and "continuity 9/10" into a
quality certificate. No required number of jokes, twists, flaws, or resolutions.

## Supply enough context, and prove what was supplied

For a whole arc that fits, prefer **all of its prose** to an author's summary.
For a chapter pass, include the chapter, neighboring transitions, and the exact
earlier/later passages its consequential facts depend on. Disclose what is absent.
For a serial, distinguish current-arc text, relevant prior-arc text, and inherited
state; do not imply that a synopsis is a full-series reading.

Have the host capture a small receipt in the existing `reviews/` area or evidence
store as files are read; do not require the author to build a parallel dossier:

- exact revision or immutable snapshot; path/hash for every supplied file;
- chapter/scene inventory, order, source byte counts, missing or truncated files;
- task, selected lenses, role, actual model, and relevant output limits;
- measured input-token usage when the provider reports it; label estimates and
  distinguish bytes, words, input tokens, output and reasoning;
- material supplied versus explicitly withheld; read-only and privacy boundaries.

Check the **actual transport**: per-file and total attachment bounds, request size,
model context, output reservation, and any automatic compaction. Advertised
capacity, locally configured capacity, successfully accepted input, and useful
reasoning over that input are four different claims. Stop or split an oversized
packet; never silently truncate or present a partial review as whole-work coverage.
A large window is headroom, not a target to fill with chats, exports, obsolete
outlines, duplicate drafts, or the author's defense of the work.

For work too large to fit reliably, assign explicit scene ranges with overlapping
transitions and shared dependencies. Keep a coverage map. Follow local passes with
cross-range checks of knowledge transfers, object movement, promises/payoffs, and
major relationship turns using the original passages. Summaries help navigation;
they do not prove that an absent setup exists. Disclose unresolved coverage rather
than certifying the whole book from chapter-local checks.

Long-context research documents position and task-complexity sensitivity, not an
inevitable failure of every later model. RULER explicitly distinguishes synthetic
checks from realistic workloads. Neither it nor Lost in the Middle measures this
workshop's current reviewer on long-form fiction.[4][5]

## Portable handoff skeleton

Use this expanded skeleton only when the simple pointer-based request needs more
precision. Remove inactive lenses. Supply file pointers through the host's approved
read mechanism; use attachments only when necessary. Never include credentials.

```text
Role: independent editorial advisor, not coauthor.
Target: <exact revision, files, chapter/scene range, hashes in receipt>.
Audience/reader promise: <brief, non-spoiling for reader-response mode>.
Review mode: <unprimed reader-response | intent-aware | focused re-review>.
Included: <prose and, only if this mode permits, labeled state/intent notes>.
Excluded/unknown: <unseen chapters, planning, previous reviews, external canon>.
Review scope: <all supplied prose, even where edits need separate approval>.
Permitted actions: read and diagnose only; no mutation, delegation or rewriting.

Task order:
1. Reader response, if selected: identify anchored engagement, confusion and drag
   before prescribing fixes. Do not claim to be a human reader.
2. Diagnose using <two to four selected lenses>. Cross-check early/middle/late
   dependencies. Distinguish textual contradiction, plausible inference, reader
   concern, and stylistic preference. Search for counterevidence before filing.
3. Return concrete evidence and a minimal repair direction, not replacement prose.

Return:
- Coverage: actual supplied range; omitted/uncertain areas and selected lenses.
- Strengths to protect, with anchors; no compulsory praise.
- Prioritized findings: ID, lens, severity, chapter/scene plus short exact quote(s),
  reader consequence, counterevidence/alternative reading, confidence, repair scope.
- Contradictions require both passages. A missing setup requires the range checked
  and an uncertainty label; absence is harder to prove than a conflicting sentence.
- Rank major findings first and group minor repetitions, but impose no arbitrary
  finding-count cap. Report every distinct useful concern identified; do not invent
  findings to meet a quota. If an output limit prevents reporting everything found,
  disclose the omitted categories and request continuation rather than silently
  suppressing feedback.
- Name what would require structural revision versus a local correction.
- End with remaining uncertainty and useful questions for the human reader.
Stop when this bounded pass is complete. No automatic new review or coauthor loop.
```

## Adjudicate, revise, and learn

Verify quotations and chapter attribution against the exact reviewed snapshot.
A quotation occurring somewhere in the book does not validate its claimed scene
or interpretation. A coverage acknowledgment does not prove exhaustive attention.
Separate the observation from the diagnosis and from the proposed fix. The reader
may correctly notice drag while suggesting the wrong scene to delete.

For each material finding, record **accept, adapt, reject, or defer**, with evidence
and reason. Protect effective passages and intentional ambiguity. Do not resolve
every model concern by adding an explanatory line: deletion, resequencing, changed
action, or no change may be better. If a local patch would conceal a structural
problem, acknowledge the larger choice. The author remains responsible for prose.

After changes, re-read adjacent prose and affected earlier/later dependencies.
Use focused re-review when a revision changes causality, disclosure order, a major
relationship turn, arc structure or ending. A typo or narrow line repair can close
on a direct check. A new full pass is warranted when changes invalidate the old
review's scope, not whenever a model declines to say "approved". Preserve the old
receipt and identify what version the follow-up actually reviewed.

Carry learning forward at the right scope:

- story-specific choice -> its decisions/voice/continuity records;
- recurring craft mechanism -> existing workshop reference, with counterexamples;
- provider transport behavior -> host integration owner, not portable fiction canon.

Evaluate the workflow on real work: were quotes accurate, were concerns verified,
did accepted changes help the intended reader, and did they cause regressions?
If comparing prompt variants, freeze the same input, record model/settings and
relevant cost, and have the reader compare revisions without author/model labels
where practical. One successful call proves operation, not superiority. Avoid
optimizing to the judge's scores or polishing every story toward one house style.

Recent blind-peer-review research supports investigating constrained feedback,
but studied roughly 300-word science fiction, largely small writer models, with
human assessment limited to nine student annotators on one configuration. It is
not evidence that a multi-agent panel or repeated review improves a novella.
Use the useful distinction—critique without surrendering authorship—without
importing an entire orchestration system.[6]

## Sources and transfer limits

Professional/practitioner guidance informs stage separation and briefing. The
long-context studies motivate verification, not a numerical success guarantee.
The packet format, lens selection and re-review gates above are workshop design
choices to be evaluated, not settled empirical laws. Sources accessed 2026-09-06.

## Sources

[1] https://www.ciep.uk/resource/what-is-copyediting.html — What is copyediting?
[2] https://janefriedman.com/before-you-hire-a-developmental-editor-what-you-need-to-know — Before You Hire a Developmental Editor: What You Need to Know | Jane Friedman
[3] https://janefriedman.com/beta-readers — Beta Readers: Who, When, Why, and So What? | Jane Friedman
[4] https://arxiv.org/html/2307.03172v3 — Lost in the Middle: How Language Models Use Long Contexts
[5] https://github.com/NVIDIA/RULER — NVIDIA/RULER: This repo contains the source code for ...
[6] https://arxiv.org/html/2601.08003 — LLM Review: Enhancing Creative Writing via Blind Peer Review Feedback
