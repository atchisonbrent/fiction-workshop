"""Dependency-free checks for layout correction and source preservation."""
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / '.agents/skills/story-development/scripts'))
from export_story import correct_epub_headings, tidy_chapter_boundaries, stringify


def heading(level, title):
    return {'t': 'Header', 'c': [level, ['', [], []], [{'t': 'Str', 'c': title}]]}


class LayoutTests(unittest.TestCase):
    def test_hierarchy_variants(self):
        para = {'t': 'Para', 'c': [{'t': 'Str', 'c': 'Unchanged prose'}]}
        for blocks in ([heading(1, 'Book'), heading(2, 'One'), para],
                       [heading(2, 'One'), para],
                       [heading(1, 'Book'), heading(1, 'One'), para]):
            result = tidy_chapter_boundaries(blocks, 'Book')
            self.assertEqual(result, [heading(1, 'One'), para])
        self.assertEqual(tidy_chapter_boundaries([heading(1, 'Book'), para], 'Book'), [para])
        with self.assertRaisesRegex(ValueError, 'ambiguous'):
            tidy_chapter_boundaries([heading(1, 'Other'), heading(2, 'One'), para], 'Book')
        self.assertEqual(stringify({'t': 'Code', 'c': [['', [], []], 'Book']}), 'Book')

    def test_correction_preserves_package_and_fails_closed(self):
        old = ('h1 {\n  margin: 3em 0 0 0;\n  font-size: 2em;\n'
               '  page-break-before: always;\n  line-height: 150%;\n}')
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'book.epub'
            with zipfile.ZipFile(path, 'w') as book:
                book.writestr('mimetype', b'application/epub+zip', compress_type=zipfile.ZIP_STORED)
                book.writestr('chapter.xhtml', b'<p>Exact prose.</p>', compress_type=zipfile.ZIP_DEFLATED)
                book.writestr('style.css', old.encode(), compress_type=zipfile.ZIP_DEFLATED)
            correct_epub_headings(path)
            with zipfile.ZipFile(path) as book:
                self.assertEqual(book.namelist(), ['mimetype', 'chapter.xhtml', 'style.css'])
                self.assertEqual(book.infolist()[0].compress_type, zipfile.ZIP_STORED)
                self.assertEqual(book.read('chapter.xhtml'), b'<p>Exact prose.</p>')
                self.assertEqual(book.getinfo('chapter.xhtml').compress_type, zipfile.ZIP_DEFLATED)
                self.assertIn(b'break-before: auto;', book.read('style.css'))
            before = path.read_bytes()
            with self.assertRaisesRegex(ValueError, 'unsupported Pandoc'):
                correct_epub_headings(path)
            self.assertEqual(path.read_bytes(), before)
