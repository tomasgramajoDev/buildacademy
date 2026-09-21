"""Import the public BIS497 four-class pilot; do not treat it as nine classes.

Only data is extracted. The external data.yaml is parsed with safe_load; its
paths/download commands are never passed to the trainer or executed.
"""
import argparse,hashlib,json,stat,zipfile,math
from pathlib import Path
from PIL import Image
import yaml
from prepare_dataset import prepare

MAPPING={'CPU Socket':'CPU_SOCKET','PCIe Slot':'PCIE_SLOT','Power Connector':'POWER_CONNECTOR','RAM Slot':'DIMM_SLOT'}
SOURCE='https://universe.roboflow.com/bis497/motherboard-part-locater/dataset/5'

def detection_labels(text):
    rows=[];converted=0
    for line in text.splitlines():
        if not line.strip():continue
        values=line.split();cid=int(values[0]);coords=list(map(float,values[1:]))
        if not all(math.isfinite(v) and 0<=v<=1 for v in coords):raise ValueError('Coordenadas invalidas')
        if len(coords)==4:rows.append(line);continue
        if len(coords)<6 or len(coords)%2:raise ValueError('Poligono invalido')
        xs=coords[::2];ys=coords[1::2];left,right=min(xs),max(xs);top,bottom=min(ys),max(ys)
        if right<=left or bottom<=top:raise ValueError('Poligono sin area')
        rows.append(f'{cid} {(left+right)/2} {(top+bottom)/2} {right-left} {bottom-top}');converted+=1
    return '\n'.join(rows),converted

def run(archive,target):
    root=Path(target).resolve();raw=root/'raw'
    if root.exists() and any(root.iterdir()): raise ValueError('Usá una carpeta de salida vacía.')
    root.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(archive) as z:
        if sum(i.file_size for i in z.infolist())>2_000_000_000: raise ValueError('ZIP demasiado grande para este importador.')
        for item in z.infolist():
            destination=(raw/item.filename).resolve()
            if not destination.is_relative_to(raw) or stat.S_ISLNK(item.external_attr>>16): raise ValueError('Ruta insegura dentro del ZIP.')
            if item.is_dir() or destination.suffix.lower() not in ['.yaml','.yml','.txt','.json','.md','.jpg','.jpeg','.png','.webp']: continue
            destination.parent.mkdir(parents=True,exist_ok=True)
            with z.open(item) as source,destination.open('wb') as output:
                import shutil
                shutil.copyfileobj(source,output)
    configs=list(raw.rglob('data.yaml'))
    if len(configs)!=1: raise ValueError('Se esperaba exactamente un data.yaml.')
    base=configs[0].parent;config=yaml.safe_load(configs[0].read_text(encoding='utf8'))
    names=config.get('names');names=[names[k] for k in sorted(names,key=int)] if isinstance(names,dict) else names
    if not isinstance(names,list) or set(names)!=set(MAPPING) or len(names)!=4: raise ValueError(f'Clases inesperadas: {names}. Revisar el dataset antes de entrenar.')
    classes=[MAPPING[n] for n in names];rows=[];seen_pixels={};group_splits={};excluded=[];converted=0
    # Preserve held-out images when duplicate originals occur across splits.
    for original_split,split in [('test','test'),('valid','val'),('train','train')]:
        directory=base/original_split/'images'
        if not directory.is_dir(): raise ValueError(f'Falta {original_split}/images.')
        for img in sorted(directory.iterdir()):
            if img.suffix.lower() not in ['.jpg','.jpeg','.png','.webp']: continue
            label=base/original_split/'labels'/(img.stem+'.txt')
            if not label.exists(): raise ValueError(f'Falta etiqueta: {img.name}')
            group=img.stem.split('.rf.')[0]
            with Image.open(img) as im:
                im.load();digest=hashlib.sha256(im.convert('RGB').tobytes()+f'{im.width}x{im.height}'.encode()).hexdigest()
            if digest in seen_pixels or (group in group_splits and group_splits[group]!=split):
                excluded.append({'image':img.name,'reason':'duplicate pixels or original filename across splits'});continue
            seen_pixels[digest]=split;group_splits[group]=split
            normalized,count=detection_labels(label.read_text());converted+=count
            detection=root/'detection_labels'/original_split/label.name;detection.parent.mkdir(parents=True,exist_ok=True);detection.write_text(normalized)
            rows.append({'image':img.relative_to(root).as_posix(),'label':detection.relative_to(root).as_posix(),'board_id':group,'source':SOURCE,'license':'CC BY 4.0; BIS497','split':split})
    manifest=root/'manifest.json';manifest.write_text(json.dumps(rows,indent=2))
    report=prepare(manifest,root/'prepared',classes)
    report['polygons_converted_to_enclosing_boxes']=converted
    report['source']=SOURCE;report['license']='CC BY 4.0';report['author']='BIS497';report['excluded']=excluded
    report['grouping']='Original filename and exact pixels only. Physical motherboard/model identity is unavailable; split by unseen hardware is NOT verified.'
    report['original_filename_groups']=report.pop('boards')
    report['archive_sha256']=hashlib.sha256(Path(archive).read_bytes()).hexdigest()
    (root/'prepared/audit.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('archive');parser.add_argument('--output',default='datasets/bis497-pilot');args=parser.parse_args();run(args.archive,args.output)
