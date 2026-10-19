import argparse, json
from pathlib import Path
from .detector import ConnectorDetector, RecognitionError

parser=argparse.ArgumentParser(description='Reconocimiento local de conexiones de motherboard')
parser.add_argument('image',type=Path)
args=parser.parse_args()
try:
    print(json.dumps(ConnectorDetector().recognize(args.image.read_bytes()),ensure_ascii=False))
except RecognitionError as error:
    print(json.dumps({'error':{'code':error.code,'message':str(error)}},ensure_ascii=False))
    raise SystemExit(1)
