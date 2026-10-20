import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'ml'))
from assess_target import assess, metrics


class AcceptanceTargetTests(unittest.TestCase):
    def test_precision_and_recall_must_pass_separately(self):
        self.assertFalse(metrics(94, 6, 0)['precision_target_met'])
        self.assertFalse(metrics(94, 0, 6)['recall_target_met'])
        self.assertTrue(metrics(95, 5, 5)['precision_target_met'])
        self.assertTrue(metrics(95, 5, 5)['recall_target_met'])
        self.assertFalse(metrics(0, 0, 0)['precision_target_met'])
        self.assertFalse(metrics(0, 0, 0)['recall_target_met'])

    def test_v5_report_fails_and_saved_rounded_metrics_are_not_trusted(self):
        data = json.loads((ROOT / 'ml/EVALUACION-INDEPENDIENTE-V5.json').read_text())
        for row in data['result']['per_class'].values():
            row['precision'] = row['recall'] = 1.0
        report = assess(data)
        self.assertEqual(report['aggregate']['precision'], .75)
        self.assertEqual(report['aggregate']['recall'], .3125)
        self.assertFalse(report['observed_aggregate_target_met'])
        self.assertFalse(report['deployment_approved'])
        for change in ('reuse', 'counts', 'missing', 'negative'):
            invalid = copy.deepcopy(data)
            if change == 'reuse':
                invalid['result']['selection_used_this_data'] = True
            elif change == 'counts':
                invalid['result']['images'][0]['tp'] += 1
            elif change == 'missing':
                del invalid['result']['per_class']['M2_SLOT']
            else:
                invalid['result']['per_class']['M2_SLOT']['fn'] = -1
            with self.assertRaises(ValueError):
                assess(invalid)


if __name__ == '__main__':
    unittest.main()
