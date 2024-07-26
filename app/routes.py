# app/routes.py

from flask import current_app as app, render_template, request, redirect, url_for, flash, jsonify, send_from_directory, send_file
import subprocess
import csv
import os
import traceback
import yaml

def load_config():
    config_file_paths = [
        '/app/config.yaml',  # Docker path
        os.path.join(os.path.dirname(__file__), '..', 'config.yaml')  # Local path
    ]

    for path in config_file_paths:
        try:
            with open(path, 'r', encoding='utf8') as file:
                return yaml.safe_load(file), path
        except FileNotFoundError:
            continue
    raise FileNotFoundError('config.yaml file not found in any specified location.')
    
def save_config(config, config_file_path):
    try:
        with open(config_file_path, 'w', encoding='utf8') as file:
            yaml.safe_dump(config, file)
    except Exception as e:
        app.logger.error(f"Error saving settings: {e}")
        raise

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
    try:
        config, config_file_path = load_config()
    except FileNotFoundError as e:
        app.logger.error(f"Error loading settings: {e}")
        config = {'home_assistant': {'home_assistant_url': '', 'access_token': ''}, 'device_fetch_template': ''}
        config_file_path = os.path.join(os.path.dirname(__file__), '..', 'config.yaml')  # Default to local path for saving

    if request.method == 'POST':
        try:
            # Update only the specific keys in the configuration
            config['home_assistant']['home_assistant_url'] = request.form['home_assistant_url']
            config['home_assistant']['access_token'] = request.form['access_token']
            config['home_assistant']['device_fetch_template'] = request.form['device_fetch_template']
            
            save_config(config, config_file_path)
            
            flash('Settings updated successfully', 'success')
        except Exception as e:
            app.logger.error(f"Error updating settings: {e}")
            flash('Failed to update settings', 'danger')
        
        return redirect(url_for('settings'))

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

@app.route('/download_devices', methods=['GET'])
def download_devices():
    devices_file_path = os.path.join(os.path.dirname(__file__), '..', 'devices.csv')
    try:
        if os.path.exists(devices_file_path):
            return send_file(devices_file_path, as_attachment=True)
        else:
            return jsonify({"message": "devices.csv file not found"}), 404
    except Exception as e:
        app.logger.error(f"Error serving devices.csv: {e}")
        app.logger.error(traceback.format_exc())
        return jsonify({"message": "An error occurred while serving devices.csv"}), 500

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

@app.route('/download_file')
def download_file():
    file_path = request.args.get('file_path')
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        return jsonify({"message": "File not found"}), 404

@app.route('/generate_nodered_json', methods=['POST'])
def generate_nodered_json():
    try:
        result = subprocess.run(['python', 'scripts/main.py'], capture_output=True, text=True)
        if result.returncode == 0:
            json_file_path = os.path.join(os.path.dirname(__file__), '..', 'node_red_flow.json')
            if os.path.exists(json_file_path):
                return jsonify({"message": "JSON file generated successfully", "file_path": json_file_path}), 200
            else:
                return jsonify({"message": "JSON file not found"}), 500
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