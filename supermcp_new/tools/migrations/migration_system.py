#!/usr/bin/env python3
"""
SuperMCP Migration System
Implements safe, incremental migrations with rollback capabilities
"""

import os
import json
import datetime
import shutil
import subprocess
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

class MigrationStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"

@dataclass
class MigrationStep:
    id: str
    version: str
    description: str
    timestamp: str
    status: MigrationStatus
    checksum: str
    rollback_script: Optional[str] = None
    validation_tests: List[str] = None
    dependencies: List[str] = None

class SuperMCPMigrationManager:
    """Manages safe incremental migrations with rollback capabilities"""
    
    def __init__(self, project_root: str = "/root/supermcp"):
        self.project_root = Path(project_root)
        self.migration_dir = self.project_root / "migrations"
        self.backup_dir = self.project_root / "backups" / "migrations"
        self.log_file = self.migration_dir / "migration.log"
        self.state_file = self.migration_dir / "migration_state.json"
        
        # Ensure directories exist
        self.migration_dir.mkdir(parents=True, exist_ok=True)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        self.current_state = self.load_migration_state()
    
    def load_migration_state(self) -> Dict:
        """Load current migration state"""
        if self.state_file.exists():
            with open(self.state_file, 'r') as f:
                return json.load(f)
        return {
            "current_version": "1.0.0",
            "migrations": [],
            "last_backup": None,
            "rollback_available": True
        }
    
    def save_migration_state(self):
        """Save current migration state"""
        with open(self.state_file, 'w') as f:
            json.dump(self.current_state, f, indent=2)
    
    def create_incremental_backup(self, version: str) -> str:
        """Create incremental backup before migration"""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"backup_v{version}_{timestamp}"
        backup_path = self.backup_dir / backup_name
        
        self.log(f"Creating incremental backup: {backup_name}")
        
        # Create backup with git if available
        if self.is_git_repo():
            self.create_git_backup(backup_name)
        else:
            # Fallback to file copy
            shutil.copytree(self.project_root, backup_path, 
                          ignore=shutil.ignore_patterns('__pycache__', '*.pyc', 'node_modules'))
        
        self.current_state["last_backup"] = str(backup_path)
        self.save_migration_state()
        
        return str(backup_path)
    
    def is_git_repo(self) -> bool:
        """Check if project is a git repository"""
        return (self.project_root / ".git").exists()
    
    def create_git_backup(self, backup_name: str):
        """Create git-based backup"""
        try:
            # Create a tag for this backup point
            subprocess.run(
                ["git", "tag", f"backup-{backup_name}"],
                cwd=self.project_root,
                check=True
            )
            
            # Create stash if there are uncommitted changes
            result = subprocess.run(
                ["git", "stash", "push", "-m", f"Migration backup {backup_name}"],
                cwd=self.project_root,
                capture_output=True
            )
            
            self.log(f"Git backup created: tag backup-{backup_name}")
            
        except subprocess.CalledProcessError as e:
            self.log(f"Git backup failed: {e}")
            raise
    
    def calculate_checksum(self, file_path: Path) -> str:
        """Calculate file checksum for integrity verification"""
        if not file_path.exists():
            return ""
        
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def run_migration_step(self, step: MigrationStep) -> bool:
        """Execute a single migration step with validation"""
        self.log(f"Starting migration step: {step.id} - {step.description}")
        
        try:
            # Update step status
            step.status = MigrationStatus.IN_PROGRESS
            self.record_migration_step(step)
            
            # Run pre-migration tests
            if step.validation_tests:
                self.log("Running pre-migration validation tests...")
                if not self.run_tests(step.validation_tests):
                    raise Exception("Pre-migration tests failed")
            
            # Execute migration logic here
            # This would be customized for each specific migration
            
            # Run post-migration tests
            if step.validation_tests:
                self.log("Running post-migration validation tests...")
                if not self.run_tests(step.validation_tests):
                    raise Exception("Post-migration tests failed")
            
            # Mark as completed
            step.status = MigrationStatus.COMPLETED
            self.record_migration_step(step)
            
            self.log(f"Migration step completed successfully: {step.id}")
            return True
            
        except Exception as e:
            self.log(f"Migration step failed: {step.id} - {str(e)}")
            step.status = MigrationStatus.FAILED
            self.record_migration_step(step)
            return False
    
    def run_tests(self, test_commands: List[str]) -> bool:
        """Run validation tests"""
        for test_cmd in test_commands:
            try:
                self.log(f"Running test: {test_cmd}")
                result = subprocess.run(
                    test_cmd.split(),
                    cwd=self.project_root,
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 minute timeout
                )
                
                if result.returncode != 0:
                    self.log(f"Test failed: {test_cmd}")
                    self.log(f"Error output: {result.stderr}")
                    return False
                    
                self.log(f"Test passed: {test_cmd}")
                
            except subprocess.TimeoutExpired:
                self.log(f"Test timed out: {test_cmd}")
                return False
            except Exception as e:
                self.log(f"Test error: {test_cmd} - {str(e)}")
                return False
        
        return True
    
    def rollback_migration(self, to_version: str = None) -> bool:
        """Rollback to previous version"""
        self.log(f"Starting rollback to version: {to_version or 'previous'}")
        
        try:
            if self.is_git_repo():
                return self.git_rollback(to_version)
            else:
                return self.file_rollback()
                
        except Exception as e:
            self.log(f"Rollback failed: {str(e)}")
            return False
    
    def git_rollback(self, to_version: str = None) -> bool:
        """Git-based rollback"""
        try:
            if to_version:
                # Rollback to specific tag
                subprocess.run(
                    ["git", "checkout", f"backup-{to_version}"],
                    cwd=self.project_root,
                    check=True
                )
            else:
                # Rollback to last backup
                backup_tags = subprocess.run(
                    ["git", "tag", "--list", "backup-*"],
                    cwd=self.project_root,
                    capture_output=True,
                    text=True
                ).stdout.strip().split('\n')
                
                if backup_tags and backup_tags[0]:
                    latest_backup = sorted(backup_tags)[-1]
                    subprocess.run(
                        ["git", "checkout", latest_backup],
                        cwd=self.project_root,
                        check=True
                    )
            
            self.log("Git rollback completed successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            self.log(f"Git rollback failed: {e}")
            return False
    
    def file_rollback(self) -> bool:
        """File-based rollback"""
        last_backup = self.current_state.get("last_backup")
        if not last_backup or not Path(last_backup).exists():
            self.log("No backup available for rollback")
            return False
        
        try:
            # Remove current files (except this script)
            backup_path = Path(last_backup)
            
            # Restore from backup
            for item in backup_path.iterdir():
                dest = self.project_root / item.name
                if dest.exists():
                    if dest.is_dir():
                        shutil.rmtree(dest)
                    else:
                        dest.unlink()
                
                if item.is_dir():
                    shutil.copytree(item, dest)
                else:
                    shutil.copy2(item, dest)
            
            self.log("File rollback completed successfully")
            return True
            
        except Exception as e:
            self.log(f"File rollback failed: {e}")
            return False
    
    def record_migration_step(self, step: MigrationStep):
        """Record migration step in state"""
        # Update or add step in current state
        step_dict = asdict(step)
        step_dict['status'] = step.status.value
        
        # Find and update existing step or add new one
        updated = False
        for i, existing_step in enumerate(self.current_state["migrations"]):
            if existing_step["id"] == step.id:
                self.current_state["migrations"][i] = step_dict
                updated = True
                break
        
        if not updated:
            self.current_state["migrations"].append(step_dict)
        
        self.save_migration_state()
    
    def log(self, message: str):
        """Log migration activities"""
        timestamp = datetime.datetime.now().isoformat()
        log_entry = f"[{timestamp}] {message}\n"
        
        with open(self.log_file, 'a') as f:
            f.write(log_entry)
        
        print(log_entry.strip())
    
    def get_migration_status(self) -> Dict:
        """Get current migration status"""
        return {
            "current_version": self.current_state["current_version"],
            "total_migrations": len(self.current_state["migrations"]),
            "completed_migrations": len([m for m in self.current_state["migrations"] 
                                       if m["status"] == "completed"]),
            "failed_migrations": len([m for m in self.current_state["migrations"] 
                                    if m["status"] == "failed"]),
            "rollback_available": self.current_state["rollback_available"],
            "last_backup": self.current_state["last_backup"]
        }

def main():
    """CLI interface for migration management"""
    import argparse
    
    parser = argparse.ArgumentParser(description="SuperMCP Migration Manager")
    parser.add_argument("--status", action="store_true", help="Show migration status")
    parser.add_argument("--backup", type=str, help="Create backup with version")
    parser.add_argument("--rollback", type=str, nargs="?", const="", help="Rollback to version")
    parser.add_argument("--test", action="store_true", help="Run validation tests")
    
    args = parser.parse_args()
    
    manager = SuperMCPMigrationManager()
    
    if args.status:
        status = manager.get_migration_status()
        print(json.dumps(status, indent=2))
    
    elif args.backup:
        backup_path = manager.create_incremental_backup(args.backup)
        print(f"Backup created: {backup_path}")
    
    elif args.rollback is not None:
        version = args.rollback if args.rollback else None
        success = manager.rollback_migration(version)
        print(f"Rollback {'successful' if success else 'failed'}")
    
    elif args.test:
        # Run basic validation tests
        test_commands = [
            "python3 -m py_compile supermcp_new/agents/swarm/intelligence_system.py",
            "python3 -m py_compile supermcp_new/ai/models/router.py"
        ]
        success = manager.run_tests(test_commands)
        print(f"Tests {'passed' if success else 'failed'}")

if __name__ == "__main__":
    main()