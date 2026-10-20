"""Report the requested precision/recall target from saved independent counts.

No inference, threshold tuning, or deployment. This is an arithmetic assessment
of supplied evidence, not verification of dataset independence or certification.
"""
import argparse
import hashlib
import json
from pathlib import Path

from prepare_dataset import CLASSES


def counts(row):
    values = [row[k] for k in ('tp', 'fp', 'fn')]
    if any(type(v) is not int or v < 0 for v in values):
        raise ValueError('Counts must be nonnegative integers.')
    return values


def metrics(tp, fp, fn):
    return {
        'tp': tp, 'fp': fp, 'fn': fn,
        'precision': tp / (tp + fp) if tp + fp else None,
        'recall': tp / (tp + fn) if tp + fn else None,
        'precision_target_met': bool(tp + fp) and 100 * tp >= 95 * (tp + fp),
        'recall_target_met': bool(tp + fn) and 100 * tp >= 95 * (tp + fn),
    }


def assess(document):
    result, provenance = document['result'], document['provenance']
    if (result.get('selection_used_this_data') is not False
            or provenance.get('purpose') != 'independent_post_selection_only'):
        raise ValueError('Expected an independent post-selection report.')
    if set(result['per_class']) != set(CLASSES):
        raise ValueError('Expected all nine classes, without extra classes.')
    per_class = {name: metrics(*counts(result['per_class'][name])) for name in CLASSES}
    total = [sum(row[k] for row in per_class.values()) for k in ('tp', 'fp', 'fn')]
    images = result['images']
    if not images or len(images) != provenance['images']:
        raise ValueError('Image count does not match provenance.')
    image_counts = [counts(row) for row in images]
    if [sum(row[i] for row in image_counts) for i in range(3)] != total:
        raise ValueError('Per-image and per-class counts disagree.')
    if sum(row['boxes'] for row in provenance['files']) != total[0] + total[2]:
        raise ValueError('Ground-truth count does not match provenance.')
    aggregate = metrics(*total)
    return {
        'model': result['model'],
        'target': {'precision_min': .95, 'recall_min': .95, 'aggregation': 'micro'},
        'aggregate': aggregate,
        'observed_aggregate_target_met': (
            aggregate['precision_target_met'] and aggregate['recall_target_met']),
        'per_class': per_class,
        'classes_without_ground_truth': [
            name for name, row in per_class.items() if row['tp'] + row['fn'] == 0],
        'sample_images': len(images),
        'sample_models': len({row['model_id'] for row in provenance['files']}),
        'deployment_approved': False,
        'limitation': (
            'Observed counts only. Small or unrepresentative samples cannot certify '
            '95% generalization. Dataset independence must be verified separately. '
            'Per-class results are diagnostic; aggregate success never auto-deploys.'),
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('report')
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    raw = Path(args.report).read_bytes()
    report = assess(json.loads(raw))
    report['source_report_sha256'] = hashlib.sha256(raw).hexdigest()
    Path(args.output).write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
