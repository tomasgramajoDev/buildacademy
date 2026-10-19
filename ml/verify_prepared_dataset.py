"""Verify the prepared copy against reviewed sources and record portable provenance."""
import argparse,hashlib,json
from pathlib import Path

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def verify(manifest,prepared):
    manifest,prepared=Path(manifest).resolve(),Path(prepared).resolve()
    rows=json.loads(manifest.read_text(encoding='utf-8'));audit=json.loads((prepared/'audit.json').read_text())
    if sha(manifest)!=audit['manifest_sha256']:raise ValueError('El manifiesto no coincide con la auditoría de entrenamiento.')
    result=[];expected=set()
    for i,row in enumerate(rows):
        source=(manifest.parent/row['image']).resolve();label=(manifest.parent/row['label']).resolve()
        im=prepared/row['split']/'images'/f'{i:06}{source.suffix.lower()}'
        lab=prepared/row['split']/'labels'/f'{i:06}.txt'
        if sha(source)!=sha(im) or sha(label)!=sha(lab):raise ValueError(f'La copia preparada difiere de la revisión: {row["model_id"]}')
        expected.update([im,lab])
        result.append({'model_id':row['model_id'],'board_id':row['board_id'],'split':row['split'],'image':im.relative_to(prepared).as_posix(),'label':lab.relative_to(prepared).as_posix(),'image_sha256':sha(im),'label_sha256':sha(lab),'source':row['source'],'license':row['license'],'identity_evidence':row['identity_evidence']})
    actual={p.resolve() for split in ['train','val','test'] for kind in ['images','labels'] for p in (prepared/split/kind).glob('*') if p.is_file()}
    if actual!=expected:raise ValueError('Archivos extra o ausentes en el dataset preparado.')
    return {'schema_version':1,'manifest_sha256':sha(manifest),'classes':audit['classes'],'files':result,'claim':'Byte-for-byte verification of prepared images and labels against reviewed sources. Not a certification of annotation accuracy.'}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--manifest',required=True);p.add_argument('--prepared',required=True);p.add_argument('--output',required=True);a=p.parse_args();r=verify(a.manifest,a.prepared);Path(a.output).write_text(json.dumps(r,indent=2,ensure_ascii=False),encoding='utf-8');print(f'Verified {len(r["files"])} image/label pairs.')
