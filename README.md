# Node-RED Home Assistant Three-Way Switch Manager

This project is a web application designed to help users manage their Home Assistant devices and mappings, focusing on creating virtual three-way switch setups and virtual parallel switch setups through Node-RED. The application allows users to independently manage their own device configurations and mappings.

## Features

- **Device Management**:
  - Fetch Home Assistant devices and entities.
  - Display devices in a table format.
  
- **Mapping Management**:
  - Create mappings between source and target devices/entities.
  - Display mappings in a table format.
  - Enable three-way switch setup with a checkbox.
  - Highlight duplicate mappings.
  - Prevent mappings with identical source and target entities.
  
- **Configuration Management**:
  - Update Home Assistant configuration settings (URL and access token) via a settings page.
  - Test Home Assistant connection to verify URL and access token.

## Requirements

- Python 3.8 or higher
- Home Assistant with relevant devices configured
- Node-RED installed in Home Assistant
- (optional) Node-RED node: [@bartbutenaers/node-red-autolayout-sidebar](https://flows.nodered.org/node/@bartbutenaers/node-red-autolayout-sidebar "@bartbutenaers/node-red-autolayout-sidebar")

### Directory Structure

```plaintext
node-red-homeassistant-three-way/
  ├── .dockerignore
  ├── .gitignore
  ├── config.py
  ├── config.yaml
  ├── CONTRIBUTING.md
  ├── devices.csv
  ├── Dockerfile
  ├── mappings.csv
  ├── README.md
  ├── requirements.txt
  ├── run.py
  ├── tests
  │   └── unit_tests
  │       └── test_functions.py
  ├── scripts
  │   ├── check_mapping.py
  │   ├── get_ha_devices_entities.py
  │   └── main.py
  └── app
      ├── routes.py
      ├── __init__.py
      ├── templates
      │   ├── devices.html
      │   ├── index.html
      │   ├── mappings.html
      │   └── settings.html
      └── static
          ├── favicon.ico
          ├── scripts.js
          └── styles.css
```

## How to run

1. **Clone the Repository**:

    ```bash
    git clone https://github.com/guimatheus92/node-red-homeassistant-three-way.git
    cd node-red-homeassistant-three-way
    ```

2. **Build the Docker Image**:

    Build the Docker image using the following command:

    ```bash
    docker-compose up --build
    ```

3. **Access the Flask Application**:

    Open your web browser and navigate to `http://localhost:5000` to access the application.

## How to use

### Accessing the Application

1. Navigate to the application's URL in your web browser (e.g., `http://127.0.0.1:5000` for local development).

### Configuration Management

1. Go to the "Settings" tab.
2. Update the Home Assistant URL and access token.

![alt text](media/settings.png)

3. Test the connection to ensure the URL and token are correct by clicking the "Test Connection" button. A message will be displayed indicating whether the connection was successful.

![alt text](media/test-connection.png)

4. Check if the template JINJA code works properly in your Home Assistant Template window. Because this code can vary from one user to another.
> In this case, this code is retrieving all devices from Tuya and MQTT sources and ignoring some entities. So, this code works on my end because I have renamed my devices and entity in a certain way.

Then first, go to your Home Assistant -> Developer Tools -> Template:
Copy and paste the code and do the changes on your end, before running in the application:

![alt text](media/template-code.png)

5. Save the settings.

### Device Management

1. Go to the "Devices" tab.
2. Click "Fetch Devices" to retrieve the latest devices from your Home Assistant (after a success message appear, refresh the page manually).
3. The devices will be listed in the table. You can also download the `devices.csv` file.

![alt text](media/devices.png)

### Mapping Management

1. Go to the "Mappings" tab.
2. Add a new mapping by selecting source and target devices and entities.

![alt text](media/source-target.png)

3. Enable the "Three Way" option if needed by checking the checkbox. You will notice that a new row will be added with entities in reverse (will turn on and turn off in both ways).

![alt text](media/three-way.png)

4. Save the mappings.
5. The mappings will be listed in the table. You can also download the `mappings.csv` file.

### Node-RED Flow

1. After everything is done, click on `Generate NodeRED JSON` button to generate a Node-RED Flow JSON. The file will be generated and downloaded automatically.

![alt text](media/nodered-flow.png)

2. Go to Node-RED, click on [Import](https://nodered.org/docs/user-guide/editor/workspace/import-export) and paste the generated JSON
3. After you manage to paste and create a new flow, you will see something like this:

![alt text](media/nodered-imported.png)

4. I would suggest to do the following:
- 4.1. CTRL + A (Select all)
- 4.2. Install Auto Layout is suggested above in this doc
- 4.3. Click on `Execute auto-layout` button

You will see the magic happening and will look something like this:

![alt text](media/nodered-autolayout.png)

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request.

## Acknowledgements

- Home Assistant: https://www.home-assistant.io/
- Node-RED: https://nodered.org/