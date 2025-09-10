# config_loader.py
import yaml
from pathlib import Path
from typing import Dict, Any
from models import Config


class ConfigLoader:
    @staticmethod
    def load_config(config_path: str = "config.yaml") -> Config:
        """Load configuration from YAML file"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)

            return Config(
                csv_file_path=data['csv']['file_path'],
                csv_encoding=data['csv']['encoding'],
                delimiter=data['csv'].get('delimiter', ','),
                columns=data['csv']['columns'],
                output_kotlin_file=data['output']['kotlin_file'],
                condition_mapping=data['mappings']['conditions'],
                package_size_mapping=data['mappings']['package_sizes']
            )
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML configuration: {e}")
        except KeyError as e:
            raise ValueError(f"Missing required configuration key: {e}")