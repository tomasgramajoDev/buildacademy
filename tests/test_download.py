import importlib.util,io,tempfile,unittest,zipfile
from pathlib import Path
from contextlib import redirect_stdout
spec=importlib.util.spec_from_file_location('download',Path(__file__).parents[1]/'ml/download_roboflow.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class Response:
 def __init__(self,status=200,data=None,body=b'',headers=None):self.status_code=status;self.data=data;self.body=body;self.headers=headers or {}
 def __enter__(self):return self
 def __exit__(self,*args):pass
 def json(self):return self.data
 def iter_content(self,*args):yield self.body
class Session:
 def __init__(self,responses):self.responses=iter(responses);self.calls=[]
 def get(self,url,**kwargs):self.calls.append((url,kwargs));return next(self.responses)
class DownloadTests(unittest.TestCase):
 def test_existing_key_only_sent_as_api_header(self):
  s=Session([Response(data={'export':{'link':'https://app.roboflow.com/ds/example'}})])
  self.assertEqual(m.export_link('test-secret',session=s),'https://app.roboflow.com/ds/example')
  self.assertNotIn('test-secret',s.calls[0][0]);self.assertEqual(s.calls[0][1]['headers'],{'Authorization':'Bearer test-secret'})
 def test_rejects_untrusted_links_and_auth_failures(self):
  for url in ['http://app.roboflow.com/ds/x','https://roboflow.com.evil.test/x','https://user:pass@app.roboflow.com/x']:
   self.assertFalse(m.allowed_url(url))
  with self.assertRaises(m.DownloadError):m.export_link('test-secret',session=Session([Response(401)]))
 def test_zip_download_separate_from_auth_and_preserves_existing_file(self):
  body=io.BytesIO()
  with zipfile.ZipFile(body,'w') as z:z.writestr('data.yaml','names: []')
  s=Session([Response(body=body.getvalue())])
  with tempfile.TemporaryDirectory() as d,redirect_stdout(io.StringIO()):
   target=Path(d)/'data.zip';m.download('https://app.roboflow.com/ds/example',target,s)
   self.assertTrue(zipfile.is_zipfile(target));self.assertNotIn('headers',s.calls[0][1])
   with self.assertRaises(m.DownloadError):m.download('https://app.roboflow.com/ds/example',target,s)
if __name__=='__main__':unittest.main()
