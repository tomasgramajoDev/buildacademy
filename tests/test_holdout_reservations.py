import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'ml'))
from build_independent_holdout import build


class ConsumedHoldoutTests(unittest.TestCase):
    def test_fresh_directory_cannot_reexport_evaluated_board(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            (root/'ml/annotations').mkdir(parents=True)
            (root/'ml/holdout_annotations').mkdir()
            (root/'ml/HOLDOUT-RESERVATIONS.json').write_text(json.dumps({'reservations':[{
                'image_sha256':'same','model_id':'reserved','status':'evaluated_once_post_selection',
                'evaluation':'report.json'}]}))
            (root/'ml/holdout_annotations/old.json').write_text(json.dumps({
                'image_sha256':'same','model_id':'reserved','status':'reviewed',
                'split':'independent_test','unresolved':[]}))
            with patch('build_independent_holdout.ROOT',root):
                with self.assertRaisesRegex(ValueError,'No reviewed independent annotations'):
                    build(root/'new-test')
            self.assertFalse((root/'new-test').exists())


if __name__=='__main__':unittest.main()
