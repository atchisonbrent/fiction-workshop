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
Chapter files are not read; frozen prose order is authoritative. EPUB splitting
uses level-two headings (level-one headings also split), matching chaptered
workshop manuscripts. Manuscripts without chapters still export.

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

## Developer checks

`python3 -m unittest discover -s tests -v` includes real converter integration
tests when both programs are installed; otherwise export tests explicitly skip.
A passing dependency-free suite is not an export integration receipt. Do not
claim export verification without running that suite with dependencies present.
