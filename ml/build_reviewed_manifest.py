"""Materialize versioned, visually reviewed labels; never infer missing labels."""
import hashlib
import json
from pathlib import Path
from PIL import Image, ImageDraw
from prepare_dataset import CLASSES

ROOT=Path(__file__).resolve().parents[1]

def build():
    reservations=ROOT/'ml/HOLDOUT-RESERVATIONS.json'
    reserved={name.strip().casefold() for row in json.loads(reservations.read_text(encoding='utf-8'))['reservations'] for name in row['excluded_model_ids']} if reservations.exists() else set()
    output=ROOT/'datasets/nine-reviewed'
    (output/'labels').mkdir(parents=True,exist_ok=True)
    (output/'previews').mkdir(exist_ok=True)
    rows=[];total_boxes=0
    for record in sorted((ROOT/'ml/annotations').glob('*.json')):
        data=json.loads(record.read_text(encoding='utf-8'))
        if data['status']!='reviewed' or data.get('unresolved'):continue
        if data['model_id'].strip().casefold() in reserved:
            raise ValueError('Placa reservada para evaluación independiente: no mezclar con el dataset de desarrollo.')
        image=ROOT/data['image']
        if hashlib.sha256(image.read_bytes()).hexdigest()!=data['image_sha256']:raise ValueError('La foto cambió desde la revisión.')
        with Image.open(image) as source:preview=source.convert('RGB')
        width,height=preview.size
        if (width,height)!=(data['width'],data['height']):raise ValueError('Dimensiones inconsistentes.')
        lines=[];draw=ImageDraw.Draw(preview)
        total_boxes+=len(data['boxes_xyxy'])
        for name,x1,y1,x2,y2 in data['boxes_xyxy']:
            if name not in CLASSES or not (0<=x1<x2<=width and 0<=y1<y2<=height):raise ValueError('Caja inválida.')
            cid=CLASSES.index(name)
            lines.append(f'{cid} {(x1+x2)/2/width:.8f} {(y1+y2)/2/height:.8f} {(x2-x1)/width:.8f} {(y2-y1)/height:.8f}')
            draw.rectangle((x1,y1,x2,y2),outline='orange',width=1)
            draw.text((x1,y1),str(cid),fill='red')
        label=output/'labels'/f'{record.stem}.txt';label.write_text('\n'.join(lines)+'\n',encoding='utf-8')
        preview.save(output/'previews'/f'{record.stem}.png')
        rows.append({'image':'../../'+data['image'],'label':'labels/'+label.name,'model_id':data['model_id'],'board_id':'conservative-model-'+data['model_group'],'source':data['source'],'license':data['license'],'split':data['split'],'review_status':'reviewed','reviewed_by':data['review_method'],'identity_evidence':data['identity_evidence'],'annotation_policy':data['annotation_policy'],'unresolved':[],'checks':{k:True for k in ['all_visible_connectors','individual_dimm_slots','pcie_physical_size','power_connector_type','duplicates_and_board_identity']}})
    (output/'manifest.json').write_text(json.dumps(rows,indent=2,ensure_ascii=False),encoding='utf-8')
    summary={'reviewed_images':len(rows),'models':len(set(r['model_id'] for r in rows)),'boxes':total_boxes,'splits':{s:sum(r['split']==s for r in rows) for s in ['train','val','test']},'status':'annotation_in_progress_not_training_ready'}
    (output/'status.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    return summary

if __name__=='__main__':print(json.dumps(build(),indent=2))
