"""Prepare a reviewed training run for the local web demo; never deploy remotely."""
import argparse,hashlib,json,shutil
from pathlib import Path

def prepare(run):
    run=Path(run);report=json.loads((run/'evaluation.json').read_text());audit=report['data_audit'];model=run/'weights/best.onnx'
    if not model.is_file():raise ValueError('Falta la exportacion ONNX evaluada.')
    classes=audit['classes']
    if classes!=['CPU_SOCKET','PCIE_SLOT','POWER_CONNECTOR','DIMM_SLOT']:raise ValueError('Revisar contrato de clases.')
    import onnxruntime as ort
    session=ort.InferenceSession(str(model),providers=['CPUExecutionProvider'])
    size=report['input_size']
    if session.get_inputs()[0].shape!=[1,3,size,size] or session.get_outputs()[0].shape[1]!=4+len(classes):raise ValueError('Contrato ONNX incorrecto')
    root=Path(__file__).resolve().parents[1]/'dist/models';root.mkdir(exist_ok=True)
    shutil.copyfile(model,root/'connectors.onnx')
    manifest={'ready':True,'version':'bis497-v5-yolo11n-pilot-1','classes':classes,'inputSize':size,'sha256':hashlib.sha256(model.read_bytes()).hexdigest(),'source':audit['source'],'license':'Dataset CC BY 4.0; modelo derivado de Ultralytics YOLO11 AGPL-3.0','author':'BIS497; entrenamiento local BuildAcademy','test':report['test'],'perClassMap50_95':report['per_class_map50_95'],'limitations':['Piloto de cuatro clases: no identifica PCIe x1/x16, ATX/EPS, M.2, SATA o FAN_HEADER por separado.','24 imagenes de test; separacion por modelo fisico de motherboard no verificada.','Una deteccion no comprueba compatibilidad, protocolo ni estado fisico.']}
    (root/'manifest.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding='utf-8')
    print(json.dumps(manifest,indent=2,ensure_ascii=False))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('run');prepare(p.parse_args().run)
