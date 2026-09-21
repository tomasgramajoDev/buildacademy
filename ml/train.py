"""Train on train, select on val, then report untouched test metrics. No auto-publish."""
import argparse, json
from pathlib import Path

def run(args):
    import torch
    from ultralytics import YOLO
    from prepare_dataset import CLASSES
    data=Path(args.data).resolve()
    if not data.is_file() or not data.with_name('audit.json').is_file(): raise ValueError('Prepará y auditá primero el dataset con prepare_dataset.py.')
    audit=json.loads(data.with_name('audit.json').read_text())
    if audit.get('classes')!=CLASSES: raise ValueError('Clases distintas al contrato de BuildAcademy')
    model=YOLO('yolo11n.pt') # Official Ultralytics pretrained initialization.
    device=0 if torch.cuda.is_available() else 'cpu'
    model.train(data=str(data),epochs=args.epochs,imgsz=640,batch=args.batch,device=device,workers=0,seed=42,deterministic=True,project='runs/buildacademy',name=args.name,exist_ok=False,patience=20)
    best=YOLO(str(model.trainer.best))
    result=best.val(data=str(data),split='test',imgsz=640,device=device,plots=True)
    report={'model':str(model.trainer.best),'data_audit':audit,'test':result.results_dict,'per_class_map50_95':dict(zip(CLASSES,result.box.maps.tolist())),'claim':'Evaluación de este dataset. No certifica generalización a nuevas placas ni compatibilidad eléctrica.'}
    report_path=Path(model.trainer.save_dir)/'evaluation.json';report_path.write_text(json.dumps(report,indent=2))
    best.export(format='onnx',imgsz=640,opset=17,simplify=False,dynamic=False,nms=False)
    print(f'Resultados: {report_path}. Revisá errores por clase antes de publicar los pesos.')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--data',default='datasets/prepared/data.yaml');p.add_argument('--epochs',type=int,default=80);p.add_argument('--batch',type=int,default=8);p.add_argument('--name',default='connectors');run(p.parse_args())
