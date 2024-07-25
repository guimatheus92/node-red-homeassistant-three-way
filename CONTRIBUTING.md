# Contributing Guidelines

All types of contributions are encouraged and valued. Please make sure to read
relevant sections in this file and in README before making your contribution. It
will make it a lot easier for us maintainers and smooth out the experience for
all involved. This project looks forward to your contributions :tada:

## How to contribute

#### Development


1. **Clone the Repository**:

    ```bash
    git clone https://github.com/guimatheus92/node-red-homeassistant-three-way.git
    cd node-red-homeassistant-three-way
    ```

2. Run the command below to install dependecies libraries:

    ```python
    pip install -r requirements.txt
    ```

3. Update the `config.yaml` file with your Home Assistant URL and access token:

    ```yaml
    home_assistant:
      home_assistant_url: 'http://your-home-assistant-url:8123'
      access_token: 'your-access-token'
    ```

4. Run app using the command below:

    ```sh
    flask run
    ```

## Submitting  Pull Request

* Ensure any install or build dependencies are working and the code is
  generating the right output before submitting a PR
* Update the README.md with details of changes to the interface, this includes
  new fields, features, etc.
* Promptly address any CI failures. If your pull request fails to build or pass
  tests, please push another commit to fix it
* Resolve any merge conflicts that occur
