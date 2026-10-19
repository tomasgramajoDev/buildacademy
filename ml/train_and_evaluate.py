"""Run training, ONNX packaging and integration evaluation without polling or deployment."""
import argparse
import json
import os
from pathlib import Path
from types import SimpleNamespace


def execute(args):
    from train import run
    from prepare_web_model import prepare
    from evaluate_runtime import evaluate
    from smoke_integration import smoke
    from verify_prepared_dataset import verify

    output = Path(args.output).resolve()
    if output.exists():
        raise ValueError('Output already exists; choose a new run directory.')
    if list(Path('runs').rglob(args.name)):
        raise ValueError('Training run name already exists; do not restart implicitly.')
    dataset = Path(args.data).resolve()
    provenance = verify(args.manifest, dataset.parent)
    output.mkdir(parents=True)

    def write(name, data):
        path = output / name
        temporary = path.with_suffix(path.suffix + '.tmp')
        temporary.write_text(json.dumps(data, indent=2), encoding='utf-8')
        temporary.replace(path)

    def state(stage, **details):
        write('status.json', {'stage': stage, 'pid': os.getpid(),
                             'published': False, **details})

    write('provenance.json', provenance)
    # Archive the exact source manifest before later annotation work changes it.
    (output / 'source-manifest.json').write_bytes(Path(args.manifest).read_bytes())
    try:
        state('training')
        report = run(SimpleNamespace(data=str(dataset), name=args.name, epochs=args.epochs,
                                    patience=100, batch=2, size=640, resume=None))
        state('packaging', training_report=str(report))
        prepare(report.parent, output / 'model', args.name)
        state('evaluating_runtime')
        write('runtime-test.json', evaluate(output / 'model', dataset.parent, 'test'))
        write('runtime-val.json', evaluate(output / 'model', dataset.parent, 'val'))
        state('checking_http')
        image = next(iter(sorted((dataset.parent / 'test/images').glob('*.jpg'))))
        result = smoke(output / 'model', image)
        write('http.json', result)
        if not all(result['checks'].values()):
            raise RuntimeError('HTTP integration check failed.')
        state('completed', training_report=str(report),
              note='Experimental candidate; accuracy review required. No deployment performed.')
    except Exception as error:
        state('failed', error_type=type(error).__name__)
        raise


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data', required=True)
    parser.add_argument('--manifest', required=True)
    parser.add_argument('--name', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--epochs', type=int, default=300)
    execute(parser.parse_args())
