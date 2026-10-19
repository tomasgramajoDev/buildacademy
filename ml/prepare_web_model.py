"""Package an evaluated run in a new directory; never replace a deployed detector."""
import argparse
import hashlib
import json
import shutil
from pathlib import Path

PILOT = ['CPU_SOCKET','PCIE_SLOT','POWER_CONNECTOR','DIMM_SLOT']
NINE = ['CPU_SOCKET','DIMM_SLOT','PCIe_X16','PCIe_X1','M2_SLOT','SATA_PORT','ATX_POWER','CPU_POWER','FAN_HEADER']


def manifest_for(report, model, version):
    audit = report['data_audit']
    classes = audit['classes']
    if classes not in [PILOT, NINE]:
        raise ValueError('Contrato de clases desconocido.')
    if classes == NINE and audit.get('review_gate') != 'passed':
        raise ValueError('Falta la revisión de anotaciones y separación por modelo.')
    if report['input_size'] not in [320,416,640] or not report.get('test'):
        raise ValueError('Falta evaluación o tamaño de entrada válido.')
    limitations = ['Una detección no comprueba compatibilidad, protocolo ni estado físico.']
    if classes == PILOT:
        limitations.append('Cuatro clases amplias; no distingue los nueve tipos de conectores.')
    else:
        limitations.extend(['Conjunto inicial pequeño; requiere revisar métricas por clase antes de usarlo.',
                             'M.2 incluye conectores Wi-Fi; no implica compatibilidad con SSD.',
                             'Las cajas SATA representan carcasas visibles, no número de puertos.'])
    return {'ready': True, 'releaseStatus': 'experimental', 'version': version,
            'classes': classes, 'inputSize': report['input_size'],
            'sha256': hashlib.sha256(model.read_bytes()).hexdigest(),
            'source': audit.get('source','Anotaciones revisadas de BIS497, versión 5'),
            'license': 'Dataset CC BY 4.0; modelo derivado de Ultralytics YOLO11 AGPL-3.0',
            'test': report['test'], 'perClassMap50_95': report['per_class_map50_95'],
            'dataAudit': audit, 'limitations': limitations}


def prepare(run, output, version):
    run, output = Path(run).resolve(), Path(output).resolve()
    deployed = Path(__file__).resolve().parents[1]/'dist/models'
    if output == deployed or deployed in output.parents:
        raise ValueError('Prepará un candidato separado; este comando no reemplaza el detector web.')
    if output.exists():
        raise ValueError('Usá un directorio de salida nuevo para no sobrescribir artefactos.')
    report = json.loads((run/'evaluation.json').read_text(encoding='utf-8'))
    model = run/'weights/best.onnx'
    manifest = manifest_for(report, model, version)
    import onnxruntime as ort
    options = ort.SessionOptions(); options.intra_op_num_threads = 2
    session = ort.InferenceSession(str(model), sess_options=options, providers=['CPUExecutionProvider'])
    size = manifest['inputSize']; shape = session.get_outputs()[0].shape
    if session.get_inputs()[0].shape != [1,3,size,size] or len(shape)!=3 or shape[0]!=1 or shape[1]!=4+len(manifest['classes']):
        raise ValueError('Contrato ONNX incorrecto.')
    output.mkdir(parents=True)
    shutil.copyfile(model, output/'connectors.onnx')
    shutil.copyfile(run/'evaluation.json', output/'evaluation.json')
    (output/'manifest.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding='utf-8')
    return manifest


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('run');p.add_argument('--output',required=True);p.add_argument('--version',required=True)
    args=p.parse_args()
    print(json.dumps(prepare(args.run,args.output,args.version),indent=2,ensure_ascii=False))
