"""Full metric panel requested by the PM, computed from the runtime detector on one split.

Operating point (precision/recall/F1 and the board-level, confusion and small-object metrics) is
fixed at --threshold (default 0.5). AP/mAP use threshold 0.05 so the whole precision-recall curve
is covered. Critical classes and the small-object definition are PROVISIONAL until the PM agrees
on them; both are written into the report. This measures the generic nine-class detector only:
identification of specific headers (A2, CPU_FAN, ...) is not implemented. Use on val/test or on a
holdout only after candidate selection.
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from recognition.detector import ConnectorDetector
from evaluate_runtime import iou

CRITICAL = ['CPU_SOCKET', 'DIMM_SLOT', 'M2_SLOT', 'ATX_POWER', 'CPU_POWER', 'FAN_HEADER']
SMALL_AREA_FRACTION = 0.005  # ground-truth box below 0.5 % of image area counts as small
PM_TARGETS = {  # (minimum, MVP); Tomi's direct 95 % precision/recall overrides the PM recall
    'precision': (.90, .95), 'recall': (.85, .95), 'f1': (.87, .95), 'map50': (.85, .95),
    'map50_95': (.65, .80), 'critical_ap50_min': (.85, .95), 'critical_precision_min': (.90, .98),
    'detection_recall_any_class': (None, .97), 'identification_accuracy': (None, .98),
    'critical_confusion_rate': (None, .01), 'complete_boards': (None, .90), 'small_recall': (None, .90),
}


def load_ground_truth(root, image, classes, w, h):
    rows = []
    for line in (root / 'labels' / (image.stem + '.txt')).read_text().splitlines():
        c, x, y, bw, bh = map(float, line.split())
        rows.append((classes[int(c)], [(x-bw/2)*w, (y-bh/2)*h, (x+bw/2)*w, (y+bh/2)*h]))
    return rows


def box_of(d):
    b = d['bbox']
    return [b['x'], b['y'], b['x']+b['width'], b['y']+b['height']]


def average_precision(scored, positives):
    """scored: list of (confidence, is_tp). 101-point interpolation."""
    if positives == 0:
        return None
    scored = sorted(scored, key=lambda s: -s[0])
    tp = np.cumsum([s[1] for s in scored]) if scored else np.array([])
    fp = np.cumsum([not s[1] for s in scored]) if scored else np.array([])
    if not len(tp):
        return 0.0
    recall, precision = tp/positives, tp/np.maximum(tp+fp, 1e-9)
    precision = np.maximum.accumulate(precision[::-1])[::-1]
    grid = np.linspace(0, 1, 101)
    idx = np.searchsorted(recall, grid, side='left')
    return float(np.mean([precision[i] if i < len(precision) else 0 for i in idx]))


def match(detections, gt, threshold, same_class):
    """Greedy by confidence. Returns list of (detection_index, gt_index) matches."""
    used, pairs = set(), []
    for di in sorted(range(len(detections)), key=lambda i: -detections[i]['confidence']):
        best, bi = threshold, -1
        for gi, (gc, gb) in enumerate(gt):
            if gi in used or (same_class and gc != detections[di]['classId']):
                continue
            v = iou(box_of(detections[di]), gb)
            if v >= best:
                best, bi = v, gi
        if bi >= 0:
            used.add(bi); pairs.append((di, bi))
    return pairs


def evaluate(model_dir, data_dir, split, threshold=.5):
    low = ConnectorDetector(model_dir, threshold=.05)
    classes = low.classes
    root = Path(data_dir) / split
    tp = {c: 0 for c in classes}; fp = dict(tp); fn = dict(tp)
    scored = {t: {c: [] for c in classes} for t in np.arange(.5, .96, .05).round(2)}
    positives = {c: 0 for c in classes}
    any_hit = any_total = ident_ok = ident_total = 0
    crit_conf = crit_total = small_hit = small_total = complete = 0
    images = sorted((root / 'images').glob('*'))
    for image in images:
        result = low.recognize(image.read_bytes())
        w, h = result['image']['width'], result['image']['height']
        gt = load_ground_truth(root, image, classes, w, h)
        for c, _ in gt:
            positives[c] += 1
        for t in scored:
            pairs = {di for di, _ in match(result['detections'], gt, t, True)}
            for di, d in enumerate(result['detections']):
                scored[t][d['classId']].append((d['confidence'], di in pairs))
        ops = [d for d in result['detections'] if d['confidence'] >= threshold]
        same = match(ops, gt, .5, True)
        hit_g = {g for _, g in same}
        for di, d in enumerate(ops):
            (tp if any(p[0] == di for p in same) else fp)[d['classId']] += 1
        for gi, (c, _) in enumerate(gt):
            if gi not in hit_g:
                fn[c] += 1
        loc = {g: ops[d]['classId'] for d, g in match(ops, gt, .5, False)}
        any_total += len(gt); any_hit += len(loc)
        for gi, (c, b) in enumerate(gt):
            if gi in loc:
                ident_total += 1; ident_ok += loc[gi] == c
                if c in CRITICAL:
                    crit_total += 1; crit_conf += loc[gi] != c
            elif c in CRITICAL:
                crit_total += 1  # missed critical connector counts in the denominator only
            if (b[2]-b[0])*(b[3]-b[1]) < SMALL_AREA_FRACTION*w*h:
                small_total += 1; small_hit += gi in hit_g
        complete += (len(hit_g) == len(gt))
    T, P, N = sum(tp.values()), sum(fp.values()), sum(fn.values())
    precision, recall = T/(T+P) if T+P else None, T/(T+N) if T+N else None
    f1 = 2*precision*recall/(precision+recall) if precision and recall else 0.0
    ap50 = {c: average_precision(scored[.5][c], positives[c]) for c in classes}
    ap_all = {c: (None if positives[c] == 0 else float(np.mean([average_precision(scored[t][c], positives[c]) for t in scored]))) for c in classes}
    valid = [v for v in ap50.values() if v is not None]
    valid_all = [v for v in ap_all.values() if v is not None]
    crit_ap = {c: ap50[c] for c in CRITICAL}
    crit_prec = {c: (tp[c]/(tp[c]+fp[c]) if tp[c]+fp[c] else None) for c in CRITICAL}
    rate = lambda a, b: a/b if b else None
    metrics = {
        'precision': precision, 'recall': recall, 'f1': f1,
        'map50': float(np.mean(valid)) if valid else None,
        'map50_95': float(np.mean(valid_all)) if valid_all else None,
        'critical_ap50_min': min((v for v in crit_ap.values() if v is not None), default=None),
        'critical_precision_min': min((v for v in crit_prec.values() if v is not None), default=None),
        'detection_recall_any_class': rate(any_hit, any_total),
        'identification_accuracy': rate(ident_ok, ident_total),
        'critical_confusion_rate': rate(crit_conf, crit_total),
        'complete_boards': rate(complete, len(images)),
        'small_recall': rate(small_hit, small_total),
    }
    # Direction: confusion is "lower is better"; everything else "higher".
    verdict = {}
    for key, (minimum, mvp) in PM_TARGETS.items():
        v = metrics[key]
        better = (lambda a, b: a <= b) if key == 'critical_confusion_rate' else (lambda a, b: a >= b)
        verdict[key] = {'value': v, 'minimum': minimum, 'mvp': mvp,
                        'mvp_met': None if v is None else bool(better(v, mvp))}
    return {
        'split': split, 'model': low.version, 'operating_threshold': threshold, 'ap_threshold': .05,
        'counts': {'tp': T, 'fp': P, 'fn': N, 'images': len(images), 'small_objects': small_total},
        'per_class': {c: {'tp': tp[c], 'fp': fp[c], 'fn': fn[c], 'ap50': ap50[c], 'ap50_95': ap_all[c]} for c in classes},
        'metrics': verdict,
        'provisional_definitions': {'critical_classes': CRITICAL, 'small_object': f'GT box area < {SMALL_AREA_FRACTION:.1%} of image',
                                    'aggregation': 'micro for P/R/F1; macro over classes with ground truth for AP/mAP'},
        'targets_note': "Tomi's precision/recall >= 95 % override the PM recall proposal (92 %).",
        'not_covered': 'Identification of specific headers (DIMM_A1, CPU_FAN, ...); photo groups by manufacturer/model.',
    }


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--model-dir', required=True); p.add_argument('--data', required=True)
    p.add_argument('--split', choices=['train', 'val', 'test'], default='val')
    p.add_argument('--threshold', type=float, default=.5); p.add_argument('--output', required=True)
    a = p.parse_args()
    r = evaluate(a.model_dir, a.data, a.split, a.threshold)
    Path(a.output).write_text(json.dumps(r, indent=2), encoding='utf-8')
    for k, v in r['metrics'].items():
        print(f"{k:28} {v['value']!s:22} mvp_met={v['mvp_met']}")
