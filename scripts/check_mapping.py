import csv
from collections import defaultdict
import os

def read_mappings(file_path):
    mappings = []
    with open(file_path, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            src_device = row['source_device']
            src_entity = row['source_entityid']
            tgt_device = row['target_device']
            tgt_entity = row['target_entityid']
            mappings.append((src_device, src_entity, tgt_device, tgt_entity))
    return mappings

def analyze_mappings(mappings):
    source_to_targets = defaultdict(set)
    target_to_sources = defaultdict(set)

    for src_device, src_entity, tgt_device, tgt_entity in mappings:
        source_to_targets[src_entity].add(tgt_entity)
        target_to_sources[tgt_entity].add(src_entity)

    all_entities = set(source_to_targets.keys()).union(set(target_to_sources.keys()))

    missing_sources = []
    missing_targets = []

    for entity in all_entities:
        if entity not in source_to_targets:
            missing_sources.append(entity)
        if entity not in target_to_sources:
            missing_targets.append(entity)

    return missing_sources, missing_targets

def main():
    mappings_file = os.path.join(os.path.dirname(__file__), '..', 'mappings.csv')
    mappings = read_mappings(mappings_file)
    
    missing_sources, missing_targets = analyze_mappings(mappings)

    result = ""
    if missing_sources:
        result += "Entities that do not turn on another switch (missing sources):\n"
        result += "\n".join(missing_sources)
    else:
        result += "All entities turn on another switch.\n"

    if missing_targets:
        result += "Entities that are not turned off by another switch (missing targets):\n"
        result += "\n".join(missing_targets)
    else:
        result += "All entities are turned off by another switch.\n"
    
    return result

if __name__ == "__main__":
    print(main())
