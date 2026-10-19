import importlib.util
import io
import tempfile
import unittest
import zipfile
from pathlib import Path

from PIL import Image

spec = importlib.util.spec_from_file_location('candidate', Path(__file__).parents[1] / 'ml/audit_candidate.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class CandidateTests(unittest.TestCase):
    def test_leakage_and_original_classes_are_reported(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            image = io.BytesIO()
            Image.new('RGB', (64, 64), 'blue').save(image, format='PNG')
            archive = root / 'candidate.zip'
            with zipfile.ZipFile(archive, 'w') as z:
                z.writestr('data.yaml', 'names: [fan_bracket]\n')
                for split in ['train', 'test']:
                    z.writestr(f'{split}/images/board.rf.{split}.png', image.getvalue())
                    z.writestr(f'{split}/labels/board.rf.{split}.txt', '0 0.25 0.25 0.75 0.25 0.75 0.75 0.25 0.75')
            report = m.audit(archive, root / 'out')
            self.assertEqual(report['classes'], ['fan_bracket'])
            self.assertEqual(report['polygons_previewed_as_enclosing_boxes'], 2)
            self.assertEqual(report['filename_groups_crossing_splits'], 1)
            self.assertEqual(report['pixel_hashes_crossing_splits'], 1)
            self.assertFalse((root / 'out' / 'prepared').exists())

    def test_unsafe_archive_path_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            archive = root / 'bad.zip'
            with zipfile.ZipFile(archive, 'w') as z:
                z.writestr('../outside.txt', 'bad')
            with self.assertRaises(ValueError):
                m.audit(archive, root / 'out')
            self.assertFalse((root / 'out' / 'outside.txt').exists())


if __name__ == '__main__':
    unittest.main()
