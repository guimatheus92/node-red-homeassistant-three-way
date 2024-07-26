# app/routes.py

from flask import current_app as app, render_template, request, redirect, url_for, flash, jsonify, send_from_directory
import subprocess
import csv
import os
import traceback
import yaml

@app.route('/')
def index():
    return redirect(url_for('devices'))

@app.route('/devices')
def devices():
    return render_template('devices.html')

@app.route('/mappings')
def mappings():
    return render_template('mappings.html')

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    config_file_path = '/app/config.yaml'
    
    if request.method == 'POST':
        with open(config_file_path, 'r', encoding='utf8') as file:
            config = yaml.safe_load(file)
        
        # Update only the specific keys in the configuration
        config['home_assistant']['home_assistant_url'] = request.form['home_assistant_url']
        config['home_assistant']['access_token'] = request.form['access_token']
        
        with open(config_file_path, 'w', encoding='utf8') as file:
            yaml.safe_dump(config, file)
        
        flash('Settings updated successfully', 'success')
        return redirect(url_for('settings'))

    with open(config_file_path, 'r', encoding='utf8') as file:
        config = yaml.safe_load(file)

    return render_template('settings.html', config=config)

@app.route('/fetch_devices', methods=['POST'])
def fetch_devices():
    try:
        app.logger.info("Starting device fetch process")
        result = subprocess.run(['python', 'scripts/get_ha_devices_entities.py'], capture_output=True, text=True)
        app.logger.info(f"Device fetch script output: {result.stdout}")
        if "successfully" in result.stdout or "successfully" in result.stderr:
            return jsonify({"message": "Devices fetched successfully. Please refresh the page manually to see the updated data."}), 200
        else:
            app.logger.error(f"Error fetching devices: {result.stdout}")
            return jsonify({"message": result.stdout}), 500
    except Exception as e:
        app.logger.error(f"Error fetching devices: {e}")
        app.logger.error(traceback.format_exc())
        return jsonify({"message": "An error occurred while fetching devices"}), 500

@app.route('/save_devices', methods=['POST'])
def save_devices():
    devices_data = request.json.get('devices')
    devices_file_path = os.path.join(os.path.dirname(__file__), '..', 'devices.csv')
    try:
        with open(devices_file_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['device', 'entity_id'])
            for device in devices_data:
                writer.writerow([device['device'], device['entity_id']])
        return jsonify({"message": "Devices saved successfully"}), 200
    except Exception as e:
        app.logger.error(f"Error saving devices: {e}")
        app.logger.error(traceback.format_exc())
        return jsonify({"message": "An error occurred while saving devices"}), 500

@app.route('/devices.csv')
def get_devices_csv():
    try:
        devices_file_path = os.path.join(os.path.dirname(__file__), '..', 'devices.csv')
        return send_from_directory(os.path.dirname(devices_file_path), os.path.basename(devices_file_path))
    except FileNotFoundError as e:
        app.logger.error(f"Error serving devices.csv: {e}")
        app.logger.error(traceback.format_exc())
        return jsonify({"message": "devices.csv file not found"}), 500
    except Exception as e:
        app.logger.error(f"Error serving devices.csv: {e}")
        app.logger.error(traceback.format_exc())
        return jsonify({"message": "An error occurred while serving devices.csv"}), 500

@app.route('/mappings.csv')
def get_mappings_csv():
    try:
        mappings_file_path = os.path.join(os.path.dirname(__file__), '..', 'mappings.csv')
        return send_from_directory(os.path.dirname(mappings_file_path), os.path.basename(mappings_file_path))
    except FileNotFoundError as e:
        app.logger.error(f"Error serving mappings.csv: {e}")
        app.logger.error(traceback.format_exc())
        return jsonify({"message": "mappings.csv file not found"}), 500
    except Exception as e:
        app.logger.error(f"Error serving mappings.csv: {e}")
        app.logger.error(traceback.format_exc())
        return jsonify({"message": "An error occurred while serving mappings.csv"}), 500

