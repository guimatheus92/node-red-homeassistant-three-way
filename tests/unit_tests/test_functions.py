# tests/unit_tests/test_functions.py

import os
import pytest
import sys
import pandas as pd

# Add the root directory of the project to the PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from scripts.check_mapping import read_mappings, analyze_mappings  # noqa: E402
from scripts.get_ha_devices_entities import read_configurations  # noqa: E402
from scripts.main import create_node_red_flow, read_mappings as read_main_mappings  # noqa: E402


@pytest.fixture(scope='module')
def mappings_file():
    return os.path.join(os.path.dirname(__file__), '../../mappings.csv')


@pytest.fixture(scope='module')
def config_file():
    return os.path.join(os.path.dirname(__file__), '../../config.yaml')

@pytest.fixture(scope='module')
def devices_file():
    return os.path.join(os.path.dirname(__file__), '../../devices.csv')

def test_devices_file(devices_file):
    with open(devices_file, 'w') as f:
        f.write('device,entity_id\n')
        f.write('switch_1_kitchen,switch.switch_1_kitchen_button_1\n')
        f.write('switch_1_room,switch.switch_1_room_button_1\n')
    df = pd.read_csv(devices_file)
    assert df.shape == (2, 2)
    assert list(df.columns) == ['device', 'entity_id']
    assert df['device'].tolist() == ['switch_1_kitchen', 'switch_1_room']
    assert df['entity_id'].tolist() == ['switch.switch_1_kitchen_button_1', 'switch.switch_1_room_button_1']

def test_analyze_mappings():
    mappings = [
        ('switch_1_kitchen', 'switch.switch_1_kitchen_button_1', 'switch_1_room', 'switch.switch_1_room_button_1'),
        ('switch_1_room', 'switch.switch_1_room_button_1', 'switch_1_kitchen', 'switch.switch_1_kitchen_button_1')
    ]
    missing_sources, missing_targets = analyze_mappings(mappings)
    assert missing_sources == []
    assert missing_targets == []


def test_read_configurations(config_file):
    with open(config_file, 'w') as f:
        f.write('home_assistant:\n  home_assistant_url: "http://test-url"\n  access_token: "test-token"\n')
    config = read_configurations()
    assert config['home_assistant']['home_assistant_url'] == 'http://test-url'
    assert config['home_assistant']['access_token'] == 'test-token'


def test_create_node_red_flow(mappings_file):
    with open(mappings_file, 'w') as f:
        f.write('source_device,source_entity_id,target_device,target_entity_id\n')
        f.write('switch_1_kitchen,switch.switch_1_kitchen_button_1,switch_1_room,switch.switch_1_room_button_1\n')
        f.write('switch_1_room,switch.switch_1_room_button_1,switch_1_kitchen,switch.switch_1_kitchen_button_1\n')
    mappings = read_main_mappings(mappings_file)
    flow = create_node_red_flow(mappings)
    assert isinstance(flow, str)
    assert 'switch_1_kitchen' in flow
    assert 'switch.switch_1_kitchen_button_1' in flow
    assert 'switch_1_room' in flow
    assert 'switch.switch_1_room_button_1' in flow
