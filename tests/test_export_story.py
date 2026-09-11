import json
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / '.agents/skills/story-development/scripts/export_story.py'


@unittest.skipUnless(shutil.which('pandoc') and shutil.which('epubcheck'),
                     'install pandoc and epubcheck for export integration tests')
class ExportStoryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.story = Path(self.temp.name) / 'story'
        shutil.copytree(ROOT / 'examples/small-mercy', self.story)

    def run_export(self, *extra):
        return subprocess.run([sys.executable, str(SCRIPT), str(self.story),
            '--release', 'short-v1', '--edition', 'reading-v1',
            '--title', 'Small Mercy', '--author', 'Example author',
            '--language', 'en', '--rights', 'Private reading edition.', *extra],
            capture_output=True, text=True)

    def test_unsafe_identifiers_rejected_before_io(self):
        for field in ('release', 'edition'):
            for value in ('../outside', '/tmp/outside', 'bad/name'):
                with self.subTest(field=field, value=value):
                    result = self.run_export('--' + field, value)
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn('unsafe ' + field, result.stderr)

    def test_symlink_export_root_is_rejected(self):
        outside = Path(self.temp.name) / 'outside'
        outside.mkdir()
        (self.story / 'exports').symlink_to(outside, target_is_directory=True)
        result = self.run_export()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('exports must be a real directory', result.stderr)
        self.assertEqual(list(outside.iterdir()), [])

    def test_embedded_content_is_rejected(self):
        import hashlib
        frozen = self.story / 'release-contracts/short-v1'
        original = (frozen / 'approved-draft.md').read_text()
        for extra in ('![picture](file:///private-image.png)',
                      '<script>alert(1)</script>', '[link](https://example.com)'):
            with self.subTest(extra=extra):
                text = original + '\n\n' + extra + '\n'
                (frozen / 'approved-draft.md').write_text(text)
                manifest = json.loads((frozen / 'manifest.json').read_text())
                manifest['files']['approved-draft.md'] = hashlib.sha256(text.encode()).hexdigest()
                (frozen / 'manifest.json').write_text(json.dumps(manifest))
                result = self.run_export()
                self.assertNotEqual(result.returncode, 0)
                self.assertIn('text-only export rejects', result.stderr)
                self.assertFalse((self.story / 'exports').exists())

    def test_blank_metadata_is_rejected(self):
        result = self.run_export('--title', '   ')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('title must be nonempty', result.stderr)

    def test_existing_edition_is_unchanged(self):
        dest = self.story / 'exports/reading-v1'
        dest.mkdir(parents=True)
        (dest / 'keep').write_text('existing edition')
        result = self.run_export()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('edition already exists', result.stderr)
        self.assertEqual([p.name for p in dest.iterdir()], ['keep'])
        self.assertEqual((dest / 'keep').read_text(), 'existing edition')

    def test_tampered_release_is_rejected(self):
        (self.story / 'release-contracts/short-v1/approved-draft.md').write_text('changed')
        result = self.run_export()
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((self.story / 'exports').exists())

    def test_exports_named_release_not_working_draft(self):
        (self.story / 'working/manuscript.md').write_text('An unrelated unfinished working draft.\n')
        before = {p.relative_to(self.story): p.read_bytes()
                  for p in self.story.rglob('*') if p.is_file()}
        result = self.run_export()
        self.assertEqual(result.returncode, 0, result.stderr)
        dest = self.story / 'exports/reading-v1'
        receipt = json.loads((dest / 'receipt.json').read_text())
        self.assertEqual(receipt['release_id'], 'short-v1')
        self.assertEqual(receipt['epubcheck'], 'passed')
        self.assertTrue(receipt['pandoc_version'].startswith('pandoc '))
        self.assertIn('EPUBCheck', receipt['epubcheck_version'])
        self.assertNotEqual((self.story / 'working/manuscript.md').read_bytes(),
                            (self.story / 'release-contracts/short-v1/approved-draft.md').read_bytes())
        self.assertEqual((dest / 'story.md').read_bytes(),
                         (self.story / 'release-contracts/short-v1/approved-draft.md').read_bytes())
        with zipfile.ZipFile(dest / 'story.epub') as book:
            self.assertEqual(book.read('mimetype'), b'application/epub+zip')
            self.assertTrue(any(n.endswith('nav.xhtml') for n in book.namelist()))
        self.assertIn('Small Mercy', (dest / 'story.html').read_text())
        for path, content in before.items():
            self.assertEqual((self.story / path).read_bytes(), content, str(path))

    def test_chapter_boundaries_carry_no_layout_artifacts(self):
        draft = self.story / 'release-contracts/short-v1/approved-draft.md'
        filler = ' '.join(['Ordinary words carry the chapter.'] * 100)
        text = (f'# Small Mercy\n\n## Chapter One\n\nFirst. {filler}\n\n---\n\nStill first.\n\n'
                f'---\n\n## Chapter Two\n\nSecond. {filler}\n\n---\n')
        draft.write_text(text)
        manifest = self.story / 'release-contracts/short-v1/manifest.json'
        data = json.loads(manifest.read_text())
        import hashlib
        data['files']['approved-draft.md'] = hashlib.sha256(draft.read_bytes()).hexdigest()
        manifest.write_text(json.dumps(data, indent=2) + '\n')
        result = self.run_export()
        self.assertEqual(result.returncode, 0, result.stderr)
        with zipfile.ZipFile(self.story / 'exports/reading-v1/story.epub') as book:
            opf = book.read('EPUB/content.opf').decode()
            spine = opf[opf.index('<spine'):opf.index('</spine>')]
            self.assertNotIn('idref="nav"', spine)
            chapters = sorted(n for n in book.namelist() if '/text/ch' in n)
            self.assertEqual(len(chapters), 2, chapters)
            bodies = [book.read(n).decode() for n in chapters]
            css = '\n'.join(book.read(n).decode() for n in book.namelist()
                            if n.endswith('.css'))
            self.assertIn('page-break-before: auto;', css)
            self.assertIn('break-before: auto;', css)
            self.assertNotIn('page-break-before: always;', css)
            self.assertEqual(book.infolist()[0].filename, 'mimetype')
            self.assertEqual(book.infolist()[0].compress_type, zipfile.ZIP_STORED)
        self.assertIn('Chapter One', bodies[0])
        self.assertIn('Still first', bodies[0])
        self.assertEqual(bodies[0].count('<hr'), 1)  # the mid-chapter rule survives
        self.assertNotIn('<hr', bodies[1])
        self.assertIn('<h1 class="title">Small Mercy', (self.story / 'exports/reading-v1/story.html').read_text())


if __name__ == '__main__':
    unittest.main()
