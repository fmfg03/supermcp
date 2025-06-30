"""
Real-time Documentation System for SuperMCP Migrations
Tracks and documents all changes during migration processes in real-time
"""

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import git
import yaml

@dataclass
class ChangeEvent:
    """Represents a single change event during migration"""
    timestamp: str
    event_type: str  # 'file_created', 'file_modified', 'file_deleted', 'migration_started', 'test_run', 'rollback'
    description: str
    file_path: Optional[str] = None
    old_content: Optional[str] = None
    new_content: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    success: bool = True
    error_message: Optional[str] = None

class RealtimeDocumentationSystem:
    """
    Sistema de documentación en tiempo real para migraciones SuperMCP
    Captura y documenta todos los cambios durante el proceso de migración
    """
    
    def __init__(self, base_path: str = "/root/supermcp"):
        self.base_path = Path(base_path)
        self.docs_path = self.base_path / "supermcp_new" / "docs" / "migrations"
        self.docs_path.mkdir(parents=True, exist_ok=True)
        
        self.current_session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_log_path = self.docs_path / f"session_{self.current_session_id}.json"
        self.markdown_path = self.docs_path / f"session_{self.current_session_id}.md"
        
        self.events: List[ChangeEvent] = []
        self.logger = logging.getLogger(__name__)
        
        # Initialize session
        self._initialize_session()
    
    def _initialize_session(self):
        """Inicializa una nueva sesión de documentación"""
        session_info = {
            "session_id": self.current_session_id,
            "start_time": datetime.now().isoformat(),
            "project_path": str(self.base_path),
            "git_branch": self._get_current_git_branch(),
            "git_commit": self._get_current_git_commit(),
            "events": []
        }
        
        with open(self.session_log_path, 'w') as f:
            json.dump(session_info, f, indent=2)
        
        self.log_event(
            event_type="migration_started",
            description=f"Migration documentation session started",
            metadata={"session_id": self.current_session_id}
        )
    
    def _get_current_git_branch(self) -> str:
        """Obtiene la rama actual de git"""
        try:
            repo = git.Repo(self.base_path)
            return repo.active_branch.name
        except Exception:
            return "unknown"
    
    def _get_current_git_commit(self) -> str:
        """Obtiene el commit actual de git"""
        try:
            repo = git.Repo(self.base_path)
            return repo.head.commit.hexsha[:8]
        except Exception:
            return "unknown"
    
    def log_event(self, 
                  event_type: str, 
                  description: str, 
                  file_path: Optional[str] = None,
                  old_content: Optional[str] = None,
                  new_content: Optional[str] = None,
                  metadata: Optional[Dict[str, Any]] = None,
                  success: bool = True,
                  error_message: Optional[str] = None):
        """Registra un evento de cambio en tiempo real"""
        
        event = ChangeEvent(
            timestamp=datetime.now().isoformat(),
            event_type=event_type,
            description=description,
            file_path=file_path,
            old_content=old_content,
            new_content=new_content,
            metadata=metadata or {},
            success=success,
            error_message=error_message
        )
        
        self.events.append(event)
        self._save_event_to_file(event)
        self._update_markdown_documentation()
        
        # Log to console
        status = "✅" if success else "❌"
        self.logger.info(f"{status} {event_type}: {description}")
        
        if file_path:
            self.logger.info(f"   📁 File: {file_path}")
        
        if error_message:
            self.logger.error(f"   ⚠️  Error: {error_message}")
    
    def _save_event_to_file(self, event: ChangeEvent):
        """Guarda el evento en el archivo JSON de la sesión"""
        try:
            with open(self.session_log_path, 'r') as f:
                session_data = json.load(f)
            
            session_data["events"].append(asdict(event))
            session_data["last_updated"] = datetime.now().isoformat()
            
            with open(self.session_log_path, 'w') as f:
                json.dump(session_data, f, indent=2)
        
        except Exception as e:
            self.logger.error(f"Error saving event to file: {e}")
    
    def _update_markdown_documentation(self):
        """Actualiza la documentación en formato Markdown"""
        try:
            content = self._generate_markdown_content()
            with open(self.markdown_path, 'w') as f:
                f.write(content)
        except Exception as e:
            self.logger.error(f"Error updating markdown documentation: {e}")
    
    def _generate_markdown_content(self) -> str:
        """Genera el contenido en formato Markdown"""
        content = [
            f"# SuperMCP Migration Session - {self.current_session_id}",
            "",
            f"**Started:** {self.events[0].timestamp if self.events else 'Unknown'}",
            f"**Git Branch:** {self._get_current_git_branch()}",
            f"**Git Commit:** {self._get_current_git_commit()}",
            f"**Total Events:** {len(self.events)}",
            "",
            "## Migration Events",
            ""
        ]
        
        # Group events by type for better organization
        events_by_type = {}
        for event in self.events:
            if event.event_type not in events_by_type:
                events_by_type[event.event_type] = []
            events_by_type[event.event_type].append(event)
        
        for event_type, events_list in events_by_type.items():
            content.append(f"### {event_type.replace('_', ' ').title()}")
            content.append("")
            
            for event in events_list:
                status_icon = "✅" if event.success else "❌"
                content.append(f"- {status_icon} **{event.timestamp}** - {event.description}")
                
                if event.file_path:
                    content.append(f"  - 📁 File: `{event.file_path}`")
                
                if event.error_message:
                    content.append(f"  - ⚠️ Error: {event.error_message}")
                
                if event.metadata:
                    for key, value in event.metadata.items():
                        content.append(f"  - {key}: {value}")
                
                content.append("")
        
        # Add summary statistics
        content.extend([
            "## Summary Statistics",
            "",
            f"- **Total Events:** {len(self.events)}",
            f"- **Successful Operations:** {sum(1 for e in self.events if e.success)}",
            f"- **Failed Operations:** {sum(1 for e in self.events if not e.success)}",
            f"- **Files Modified:** {len(set(e.file_path for e in self.events if e.file_path))}",
            ""
        ])
        
        return "\n".join(content)
    
    def log_file_creation(self, file_path: str, content: str, metadata: Optional[Dict] = None):
        """Registra la creación de un archivo"""
        self.log_event(
            event_type="file_created",
            description=f"Created file: {Path(file_path).name}",
            file_path=file_path,
            new_content=content[:500] + "..." if len(content) > 500 else content,
            metadata=metadata
        )
    
    def log_file_modification(self, file_path: str, old_content: str, new_content: str, metadata: Optional[Dict] = None):
        """Registra la modificación de un archivo"""
        self.log_event(
            event_type="file_modified",
            description=f"Modified file: {Path(file_path).name}",
            file_path=file_path,
            old_content=old_content[:500] + "..." if len(old_content) > 500 else old_content,
            new_content=new_content[:500] + "..." if len(new_content) > 500 else new_content,
            metadata=metadata
        )
    
    def log_file_deletion(self, file_path: str, metadata: Optional[Dict] = None):
        """Registra la eliminación de un archivo"""
        self.log_event(
            event_type="file_deleted",
            description=f"Deleted file: {Path(file_path).name}",
            file_path=file_path,
            metadata=metadata
        )
    
    def log_test_execution(self, test_name: str, success: bool, results: Dict, metadata: Optional[Dict] = None):
        """Registra la ejecución de pruebas"""
        self.log_event(
            event_type="test_run",
            description=f"Executed test: {test_name}",
            success=success,
            metadata={**(metadata or {}), "test_results": results}
        )
    
    def log_rollback_operation(self, rollback_type: str, target_version: str, success: bool, error_message: Optional[str] = None):
        """Registra operaciones de rollback"""
        self.log_event(
            event_type="rollback",
            description=f"Rollback to {target_version} using {rollback_type}",
            success=success,
            error_message=error_message,
            metadata={"rollback_type": rollback_type, "target_version": target_version}
        )
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Obtiene un resumen de la sesión actual"""
        successful_ops = sum(1 for e in self.events if e.success)
        failed_ops = sum(1 for e in self.events if not e.success)
        modified_files = set(e.file_path for e in self.events if e.file_path)
        
        return {
            "session_id": self.current_session_id,
            "total_events": len(self.events),
            "successful_operations": successful_ops,
            "failed_operations": failed_ops,
            "success_rate": (successful_ops / len(self.events)) * 100 if self.events else 0,
            "modified_files_count": len(modified_files),
            "modified_files": list(modified_files),
            "start_time": self.events[0].timestamp if self.events else None,
            "last_update": self.events[-1].timestamp if self.events else None
        }
    
    def finalize_session(self):
        """Finaliza la sesión de documentación"""
        self.log_event(
            event_type="migration_completed",
            description="Migration documentation session completed",
            metadata=self.get_session_summary()
        )
        
        # Generate final report
        summary = self.get_session_summary()
        self.logger.info(f"📋 Migration Session Summary:")
        self.logger.info(f"   Total Events: {summary['total_events']}")
        self.logger.info(f"   Success Rate: {summary['success_rate']:.1f}%")
        self.logger.info(f"   Modified Files: {summary['modified_files_count']}")
        self.logger.info(f"   Documentation: {self.markdown_path}")

# Global instance for easy access
documentation_system = RealtimeDocumentationSystem()

def log_change(event_type: str, description: str, **kwargs):
    """Función helper para registrar cambios fácilmente"""
    documentation_system.log_event(event_type, description, **kwargs)

def log_file_change(operation: str, file_path: str, **kwargs):
    """Función helper para registrar cambios de archivos"""
    if operation == "create":
        documentation_system.log_file_creation(file_path, **kwargs)
    elif operation == "modify":
        documentation_system.log_file_modification(file_path, **kwargs)
    elif operation == "delete":
        documentation_system.log_file_deletion(file_path, **kwargs)