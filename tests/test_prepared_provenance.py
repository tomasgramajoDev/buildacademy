import hashlib,json,tempfile,unittest
from pathlib import Path
from ml.verify_prepared_dataset import verify

class PreparedProvenanceTests(unittest.TestCase):
    def test_prepared_label_mutation_and_extra_image_are_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);prepared=root/'prepared';(prepared/'train/images').mkdir(parents=True);(prepared/'train/labels').mkdir()
            (root/'source.jpg').write_bytes(b'image fixture');(root/'source.txt').write_text('0 .5 .5 .1 .1')
            manifest=root/'manifest.json';manifest.write_text(json.dumps([{'image':'source.jpg','label':'source.txt','split':'train','model_id':'fixture','board_id':'fixture','source':'fixture','license':'fixture','identity_evidence':'fixture'}]))
            (prepared/'audit.json').write_text(json.dumps({'manifest_sha256':hashlib.sha256(manifest.read_bytes()).hexdigest(),'classes':['fixture']}))
            (prepared/'train/images/000000.jpg').write_bytes((root/'source.jpg').read_bytes());label=prepared/'train/labels/000000.txt';label.write_bytes((root/'source.txt').read_bytes())
            self.assertEqual(len(verify(manifest,prepared)['files']),1)
            label.write_text('0 .2 .2 .1 .1')
            with self.assertRaises(ValueError):verify(manifest,prepared)
            label.write_bytes((root/'source.txt').read_bytes());(prepared/'train/images/extra.jpg').write_bytes(b'extra')
            with self.assertRaises(ValueError):verify(manifest,prepared)

if __name__=='__main__':unittest.main()
