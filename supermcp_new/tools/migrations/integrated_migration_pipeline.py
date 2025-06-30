"""
Integrated Migration Pipeline for SuperMCP
Combines migration system, continuous testing, and real-time documentation
"""

import asyncio
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
import sys
import os

# Add the parent directory to sys.path to import our modules
sys.path.append(str(Path(__file__).parent.parent.parent))

from tools.migrations.migration_system import SuperMCPMigrationManager
from tools.migrations.continuous_testing import ContinuousTestingFramework
from tools.migrations.realtime_documentation import RealtimeDocumentationSystem

class IntegratedMigrationPipeline:
    """
    Pipeline integrado que combina:
    - Sistema de migración segura con rollback
    - Testing continuo post-migración
    - Documentación en tiempo real de cambios
    """
    
    def __init__(self, base_path: str = "/root/supermcp"):
        self.base_path = Path(base_path)
        
        # Initialize subsystems
        self.migration_manager = SuperMCPMigrationManager(str(base_path))
        self.testing_framework = ContinuousTestingFramework(str(base_path))
        self.documentation_system = RealtimeDocumentationSystem(str(base_path))
        
        self.logger = logging.getLogger(__name__)
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    async def execute_safe_migration(self, 
                                   migration_name: str,
                                   migration_steps: List[Dict[str, Any]],
                                   test_after_each_step: bool = True,
                                   rollback_on_failure: bool = True) -> Dict[str, Any]:
        """
        Ejecuta una migración segura con testing y documentación integrados
        """
        
        self.documentation_system.log_event(
            event_type="migration_started",
            description=f"Starting integrated migration: {migration_name}",
            metadata={"steps_count": len(migration_steps)}
        )
        
        migration_result = {
            "migration_name": migration_name,
            "success": False,
            "completed_steps": 0,
            "total_steps": len(migration_steps),
            "backup_version": None,
            "test_results": [],
            "rollback_performed": False,
            "documentation_session": self.documentation_system.current_session_id
        }
        
        try:
            # Create incremental backup before starting
            backup_version = self.migration_manager.create_incremental_backup(
                f"pre_{migration_name}"
            )
            migration_result["backup_version"] = backup_version
            
            self.documentation_system.log_event(
                event_type="backup_created",
                description=f"Created backup version: {backup_version}",
                metadata={"migration_name": migration_name}
            )
            
            # Execute migration steps
            for i, step in enumerate(migration_steps, 1):
                step_name = step.get("name", f"Step {i}")
                
                self.documentation_system.log_event(
                    event_type="migration_step_started",
                    description=f"Starting {step_name}",
                    metadata={"step_number": i, "step_details": step}
                )
                
                try:
                    # Execute the migration step
                    await self._execute_migration_step(step)
                    
                    migration_result["completed_steps"] = i
                    
                    self.documentation_system.log_event(
                        event_type="migration_step_completed",
                        description=f"Completed {step_name}",
                        metadata={"step_number": i}
                    )
                    
                    # Run tests after each step if requested
                    if test_after_each_step:
                        test_results = await self.testing_framework.run_post_migration_tests()
                        migration_result["test_results"].append({
                            "step": i,
                            "step_name": step_name,
                            "results": test_results
                        })
                        
                        self.documentation_system.log_test_execution(
                            test_name=f"Post-step-{i} validation",
                            success=test_results["overall_success"],
                            results=test_results
                        )
                        
                        # Check if tests failed and rollback is enabled
                        if not test_results["overall_success"] and rollback_on_failure:
                            self.logger.error(f"Tests failed after step {i}, initiating rollback")
                            
                            rollback_success = self.migration_manager.rollback_migration(backup_version)
                            migration_result["rollback_performed"] = True
                            
                            self.documentation_system.log_rollback_operation(
                                rollback_type="incremental_backup",
                                target_version=backup_version,
                                success=rollback_success,
                                error_message=None if rollback_success else "Rollback failed"
                            )
                            
                            if rollback_success:
                                self.logger.info("Rollback completed successfully")
                                migration_result["success"] = False
                                return migration_result
                            else:
                                self.logger.error("Rollback failed - manual intervention required")
                                raise Exception("Migration failed and rollback also failed")
                
                except Exception as step_error:
                    self.logger.error(f"Error in migration step {i}: {step_error}")
                    
                    self.documentation_system.log_event(
                        event_type="migration_step_failed",
                        description=f"Failed {step_name}",
                        success=False,
                        error_message=str(step_error),
                        metadata={"step_number": i}
                    )
                    
                    if rollback_on_failure:
                        rollback_success = self.migration_manager.rollback_migration(backup_version)
                        migration_result["rollback_performed"] = True
                        
                        self.documentation_system.log_rollback_operation(
                            rollback_type="incremental_backup",
                            target_version=backup_version,
                            success=rollback_success,
                            error_message=str(step_error)
                        )
                    
                    raise step_error
            
            # Run final comprehensive tests
            final_test_results = await self.testing_framework.run_post_migration_tests()
            migration_result["test_results"].append({
                "step": "final",
                "step_name": "Final validation",
                "results": final_test_results
            })
            
            self.documentation_system.log_test_execution(
                test_name="Final migration validation",
                success=final_test_results["overall_success"],
                results=final_test_results
            )
            
            if final_test_results["overall_success"]:
                migration_result["success"] = True
                self.documentation_system.log_event(
                    event_type="migration_completed",
                    description=f"Migration {migration_name} completed successfully",
                    metadata={"final_test_results": final_test_results}
                )
            else:
                if rollback_on_failure:
                    rollback_success = self.migration_manager.rollback_migration(backup_version)
                    migration_result["rollback_performed"] = True
                    
                    self.documentation_system.log_rollback_operation(
                        rollback_type="incremental_backup",
                        target_version=backup_version,
                        success=rollback_success,
                        error_message="Final validation failed"
                    )
                
                raise Exception("Final validation tests failed")
        
        except Exception as e:
            self.logger.error(f"Migration {migration_name} failed: {e}")
            
            self.documentation_system.log_event(
                event_type="migration_failed",
                description=f"Migration {migration_name} failed",
                success=False,
                error_message=str(e)
            )
            
            migration_result["success"] = False
            migration_result["error"] = str(e)
        
        finally:
            # Finalize documentation
            self.documentation_system.finalize_session()
        
        return migration_result
    
    async def _execute_migration_step(self, step: Dict[str, Any]):
        """Ejecuta un paso individual de migración"""
        step_type = step.get("type", "unknown")
        
        if step_type == "file_operation":
            await self._execute_file_operation(step)
        elif step_type == "directory_operation":
            await self._execute_directory_operation(step)
        elif step_type == "command_execution":
            await self._execute_command(step)
        elif step_type == "custom_function":
            await self._execute_custom_function(step)
        else:
            raise ValueError(f"Unknown migration step type: {step_type}")
    
    async def _execute_file_operation(self, step: Dict[str, Any]):
        """Ejecuta operaciones de archivo"""
        operation = step.get("operation")  # create, modify, delete, move
        file_path = step.get("file_path")
        
        if operation == "create":
            content = step.get("content", "")
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w') as f:
                f.write(content)
            
            self.documentation_system.log_file_creation(
                file_path=file_path,
                content=content,
                metadata={"operation": "create"}
            )
        
        elif operation == "modify":
            # Read old content first
            old_content = ""
            if Path(file_path).exists():
                with open(file_path, 'r') as f:
                    old_content = f.read()
            
            new_content = step.get("content", "")
            with open(file_path, 'w') as f:
                f.write(new_content)
            
            self.documentation_system.log_file_modification(
                file_path=file_path,
                old_content=old_content,
                new_content=new_content,
                metadata={"operation": "modify"}
            )
        
        elif operation == "delete":
            if Path(file_path).exists():
                Path(file_path).unlink()
                self.documentation_system.log_file_deletion(
                    file_path=file_path,
                    metadata={"operation": "delete"}
                )
    
    async def _execute_directory_operation(self, step: Dict[str, Any]):
        """Ejecuta operaciones de directorio"""
        operation = step.get("operation")  # create, delete, move
        dir_path = step.get("dir_path")
        
        if operation == "create":
            Path(dir_path).mkdir(parents=True, exist_ok=True)
            self.documentation_system.log_event(
                event_type="directory_created",
                description=f"Created directory: {dir_path}",
                file_path=dir_path
            )
        
        elif operation == "delete":
            if Path(dir_path).exists():
                import shutil
                shutil.rmtree(dir_path)
                self.documentation_system.log_event(
                    event_type="directory_deleted",
                    description=f"Deleted directory: {dir_path}",
                    file_path=dir_path
                )
    
    async def _execute_command(self, step: Dict[str, Any]):
        """Ejecuta comandos del sistema"""
        command = step.get("command")
        
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        success = process.returncode == 0
        
        self.documentation_system.log_event(
            event_type="command_executed",
            description=f"Executed command: {command}",
            success=success,
            error_message=stderr.decode() if stderr else None,
            metadata={
                "command": command,
                "stdout": stdout.decode(),
                "returncode": process.returncode
            }
        )
        
        if not success:
            raise Exception(f"Command failed: {command}, Error: {stderr.decode()}")
    
    async def _execute_custom_function(self, step: Dict[str, Any]):
        """Ejecuta funciones personalizadas"""
        function_name = step.get("function")
        function_args = step.get("args", {})
        
        # This would need to be implemented based on specific custom functions
        self.documentation_system.log_event(
            event_type="custom_function_executed",
            description=f"Executed custom function: {function_name}",
            metadata={"function": function_name, "args": function_args}
        )
    
    def get_migration_status(self) -> Dict[str, Any]:
        """Obtiene el estado actual de la migración"""
        return {
            "documentation_session": self.documentation_system.current_session_id,
            "session_summary": self.documentation_system.get_session_summary(),
            "available_backups": self.migration_manager.list_available_backups(),
            "testing_framework_ready": True
        }

