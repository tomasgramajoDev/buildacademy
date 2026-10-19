"""Measure the integration runtime at its fixed operating threshold, without tuning it."""
import argparse,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from recognition.detector import ConnectorDetector

def iou(a,b):
    overlap=max(0,min(a[2],b[2])-max(a[0],b[0]))*max(0,min(a[3],b[3])-max(a[1],b[1]))
    union=(a[2]-a[0])*(a[3]-a[1])+(b[2]-b[0])*(b[3]-b[1])-overlap
    return overlap/union if union else 0

def evaluate(model_dir,data_dir,split,threshold=0.5):
    detector=ConnectorDetector(model_dir,threshold=threshold); totals={c:{'tp':0,'fp':0,'fn':0} for c in detector.classes};details=[]
    root=Path(data_dir)/split
    for image in sorted((root/'images').glob('*')):
        result=detector.recognize(image.read_bytes());w=result['image']['width'];h=result['image']['height'];gt=[]
        for line in (root/'labels'/(image.stem+'.txt')).read_text().splitlines():
            c,x,y,bw,bh=map(float,line.split());gt.append((detector.classes[int(c)],[(x-bw/2)*w,(y-bh/2)*h,(x+bw/2)*w,(y+bh/2)*h]))
        matched=set();local={'image':image.name,'tp':0,'fp':0,'fn':0}
        for pred in result['detections']:
            c=pred['classId'];b=pred['bbox'];box=[b['x'],b['y'],b['x']+b['width'],b['y']+b['height']]
            candidates=[(iou(box,g),i) for i,(gc,g) in enumerate(gt) if i not in matched and gc==c]
            score,index=max(candidates,default=(0,-1))
            key='tp' if score>=.5 else 'fp';totals[c][key]+=1;local[key]+=1
            if key=='tp':matched.add(index)
        for i,(c,_) in enumerate(gt):
            if i not in matched:totals[c]['fn']+=1;local['fn']+=1
        details.append(local)
    for counts in totals.values():
        counts['precision']=counts['tp']/(counts['tp']+counts['fp']) if counts['tp']+counts['fp'] else None
        counts['recall']=counts['tp']/(counts['tp']+counts['fn']) if counts['tp']+counts['fn'] else None
    return {'split':split,'model':detector.version,'confidence_threshold':threshold,'nms_iou':.45,'matching_iou':.5,'runtime':'recognition.ConnectorDetector ONNXRuntime CPU','per_class':totals,'images':details,'claim':'Small grouped dataset; reused test results are diagnostic, not independent certification.'}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--model-dir',required=True);p.add_argument('--data',required=True);p.add_argument('--split',choices=['train','val','test'],default='test');p.add_argument('--output',required=True);a=p.parse_args();r=evaluate(a.model_dir,a.data,a.split);Path(a.output).write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
