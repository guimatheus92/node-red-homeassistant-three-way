# scripts/get_ha_devices_entities.py

import requests
import pandas as pd
import os
import yaml
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def read_configurations():
    """
    Function to read the configuration from the .yaml file
    """
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config.yaml')
    if not os.path.exists(config_path):
        logging.error('Error: config.yaml file not found. Make sure config.yaml is placed in the folder.')
        exit()

    with open(config_path, 'r', encoding='utf8') as file:
        return yaml.safe_load(file)

def fetch_devices(home_assistant_url, access_token):
    """
    Function to fetch devices and entities from Home Assistant
    """
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json; charset=utf-8"
    }

    template = '''
    {%- set mqtt_devices = integration_entities('mqtt') | map('device_id') | unique | reject('eq', None) | list -%}
    {%- set tuya_devices = integration_entities('tuya') | map('device_id') | unique | reject('eq', None) | list -%}
    {%- set devices = mqtt_devices + tuya_devices | unique | list -%}
    {%- for device in devices -%}
      {%- set device_name = device_attr(device, 'name') -%}
      {%- if ('interruptor' in device_name) -%}
        {%- if not ('cenas' in device_name) -%}
            {%- set entities = device_entities(device) | list -%}
            {%- for entity in entities -%}
            {%- set entity_name = state_attr(entity, 'friendly_name') or entity -%}
            {%- if not ('Backlight' in entity_name or 'Power-on' in entity_name or 'countdown' in entity_name) -%}
            [{{ device_name }},{{ entity }}]
            {%- endif -%}
            {%- endfor -%}
        {%- endif -%}
      {%- endif -%}
    {%- endfor -%}
    '''

    payload = {"template": template}

    try:
        response = requests.post(f"{home_assistant_url}/api/template", headers=headers, json=payload)
        response.raise_for_status()
    except requests.RequestException as e:
        logging.error(f"Failed to fetch data: {e}")
        return f"Failed to fetch data: {e}"

    result = response.content.decode('utf-8').strip()[1:-1].split('][')
    data = [tuple(item.strip('[]').split(',')) for item in result]

    df = pd.DataFrame(data, columns=["device", "entity_id"]).sort_values(by=["device", "entity_id"])

    output_file = os.path.join(os.path.dirname(__file__), '..', 'devices.csv')
    df.to_csv(output_file, index=False)

    logging.info("devices.csv file has been created successfully.")
    return

def main():
    config = read_configurations()
    home_assistant_url = os.getenv('HOME_ASSISTANT_URL', config['home_assistant']['home_assistant_url'])
    access_token = os.getenv('HOME_ASSISTANT_TOKEN', config['home_assistant']['access_token'])

    result = fetch_devices(home_assistant_url, access_token)
    logging.info(result)

if __name__ == "__main__":
    main()