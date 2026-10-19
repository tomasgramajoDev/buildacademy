"""Compare completed candidates on identical validation data; never select on test."""
import argparse
import json
from pathlib import Path
from prepare_dataset import CLASSES


def validation_summary(report):
    if report.get('split') != 'val' or set(report.get('per_class', {})) != set(CLASSES):
        raise ValueError('Expected validation results for all nine classes.')
    scores = {}
    for name, counts in report['per_class'].items():
        values = [counts.get(k) for k in ['tp', 'fp', 'fn']]
        if any(type(n) is not int or n < 0 for n in values):
            raise ValueError('Invalid detection counts.')
        tp, fp, fn = values
        if tp+fn == 0:
            raise ValueError('Every class needs validation ground truth.')
        scores[name] = {'f1': 2*tp/(2*tp+fp+fn), 'recall': tp/(tp+fn),
                        'tp':tp, 'fp':fp, 'fn':fn}
    return {'macro_f1':sum(v['f1'] for v in scores.values())/len(CLASSES),
            'per_class':scores,
            'zero_recall_classes':[name for name, value in scores.items() if value['tp']==0]}


def load_candidate(directory):
    directory = Path(directory)
    read = lambda name: json.loads((directory/name).read_text(encoding='utf-8'))
    if read('status.json').get('stage') != 'completed':
        raise ValueError('Candidate pipeline has not completed.')
    report, provenance = read('runtime-val.json'), read('provenance.json')
    rows = [r for r in provenance['files'] if r['split']=='val']
    identity = sorted((r['model_id'], r['image_sha256'], r['label_sha256']) for r in rows)
    if not identity or len(identity) != len(set(identity)):
        raise ValueError('Missing or duplicate validation provenance.')
    if len(report['images']) != len(identity):
        raise ValueError('Validation image count differs from provenance.')
    operating = {key:report[key] for key in ['confidence_threshold','nms_iou','matching_iou','runtime']}
    return {'model':report['model'], **validation_summary(report)}, identity, operating


def compare(first, second):
    a, images_a, operating_a = load_candidate(first)
    b, images_b, operating_b = load_candidate(second)
    if images_a != images_b:
        raise ValueError('Candidates used different validation images, labels or model groups.')
    if operating_a != operating_b:
        raise ValueError('Candidates used different operating thresholds or runtimes.')
    for name in CLASSES:
        ca, cb = a['per_class'][name], b['per_class'][name]
        if ca['tp']+ca['fn'] != cb['tp']+cb['fn']:
            raise ValueError('Validation ground-truth counts differ despite matching provenance.')
    winner = None if a['macro_f1']==b['macro_f1'] else max([a,b],key=lambda x:x['macro_f1'])['model']
    return {'selection_split':'val', 'selection_metric':'macro F1 across nine classes',
            'preferred_for_further_review':winner, 'candidates':[a,b], 'operating':operating_a,
            'validation_images':len(images_a), 'deployment_approved':False,
            'limitations':['Small reused validation set; ranking is not independent certification.',
                           'Test metrics were not read or used to rank candidates.',
                           'Inspect class failures and fresh held-out boards before deployment.']}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('first');parser.add_argument('second');parser.add_argument('--output',required=True)
    args=parser.parse_args()
    result=compare(args.first,args.second)
    Path(args.output).write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'preferred_for_further_review':result['preferred_for_further_review'],
                      'deployment_approved':False}))
