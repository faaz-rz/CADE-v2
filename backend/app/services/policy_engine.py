import os
import yaml
from typing import Dict, Any

class PolicyEngine:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PolicyEngine, cls).__new__(cls)
            cls._instance.config = cls._instance._load_yaml()
        return cls._instance

    def _load_yaml(self) -> Dict[str, Any]:
        config_path = os.path.join(os.path.dirname(__file__), "..", "config", "policies.yaml")
        if not os.path.exists(config_path):
            print(f"Warning: Policy config not found at {config_path}")
            return {"categories": {}, "default": {
                "spend_threshold": 5000,
                "frequency_threshold": 5,
                "savings_rate": 0.10,
                "regulatory_sensitive": False,
                "operational_critical": False
            }}
            
        try:
            with open(config_path, "r") as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            print(f"Error loading policies.yaml: {e}")
            return {"categories": {}, "default": {}}

    def get_policy(self, category: str) -> Dict[str, Any]:
        categories = self.config.get("categories", {})
        return categories.get(category, self.config.get("default", {}))

policy_engine = PolicyEngine()
