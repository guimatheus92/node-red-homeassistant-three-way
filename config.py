# config.py

import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    # Add other general configuration settings here

class DevelopmentConfig(Config):
    DEBUG = True
    # Add other development-specific settings here

class TestingConfig(Config):
    TESTING = True
    # Add other testing-specific settings here

class ProductionConfig(Config):
    DEBUG = False
    # Add other production-specific settings here
