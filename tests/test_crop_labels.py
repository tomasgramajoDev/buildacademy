import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'ml'))
from augment_training import clip_labels


class CropLabelTests(unittest.TestCase):
    def test_partial_object_and_outside_object(self):
        result = clip_labels(['8 0.5 0.5 0.4 0.4', '2 0.9 0.9 0.1 0.1'], 100, 100, (0,0,50,50))
        self.assertEqual(len(result), 1)
        self.assertEqual(list(map(float, result[0].split())), [8, .8, .8, .4, .4])

    def test_offset_and_edge_touching(self):
        result = clip_labels(['3 0.7 0.6 0.2 0.2', '1 0.2 0.5 0.4 0.2'], 100, 200, (40,80,100,200))
        self.assertEqual(len(result), 1)
        actual = list(map(float, result[0].split()))
        for a, b in zip(actual, [3, .5, 1/3, 1/3, 1/3]):
            self.assertAlmostEqual(a, b, places=7)

    def test_tiny_visible_fragment_is_not_dropped(self):
        result = clip_labels(['8 0.6 0.5 0.22 0.1'], 100, 100, (0,0,50,50))
        self.assertEqual(len(result), 1)
        self.assertGreater(float(result[0].split()[3]), 0)


if __name__ == '__main__':
    unittest.main()
