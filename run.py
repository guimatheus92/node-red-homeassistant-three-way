# run.py

from app import create_app

app = create_app('config.ProductionConfig')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)