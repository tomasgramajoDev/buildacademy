"""Board-grouped k-fold cross-validation over every annotated board except reserved holdouts.

Each fold trains on three folds, uses one fold for validation (checkpoint selection) and reports on a
fourth fold the model never saw, so every board is scored out-of-fold exactly once. Photos of the same
model never cross folds. Pooled out-of-fold counts give a far steadier estimate than one 5-board test.
Reserved boards listed in --exclude stay untouched (default: ASUS Prime Z690-A).
Run with the GPU environment: .venv-gpu/Scripts/python.exe ml/cross_validate.py --output tmp/cv-v16
"""
import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'ml'))

CLASSES = ['CPU_SOCKET', 'DIMM_SLOT', 'PCIe_X16', 'PCIe_X1', 'M2_SLOT', 'SATA_PORT',
           'ATX_POWER', 'CPU_POWER', 'FAN_HEADER']


def load_boards(exclude):
    boards = {}
    for folder in ['annotations', 'holdout_annotations']:
        for path in sorted((ROOT / 'ml' / folder).glob('*.json')):
            data = json.loads(path.read_text(encoding='utf-8'))
            if data['status'] != 'reviewed' or data.get('unresolved'):
                continue
            if any(word.casefold() in data['model_id'].casefold() for word in exclude):
                continue
            image = ROOT / data['image']
            if hashlib.sha256(image.read_bytes()).hexdigest() != data['image_sha256']:
                raise ValueError(f'Image changed since review: {path.name}')
            boards.setdefault(data['model_group'], []).append(data)
    return boards


def assign_folds(boards, k):
    folds = [[] for _ in range(k)]
    load = [0] * k
    for group, items in sorted(boards.items(), key=lambda kv: -sum(len(i['boxes_xyxy']) for i in kv[1])):
        target = min(range(k), key=lambda i: (load[i], len(folds[i])))
        folds[target].append(group)
        load[target] += sum(len(i['boxes_xyxy']) for i in items)
    return folds


def write_split(root, split, items):
    (root / split / 'images').mkdir(parents=True, exist_ok=True)
    (root / split / 'labels').mkdir(parents=True, exist_ok=True)
    for number, data in enumerate(items):
        stem = f"{number:04d}-{data['model_group']}"
        image = ROOT / data['image']
        shutil.copyfile(image, root / split / 'images' / f'{stem}{image.suffix.lower()}')
        w, h = data['width'], data['height']
        lines = [f'{CLASSES.index(c)} {(a+c2)/2/w:.8f} {(b+d)/2/h:.8f} {(c2-a)/w:.8f} {(d-b)/h:.8f}'
                 for c, a, b, c2, d in data['boxes_xyxy']]
        (root / split / 'labels' / f'{stem}.txt').write_text('\n'.join(lines) + '\n', encoding='utf-8')


def run_fold(index, folds, boards, output, args):
    from ultralytics import YOLO
    import torch
    k = len(folds)
    test_groups, val_groups = folds[index], folds[(index + 1) % k]
    train_groups = [g for i, f in enumerate(folds) if i not in (index, (index + 1) % k) for g in f]
    root = output / f'fold{index}'
    if root.exists():
        raise ValueError(f'{root} already exists; choose a new output directory.')
    for split, groups in [('train', train_groups), ('val', val_groups), ('test', test_groups)]:
        write_split(root, split, [d for g in groups for d in boards[g]])
    (root / 'data.yaml').write_text(
        f'path: {root.as_posix()}\ntrain: train/images\nval: val/images\ntest: test/images\n'
        f'nc: {len(CLASSES)}\nnames: {CLASSES}\n', encoding='utf-8')
    name = f'{output.name}-fold{index}'
    model = YOLO(args.weights)
    model.train(data=str(root / 'data.yaml'), epochs=args.epochs, imgsz=args.size, batch=args.batch,
                device=0 if torch.cuda.is_available() else 'cpu', workers=0, seed=42, deterministic=True,
                project=str((output / 'runs').resolve()), name=name, exist_ok=False, patience=args.patience, plots=False, **json.loads(args.train_args))
    best = YOLO(str(model.trainer.best))
    onnx = Path(best.export(format='onnx', imgsz=args.size, opset=17, simplify=False, dynamic=False, nms=False))
    package = root / 'model'
    package.mkdir()
    shutil.copyfile(onnx, package / 'connectors.onnx')
    (package / 'manifest.json').write_text(json.dumps({
        'ready': True, 'version': name, 'classes': CLASSES, 'inputSize': args.size,
        'sha256': hashlib.sha256((package / 'connectors.onnx').read_bytes()).hexdigest()}), encoding='utf-8')
    from pm_metrics import evaluate
    result = evaluate(package, root, 'test', args.threshold)
    result['fold'] = index
    result['test_groups'] = test_groups
    (output / f'fold{index}-result.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    return result


def pool(results):
    total = {c: {'tp': 0, 'fp': 0, 'fn': 0} for c in CLASSES}
    for result in results:
        for c, row in result['per_class'].items():
            for key in total[c]:
                total[c][key] += row[key]
    tp, fp, fn = (sum(row[key] for row in total.values()) for key in ('tp', 'fp', 'fn'))
    summary = {'tp': tp, 'fp': fp, 'fn': fn,
               'precision': tp / (tp + fp) if tp + fp else None, 'recall': tp / (tp + fn) if tp + fn else None,
               'per_class': {c: {**row, 'precision': row['tp'] / (row['tp'] + row['fp']) if row['tp'] + row['fp'] else None,
                                 'recall': row['tp'] / (row['tp'] + row['fn']) if row['tp'] + row['fn'] else None}
                             for c, row in total.items()},
               'per_fold': [{'fold': r['fold'], 'precision': r['counts']['tp'] / max(1, r['counts']['tp'] + r['counts']['fp']),
                             'recall': r['counts']['tp'] / max(1, r['counts']['tp'] + r['counts']['fn'])} for r in results]}
    return summary


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True)
    parser.add_argument('--folds', type=int, default=5)
    parser.add_argument('--weights', default='yolo11s.pt')
    parser.add_argument('--size', type=int, default=960)
    parser.add_argument('--batch', type=int, default=8)
    parser.add_argument('--epochs', type=int, default=200)
    parser.add_argument('--patience', type=int, default=50)
    parser.add_argument('--threshold', type=float, default=.5)
    parser.add_argument('--train-args', default='{}', help='JSON of extra Ultralytics train arguments, e.g. {"cls":1.5}')
    parser.add_argument('--exclude', nargs='*', default=['Prime Z690-A'])
    args = parser.parse_args()
    output = (ROOT / args.output).resolve()
    output.mkdir(parents=True, exist_ok=False)
    boards = load_boards(args.exclude)
    folds = assign_folds(boards, args.folds)
    (output / 'folds.json').write_text(json.dumps(folds, indent=2), encoding='utf-8')
    results = []
    for i in range(args.folds):
        results.append(run_fold(i, folds, boards, output, args))
        (output / 'summary.json').write_text(json.dumps(pool(results), indent=2), encoding='utf-8')
    summary = pool(results)
    print(json.dumps({k: summary[k] for k in ('tp', 'fp', 'fn', 'precision', 'recall')}))
