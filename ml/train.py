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
    classes=audit.get('classes');allowed=set(CLASSES+['PCIE_SLOT','POWER_CONNECTOR'])
    if not classes or any(c not in allowed for c in classes): raise ValueError('Clases distintas al contrato de BuildAcademy')
    model=YOLO('yolo11n.pt') # Official Ultralytics pretrained initialization.
    device=0 if torch.cuda.is_available() else 'cpu'
    torch.set_num_threads(8)
    model.train(data=str(data),epochs=args.epochs,imgsz=args.size,batch=args.batch,device=device,workers=0,seed=42,deterministic=True,project='runs/buildacademy',name=args.name,exist_ok=False,patience=20)
    best=YOLO(str(model.trainer.best))
    result=best.val(data=str(data),split='test',imgsz=args.size,device=device,plots=True)
    report={'model':str(model.trainer.best),'data_audit':audit,'input_size':args.size,'test':result.results_dict,'per_class_map50_95':dict(zip(classes,result.box.maps.tolist())),'claim':'Evaluación de este dataset. No certifica generalización a nuevas placas ni compatibilidad eléctrica.'}
    report_path=Path(model.trainer.save_dir)/'evaluation.json';report_path.write_text(json.dumps(report,indent=2))
    best.export(format='onnx',imgsz=args.size,opset=17,simplify=False,dynamic=False,nms=False)
    print(f'Resultados: {report_path}. Revisá errores por clase antes de publicar los pesos.')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--data',default='datasets/prepared/data.yaml');p.add_argument('--epochs',type=int,default=80);p.add_argument('--batch',type=int,default=8);p.add_argument('--size',type=int,choices=[320,416,640],default=640);p.add_argument('--name',default='connectors');run(p.parse_args())
