import json,sys,tempfile,unittest,zipfile,io,contextlib
from pathlib import Path
from PIL import Image
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'ml'))
from prepare_dataset import validate,prepare
from import_roboflow import run as import_roboflow

class DatasetTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name);self.rows=[]
        for index,split in enumerate(['train','val','test']):
            Image.new('RGB',(64,64),(index*50,40,30)).save(self.root/f'{index}.png')
            (self.root/f'{index}.txt').write_text('\n'.join(f'{i} 0.5 0.5 0.2 0.2' for i in range(9)))
            self.rows.append(dict(image=f'{index}.png',label=f'{index}.txt',board_id=f'board-{index}',source='fixture',license='test-only',split=split))
        self.manifest=self.root/'manifest.json';self.write()
    def write(self):self.manifest.write_text(json.dumps(self.rows))
    def tearDown(self):self.tmp.cleanup()
    def test_valid_and_prepare(self):
        report=prepare(self.manifest,self.root/'out');self.assertEqual(report['boards'],3);self.assertTrue((self.root/'out/data.yaml').exists())
    def test_group_leakage(self):
        self.rows[1]['board_id']='board-0';self.write()
        with self.assertRaisesRegex(ValueError,'Fuga'):validate(self.manifest)
    def test_duplicate_pixels(self):
        Image.open(self.root/'0.png').save(self.root/'1.png')
        with self.assertRaisesRegex(ValueError,'duplicada'):validate(self.manifest)
    def test_bad_boxes(self):
        (self.root/'0.txt').write_text('0 .9 .5 .5 .2')
        with self.assertRaisesRegex(ValueError,'rango'):validate(self.manifest)
    def test_missing_class(self):
        (self.root/'0.txt').write_text('0 .5 .5 .2 .2')
        with self.assertRaisesRegex(ValueError,'faltan ejemplos'):validate(self.manifest)
    def test_public_pilot_preserves_four_classes(self):
        archive=self.root/'pilot.zip'
        with zipfile.ZipFile(archive,'w') as z:
            z.writestr('data.yaml',json.dumps({'names':['CPU Socket','PCIe Slot','Power Connector','RAM Slot'],'download':'DO NOT EXECUTE'}))
            for i,split in enumerate(['train','valid','test']):
                z.write(self.root/f'{i}.png',f'{split}/images/{i}.png')
                z.writestr(f'{split}/labels/{i}.txt','\n'.join(f'{k} .5 .5 .2 .2' for k in range(4)))
        with contextlib.redirect_stdout(io.StringIO()):import_roboflow(archive,self.root/'pilot')
        audit=json.loads((self.root/'pilot/prepared/audit.json').read_text())
        self.assertEqual(audit['classes'],['CPU_SOCKET','PCIE_SLOT','POWER_CONNECTOR','DIMM_SLOT'])
        self.assertIn('NOT verified',audit['grouping'])
    def test_zip_cannot_escape_target(self):
        archive=self.root/'invalid.zip'
        with zipfile.ZipFile(archive,'w') as z:z.writestr('../escape.txt','no')
        with self.assertRaisesRegex(ValueError,'insegura'):import_roboflow(archive,self.root/'invalid')
        self.assertFalse((self.root/'escape.txt').exists())

if __name__=='__main__':unittest.main()