@app.route('/save_mappings', methods=['POST'])
def save_mappings():
    mappings_data = request.json.get('mappings')
    mappings_file_path = os.path.join(os.path.dirname(__file__), '..', 'mappings.csv')
    try:
        with open(mappings_file_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['source_device', 'source_entity_id', 'target_device', 'target_entity_id'])
            for mapping in mappings_data:
                writer.writerow([
                    mapping['source_device'],
                    mapping['source_entity_id'],
                    mapping['target_device'],
                    mapping['target_entity_id']
                ])
        return jsonify({"message": "Mappings saved successfully"}), 200
    except Exception as e:
        app.logger.error(f"Error saving mappings: {e}")
        app.logger.error(traceback.format_exc())
        return jsonify({"message": "An error occurred while saving mappings"}), 500

@app.route('/entities/<device>')
def get_entities(device):
    devices_file_path = os.path.join(os.path.dirname(__file__), '..', 'devices.csv')
    entities = []
    try:
        with open(devices_file_path, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row['device'] == device:
                    entities.append(row['entity_id'])
    except FileNotFoundError as e:
        app.logger.error(f"Error reading devices.csv: {e}")
        app.logger.error(traceback.format_exc())
        return jsonify({"message": "devices.csv file not found"}), 500
    except Exception as e:
        app.logger.error(f"Error reading devices.csv: {e}")
        app.logger.error(traceback.format_exc())
        return jsonify({"message": "An error occurred while reading devices.csv"}), 500
    
    return jsonify({"entities": entities})

@app.route('/devices_list')
def get_devices_list():
    devices_file_path = os.path.join(os.path.dirname(__file__), '..', 'devices.csv')
    devices = set()
    try:
        with open(devices_file_path, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                devices.add(row['device'])
    except FileNotFoundError as e:
        app.logger.error(f"Error reading devices.csv: {e}")
        app.logger.error(traceback.format_exc())
        return jsonify({"message": "devices.csv file not found"}), 500
    except Exception as e:
        app.logger.error(f"Error reading devices.csv: {e}")
        app.logger.error(traceback.format_exc())
        return jsonify({"message": "An error occurred while reading devices.csv"}), 500
    
    return jsonify({"devices": list(devices)})

@app.route('/get_mappings')
def get_mappings():
    mappings_file_path = os.path.join(os.path.dirname(__file__), '..', 'mappings.csv')
    mappings = []
    try:
        with open(mappings_file_path, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                mappings.append(row)
    except FileNotFoundError:
        app.logger.error(f"Error reading mappings.csv: File not found at {mappings_file_path}")
        return jsonify({"mappings": mappings}), 500
    except Exception as e:
        app.logger.error(f"Error reading mappings.csv: {e}")
        app.logger.error(traceback.format_exc())
        return jsonify({"mappings": mappings}), 500
    
    return jsonify({"mappings": mappings})

@app.route('/run_main', methods=['POST'])
def run_main():
    try:
        result = subprocess.run(['python', 'scripts/main.py'], capture_output=True, text=True)
        if result.returncode == 0:
            return jsonify({"message": "Main function executed successfully."}), 200
        else:
            return jsonify({"message": f"Main function failed: {result.stderr}"}), 500
    except Exception as e:
        app.logger.error(f"Error running main function: {e}")
        app.logger.error(traceback.format_exc())
        return jsonify({"message": "An error occurred while running the main function."}), 500

@app.route('/clear_mappings', methods=['POST'])
def clear_mappings():
    mappings_file_path = os.path.join(os.path.dirname(__file__), '..', 'mappings.csv')
    try:
        with open(mappings_file_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['source_device', 'source_entity_id', 'target_device', 'target_entity_id'])
        return jsonify({"success": True, "message": "All mappings cleared successfully"}), 200
    except Exception as e:
        app.logger.error(f"Error clearing mappings: {e}")
        app.logger.error(traceback.format_exc())
        return jsonify({"success": False, "message": "An error occurred while clearing mappings"}), 500

@app.route('/clear_devices', methods=['POST'])
def clear_devices():
    devices_file_path = os.path.join(os.path.dirname(__file__), '..', 'devices.csv')
    try:
        with open(devices_file_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['device', 'entity_id'])
        return jsonify({"success": True, "message": "All devices cleared successfully"}), 200
    except Exception as e:
        app.logger.error(f"Error clearing devices: {e}")
        app.logger.error(traceback.format_exc())
        return jsonify({"success": False, "message": "An error occurred while clearing devices"}), 500    