import json
import tempfile
import unittest
from pathlib import Path
from ml.prepare_web_model import manifest_for, prepare, NINE

class ModelPackageTests(unittest.TestCase):
    def test_nine_class_review_required_and_order_preserved(self):
        with tempfile.TemporaryDirectory() as folder:
            model=Path(folder)/'model.onnx'; model.write_bytes(b'fixture')
            report={'data_audit':{'classes':NINE},'input_size':640,'test':{'metrics/mAP50(B)':.1},'per_class_map50_95':dict.fromkeys(NINE,.1)}
            with self.assertRaises(ValueError):manifest_for(report,model,'test')
            report['data_audit']['review_gate']='passed'
            result=manifest_for(report,model,'test')
            self.assertEqual(result['classes'],NINE)
            self.assertEqual(result['releaseStatus'],'experimental')
            self.assertEqual(len(result['sha256']),64)

    def test_deployed_directory_cannot_be_overwritten(self):
        target=Path(__file__).resolve().parents[1]/'dist/models'
        before=(target/'manifest.json').read_bytes()
        with self.assertRaises(ValueError):prepare('missing-run',target,'test')
        self.assertEqual(before,(target/'manifest.json').read_bytes())

if __name__=='__main__':unittest.main()
