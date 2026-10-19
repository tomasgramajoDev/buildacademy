"""Select on validation, then record one independent evaluation without deployment."""
import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from compare_candidates import compare
from evaluate_runtime import evaluate


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def verify_holdout(directory, jobs):
    directory = Path(directory)
    audit = read(directory/'audit.json')
    if audit.get('purpose') != 'independent_post_selection_only' or audit.get('evaluated') is not False:
        raise ValueError('Expected an unused independent holdout.')
    images = sorted((directory/'test/images').glob('*'))
    labels = sorted((directory/'test/labels').glob('*.txt'))
    if not images or len(images) != audit['images'] or len(labels) != len(images):
        raise ValueError('Holdout file count changed.')
    sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    actual = Counter((sha(p), sha(directory/'test/labels'/(p.stem+'.txt'))) for p in images)
    expected = Counter((r['image_sha256'],r['label_sha256']) for r in audit['files'])
    if actual != expected:
        raise ValueError('Holdout image or label hashes changed.')
    for job in jobs:
        rows = read(Path(job)/'provenance.json')['files']
        models = {r['model_id'].strip().casefold() for r in rows}
        hashes = {r['image_sha256'] for r in rows}
        if any(r['model_id'].strip().casefold() in models or r['image_sha256'] in hashes for r in audit['files']):
            raise ValueError('Independent holdout overlaps candidate development data.')
    return audit


def finalize(first, second, holdout, output):
    jobs = [Path(first),Path(second)]
    output = Path(output)
    if output.exists():
        raise ValueError('Output exists; preserve the first independent result.')
    comparison = compare(*jobs)
    audit = verify_holdout(holdout,jobs)
    preferred = comparison['preferred_for_further_review']
    if preferred is None:
        raise ValueError('Validation tie requires a decision before independent inference.')
    matches = [j for j in jobs if read(j/'runtime-val.json')['model']==preferred]
    if len(matches)!=1:
        raise ValueError('Candidate model versions must uniquely identify the winner.')
    output.mkdir(parents=True)
    write = lambda name,value: (output/name).write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8')
    write('selection.json',comparison)
    write('holdout-provenance.json',audit)
    write('status.json',{'stage':'evaluating','published':False})
    # Exclusive marker prevents retrying inference against the same held-out set.
    marker = Path(holdout)/'evaluation-started.json'
    try:
        with marker.open('x',encoding='utf-8') as stream:
            json.dump({'model':preferred,'output':str(output.resolve())},stream)
        result = evaluate(matches[0]/'model',holdout,'test',
                          threshold=comparison['operating']['confidence_threshold'])
        result['claim'] = 'Independent post-selection diagnostic on a small manually reviewed holdout; not production certification.'
        result['selection_used_this_data'] = False
        write('independent-test.json',result)
        write('status.json',{'stage':'completed','selected_model':preferred,'published':False,
                             'deployment_approved':False})
    except Exception as error:
        write('status.json',{'stage':'failed','error_type':type(error).__name__,'published':False})
        raise
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('first');parser.add_argument('second')
    parser.add_argument('--holdout',required=True);parser.add_argument('--output',required=True)
    args=parser.parse_args()
    finalize(args.first,args.second,args.holdout,args.output)
