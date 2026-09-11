# Reading editions

Keep canonical stories in the user's existing private content repository when
one exists. Task evidence folders are not a substitute for that repository.
Resolve the destination before drafting; do not publish private prose in the
public tooling repository. An immutable story release is a source snapshot,
not permission for public distribution.

## Export a frozen version

Optional dependencies: Pandoc (tested with 3.11) and EPUBCheck (tested with
5.3.0) on PATH; EPUBCheck needs Java. These are not required for normal story
validation. Official references: https://pandoc.org/epub.html and
https://www.w3.org/publishing/epubcheck/ . Use your supported package manager.

Resolve SCRIPT from the installed skill's directory, then run:

```text
python3 SCRIPT/scripts/export_story.py /path/to/private-story \
  --release short-v1 --edition reading-v1 \
  --title "Story title" --author "Author or attribution" \
  --language en --rights "Private reading edition; rights notice here."
```

The command validates the full story and frozen manifests, reads only the named
release's approved-draft.md as prose, and creates `exports/reading-v1/` containing
`story.epub`, `story.html`, an exact `story.md` sharing copy, `epubcheck.txt`, and
`receipt.json` with source/output hashes, metadata, and converter versions.
The receipt hashes the generated files, not itself; retain it in version control
for an external integrity record. EPUBCheck success logs preserve stdout only;
the receipt records a passing exit status, not a promise of zero warnings. A
missing named release fails with a filesystem error and creates no edition.
No outline, review, kernel, or canon is included in reading content. Rights and
author are explicit user-supplied edition metadata, not a legal determination.

The exporter supports text-only Markdown with headings and inline formatting.
It rejects raw markup, images and links instead of silently dropping them or
fetching resources. YAML prose metadata is ignored in favor of explicit export
metadata. Pandoc runs in sandbox mode without filters or custom templates.
Chapter files are not read; frozen prose order is authoritative. The current
chapter-boundary exporter removes a matching redundant manuscript title heading,
promotes the remaining headings one level, and splits at level one. It omits the
navigation document from the linear spine while retaining the reader's contents
menu, and removes horizontal rules immediately before chapter headings or at the
end. In-chapter rules remain. Inspect the generated package rather than assuming
these transformations suit every heading hierarchy. Manuscripts without chapters
still export.

An existing edition is never overwritten. Choose a new edition ID for formatting
changes; this does not require a new story release if prose stays unchanged.
Exports are separate from frozen source. Generation/checking finishes in a temp
folder before destination creation; failed copies remove the new destination.
Do not run concurrent exporters or edit/swap directories while exporting: this
local CLI is not a hostile-filesystem or multi-writer service. It makes no
byte-reproducibility promise across converter versions or timestamps.

## Deliver, do not just store

EPUB is the default sustained-reading artifact; HTML is a quick preview and
Markdown is for source review. Put private download links in the content repo's
reader index. Verify the download retrieves the exact edition. A local filesystem
link or a desktop page tested at phone width is not cross-device delivery.
Never expose private works through a public site or release without explicit
publication authorization. A private repository's file/download UI is sufficient;
no custom server or continuous publishing job is required.

Before calling a reading edition ready, check chapter order and text preservation,
inspect HTML at a narrow width, and open the EPUB in an actual reader. EPUBCheck
validates format, not content or reader usability. If reader access is blocked,
state the precise gap. Treat importing into a cloud-synced personal library as a
separate effect; prefer a temporary/local reader for verification.

## Chapter assembly and continuous-scroll acceptance

**Heading semantics and layout are separate decisions.** Promoting `h2` chapters
into `h1` changes which stylesheet rules apply. Pandoc 3.11's bundled `h1`
rule introduces `page-break-before: always`, a `3em` top margin, `2em` font size,
and `150%` line height. Do not inherit those accidentally merely to obtain one
chapter per spine document.

For the tested Books continuous-scroll correction, replace that bundled `h1`
rule in the generated EPUB stylesheet with:

```css
h1 {
  margin: 1.5em 0 0 0;
  font-size: 1.5em;
  page-break-before: auto;
  break-before: auto;
  line-height: 135%;
}
```

These restore the earlier chapter-heading dimensions and remove the forced page
break. This is a tested compatibility recipe, not an EPUB requirement or a claim
that every reading system rejects forced breaks. A heading-scoped stylesheet can
be designed separately; the exact tested correction above applied to all `h1`
elements, including the title page.

**Implementation boundary:** the current `export_story.py` chapter-boundary
change does not yet apply this CSS correction automatically. Its output is not
the final tested recipe until the stylesheet is corrected and the package is
validated again. Do not treat the earlier structural cleanup alone as the fix.

### Reproducible assembly/check sequence

1. Export the newest frozen source under a new edition ID. Never edit the frozen
   draft or overwrite a previous reading edition to make a formatting change.
2. Inspect the actual OPF spine: title page then chapters in order, no redundant
   title-only document. Keep a valid navigation document and chapter anchors;
   a visible contents page is optional, not a reason to lose the contents menu.
3. Inspect the generated CSS after heading transformations. Apply the rule above
   for this compatibility path. Keep prose and unrelated layout unchanged.
4. If repairing an existing EPUB, work on a new copy, preserve all chapter XHTML
   bytes, and allowlist changed members: stylesheet, package identifier, NCX
   identifier, and edition label on the title page. Preserve ZIP structure,
   especially the first, uncompressed `mimetype` entry. Use a new identifier
   consistent with the new edition; do not reuse a previously imported identity.
5. Verify **every** chapter's paragraph sequence/order against the prior edition
   (or byte equality when XHTML was not regenerated). Count chapters
   programmatically and resolve every navigation target and fragment. Retain
   source/output hashes and converter versions in the private edition receipt.
6. Run EPUBCheck on the final packaged bytes, after any CSS/package changes.
   Inspect the CSS in a browser as a limited check: the computed heading break
   must be `auto`, and the correct opening paragraph must be present. Neither
   this nor EPUBCheck proves native reader scrolling.
7. Import the exact new edition only when authorized, read back its identity,
   then test **on the affected reader**: scroll from the final paragraphs of one
   chapter into the next heading and opening; scroll back; check that no text
   skips or snaps to a different position. Exercise subsequent chapter boundaries
   and the contents menu. Record the device/mode and which checks actually ran.

### Evidence boundary

A reader reported that the CSS-corrected edition resolved the skipping in iPhone
Books continuous scrolling on iOS 27 beta 8. All chapter XHTML and navigation
were unchanged from the preceding failing edition; only the heading rule and
edition identity/label changed. This supports the recipe in that environment.
It does not isolate forced breaks from heading dimensions or import identity,
prove an Apple-internal root cause, or establish compatibility for all devices.
The preceding removal of redundant spine documents and chapter-join rules did
not resolve the reported problem on its own.

When an edition passes EPUBCheck but fails this native test, report it as a
readability failure. Identical chapter bytes across two editions do not prove
that the reader alone is at fault: package layout, CSS and reader state remain
variables. Keep private manuscripts, screenshots, IDs and detailed receipts in
the private works repository, not in this portable workshop.

## Developer checks

`python3 -m unittest discover -s tests -v` includes real converter integration
tests when both programs are installed; otherwise export tests explicitly skip.
A passing dependency-free suite is not an export integration receipt. Do not
claim export verification without running that suite with dependencies present.
