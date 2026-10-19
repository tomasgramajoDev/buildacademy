import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'ml'))
from finalize_candidates import finalize, verify_holdout


class HoldoutFinalizationTests(unittest.TestCase):
    def fixture(self, root):
        holdout=root/'holdout'
        (holdout/'test/images').mkdir(parents=True)
        (holdout/'test/labels').mkdir()
        image=b'fixture image';label=b'0 .5 .5 .2 .2\n'
        (holdout/'test/images/0.jpg').write_bytes(image)
        (holdout/'test/labels/0.txt').write_bytes(label)
        row={'model_id':'reserved','image_sha256':hashlib.sha256(image).hexdigest(),
             'label_sha256':hashlib.sha256(label).hexdigest()}
        (holdout/'audit.json').write_text(json.dumps({'purpose':'independent_post_selection_only',
            'evaluated':False,'images':1,'files':[row]}))
        jobs=[root/'a',root/'b']
        for i,job in enumerate(jobs):
            job.mkdir()
            (job/'provenance.json').write_text(json.dumps({'files':[{'model_id':'training',
                'image_sha256':'other'}]}))
            (job/'runtime-val.json').write_text(json.dumps({'model':str(i)}))
        return holdout,jobs

    def test_modified_labels_and_development_overlap_are_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            holdout,jobs=self.fixture(Path(tmp))
            verify_holdout(holdout,jobs)
            label=holdout/'test/labels/0.txt';original=label.read_bytes()
            label.write_bytes(b'changed')
            with self.assertRaisesRegex(ValueError,'hashes'):verify_holdout(holdout,jobs)
            label.write_bytes(original)
            (jobs[0]/'provenance.json').write_text(json.dumps({'files':[{
                'model_id':'RESERVED','image_sha256':'different-photo'}]}))
            with self.assertRaisesRegex(ValueError,'overlaps'):verify_holdout(holdout,jobs)

    def test_selection_precedes_inference_and_holdout_cannot_be_rerun(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);holdout,jobs=self.fixture(root)
            selection={'preferred_for_further_review':'1','operating':{'confidence_threshold':.5}}
            def inference(*args,**kwargs):
                self.assertTrue((root/'result/selection.json').exists())
                return {'images':[]}
            with patch('finalize_candidates.compare',return_value=selection), \
                 patch('finalize_candidates.evaluate',side_effect=inference) as run:
                finalize(*jobs,holdout,root/'result')
                self.assertEqual(run.call_count,1)
                with self.assertRaises(FileExistsError):finalize(*jobs,holdout,root/'retry')
                self.assertEqual(run.call_count,1)
                self.assertFalse(json.loads((root/'result/status.json').read_text())['deployment_approved'])


if __name__=='__main__':unittest.main()
