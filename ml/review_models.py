"""Compare both ONNX models at conf=.5, NMS=.45 and matching IoU=.5.
Uses Ultralytics preprocessing, not a browser execution test.
"""
from pathlib import Path
import json
from ultralytics import YOLO
from PIL import Image
import torch
torch.set_num_threads(4)
root=Path('datasets/bis497-detection/prepared/test')
out=Path('tmp/model-review');out.mkdir(exist_ok=True)
results={}
for tag,modelpath,size in [('current','dist/models/connectors.onnx',320),('candidate','runs/detect/runs/buildacademy/bis497-416-20261019/weights/best.onnx',416)]:
 model=YOLO(modelpath,task='detect');tp=fp=fn=0;details=[]
 for im in sorted((root/'images').glob('*')):
  w,h=Image.open(im).size;gt=[]
  for l in (root/'labels'/(im.stem+'.txt')).read_text().splitlines():
   c,x,y,bw,bh=map(float,l.split());gt.append((int(c),[(x-bw/2)*w,(y-bh/2)*h,(x+bw/2)*w,(y+bh/2)*h]))
  r=model.predict(str(im),imgsz=size,conf=.5,iou=.45,max_det=100,verbose=False)[0]
  matched=set();localtp=0
  for box,c in zip(r.boxes.xyxy.tolist(),r.boxes.cls.tolist()):
   best=0;ix=None
   for j,(gc,g) in enumerate(gt):
    if j in matched or gc!=int(c):continue
    inter=max(0,min(box[2],g[2])-max(box[0],g[0]))*max(0,min(box[3],g[3])-max(box[1],g[1]));union=(box[2]-box[0])*(box[3]-box[1])+(g[2]-g[0])*(g[3]-g[1])-inter
    v=inter/union if union else 0
    if v>best:best=v;ix=j
   if best>=.5:matched.add(ix);localtp+=1
  tp+=localtp;fp+=len(r.boxes)-localtp;fn+=len(gt)-localtp
  details.append({'image':im.name,'tp':localtp,'fp':len(r.boxes)-localtp,'fn':len(gt)-localtp})
 results[tag]={'tp':tp,'fp':fp,'fn':fn,'precision':tp/(tp+fp),'recall':tp/(tp+fn),'images':details}
(out/'comparison.json').write_text(json.dumps(results,indent=2))
print(json.dumps({k:{a:b for a,b in v.items() if a!='images'} for k,v in results.items()}))