# Example usage function
async def example_supermcp_reorganization():
    """Ejemplo de cómo usar el pipeline integrado para reorganizar SuperMCP"""
    
    pipeline = IntegratedMigrationPipeline()
    
    # Define migration steps for SuperMCP reorganization
    migration_steps = [
        {
            "name": "Create new directory structure",
            "type": "directory_operation",
            "operation": "create",
            "dir_path": "/root/supermcp/supermcp_new/agents/swarm"
        },
        {
            "name": "Move swarm intelligence system",
            "type": "file_operation",
            "operation": "create",
            "file_path": "/root/supermcp/supermcp_new/agents/swarm/intelligence_system.py",
            "content": "# Moved swarm intelligence system\n# Content would be the actual file content"
        },
        {
            "name": "Update configuration",
            "type": "file_operation",
            "operation": "create",
            "file_path": "/root/supermcp/supermcp_new/config/swarm_config.yaml",
            "content": "# Swarm configuration\nswarm:\n  enabled: true\n  port: 8400"
        }
    ]
    
    # Execute the migration
    result = await pipeline.execute_safe_migration(
        migration_name="supermcp_reorganization",
        migration_steps=migration_steps,
        test_after_each_step=True,
        rollback_on_failure=True
    )
    
    print(f"Migration completed: {result['success']}")
    print(f"Documentation session: {result['documentation_session']}")
    
    return result

if __name__ == "__main__":
    # Run example
    asyncio.run(example_supermcp_reorganization())