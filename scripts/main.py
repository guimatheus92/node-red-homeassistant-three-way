import csv
import json
import uuid
from collections import defaultdict
import os

def create_node_red_flow(mappings):
    # Track the count of target entities per source entity
    device_to_source_targets = defaultdict(lambda: defaultdict(set))
    for mapping in mappings:
        device_to_source_targets[mapping[0]][mapping[1]].add(mapping[3])

    flow = [
        {
            "id": str(uuid.uuid4()),
            "type": "tab",
            "label": "Paralelos Virtuais",
            "disabled": False,
            "info": "",
            "env": []
        }
    ]

    for device, source_targets in device_to_source_targets.items():
        group_id = str(uuid.uuid4())
        group_nodes = []

        flow.append({
            "id": group_id,
            "type": "group",
            "z": flow[0]['id'],
            "name": device,
            "style": {
                "label": True,
                "color": "#000000"
            },
            "nodes": group_nodes,
            "x": 153.5,
            "y": 99,
            "w": 1055.5,
            "h": 319
        })

        for src_entity, target_entities in source_targets.items():
            state_changed_node_id = str(uuid.uuid4())
            group_nodes.append(state_changed_node_id)

            flow.append({
                "id": state_changed_node_id,
                "type": "server-state-changed",
                "z": flow[0]['id'],
                "g": group_id,
                "name": src_entity,
                "server": "20b962a5.ede7ee",
                "version": 5,
                "outputs": 2,
                "entityId": src_entity,
                "entityIdType": "exact",
                "outputInitially": True,
                "stateType": "str",
                "ifState": "on",
                "ifStateType": "str",
                "ifStateOperator": "is",
                "outputOnlyOnStateChange": True,
                "for": "0",
                "forType": "num",
                "forUnits": "minutes",
                "ignorePrevStateNull": False,
                "ignorePrevStateUnknown": False,
                "ignorePrevStateUnavailable": False,
                "ignoreCurrentStateUnknown": False,
                "ignoreCurrentStateUnavailable": False,
                "outputProperties": [
                    {"property": "payload", "propertyType": "msg", "value": "", "valueType": "entityState"},
                    {"property": "data", "propertyType": "msg", "value": "", "valueType": "eventData"},
                    {"property": "topic", "propertyType": "msg", "value": "", "valueType": "triggerId"}
                ],
                "x": 100,
                "y": 100,
                "wires": [[], []]
            })

            for i, tgt_entity in enumerate(target_entities):
                api_current_state_id_0 = str(uuid.uuid4())
                api_current_state_id_1 = str(uuid.uuid4())
                turn_on_node_id = str(uuid.uuid4())
                turn_off_node_id = str(uuid.uuid4())

                group_nodes.extend([api_current_state_id_0, api_current_state_id_1, turn_on_node_id, turn_off_node_id])

                flow.append({
                    "id": api_current_state_id_0,
                    "type": "api-current-state",
                    "z": flow[0]['id'],
                    "g": group_id,
                    "name": f"Check {tgt_entity} ON",
                    "server": "20b962a5.ede7ee",
                    "version": 3,
                    "outputs": 2,
                    "halt_if": "on",
                    "halt_if_type": "str",
                    "halt_if_compare": "is",
                    "entity_id": tgt_entity,
                    "state_type": "str",
                    "blockInputOverrides": False,
                    "outputProperties": [
                        {"property": "payload", "propertyType": "msg", "value": "", "valueType": "entityState"},
                        {"property": "data", "propertyType": "msg", "value": "", "valueType": "entity"}
                    ],
                    "for": "0",
                    "forType": "num",
                    "forUnits": "minutes",
                    "override_topic": False,
                    "state_location": "payload",
                    "override_payload": "msg",
                    "entity_location": "data",
                    "override_data": "msg",
                    "x": 300,
                    "y": 100 + i * 80,
                    "wires": [[], [turn_on_node_id]]
                })

                flow.append({
                    "id": api_current_state_id_1,
                    "type": "api-current-state",
                    "z": flow[0]['id'],
                    "g": group_id,
                    "name": f"Check {tgt_entity} OFF",
                    "server": "20b962a5.ede7ee",
                    "version": 3,
                    "outputs": 2,
                    "halt_if": "on",
                    "halt_if_type": "str",
                    "halt_if_compare": "is",
                    "entity_id": tgt_entity,
                    "state_type": "str",
                    "blockInputOverrides": False,
                    "outputProperties": [
                        {"property": "payload", "propertyType": "msg", "value": "", "valueType": "entityState"},
                        {"property": "data", "propertyType": "msg", "value": "", "valueType": "entity"}
                    ],
                    "for": "0",
                    "forType": "num",
                    "forUnits": "minutes",
                    "override_topic": False,
                    "state_location": "payload",
                    "override_payload": "msg",
                    "entity_location": "data",
                    "override_data": "msg",
                    "x": 300,
                    "y": 180 + i * 80,
                    "wires": [[turn_off_node_id], []]
                })

                flow.append({
                    "id": turn_on_node_id,
                    "type": "api-call-service",
                    "z": flow[0]['id'],
                    "g": group_id,
                    "name": f"Turn ON {tgt_entity}",
                    "server": "20b962a5.ede7ee",
                    "version": 5,
                    "domain": "switch",
                    "service": "turn_on",
                    "areaId": [],
                    "deviceId": [],
                    "entityId": [tgt_entity],
                    "data": "",
                    "dataType": "jsonata",
                    "mergeContext": "",
                    "mustacheAltTags": False,
                    "outputProperties": [],
                    "queue": "none",
                    "x": 500,
                    "y": 180 + i * 80,
                    "wires": [[]]
                })

                flow.append({
                    "id": turn_off_node_id,
                    "type": "api-call-service",
                    "z": flow[0]['id'],
                    "g": group_id,
                    "name": f"Turn OFF {tgt_entity}",
                    "server": "20b962a5.ede7ee",
                    "version": 5,
                    "domain": "switch",
                    "service": "turn_off",
                    "areaId": [],
                    "deviceId": [],
                    "entityId": [tgt_entity],
                    "data": "",
                    "dataType": "jsonata",
                    "mergeContext": "",
                    "mustacheAltTags": False,
                    "outputProperties": [],
                    "queue": "none",
                    "x": 500,
                    "y": 100 + i * 80,
                    "wires": [[]]
                })

                # Wire state-changed node to api-current-state nodes
                state_changed_node = next(node for node in flow if node["id"] == state_changed_node_id)
                state_changed_node["wires"][0].append(api_current_state_id_0)
                state_changed_node["wires"][1].append(api_current_state_id_1)

    flow.append({
        "id": "20b962a5.ede7ee",
        "type": "server",
        "name": "Home Assistant",
        "addon": True
    })

    return json.dumps(flow, indent=4)

def read_mappings(file_path):
    mappings = []
    with open(file_path, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            src_device = row['source_device']
            src_entity = row['source_entity_id']
            tgt_device = row['target_device']
            tgt_entity = row['target_entity_id']
            mappings.append((src_device, src_entity, tgt_device, tgt_entity))
    return mappings

def main():
    mappings_file = os.path.join(os.path.dirname(__file__), '..', 'mappings.csv')
    mappings = read_mappings(mappings_file)
    flow = create_node_red_flow(mappings)
    output_file = os.path.join(os.path.dirname(__file__), '..', 'node_red_flow.json')
    with open(output_file, "w") as file:
        file.write(flow)
    return "Node-RED flow JSON has been generated and saved to node_red_flow.json"

if __name__ == "__main__":
    print(main())