"""Check the five documentary examples, without running a protocol mapper."""
import copy
import json
from pathlib import Path


def need(condition, message):
    if not condition:
        raise ValueError(message)


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        need(key not in result, 'Duplicate JSON key: ' + key)
        result[key] = value
    return result


def verify(document):
    need(document['schema'] == 'atlas-parent-key-documentary-supplement/1', 'Schema')
    need(document['synthetic'] is True and document['private_data'] is False, 'Origin')
    for flag in ['normative', 'product_0_2_1_executed', 'arc09_approved']:
        need(document[flag] is False, 'Authority: ' + flag)
    cases = document['cases']
    need([case['id'] for case in cases] == ['N1', 'N2', 'N3', 'N4', 'N5'], 'Inventory')
    expected = {'import_result': 'REJECT_ATOMIC', 'descriptor_emitted': False,
                'parent_key_presence_emitted': False, 'partial_tree_emitted': False}
    for case, value in zip(cases, ['', 17, False, {}, []]):
        actual = case['input']['node']['parent_key']
        need(type(actual) is type(value) and actual == value, case['id'] + ': input')
        outcome = case['expected_future']
        need(set(outcome) == set(expected), case['id'] + ': expected fields')
        for key, required in expected.items():
            need(type(outcome[key]) is type(required) and outcome[key] == required,
                 case['id'] + ': expected ' + key)
    return len(cases)


def negative_controls(document):
    mutations = []
    for label in ['missing_case', 'duplicate_id', 'bool_as_integer',
                  'partial_descriptor', 'accepted_input', 'private_origin']:
        changed = copy.deepcopy(document)
        if label == 'missing_case':
            changed['cases'].pop()
        elif label == 'duplicate_id':
            changed['cases'][1]['id'] = 'N1'
        elif label == 'bool_as_integer':
            changed['cases'][1]['input']['node']['parent_key'] = True
        elif label == 'partial_descriptor':
            changed['cases'][0]['expected_future']['descriptor_emitted'] = True
        elif label == 'accepted_input':
            changed['cases'][0]['expected_future']['import_result'] = 'ACCEPT'
        else:
            changed['private_data'] = True
        try:
            verify(changed)
        except ValueError:
            mutations.append(label)
        else:
            raise ValueError('Negative control accepted: ' + label)
    return mutations


if __name__ == '__main__':
    document = json.loads(Path(__file__).with_name('PARENT-KEY-NEGATIVE-ORACLES.json')
                          .read_text(encoding='utf8'), object_pairs_hook=unique_object)
    count = verify(document)
    controls = negative_controls(document)
    print(json.dumps({'status': 'PASS_DOCUMENTARY_SUPPLEMENT', 'oracles': count,
                      'negative_controls_rejected': controls,
                      'product_0_2_1_executed': False, 'arc09_approved': False}))
