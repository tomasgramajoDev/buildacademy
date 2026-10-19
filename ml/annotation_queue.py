"""Collect one source image per original group for nine-class relabeling.

This is a review queue, never a training manifest. Old groups are filename
hints, not verified physical motherboard identities. No labels are promoted.
"""
import argparse
import json
import shutil
from pathlib import Path

CLASSES = ['CPU_SOCKET', 'DIMM_SLOT', 'PCIe_X16', 'PCIe_X1', 'M2_SLOT',
           'SATA_PORT', 'ATX_POWER', 'CPU_POWER', 'FAN_HEADER']


def create_queue(manifest, output):
    manifest, output = Path(manifest).resolve(), Path(output).resolve()
    rows = json.loads(manifest.read_text(encoding='utf-8'))
    if output.exists() and any(output.iterdir()):
        raise ValueError('La salida debe estar vacía; no se sobrescriben revisiones.')
    groups = {}
    for row in rows:
        groups.setdefault(row['board_id'], []).append(row)
    # Resolve every input before copying. Keep old labels as reference only.
    selected = []
    for group, variants in sorted(groups.items()):
        row = sorted(variants, key=lambda r: r['image'])[0]
        image = manifest.parent / row['image']
        label = manifest.parent / row['label']
        if not image.is_file() or not label.is_file():
            raise ValueError('Faltan archivos del dataset original.')
        selected.append((group, variants, row, image, label))
    (output / 'images').mkdir(parents=True, exist_ok=True)
    (output / 'reference_labels').mkdir()
    queue = []
    for index, (group, variants, row, image, label) in enumerate(selected):
        image_name = f'images/{index:06}{image.suffix.lower()}'
        label_name = f'reference_labels/{index:06}.txt'
        shutil.copy2(image, output / image_name)
        shutil.copy2(label, output / label_name)
        queue.append({
            'image': image_name, 'reference_label': label_name,
            'source_group_hint': group, 'source_variants': len(variants),
            'source': row['source'], 'license': row['license'],
            'original_split': row['split'], 'model_id': None,
            'board_id': None, 'split': None, 'review_status': 'pending',
            'reviewed_by': None, 'label': None,
            'checks': {'all_visible_connectors': False, 'individual_dimm_slots': False,
                       'pcie_physical_size': False, 'power_connector_type': False,
                       'duplicates_and_board_identity': False},
        })
    report = {'status': 'pending_annotation', 'images': len(queue),
              'source_images': len(rows), 'reviewed_images': 0,
              'target_classes': CLASSES,
              'reference_classes': ['CPU_SOCKET', 'PCIE_SLOT', 'POWER_CONNECTOR', 'DIMM_SLOT'],
              'warning': 'Las etiquetas de referencia no son etiquetas de nueve clases. '
                         'Confirmar identidad, revisar todas las conexiones y reservar test antes de entrenar.'}
    (output / 'queue.json').write_text(json.dumps(queue, indent=2, ensure_ascii=False), encoding='utf-8')
    (output / 'status.json').write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('manifest')
    parser.add_argument('--output', default='datasets/connectors-nine-review')
    args = parser.parse_args()
    print(json.dumps(create_queue(args.manifest, args.output), indent=2))
