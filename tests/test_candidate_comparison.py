import json
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'ml'))
from compare_candidates import compare, validation_summary, CLASSES


class CandidateComparisonTests(unittest.TestCase):
    def fixture(self, path, name, tp=1):
        path.mkdir()
        files={'status.json':{'stage':'completed'},
               'runtime-val.json':{'split':'val','model':name,'confidence_threshold':.5,
                   'nms_iou':.45,'matching_iou':.5,'runtime':'test runtime','images':[{}],
                   'per_class':{c:{'tp':tp,'fp':0,'fn':2-tp} for c in CLASSES}},
               'provenance.json':{'files':[{'split':'val','model_id':'board',
                   'image_sha256':'same-image','label_sha256':'same-label'}]}}
        for name, value in files.items():
            (path/name).write_text(json.dumps(value),encoding='utf-8')

    def test_validation_selection_does_not_need_test_report(self):
        with tempfile.TemporaryDirectory() as root:
            a,b=Path(root)/'a',Path(root)/'b'
            self.fixture(a,'first',1);self.fixture(b,'second',2)
            result=compare(a,b)
            self.assertEqual(result['preferred_for_further_review'],'second')
            self.assertFalse(result['deployment_approved'])
            p=b/'provenance.json';data=json.loads(p.read_text())
            data['files'][0]['label_sha256']='changed-label';p.write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError,'different validation'):compare(a,b)

    def test_zero_recall_counts_in_macro_average(self):
        report={'split':'val','per_class':{c:{'tp':1,'fp':0,'fn':0} for c in CLASSES}}
        report['per_class']['FAN_HEADER']={'tp':0,'fp':0,'fn':5}
        summary=validation_summary(report)
        self.assertAlmostEqual(summary['macro_f1'],8/9)
        self.assertEqual(summary['zero_recall_classes'],['FAN_HEADER'])
        report['split']='test'
        with self.assertRaises(ValueError):validation_summary(report)


if __name__=='__main__':unittest.main()
