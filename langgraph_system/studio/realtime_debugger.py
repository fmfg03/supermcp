"""
Realtime Debugger Module
Stub implementation for missing module
"""

class RealtimeDebugger:
    def __init__(self):
        self.is_running = False
        self.session_states = {}
    
    def get_session_summary(self, session_id):
        return {"error": "Session not found"}
    
    def export_session_trace(self, session_id, format="json"):
        return {"error": "No trace available"}

_debugger_instance = RealtimeDebugger()

def get_realtime_debugger():
    return _debugger_instance

def start_debugging():
    _debugger_instance.is_running = True