"""Require reviewed identity and complete annotations before nine-class training.

This gate records review claims, not proof that labels are correct. Inspect
the images and evidence; assigning a status cannot replace that inspection.
"""
import argparse
import json
from pathlib import Path


def validate_reviews(rows):
    models = {}
    required_checks = ['all_visible_connectors', 'individual_dimm_slots',
                       'pcie_physical_size', 'power_connector_type',
                       'duplicates_and_board_identity']
    if not rows:
        raise ValueError('No hay anotaciones revisadas.')
    for i, row in enumerate(rows):
        for key in ['model_id', 'board_id', 'reviewed_by', 'identity_evidence', 'label']:
            if not isinstance(row.get(key), str) or not row[key].strip():
                raise ValueError(f'Fila {i}: falta {key}.')
        if row.get('review_status') != 'reviewed' or row.get('unresolved'):
            raise ValueError(f'Fila {i}: anotación pendiente o ambigua.')
        if any(row.get('checks', {}).get(k) is not True for k in required_checks):
            raise ValueError(f'Fila {i}: revisión incompleta.')
        split = row.get('split')
        if split not in ['train', 'val', 'test']:
            raise ValueError(f'Fila {i}: split pendiente.')
        model = row['model_id'].strip().casefold()
        if model in models and models[model] != split:
            raise ValueError(f'Fuga de modelo: {model}.')
        models[model] = split
    return models


if __name__ == '__main__':
    from prepare_dataset import prepare
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('manifest')
    parser.add_argument('--output', default='datasets/connectors-nine-prepared')
    args = parser.parse_args()
    manifest = Path(args.manifest)
    models = validate_reviews(json.loads(manifest.read_text(encoding='utf-8')))
    report = prepare(manifest, args.output)
    report['review_gate'] = 'passed'
    report['model_count'] = len(models)
    (Path(args.output) / 'audit.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps(report, indent=2))
