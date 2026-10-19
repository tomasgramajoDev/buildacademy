import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / 'ml'))
from review_gate import validate_reviews


def row(model, split):
    return {'model_id': model, 'board_id': model + '-physical',
            'reviewed_by': 'test-reviewer', 'identity_evidence': 'test-manual',
            'label': 'test.txt', 'review_status': 'reviewed', 'split': split,
            'checks': {k: True for k in ['all_visible_connectors', 'individual_dimm_slots',
                       'pcie_physical_size', 'power_connector_type', 'duplicates_and_board_identity']}}


class ReviewGateTests(unittest.TestCase):
    def test_same_model_different_physical_boards_cannot_cross_splits(self):
        a, b = row('Board A', 'train'), row('board a', 'test')
        b['board_id'] = 'another-physical-board'
        with self.assertRaisesRegex(ValueError, 'Fuga'):
            validate_reviews([a, b])

    def test_drafts_ambiguities_and_incomplete_reviews_are_rejected(self):
        for change in [{'review_status': 'draft'}, {'unresolved': ['SATA']},
                       {'checks': {}}, {'identity_evidence': ''}]:
            a = row('A', 'train')
            a.update(change)
            with self.assertRaises(ValueError):
                validate_reviews([a])

    def test_distinct_reviewed_models_pass_identity_gate(self):
        self.assertEqual(len(validate_reviews([row('A', 'train'), row('B', 'test')])), 2)


if __name__ == '__main__':
    unittest.main()
