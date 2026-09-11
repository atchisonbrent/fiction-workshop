#!/usr/bin/env python3
"""Export a validated, frozen story release to private EPUB and HTML editions.

Requires Pandoc and EPUBCheck on PATH. Does not publish, alter source, or import
into a reader. This text-only exporter intentionally rejects embedded resources.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

from validate_story import RELEASE_ID_RE, validate_story


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def run(command: list[str], *, data: str | None = None, cwd: Path) -> str:
    result = subprocess.run(command, input=data, cwd=cwd, text=True,
                            capture_output=True, timeout=120, check=False)
    if result.returncode:
        raise ValueError(f'{command[0]} failed: {result.stderr or result.stdout}')
    return result.stdout


def stringify(node) -> str:
    """Plain text of Pandoc inline nodes, whitespace-normalised."""
    if isinstance(node, dict):
        if node.get('t') in {'Code', 'Math'}:
            return node['c'][-1]
        if node.get('t') == 'Str':
            return node['c']
        if node.get('t') in {'Space', 'SoftBreak', 'LineBreak'}:
            return ' '
        return stringify(node.get('c'))
    if isinstance(node, list):
        return ''.join(stringify(child) for child in node)
    return ''


def tidy_chapter_boundaries(blocks: list, title: str) -> list:
    """Remove layout artifacts that sit exactly on reader chapter boundaries.

    Concatenated chapter sources leave a horizontal rule before every chapter
    heading and after the last one; a lone top-level heading repeating the
    edition title becomes a one-line spine document behind the first chapter
    (and Pandoc's EPUB writer inserts one itself unless the body opens with a
    level-1 heading). Both are valid EPUB and both give scrolling readers an
    extra element to re-anchor on at the seam. So: drop the title heading,
    promote every remaining heading one level so chapters are level 1, and
    drop rules that abut a chapter heading or end the book. Rules inside a
    chapter are kept.
    """
    leading_title = (blocks and blocks[0].get('t') == 'Header'
                     and blocks[0]['c'][0] == 1
                     and ' '.join(stringify(blocks[0]['c'][2]).split()) == ' '.join(title.split()))
    later_h1 = any(b.get('t') == 'Header' and b['c'][0] == 1 for b in blocks[1:])
    if leading_title and (not later_h1 or (
            len(blocks) > 1 and blocks[1].get('t') == 'Header')):
        blocks = blocks[1:]
    elif (blocks and blocks[0].get('t') == 'Header' and blocks[0]['c'][0] == 1
          and not later_h1 and any(b.get('t') == 'Header' for b in blocks[1:])):
        raise ValueError('ambiguous manuscript title/chapter hierarchy; match edition title to source')
    if not any(b.get('t') == 'Header' and b['c'][0] == 1 for b in blocks):
        blocks = [{**b, 'c': [b['c'][0] - 1, *b['c'][1:]]} if b.get('t') == 'Header' else b
                  for b in blocks]
    kept: list = []
    for index, block in enumerate(blocks):
        if block.get('t') == 'HorizontalRule':
            following = blocks[index + 1] if index + 1 < len(blocks) else None
            at_boundary = following is None or (
                following.get('t') == 'Header' and following['c'][0] == 1)
            if at_boundary:
                continue
        kept.append(block)
    return kept


def correct_epub_headings(path: Path) -> None:
    """Apply the reader-tested rule, preserving every other package member.

    Fail closed if Pandoc changes its bundled rule; never silently publish an
    edition without the correction. This runs in staging before EPUBCheck.
    """
    old = ('h1 {\n  margin: 3em 0 0 0;\n  font-size: 2em;\n'
           '  page-break-before: always;\n  line-height: 150%;\n}')
    new = ('h1 {\n  margin: 1.5em 0 0 0;\n  font-size: 1.5em;\n'
           '  page-break-before: auto;\n  break-before: auto;\n'
           '  line-height: 135%;\n}')
    with zipfile.ZipFile(path) as book:
        infos = book.infolist()
        contents = {info.filename: book.read(info) for info in infos}
    css_files = [name for name in contents if name.endswith('.css')]
    matches = [name for name in css_files if old.encode() in contents[name]]
    if len(matches) != 1 or contents[matches[0]].count(old.encode()) != 1:
        raise ValueError('unsupported Pandoc EPUB heading CSS; review converter output')
    name = matches[0]
    contents[name] = contents[name].replace(old.encode(), new.encode())
    replacement = path.with_suffix('.corrected.epub')
    with zipfile.ZipFile(replacement, 'w') as book:
        for info in infos:
            book.writestr(info, contents[info.filename])
    replacement.replace(path)


def export_story(story: Path, release: str, edition: str, title: str,
                 author: str, language: str, rights: str) -> Path:
    for label, value in (('title', title), ('author', author),
                         ('language', language), ('rights', rights)):
        if not value.strip():
            raise ValueError(f'{label} must be nonempty')
    for label, value in (('release', release), ('edition', edition)):
        if not RELEASE_ID_RE.fullmatch(value):
            raise ValueError(f'unsafe {label} identifier')
    story = story.resolve()
    exports = story / 'exports'
    if exports.is_symlink() or (exports.exists() and not exports.is_dir()):
        raise ValueError('exports must be a real directory')
    destination = exports / edition
    if destination.exists() or destination.is_symlink():
        raise ValueError('edition already exists; choose a new edition ID')
    validate_story(story)
    source = story / 'release-contracts' / release
    manuscript = (source / 'approved-draft.md').read_bytes()
    with tempfile.TemporaryDirectory(prefix='story-export-') as temp:
        stage = Path(temp)
        doc = json.loads(run(['pandoc', '--sandbox', '-f', 'markdown', '-t', 'json'],
                             data=manuscript.decode('utf-8'), cwd=stage))
        pending = [doc['blocks']]
        while pending:
            node = pending.pop()
            if isinstance(node, dict):
                if node.get('t') in {'RawBlock', 'RawInline', 'Image', 'Link'}:
                    raise ValueError('text-only export rejects raw markup, images and links')
                pending.extend(node.values())
            elif isinstance(node, list):
                pending.extend(node)
        doc['blocks'] = tidy_chapter_boundaries(doc['blocks'], title)
        # Metadata is explicit edition data, never inherited from prose YAML.
        doc['meta'] = {key: {'t': 'MetaString', 'c': value} for key, value in {
            'title': title, 'author': author, 'lang': language, 'rights': rights,
            'subtitle': f'{release} / {edition}',
            'identifier': 'urn:sha256:' + digest(manuscript + edition.encode()),
        }.items()}
        payload = json.dumps(doc, ensure_ascii=False)
        # Chapters are level-1 headings, one spine document each. The EPUB keeps
        # its required nav document for the reader's contents menu but omits it
        # from the linear spine (Pandoc adds it only with --toc), so nothing sits
        # between the title page and chapter one.
        for target, name, toc in [('html5', 'story.html', ['--toc']),
                                  ('epub3', 'story.epub', [])]:
            run(['pandoc', '--sandbox', '-f', 'json', '-t', target, '--standalone',
                 *toc, '--split-level=1', '-o', name],
                data=payload, cwd=stage)
        correct_epub_headings(stage / 'story.epub')
        check = run(['epubcheck', 'story.epub'], cwd=stage)
        (stage / 'story.md').write_bytes(manuscript)
        (stage / 'epubcheck.txt').write_text(check, encoding='utf-8')
        receipt = {
            'schema_version': 1, 'release_id': release, 'edition_id': edition,
            'source_sha256': digest(manuscript), 'epubcheck': 'passed',
            'metadata': {'title': title, 'author': author, 'language': language,
                         'rights': rights},
            'pandoc_version': run(['pandoc', '--version'], cwd=stage).splitlines()[0],
            'epubcheck_version': run(['epubcheck', '--version'], cwd=stage).strip(),
            'files': {p.name: digest(p.read_bytes()) for p in sorted(stage.iterdir())},
        }
        (stage / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n',
                                            encoding='utf-8')
        destination = story / 'exports' / edition
        destination.parent.mkdir(exist_ok=True)
        destination.mkdir()  # Never overwrite an edition.
        try:
            for path in stage.iterdir():
                shutil.copyfile(path, destination / path.name)
        except BaseException:
            shutil.rmtree(destination)
            raise
    return destination


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('story', type=Path)
    for name in ('release', 'edition', 'title', 'author', 'language', 'rights'):
        parser.add_argument('--' + name, required=True)
    args = parser.parse_args()
    try:
        output = export_story(args.story, args.release, args.edition, args.title,
                              args.author, args.language, args.rights)
    except (ValueError, OSError, subprocess.TimeoutExpired) as exc:
        print(f'export failed: {exc}', file=sys.stderr)
        return 1
    print(f'exported: {output}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
