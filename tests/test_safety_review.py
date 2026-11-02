import contextlib
import csv
import io
import tempfile
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from safety_review import read_cases, make_template, summarize

class ReviewTests(unittest.TestCase):
    def test_round_trip_and_unreviewed(self):
        cases = read_cases(Path(__file__).resolve().parents[1] / 'examples/starter_cases.jsonl')
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / 'review.csv'
            make_template(cases, output)
            with output.open(newline='', encoding='utf-8') as f:
                rows = list(csv.DictReader(f))
            rows[0].update(response='Use a redacted sample.', verdict='pass')
            rows[1].update(response='Unknown.', verdict='uncertain')
            with output.open('w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=rows[0].keys())
                writer.writeheader(); writer.writerows(rows)
            captured = io.StringIO()
            with contextlib.redirect_stdout(captured): summarize(output)
            self.assertIn('pass: 1', captured.getvalue())
            self.assertIn('uncertain: 1', captured.getvalue())
            self.assertIn('unreviewed: 2', captured.getvalue())
            with self.assertRaises(FileExistsError): make_template(cases, output)

    def test_duplicate_case_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            p = Path(folder) / 'cases.jsonl'
            line = '{"id":"x","category":"c","prompt":"p","criterion":"q"}\n'
            p.write_text(line * 2)
            with self.assertRaisesRegex(ValueError, 'duplicate'): read_cases(p)

    def test_verdict_requires_response(self):
        with tempfile.TemporaryDirectory() as folder:
            p = Path(folder) / 'reviews.csv'
            p.write_text('id,category,response,verdict\nx,c,,pass\n')
            with self.assertRaisesRegex(ValueError, 'requires a response'): summarize(p)

if __name__ == '__main__': unittest.main()
