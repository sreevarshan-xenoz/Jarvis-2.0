#!/usr/bin/env python3
"""
Jarvis Voice Assistant - Dataset Manager Module

This module provides functionality for managing custom datasets,
allowing users to add, validate, and utilize custom training data.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Union
from datetime import datetime

class DatasetManager:
    """
    Manages custom datasets for training and enhancing Jarvis capabilities.
    Supports various data types and provides validation and preprocessing.
    """
    
    def __init__(self):
        """
        Initialize the dataset manager.
        """
        self.datasets_dir = Path(os.path.dirname(os.path.dirname(__file__))) / "data" / "datasets"
        self.datasets_dir.mkdir(parents=True, exist_ok=True)
        
        # Track loaded datasets
        self.loaded_datasets: Dict[str, Dict] = {}
        
        # Dataset schemas for validation
        self.schemas = {
            "command_responses": {
                "required": ["command", "response"],
                "optional": ["context", "tags"]
            },
            "gesture_patterns": {
                "required": ["gesture_name", "landmarks"],
                "optional": ["description", "confidence_threshold"]
            },
            "voice_patterns": {
                "required": ["phrase", "phonemes"],
                "optional": ["language", "accent"]
            }
        }
    
    def add_dataset(self, name: str, data: List[Dict], dataset_type: str) -> bool:
        """
        Add a new dataset or update an existing one.
        
        Args:
            name: Name of the dataset
            data: List of data entries
            dataset_type: Type of dataset (must match a known schema)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Validate dataset type
            if dataset_type not in self.schemas:
                raise ValueError(f"Unknown dataset type: {dataset_type}")
            
            # Validate data against schema
            if not self._validate_dataset(data, dataset_type):
                return False
            
            # Prepare dataset metadata
            dataset = {
                "type": dataset_type,
                "created": datetime.now().isoformat(),
                "updated": datetime.now().isoformat(),
                "entries": data
            }
            
            # Save dataset
            dataset_path = self.datasets_dir / f"{name}.json"
            with open(dataset_path, "w") as f:
                json.dump(dataset, f, indent=2)
            
            # Update loaded datasets
            self.loaded_datasets[name] = dataset
            return True
            
        except Exception as e:
            print(f"Error adding dataset {name}: {e}")
            return False
    
    def get_dataset(self, name: str) -> Optional[Dict]:
        """
        Retrieve a dataset by name.
        
        Args:
            name: Name of the dataset
            
        Returns:
            Optional[Dict]: The dataset if found, None otherwise
        """
        try:
            # Check if already loaded
            if name in self.loaded_datasets:
                return self.loaded_datasets[name]
            
            # Try to load from disk
            dataset_path = self.datasets_dir / f"{name}.json"
            if dataset_path.exists():
                with open(dataset_path, "r") as f:
                    dataset = json.load(f)
                self.loaded_datasets[name] = dataset
                return dataset
            
            return None
            
        except Exception as e:
            print(f"Error loading dataset {name}: {e}")
            return None
    
    def list_datasets(self) -> List[str]:
        """
        List all available datasets.
        
        Returns:
            List[str]: Names of available datasets
        """
        try:
            return [f.stem for f in self.datasets_dir.glob("*.json")]
        except Exception as e:
            print(f"Error listing datasets: {e}")
            return []
    
    def remove_dataset(self, name: str) -> bool:
        """
        Remove a dataset.
        
        Args:
            name: Name of the dataset
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            dataset_path = self.datasets_dir / f"{name}.json"
            if dataset_path.exists():
                dataset_path.unlink()
                if name in self.loaded_datasets:
                    del self.loaded_datasets[name]
                return True
            return False
            
        except Exception as e:
            print(f"Error removing dataset {name}: {e}")
            return False
    
    def _validate_dataset(self, data: List[Dict], dataset_type: str) -> bool:
        """
        Validate dataset entries against schema.
        
        Args:
            data: List of data entries to validate
            dataset_type: Type of dataset to validate against
            
        Returns:
            bool: True if valid, False otherwise
        """
        schema = self.schemas[dataset_type]
        required_fields = schema["required"]
        
        for entry in data:
            # Check required fields
            if not all(field in entry for field in required_fields):
                print(f"Missing required fields in entry: {entry}")
                return False
            
            # Additional type-specific validation could be added here
            
        return True
    
    def get_dataset_schema(self, dataset_type: str) -> Optional[Dict]:
        """
        Get the schema for a dataset type.
        
        Args:
            dataset_type: Type of dataset
            
        Returns:
            Optional[Dict]: Schema if found, None otherwise
        """
        return self.schemas.get(dataset_type)
    
    def merge_datasets(self, name1: str, name2: str, output_name: str) -> bool:
        """
        Merge two datasets of the same type.
        
        Args:
            name1: Name of first dataset
            name2: Name of second dataset
            output_name: Name for merged dataset
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            dataset1 = self.get_dataset(name1)
            dataset2 = self.get_dataset(name2)
            
            if not dataset1 or not dataset2:
                return False
            
            if dataset1["type"] != dataset2["type"]:
                print("Cannot merge datasets of different types")
                return False
            
            # Merge entries
            merged_entries = dataset1["entries"] + dataset2["entries"]
            
            # Create new dataset
            return self.add_dataset(
                output_name,
                merged_entries,
                dataset1["type"]
            )
            
        except Exception as e:
            print(f"Error merging datasets: {e}")
            return False