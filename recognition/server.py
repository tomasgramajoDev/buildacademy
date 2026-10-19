"""WSGI adapter. Bind only to loopback; backend owns authentication and quotas."""
import json
from threading import BoundedSemaphore
from .detector import ConnectorDetector, RecognitionError


def create_app(detector=None):
    detector=detector or ConnectorDetector()
    slot=BoundedSemaphore(1)
    def app(env,start_response):
        status='200 OK'
        if env.get('PATH_INFO')!='/v1/recognitions':
            status='404 Not Found';result={'error':{'code':'not_found'}}
        elif env.get('REQUEST_METHOD')!='POST':
            status='405 Method Not Allowed';result={'error':{'code':'method_not_allowed'}}
        elif env.get('CONTENT_TYPE','').split(';')[0].strip() not in ['image/jpeg','image/png','image/webp']:
            status='415 Unsupported Media Type';result={'error':{'code':'unsupported_image'}}
        else:
            try:length=int(env.get('CONTENT_LENGTH',''))
            except (ValueError,TypeError):length=-1
            if not 0 < length <= 15*1024*1024:
                status='413 Content Too Large' if length>15*1024*1024 else '400 Bad Request'
                result={'error':{'code':'invalid_image_size'}}
            elif not slot.acquire(blocking=False):
                status='429 Too Many Requests';result={'error':{'code':'busy'}}
            else:
                try:
                    data=env['wsgi.input'].read(length)
                    if len(data)!=length:raise RecognitionError('incomplete_image','Imagen incompleta.')
                    result=detector.recognize(data)
                except RecognitionError as error:
                    status='400 Bad Request';result={'error':{'code':error.code,'message':str(error)}}
                except Exception:
                    status='500 Internal Server Error';result={'error':{'code':'recognition_failed'}}
                finally:slot.release()
        body=json.dumps(result,ensure_ascii=False).encode('utf-8')
        headers=[('Content-Type','application/json; charset=utf-8'),('Content-Length',str(len(body))),('Cache-Control','no-store')]
        if status.startswith('405'):headers.append(('Allow','POST'))
        start_response(status,headers)
        return [body]
    return app


if __name__=='__main__':
    import argparse
    from wsgiref.simple_server import make_server
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--model-dir',help='Paquete local de modelo revisado')
    parser.add_argument('--port',type=int,default=8770)
    args=parser.parse_args()
    with make_server('127.0.0.1',args.port,create_app(ConnectorDetector(args.model_dir))) as server:
        print(f'Recognition development adapter: http://127.0.0.1:{args.port}/v1/recognitions',flush=True)
        server.serve_forever()
