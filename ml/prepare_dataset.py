"""Validate human labels and split by physical motherboard identity, not by image.

Manifest JSON: [{image, label, board_id, source, license, split}].
Paths are relative to manifest. split is train, val or test; a board_id may occur
in only one split. An empty label file explicitly represents a negative image.
"""
import argparse, hashlib, json, math, shutil
from pathlib import Path
CLASSES=['CPU_SOCKET','DIMM_SLOT','PCIe_X16','PCIe_X1','M2_SLOT','SATA_PORT','ATX_POWER','CPU_POWER','FAN_HEADER']

def validate(manifest):
    from PIL import Image
    path=Path(manifest).resolve(); records=json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(records,list) or not records: raise ValueError('El manifiesto debe contener imágenes etiquetadas.')
    groups={}; hashes={}; checked=[]; counts={s:[0]*len(CLASSES) for s in ['train','val','test']}
    for index,row in enumerate(records):
        if not isinstance(row,dict) or any(not isinstance(row.get(k),str) or not row[k].strip() for k in ['image','label','board_id','source','license','split']): raise ValueError(f'Fila {index}: faltan procedencia, licencia, grupo o rutas.')
        split=row['split']; group=row['board_id']
        if split not in counts: raise ValueError('Split inválido')
        if group in groups and groups[group]!=split: raise ValueError(f'Fuga de datos: motherboard {group} en más de un split')
        groups[group]=split
        img=(path.parent/row['image']).resolve(); label=(path.parent/row['label']).resolve()
        if not img.is_file() or not label.is_file(): raise ValueError(f'Archivos ausentes: {index}')
        if img.suffix.lower() not in ['.jpg','.jpeg','.png','.webp']: raise ValueError('Formato de imagen no admitido')
        with Image.open(img) as im:
            im.load()
            if im.width<32 or im.height<32 or im.width*im.height>40000000: raise ValueError('Dimensiones de imagen inválidas')
            digest=hashlib.sha256(im.convert('RGB').tobytes()+f'{im.width}x{im.height}'.encode()).hexdigest()
        if digest in hashes: raise ValueError(f'Imagen duplicada: {index} y {hashes[digest]}')
        hashes[digest]=index
        for line in label.read_text().splitlines():
            values=line.split()
            if len(values)!=5: raise ValueError(f'Etiqueta YOLO inválida en {label}')
            cid=int(values[0]); x,y,w,h=map(float,values[1:])
            if cid<0 or cid>=len(CLASSES) or not all(math.isfinite(v) for v in [x,y,w,h]) or w<=0 or h<=0 or x-w/2<-.000001 or x+w/2>1.000001 or y-h/2<-.000001 or y+h/2>1.000001: raise ValueError(f'Caja fuera de rango en {label}')
            counts[split][cid]+=1
        checked.append((img,label,split,index))
    for split,values in counts.items():
        missing=[CLASSES[i] for i,n in enumerate(values) if not n]
        if missing: raise ValueError(f'{split}: faltan ejemplos de {missing}. No se declara cobertura inexistente.')
    return checked,{'images':len(checked),'boards':len(groups),'boxes':counts,'classes':CLASSES,'manifest_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'limitation':'El validador detecta duplicados exactos; revisar manualmente similares y la identidad de cada placa.'}

def prepare(manifest,output):
    checked,report=validate(manifest); target=Path(output).resolve()
    if target.exists() and any(target.iterdir()): raise ValueError('La salida debe estar vacía para no mezclar datasets.')
    for image,label,split,index in checked:
        a=target/split/'images'; b=target/split/'labels';a.mkdir(parents=True,exist_ok=True);b.mkdir(parents=True,exist_ok=True)
        shutil.copy2(image,a/f'{index:06}{image.suffix.lower()}');shutil.copy2(label,b/f'{index:06}.txt')
    # JSON is a subset of YAML and avoids platform path escaping mistakes.
    (target/'data.yaml').write_text(json.dumps({'path':target.as_posix(),'train':'train/images','val':'val/images','test':'test/images','names':dict(enumerate(CLASSES))},indent=2))
    (target/'audit.json').write_text(json.dumps(report,indent=2));return report

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('manifest');parser.add_argument('--output',default='datasets/prepared');args=parser.parse_args();print(json.dumps(prepare(args.manifest,args.output),indent=2))
