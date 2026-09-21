"""Real CLI/converter tests for opt-in edition illustrations."""
import base64
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / '.agents/skills/story-development/scripts/export_story.py'
PNG = base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+aN6kAAAAASUVORK5CYII=')
ANCHOR = 'The customs desk on Lacuna Station had three temperatures.'


@unittest.skipUnless(shutil.which('pandoc') and shutil.which('epubcheck'),
                     'install pandoc and epubcheck for export integration tests')
class IllustrationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.story = Path(self.temp.name) / 'story'
        shutil.copytree(ROOT / 'examples/small-mercy', self.story)
        self.art = self.story / 'illustrations'
        self.art.mkdir()
        (self.art / 'plate.png').write_bytes(PNG)
        self.source = self.story / 'release-contracts/short-v1/approved-draft.md'
        self.manifest = self.art / 'plates.json'
        self.data = {'schema_version': 1, 'release_id': 'short-v1',
                     'source_sha256': hashlib.sha256(self.source.read_bytes()).hexdigest(),
                     'images': [{'after': ANCHOR, 'path': 'plate.png',
                                 'alt': 'A tiny test illustration.'}]}

    def run_export(self, write_manifest=True, illustrated=True):
        if write_manifest:
            self.manifest.write_text(json.dumps(self.data))
        command = [sys.executable, str(SCRIPT), str(self.story),
            '--release', 'short-v1', '--edition', 'illustrated-v1',
            '--title', 'Small Mercy', '--author', 'Example author',
            '--language', 'en', '--rights', 'Private reading edition.']
        if illustrated:
            command += ['--illustrations', str(self.manifest)]
        return subprocess.run(command, capture_output=True, text=True)

    def replace_fixture_prose(self, text):
        self.source.write_text(text)
        manifest = self.source.parent / 'manifest.json'
        data = json.loads(manifest.read_text())
        digest = hashlib.sha256(self.source.read_bytes()).hexdigest()
        data['files']['approved-draft.md'] = digest
        manifest.write_text(json.dumps(data))
        self.data['source_sha256'] = digest

    def test_plates_cannot_supply_prose_anchors(self):
        self.data['images'][0]['alt'] = 'No such prose paragraph.'
        self.data['images'].append({'after': 'No such prose paragraph.',
                                   'path': 'plate.png', 'alt': 'Second plate.'})
        result = self.run_export()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('exactly one paragraph', result.stderr)
        self.assertFalse((self.story / 'exports').exists())

    def test_two_chapters_with_alt_matching_later_anchor(self):
        filler = ' '.join(['Ordinary words carry the chapter.'] * 100)
        self.replace_fixture_prose(f'# Small Mercy\n\n## Chapter One\n\nAlpha.\n\n{filler}\n\n'
                                   f'## Chapter Two\n\n**Beta.**\n\n{filler}\n')
        self.data['images'] = [
            {'after': 'Alpha.', 'path': 'plate.png', 'alt': 'Beta.'},
            {'after': 'Beta.', 'path': 'plate.png', 'alt': 'Last plate.'}]
        result = self.run_export()
        self.assertEqual(result.returncode, 0, result.stderr)
        dest = self.story / 'exports/illustrated-v1'
        with zipfile.ZipFile(dest / 'story.epub') as book:
            names = sorted(n for n in book.namelist() if '/text/ch' in n)
            self.assertEqual(len(names), 2)
            bodies = [book.read(n).decode() for n in names]
        self.assertLess(bodies[0].index('Alpha.'), bodies[0].index('<img'))
        self.assertIn('alt="Beta."', bodies[0])
        self.assertNotIn('Last plate.', bodies[0])
        self.assertLess(bodies[1].index('<strong>Beta.</strong>'), bodies[1].index('<img'))
        self.assertIn('alt="Last plate."', bodies[1])
        receipt = json.loads((dest / 'receipt.json').read_text())
        self.assertEqual([r['after'] for r in receipt['illustrations']['images']], ['Alpha.', 'Beta.'])

    def test_identifier_preserves_default_and_binds_art(self):
        result = self.run_export(illustrated=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        dest = self.story / 'exports/illustrated-v1'
        def identifier():
            with zipfile.ZipFile(dest / 'story.epub') as book:
                opf = ET.fromstring(book.read('EPUB/content.opf'))
            element = opf.find('.//{http://purl.org/dc/elements/1.1/}identifier')
            self.assertIsNotNone(element)
            assert element is not None
            return element.text
        plain = identifier()
        self.assertEqual(plain, 'urn:sha256:' + hashlib.sha256(
            self.source.read_bytes() + b'illustrated-v1').hexdigest())
        shutil.rmtree(dest)  # this test owns its temporary output
        self.assertEqual(self.run_export().returncode, 0)
        illustrated = identifier()
        self.assertNotEqual(plain, illustrated)
        shutil.rmtree(dest)
        self.data['images'][0]['alt'] = 'A changed description.'
        self.assertEqual(self.run_export().returncode, 0)
        self.assertNotEqual(illustrated, identifier())

    def test_manifest_and_image_user_errors(self):
        original = self.manifest
        for mode in ('malformed', 'outside', 'directory', 'image-directory'):
            with self.subTest(mode=mode):
                self.manifest = original
                if mode == 'malformed':
                    self.manifest.write_text('{')
                    result = self.run_export(write_manifest=False)
                elif mode == 'outside':
                    self.manifest = Path(self.temp.name) / 'external.json'
                    result = self.run_export()
                elif mode == 'directory':
                    self.manifest = self.art
                    result = self.run_export(write_manifest=False)
                else:
                    self.data['images'][0]['path'] = '.'
                    result = self.run_export()
                self.assertNotEqual(result.returncode, 0)
                self.assertIn('export failed:', result.stderr)
                self.assertNotIn('Traceback', result.stderr)
                self.assertFalse((self.story / 'exports').exists())

    def test_ambiguous_prose_anchor(self):
        self.replace_fixture_prose(self.source.read_text() + '\n\n' + ANCHOR + '\n')
        result = self.run_export()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('exactly one paragraph', result.stderr)
        self.assertFalse((self.story / 'exports').exists())

    def test_jpeg_packaging_and_extension_mismatch(self):
        # Valid one-pixel JPEG; no image-library dependency in this suite.
        jpeg = base64.b64decode(
            '/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJCQwLDBgNDRgyIRwhMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjL/wAARCAABAAEDASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQAAAF9AQIDAAQRBRIhMUEGE1FhByJxFDKBkaEII0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqDhIWGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi4+Tl5ufo6erx8vP09fb3+Pn6/8QAHwEAAwEBAQEBAQEBAQAAAAAAAAECAwQFBgcICQoL/8QAtREAAgECBAQDBAcFBAQAAQJ3AAECAxEEBSExBhJBUQdhcRMiMoEIFEKRobHBCSMzUvAVYnLRChYkNOEl8RcYGRomJygpKjU2Nzg5OkNERUZHSElKU1RVVldYWVpjZGVmZ2hpanN0dXZ3eHl6goOEhYaHiImKkpOUlZaXmJmaoqOkpaanqKmqsrO0tba3uLm6wsPExcbHyMnK0tPU1dbX2Nna4uPk5ebn6Onq8vP09fb3+Pn6/9oADAMBAAIRAxEAPwD3+iiigD//2Q==')
        (self.art / 'plate.png').write_bytes(jpeg)
        result = self.run_export()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('PNG or JPEG', result.stderr)
        (self.art / 'plate.jpg').write_bytes(jpeg)
        self.data['images'][0]['path'] = 'plate.jpg'
        result = self.run_export()
        self.assertEqual(result.returncode, 0, result.stderr)
        dest = self.story / 'exports/illustrated-v1'
        self.assertIn('data:image/jpeg;base64,', (dest / 'story.html').read_text())
        with zipfile.ZipFile(dest / 'story.epub') as book:
            names = [n for n in book.namelist() if n.endswith('.jpg')]
            self.assertEqual(len(names), 1)
            self.assertEqual(book.read(names[0]), jpeg)
            self.assertIn('media-type="image/jpeg"', book.read('EPUB/content.opf').decode())

    def test_local_plate_packaged_without_changing_frozen_prose(self):
        before = self.source.read_bytes()
        result = self.run_export()
        self.assertEqual(result.returncode, 0, result.stderr)
        dest = self.story / 'exports/illustrated-v1'
        self.assertEqual(self.source.read_bytes(), before)
        self.assertEqual((dest / 'story.md').read_bytes(), before)
        html = (dest / 'story.html').read_text()
        self.assertIn('data:image/png;base64,', html)
        self.assertIn('alt="A tiny test illustration."', html)
        self.assertLess(html.index(ANCHOR), html.index('data:image/png;base64,'))
        self.assertLess(html.index('data:image/png;base64,'), html.index('Green meant'))
        with zipfile.ZipFile(dest / 'story.epub') as book:
            images = [name for name in book.namelist() if name.endswith('.png')]
            self.assertEqual(len(images), 1)
            self.assertEqual(book.read(images[0]), PNG)
            chapters = [ET.fromstring(book.read(name)) for name in book.namelist()
                        if '/text/ch' in name and name.endswith('.xhtml')]
            plates = [e for chapter in chapters for e in chapter.iter()
                      if e.tag.endswith('}img')]
            self.assertEqual(len(plates), 1)
            self.assertEqual(plates[0].get('alt'), 'A tiny test illustration.')
        receipt = json.loads((dest / 'receipt.json').read_text())
        self.assertEqual(receipt['illustrations']['manifest_sha256'],
                         hashlib.sha256(self.manifest.read_bytes()).hexdigest())
        self.assertEqual(receipt['illustrations']['images'][0]['sha256'],
                         hashlib.sha256(PNG).hexdigest())
        self.assertEqual(receipt['epubcheck'], 'passed')


    def test_unsafe_or_ambiguous_input_fails_without_an_edition(self):
        original = json.loads(json.dumps(self.data))
        cases = [
            ('wrong source', {'source_sha256': '0' * 64}, None),
            ('wrong release', {'release_id': 'novella-v1'}, None),
            ('empty images', {'images': []}, None),
            ('unknown field', {'remote': True}, None),
            ('bad root', [], None),
            ('missing alt', None, {'alt': ''}),
            ('missing paragraph', None, {'after': 'No such paragraph.'}),
            ('external file', None, {'path': '/etc/hosts'}),
            ('traversal', None, {'path': '../illustrations/plate.png'}),
            ('url', None, {'path': 'https://example.com/image.png'}),
            ('file uri', None, {'path': 'file:///etc/hosts'}),
            ('unknown image field', None, {'width': '90%'}),
        ]
        for label, root_change, image_change in cases:
            with self.subTest(label=label):
                self.data = json.loads(json.dumps(original))
                if isinstance(root_change, dict):
                    self.data.update(root_change)
                elif root_change is not None:
                    self.data = root_change
                if image_change:
                    self.data['images'][0].update(image_change)
                result = self.run_export()
                self.assertNotEqual(result.returncode, 0, label)
                self.assertIn('export failed:', result.stderr)
                self.assertNotIn('Traceback', result.stderr)
                self.assertFalse((self.story / 'exports').exists())

    def test_duplicate_anchor_rejected(self):
        self.data['images'].append(dict(self.data['images'][0]))
        result = self.run_export()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('duplicate illustration anchor', result.stderr)
        self.assertFalse((self.story / 'exports').exists())

    def test_symlink_and_disguised_nonimage_rejected(self):
        image = self.art / 'plate.png'
        image.unlink()
        outside = Path(self.temp.name) / 'outside.png'
        outside.write_bytes(PNG)
        image.symlink_to(outside)
        result = self.run_export()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('symlink', result.stderr)
        image.unlink()
        image.write_bytes(b'<svg xmlns="http://www.w3.org/2000/svg"></svg>')
        result = self.run_export()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('PNG or JPEG', result.stderr)
        self.assertFalse((self.story / 'exports').exists())

    def test_symlinked_manifest_rejected(self):
        actual = self.art / 'real.json'
        actual.write_text(json.dumps(self.data))
        self.manifest.symlink_to(actual)
        result = self.run_export()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('symlink', result.stderr)
        self.assertFalse((self.story / 'exports').exists())


if __name__ == '__main__':
    unittest.main()
