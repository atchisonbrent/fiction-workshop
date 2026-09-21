#!/usr/bin/env python3
"""Export a validated, frozen story release to private EPUB and HTML editions.

Requires Pandoc and EPUBCheck on PATH. Does not publish, alter source, or import
into a reader. Text-only by default; optional local plates use --illustrations.
Resources embedded in manuscript Markdown remain unsupported.
"""
from __future__ import annotations

import argparse
import base64
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


def local_art_file(path: Path, story: Path) -> Path:
    """Require a regular story-local file and reject below-root symlink traversal.

    System ancestors (for example macOS /var) and a component resolving exactly
    to the story root may be aliases; links encountered below it are rejected.
    Concurrent filesystem edits are not supported.
    """
    resolved = path.resolve()
    if not resolved.is_relative_to(story):
        raise ValueError('illustration file is outside the story or uses a symlink')
    absolute = path.absolute()
    for current in (absolute, *absolute.parents):
        if current.resolve() == story:
            break
        if current.is_symlink():
            raise ValueError('illustration files must not use symlinks')
    else:
        raise ValueError('illustration path does not enter the story root')
    if not resolved.is_file():
        raise ValueError('illustration input must be a regular file')
    return resolved


def add_illustrations(doc: dict, manifest: Path, story: Path,
                      release: str, manuscript: bytes) -> dict:
    """Insert local PNG/JPEG plates into the AST, never into frozen prose."""
    manifest = local_art_file(manifest, story)
    raw = manifest.read_bytes()
    spec = json.loads(raw)
    if (not isinstance(spec, dict)
            or set(spec) != {'schema_version', 'release_id', 'source_sha256', 'images'}
            or type(spec['schema_version']) is not int or spec['schema_version'] != 1
            or spec['release_id'] != release
            or spec['source_sha256'] != digest(manuscript)):
        raise ValueError('illustration manifest does not match frozen release or schema')
    if not isinstance(spec['images'], list) or not spec['images']:
        raise ValueError('illustration manifest requires a nonempty images list')
    records = []
    anchors = set()
    insertions = []
    for item in spec['images']:
        if (not isinstance(item, dict) or set(item) != {'after', 'path', 'alt'}
                or any(not isinstance(value, str) or not value.strip()
                       for value in item.values())):
            raise ValueError('each illustration requires only nonempty after, path and alt strings')
        if item['after'] in anchors:
            raise ValueError('duplicate illustration anchor')
        anchors.add(item['after'])
        matches = [i for i, block in enumerate(doc['blocks'])
                   if block.get('t') == 'Para' and stringify(block) == item['after']]
        if len(matches) != 1:
            raise ValueError('illustration anchor must match exactly one paragraph')
        name = item['path']
        if (Path(name).is_absolute() or '..' in Path(name).parts
                or any(c in name for c in ':\\\x00\r\n')):
            raise ValueError('illustration path must be local and relative without traversal')
        image = local_art_file(manifest.parent / name, story)
        content = image.read_bytes()
        if image.suffix.lower() == '.png' and content.startswith(b'\x89PNG\r\n\x1a\n'):
            media_type = 'image/png'
        elif image.suffix.lower() in {'.jpg', '.jpeg'} and content.startswith(b'\xff\xd8\xff'):
            media_type = 'image/jpeg'
        else:
            raise ValueError('illustrations must be PNG or JPEG files with matching signatures')
        uri = 'data:' + media_type + ';base64,' + base64.b64encode(content).decode('ascii')
        plate = {'t': 'Para', 'c': [{'t': 'Image', 'c': [
            ['', [], []], [{'t': 'Str', 'c': item['alt']}], [uri, '']]}]}
        insertions.append((matches[0] + 1, plate))
        records.append({'path': image.relative_to(story).as_posix(),
                        'sha256': digest(content), 'alt': item['alt'], 'after': item['after']})
    # All anchors resolve against original prose. Alt text must never create an
    # anchor, and reverse insertion preserves every original block index.
    for index, plate in sorted(insertions, key=lambda pair: pair[0], reverse=True):
        doc['blocks'].insert(index, plate)
    return {'manifest_sha256': digest(raw), 'images': records}


def export_story(story: Path, release: str, edition: str, title: str,
                 author: str, language: str, rights: str,
                 illustrations: Path | None = None) -> Path:
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
        art = (add_illustrations(doc, illustrations, story, release, manuscript)
               if illustrations is not None else None)
        # Include selected artwork in illustrated-edition identity without changing
        # the identifier of existing text-only exports.
        identity = manuscript + edition.encode()
        if art is not None:
            identity += json.dumps(art, sort_keys=True).encode()
        # Metadata is explicit edition data, never inherited from prose YAML.
        doc['meta'] = {key: {'t': 'MetaString', 'c': value} for key, value in {
            'title': title, 'author': author, 'lang': language, 'rights': rights,
            'subtitle': f'{release} / {edition}',
            'identifier': 'urn:sha256:' + digest(identity),
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
        if art is not None:
            receipt['illustrations'] = art
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
    parser.add_argument('--illustrations', type=Path,
                        help='opt-in local illustration manifest for this edition')
    for name in ('release', 'edition', 'title', 'author', 'language', 'rights'):
        parser.add_argument('--' + name, required=True)
    args = parser.parse_args()
    try:
        output = export_story(args.story, args.release, args.edition, args.title,
                              args.author, args.language, args.rights, args.illustrations)
    except (ValueError, OSError, subprocess.TimeoutExpired) as exc:
        print(f'export failed: {exc}', file=sys.stderr)
        return 1
    print(f'exported: {output}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
