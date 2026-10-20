"""Export reserved reviewed labels for post-selection evaluation, never training."""
import argparse
import hashlib
import json
import math
import shutil
from pathlib import Path
from PIL import Image
from prepare_dataset import CLASSES

ROOT = Path(__file__).resolve().parents[1]


def build(output):
    output = Path(output).resolve()
    if output.exists():
        raise ValueError('Use a fresh output to preserve earlier evaluations.')
    reservations = json.loads((ROOT/'ml/HOLDOUT-RESERVATIONS.json').read_text(encoding='utf-8'))['reservations']
    reserved = {r['image_sha256']: r for r in reservations}
    development = [json.loads(p.read_text(encoding='utf-8')) for p in (ROOT/'ml/annotations').glob('*.json')]
    dev_models = {d['model_id'].strip().casefold() for d in development}
    dev_images = {d['image_sha256'] for d in development}
    checked = []
    for path in sorted((ROOT/'ml/holdout_annotations').glob('*.json')):
        data = json.loads(path.read_text(encoding='utf-8'))
        if data.get('status')!='reviewed' or data.get('unresolved') or data.get('split')!='independent_test':
            raise ValueError('Holdout annotation is incomplete.')
        reservation = reserved.get(data['image_sha256'])
        if not reservation or data['model_id']!=reservation['model_id']:
            raise ValueError('Image and model must match an explicit reservation.')
        if reservation.get('evaluation') or reservation.get('status','').startswith('evaluated'):
            # A fresh output directory must not make a previously consulted board
            # appear to be a new independent test.
            continue
        if dev_models.intersection(n.strip().casefold() for n in reservation['excluded_model_ids']) or data['image_sha256'] in dev_images:
            raise ValueError('Reserved motherboard overlaps development data.')
        image = ROOT/data['image']
        if hashlib.sha256(image.read_bytes()).hexdigest()!=data['image_sha256'] or data['classes']!=CLASSES:
            raise ValueError('Image hash or class contract changed.')
        with Image.open(image) as im:
            width,height=im.size
        if (width,height)!=(data['width'],data['height']):
            raise ValueError('Annotation dimensions differ from image.')
        labels=[]
        for name,x1,y1,x2,y2 in data['boxes_xyxy']:
            if name not in CLASSES or not all(math.isfinite(v) for v in [x1,y1,x2,y2]) or not 0<=x1<x2<=width or not 0<=y1<y2<=height:
                raise ValueError('Invalid holdout bounding box.')
            labels.append(f'{CLASSES.index(name)} {(x1+x2)/2/width:.8f} {(y1+y2)/2/height:.8f} {(x2-x1)/width:.8f} {(y2-y1)/height:.8f}')
        checked.append((data,image,labels,hashlib.sha256(path.read_bytes()).hexdigest()))
    if not checked:raise ValueError('No reviewed independent annotations.')
    (output/'test/images').mkdir(parents=True)
    (output/'test/labels').mkdir()
    provenance=[]
    for i,(data,image,labels,annotation_hash) in enumerate(checked):
        name=f'{i:06}'
        shutil.copy2(image,output/'test/images'/f'{name}{image.suffix.lower()}')
        label=output/'test/labels'/f'{name}.txt'
        label.write_text('\n'.join(labels)+'\n',encoding='utf-8')
        provenance.append({'model_id':data['model_id'],'image_sha256':data['image_sha256'],
                           'label_sha256':hashlib.sha256(label.read_bytes()).hexdigest(),
                           'annotation_sha256':annotation_hash,'boxes':len(labels),
                           'identity_evidence':data['identity_evidence']})
    report={'purpose':'independent_post_selection_only','review_gate':'not_a_training_dataset',
            'classes':CLASSES,'images':len(checked),'models':len({d['model_id'] for d,_,_,_ in checked}),
            'files':provenance,'evaluated':False,
            'limitation':'Small manually annotated holdout; not independent human certification. Never use for candidate selection.'}
    (output/'audit.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    return report


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',required=True)
    args=parser.parse_args();r=build(args.output);print(json.dumps({'images':r['images'],'models':r['models'],'evaluated':False}))
