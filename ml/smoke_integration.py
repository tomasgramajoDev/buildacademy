"""Exercise a real ONNX model through the local HTTP adapter, without changing defaults."""
import argparse,json,sys,threading,urllib.request,urllib.error
from pathlib import Path
from wsgiref.simple_server import make_server,WSGIRequestHandler
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from recognition.detector import ConnectorDetector
from recognition.server import create_app

class QuietHandler(WSGIRequestHandler):
    def log_message(self,*args): pass

def smoke(model_dir,image_path):
    detector=ConnectorDetector(model_dir)
    server=make_server('127.0.0.1',0,create_app(detector),handler_class=QuietHandler)
    worker=threading.Thread(target=server.serve_forever,daemon=True);worker.start()
    url=f'http://127.0.0.1:{server.server_port}/v1/recognitions'
    def request(data,ctype,method='POST'):
        req=urllib.request.Request(url,data=data,headers={'Content-Type':ctype},method=method)
        try:
            with urllib.request.urlopen(req,timeout=30) as response:return response.status,json.load(response)
        except urllib.error.HTTPError as error:return error.code,json.load(error)
    try:
        code,result=request(Path(image_path).read_bytes(),'image/jpeg')
        assert code==200 and result['model']['classes']==detector.classes
        assert result['compatibilityVerified'] is False
        assert all(d['classId'] in detector.classes for d in result['detections'])
        invalid,_=request(b'not an image','image/jpeg');assert invalid==400
        unsupported,_=request(b'{}','application/json');assert unsupported==415
        method,_=request(None,'image/jpeg','GET');assert method==405
        return {'checks':{'real_model_http':True,'invalid_image_400':True,'unsupported_type_415':True,'method_405':True},'result':result,'claim':'Protocol/runtime validation only; not evidence of detection accuracy.'}
    finally:
        server.shutdown();server.server_close();worker.join(timeout=5)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--model-dir',required=True);p.add_argument('--image',required=True);p.add_argument('--output',required=True);a=p.parse_args();r=smoke(a.model_dir,a.image);Path(a.output).write_text(json.dumps(r,indent=2));print(json.dumps(r['checks']))
