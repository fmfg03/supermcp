"""
Studio Config Module
Stub implementation for missing module
"""

class StudioConfig:
    def __init__(self):
        self.config = {
            "hot_reload": True,
            "debug_mode": True
        }
    
    def get(self, key, default=None):
        return self.config.get(key, default)
    
    def update(self, updates):
        self.config.update(updates)

def get_studio_config():
    return StudioConfig()