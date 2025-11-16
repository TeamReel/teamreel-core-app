#!/usr/bin/env python3
"""
Template Synchronization Mechanism - T034

Maintains consistency between project configurations and master templates.
Detects template drift, synchronizes updates, and manages version conflicts.

Part of TeamReel's SDD Constitutional Foundation & Enforcement system.
"""

import os
import yaml
import json
import hashlib
import shutil
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Set, Tuple, Union
from dataclasses import dataclass, asdict, field
from enum import Enum
import argparse


class SyncStatus(Enum):
    """Status of template synchronization."""
    IN_SYNC = "in_sync"
    DRIFT_DETECTED = "drift_detected"
    UPDATE_AVAILABLE = "update_available"
    CONFLICT = "conflict"
    SYNC_ERROR = "sync_error"
    PENDING_REVIEW = "pending_review"


class DriftSeverity(Enum):
    """Severity levels for template drift."""
    LOW = "low"           # Minor cosmetic changes
    MEDIUM = "medium"     # Configuration changes
    HIGH = "high"         # Structural changes
    CRITICAL = "critical" # Breaking changes


@dataclass
class TemplateVersion:
    """Version information for a template."""
    version: str
    hash: str
    created: str
    author: str
    changelog: List[str]
    constitutional_version: str


@dataclass
class DriftDetection:
    """Details about detected template drift."""
    template_name: str
    local_version: str
    remote_version: str
    local_hash: str
    remote_hash: str
    severity: DriftSeverity
    affected_sections: List[str]
    changes_description: str
    detected_at: str
    auto_fixable: bool


@dataclass
class SyncResult:
    """Result of a synchronization operation."""
    template_name: str
    status: SyncStatus
    previous_version: str
    new_version: str
    changes_applied: List[str]
    conflicts: List[str]
    sync_timestamp: str
    backup_created: bool
    requires_manual_review: bool


class TemplateSynchronizer:
    """Manages template synchronization and drift detection."""
    
    def __init__(self, config_dir: Path, templates_dir: Path):
        """Initialize template synchronizer."""
        self.config_dir = Path(config_dir)
        self.templates_dir = Path(templates_dir)
        
        # Create directories
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        
        # Sync configuration
        self.sync_config_path = self.config_dir / "sync_config.yaml"
        self.sync_history_path = self.config_dir / "sync_history.yaml"
        self.drift_log_path = self.config_dir / "drift_log.yaml"
        
        # Backup directory
        self.backup_dir = self.templates_dir / "backups"
        self.backup_dir.mkdir(exist_ok=True)
        
        # Load configuration
        self.sync_config = self._load_sync_config()
        self.sync_history = self._load_sync_history()
        
    def _load_sync_config(self) -> Dict[str, Any]:
        """Load synchronization configuration."""
        if self.sync_config_path.exists():
            try:
                with open(self.sync_config_path, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f)
            except Exception as e:
                print(f"⚠️ Failed to load sync config: {e}")
        
        return self._create_default_sync_config()
    
    def _create_default_sync_config(self) -> Dict[str, Any]:
        """Create default synchronization configuration."""
        default_config = {
            'sync_settings': {
                'auto_sync_enabled': True,
                'sync_interval_hours': 24,
                'auto_fix_low_severity': True,
                'backup_before_sync': True,
                'max_backups': 10,
                'require_approval_for_high_severity': True
            },
            'remote_sources': {
                'primary': {
                    'type': 'github',
                    'url': 'https://api.github.com/repos/teamreel/constitutional-templates',
                    'branch': 'main',
                    'auth_required': False
                }
            },
            'templates': {
                'se_rules_standard': {
                    'sync_enabled': True,
                    'allow_customizations': True,
                    'protected_sections': ['constitutional_enforcement.version'],
                    'auto_merge_strategy': 'conservative'
                },
                'quality_gates_standard': {
                    'sync_enabled': True,
                    'allow_customizations': True,
                    'protected_sections': ['quality_gates.version'],
                    'auto_merge_strategy': 'conservative'
                },
                'naming_conventions_teamreel': {
                    'sync_enabled': True,
                    'allow_customizations': True,
                    'protected_sections': [],
                    'auto_merge_strategy': 'liberal'
                }
            },
            'notifications': {
                'drift_detected': True,
                'sync_completed': True,
                'conflicts_require_attention': True,
                'high_severity_changes': True
            }
        }
        
        with open(self.sync_config_path, 'w', encoding='utf-8') as f:
            yaml.dump(default_config, f, default_flow_style=False, indent=2)
        
        return default_config
    
    def _load_sync_history(self) -> List[SyncResult]:
        """Load synchronization history."""
        if self.sync_history_path.exists():
            try:
                with open(self.sync_history_path, 'r', encoding='utf-8') as f:
                    history_data = yaml.safe_load(f)
                    
                results = []
                for result_data in history_data.get('sync_history', []):
                    result = SyncResult(
                        template_name=result_data['template_name'],
                        status=SyncStatus(result_data['status']),
                        previous_version=result_data['previous_version'],
                        new_version=result_data['new_version'],
                        changes_applied=result_data['changes_applied'],
                        conflicts=result_data['conflicts'],
                        sync_timestamp=result_data['sync_timestamp'],
                        backup_created=result_data['backup_created'],
                        requires_manual_review=result_data['requires_manual_review']
                    )
                    results.append(result)
                
                return results
            except Exception as e:
                print(f"⚠️ Failed to load sync history: {e}")
        
        return []
    
    def _save_sync_history(self) -> None:
        """Save synchronization history."""
        history_data = {
            'sync_history': [asdict(result) for result in self.sync_history]
        }
        
        with open(self.sync_history_path, 'w', encoding='utf-8') as f:
            yaml.dump(history_data, f, default_flow_style=False, indent=2)
    
    def detect_template_drift(self) -> List[DriftDetection]:
        """Detect drift between local and remote templates."""
        print("🔍 Detecting template drift...")
        
        drift_detections = []
        
        for template_name, template_config in self.sync_config['templates'].items():
            if not template_config.get('sync_enabled', True):
                continue
            
            try:
                drift = self._check_single_template_drift(template_name, template_config)
                if drift:
                    drift_detections.append(drift)
                    print(f"  🔄 Drift detected: {template_name} ({drift.severity.value})")
                else:
                    print(f"  ✅ In sync: {template_name}")
            except Exception as e:
                print(f"  ❌ Error checking {template_name}: {e}")
        
        # Log drift detections
        self._log_drift_detections(drift_detections)
        
        return drift_detections
    
    def _check_single_template_drift(self, template_name: str, 
                                   template_config: Dict[str, Any]) -> Optional[DriftDetection]:
        """Check drift for a single template."""
        local_template_path = self.templates_dir / f"{template_name}.yaml"
        
        if not local_template_path.exists():
            # Template doesn't exist locally - this is drift
            return DriftDetection(
                template_name=template_name,
                local_version="missing",
                remote_version="unknown",
                local_hash="",
                remote_hash="",
                severity=DriftSeverity.HIGH,
                affected_sections=["entire_template"],
                changes_description="Template missing locally",
                detected_at=datetime.utcnow().isoformat() + 'Z',
                auto_fixable=True
            )
        
        # Calculate local hash
        local_hash = self._calculate_file_hash(local_template_path)
        
        # For this implementation, we'll simulate remote template checking
        # In a real implementation, this would fetch from GitHub API or other remote source
        remote_template_data = self._fetch_remote_template(template_name)
        
        if not remote_template_data:
            return None
        
        remote_hash = self._calculate_content_hash(yaml.dump(remote_template_data))
        
        if local_hash == remote_hash:
            return None  # No drift
        
        # Analyze the differences
        local_template_data = self._load_template_file(local_template_path)
        drift_analysis = self._analyze_template_differences(
            local_template_data, remote_template_data, template_config
        )
        
        return DriftDetection(
            template_name=template_name,
            local_version=local_template_data.get('metadata', {}).get('version', 'unknown'),
            remote_version=remote_template_data.get('metadata', {}).get('version', 'unknown'),
            local_hash=local_hash,
            remote_hash=remote_hash,
            severity=drift_analysis['severity'],
            affected_sections=drift_analysis['affected_sections'],
            changes_description=drift_analysis['description'],
            detected_at=datetime.utcnow().isoformat() + 'Z',
            auto_fixable=drift_analysis['auto_fixable']
        )
    
    def _fetch_remote_template(self, template_name: str) -> Optional[Dict[str, Any]]:
        """Fetch remote template data. This is a simulation for the demo."""
        # In a real implementation, this would make HTTP requests to GitHub API
        # For now, we'll return sample data that shows what drift detection would look like
        
        # Simulate some templates having updates available
        if template_name == "se_rules_standard":
            return {
                'metadata': {
                    'version': '1.1.0',  # Newer version
                    'created': '2024-01-15T10:00:00Z',
                    'author': 'TeamReel Constitutional Foundation'
                },
                'constitutional_enforcement': {
                    'version': '1.1.0',
                    'strict_mode': True,
                    'violation_threshold': 'medium',
                    'principles': {
                        'SRP': {
                            'enabled': True,
                            'weight': 1.0,
                            'metrics': {
                                'max_methods_per_class': 8,  # Changed from 10
                                'max_lines_per_function': 45,  # Changed from 50
                                'max_responsibilities': 1
                            }
                        }
                    }
                }
            }
        elif template_name == "quality_gates_standard":
            return {
                'metadata': {
                    'version': '1.0.1',  # Minor update
                    'created': '2024-01-10T15:30:00Z'
                },
                'quality_gates': {
                    'version': '1.0.1',
                    'gates': {
                        'coverage': {
                            'enabled': True,
                            'threshold': 85.0,  # Increased from 80.0
                            'fail_under': True
                        },
                        'security': {
                            'enabled': True,
                            'severity_threshold': 'medium',  # Changed from 'high'
                            'fail_on_critical': True
                        }
                    }
                }
            }
        
        return None  # No remote template found
    
    def _analyze_template_differences(self, local_data: Dict[str, Any], 
                                    remote_data: Dict[str, Any],
                                    template_config: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze differences between local and remote templates."""
        affected_sections = []
        changes = []
        severity = DriftSeverity.LOW
        auto_fixable = True
        
        # Compare versions
        local_version = local_data.get('metadata', {}).get('version', '0.0.0')
        remote_version = remote_data.get('metadata', {}).get('version', '0.0.0')
        
        if self._is_version_newer(remote_version, local_version):
            changes.append(f"Version update: {local_version} → {remote_version}")
            severity = DriftSeverity.MEDIUM
        
        # Deep compare configurations
        local_config = {k: v for k, v in local_data.items() if k != 'metadata'}
        remote_config = {k: v for k, v in remote_data.items() if k != 'metadata'}
        
        diff_result = self._deep_compare_configs(local_config, remote_config, "")
        
        affected_sections.extend(diff_result['changed_sections'])
        changes.extend(diff_result['changes'])
        
        # Determine severity based on changes
        protected_sections = template_config.get('protected_sections', [])
        
        for section in affected_sections:
            if any(section.startswith(protected) for protected in protected_sections):
                severity = DriftSeverity.HIGH
                auto_fixable = False
                break
        
        # Check for breaking changes
        if any('removed' in change.lower() or 'deleted' in change.lower() for change in changes):
            severity = DriftSeverity.CRITICAL
            auto_fixable = False
        
        return {
            'severity': severity,
            'affected_sections': affected_sections,
            'description': '; '.join(changes[:5]),  # Limit description length
            'auto_fixable': auto_fixable and severity in [DriftSeverity.LOW, DriftSeverity.MEDIUM]
        }
    
    def _deep_compare_configs(self, local: Dict[str, Any], remote: Dict[str, Any], 
                            path: str) -> Dict[str, Any]:
        """Deep compare two configuration dictionaries."""
        changed_sections = []
        changes = []
        
        # Check for added/modified keys in remote
        for key, remote_value in remote.items():
            current_path = f"{path}.{key}" if path else key
            
            if key not in local:
                changed_sections.append(current_path)
                changes.append(f"Added: {current_path}")
            elif isinstance(remote_value, dict) and isinstance(local[key], dict):
                nested_result = self._deep_compare_configs(local[key], remote_value, current_path)
                changed_sections.extend(nested_result['changed_sections'])
                changes.extend(nested_result['changes'])
            elif local[key] != remote_value:
                changed_sections.append(current_path)
                changes.append(f"Changed: {current_path} ({local[key]} → {remote_value})")
        
        # Check for removed keys
        for key in local:
            if key not in remote:
                current_path = f"{path}.{key}" if path else key
                changed_sections.append(current_path)
                changes.append(f"Removed: {current_path}")
        
        return {
            'changed_sections': changed_sections,
            'changes': changes
        }
    
    def synchronize_templates(self, template_names: Optional[List[str]] = None,
                            auto_resolve_conflicts: bool = False) -> List[SyncResult]:
        """Synchronize templates with remote sources."""
        print("🔄 Synchronizing templates...")
        
        if template_names is None:
            template_names = list(self.sync_config['templates'].keys())
        
        sync_results = []
        
        for template_name in template_names:
            try:
                result = self._synchronize_single_template(template_name, auto_resolve_conflicts)
                sync_results.append(result)
                
                status_icon = {
                    SyncStatus.IN_SYNC: "✅",
                    SyncStatus.UPDATE_AVAILABLE: "🔄",
                    SyncStatus.CONFLICT: "⚠️",
                    SyncStatus.SYNC_ERROR: "❌",
                    SyncStatus.PENDING_REVIEW: "👀"
                }.get(result.status, "❓")
                
                print(f"  {status_icon} {template_name}: {result.status.value}")
                
            except Exception as e:
                error_result = SyncResult(
                    template_name=template_name,
                    status=SyncStatus.SYNC_ERROR,
                    previous_version="unknown",
                    new_version="unknown",
                    changes_applied=[],
                    conflicts=[f"Sync error: {e}"],
                    sync_timestamp=datetime.utcnow().isoformat() + 'Z',
                    backup_created=False,
                    requires_manual_review=True
                )
                sync_results.append(error_result)
                print(f"  ❌ {template_name}: sync error - {e}")
        
        # Update sync history
        self.sync_history.extend(sync_results)
        self._save_sync_history()
        
        return sync_results
    
    def _synchronize_single_template(self, template_name: str, 
                                   auto_resolve_conflicts: bool) -> SyncResult:
        """Synchronize a single template."""
        template_config = self.sync_config['templates'].get(template_name, {})
        local_template_path = self.templates_dir / f"{template_name}.yaml"
        
        # Get remote template
        remote_template_data = self._fetch_remote_template(template_name)
        if not remote_template_data:
            return SyncResult(
                template_name=template_name,
                status=SyncStatus.IN_SYNC,
                previous_version="unknown",
                new_version="unknown",
                changes_applied=["No remote template found"],
                conflicts=[],
                sync_timestamp=datetime.utcnow().isoformat() + 'Z',
                backup_created=False,
                requires_manual_review=False
            )
        
        # Load local template
        local_template_data = {}
        previous_version = "missing"
        
        if local_template_path.exists():
            local_template_data = self._load_template_file(local_template_path)
            previous_version = local_template_data.get('metadata', {}).get('version', 'unknown')
        
        new_version = remote_template_data.get('metadata', {}).get('version', 'unknown')
        
        # Create backup if configured
        backup_created = False
        if (self.sync_config['sync_settings'].get('backup_before_sync', True) and 
            local_template_path.exists()):
            backup_created = self._create_backup(template_name, local_template_data)
        
        # Detect conflicts
        conflicts = self._detect_sync_conflicts(local_template_data, remote_template_data, template_config)
        
        # Determine sync strategy
        if conflicts and not auto_resolve_conflicts:
            return SyncResult(
                template_name=template_name,
                status=SyncStatus.CONFLICT,
                previous_version=previous_version,
                new_version=new_version,
                changes_applied=[],
                conflicts=conflicts,
                sync_timestamp=datetime.utcnow().isoformat() + 'Z',
                backup_created=backup_created,
                requires_manual_review=True
            )
        
        # Apply synchronization
        try:
            merged_template = self._merge_templates(
                local_template_data, remote_template_data, template_config
            )
            
            # Save merged template
            with open(local_template_path, 'w', encoding='utf-8') as f:
                yaml.dump(merged_template, f, default_flow_style=False, indent=2)
            
            # Generate change summary
            changes_applied = self._generate_change_summary(local_template_data, merged_template)
            
            return SyncResult(
                template_name=template_name,
                status=SyncStatus.IN_SYNC,
                previous_version=previous_version,
                new_version=new_version,
                changes_applied=changes_applied,
                conflicts=conflicts if auto_resolve_conflicts else [],
                sync_timestamp=datetime.utcnow().isoformat() + 'Z',
                backup_created=backup_created,
                requires_manual_review=len(conflicts) > 0
            )
            
        except Exception as e:
            return SyncResult(
                template_name=template_name,
                status=SyncStatus.SYNC_ERROR,
                previous_version=previous_version,
                new_version=new_version,
                changes_applied=[],
                conflicts=[f"Merge error: {e}"],
                sync_timestamp=datetime.utcnow().isoformat() + 'Z',
                backup_created=backup_created,
                requires_manual_review=True
            )
    
    def _detect_sync_conflicts(self, local_data: Dict[str, Any], 
                             remote_data: Dict[str, Any],
                             template_config: Dict[str, Any]) -> List[str]:
        """Detect conflicts that prevent automatic synchronization."""
        conflicts = []
        
        # Check protected sections
        protected_sections = template_config.get('protected_sections', [])
        
        for section in protected_sections:
            local_value = self._get_nested_value(local_data, section)
            remote_value = self._get_nested_value(remote_data, section)
            
            if local_value != remote_value and local_value is not None:
                conflicts.append(f"Protected section modified: {section}")
        
        # Check for breaking changes
        local_version = local_data.get('metadata', {}).get('version', '0.0.0')
        remote_version = remote_data.get('metadata', {}).get('version', '0.0.0')
        
        if self._is_breaking_change(local_version, remote_version):
            conflicts.append(f"Breaking version change: {local_version} → {remote_version}")
        
        return conflicts
    
    def _merge_templates(self, local_data: Dict[str, Any], 
                        remote_data: Dict[str, Any],
                        template_config: Dict[str, Any]) -> Dict[str, Any]:
        """Merge local customizations with remote updates."""
        merge_strategy = template_config.get('auto_merge_strategy', 'conservative')
        
        if merge_strategy == 'liberal':
            # Take remote version with minimal local preservation
            merged = remote_data.copy()
            
            # Preserve specific local customizations if they exist
            if template_config.get('allow_customizations', True):
                # This is a simplified merge - real implementation would be more sophisticated
                pass
                
        else:  # conservative
            # Start with local, selectively apply remote changes
            merged = local_data.copy() if local_data else {}
            
            # Always update metadata
            merged['metadata'] = remote_data.get('metadata', {})
            
            # Selectively merge configuration sections
            for key, remote_value in remote_data.items():
                if key == 'metadata':
                    continue
                    
                if key not in merged:
                    merged[key] = remote_value
                elif isinstance(remote_value, dict) and isinstance(merged[key], dict):
                    merged[key] = self._merge_dict_conservative(merged[key], remote_value)
                else:
                    # For non-dict values, keep local unless it's clearly an update
                    if not template_config.get('allow_customizations', True):
                        merged[key] = remote_value
        
        return merged
    
    def _merge_dict_conservative(self, local_dict: Dict[str, Any], 
                               remote_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Conservative merge of nested dictionaries."""
        merged = local_dict.copy()
        
        for key, remote_value in remote_dict.items():
            if key not in merged:
                merged[key] = remote_value
            elif isinstance(remote_value, dict) and isinstance(merged[key], dict):
                merged[key] = self._merge_dict_conservative(merged[key], remote_value)
            # Keep local value for leaf nodes (conservative approach)
        
        return merged
    
    def _create_backup(self, template_name: str, template_data: Dict[str, Any]) -> bool:
        """Create backup of template before synchronization."""
        try:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"{template_name}_{timestamp}.yaml"
            backup_path = self.backup_dir / backup_filename
            
            with open(backup_path, 'w', encoding='utf-8') as f:
                yaml.dump(template_data, f, default_flow_style=False, indent=2)
            
            # Clean up old backups
            self._cleanup_old_backups(template_name)
            
            return True
        except Exception as e:
            print(f"⚠️ Failed to create backup for {template_name}: {e}")
            return False
    
    def _cleanup_old_backups(self, template_name: str) -> None:
        """Remove old backups beyond the configured limit."""
        max_backups = self.sync_config['sync_settings'].get('max_backups', 10)
        
        backup_pattern = f"{template_name}_*.yaml"
        backup_files = list(self.backup_dir.glob(backup_pattern))
        
        if len(backup_files) > max_backups:
            # Sort by modification time and remove oldest
            backup_files.sort(key=lambda f: f.stat().st_mtime)
            
            for old_backup in backup_files[:-max_backups]:
                try:
                    old_backup.unlink()
                except Exception as e:
                    print(f"⚠️ Failed to remove old backup {old_backup}: {e}")
    
    def _generate_change_summary(self, local_data: Dict[str, Any], 
                               merged_data: Dict[str, Any]) -> List[str]:
        """Generate summary of changes applied during sync."""
        changes = []
        
        # Compare versions
        local_version = local_data.get('metadata', {}).get('version', 'unknown')
        merged_version = merged_data.get('metadata', {}).get('version', 'unknown')
        
        if local_version != merged_version:
            changes.append(f"Version updated: {local_version} → {merged_version}")
        
        # This is a simplified change detection - real implementation would be more detailed
        if local_data != merged_data:
            changes.append("Configuration updated with remote changes")
        
        return changes
    
    def _log_drift_detections(self, drift_detections: List[DriftDetection]) -> None:
        """Log drift detections to file."""
        if not drift_detections:
            return
        
        try:
            # Load existing drift log
            drift_log = []
            if self.drift_log_path.exists():
                with open(self.drift_log_path, 'r', encoding='utf-8') as f:
                    drift_log = yaml.safe_load(f).get('drift_detections', [])
            
            # Add new detections
            for drift in drift_detections:
                drift_log.append(asdict(drift))
            
            # Keep only recent detections (last 100)
            drift_log = drift_log[-100:]
            
            # Save updated log
            with open(self.drift_log_path, 'w', encoding='utf-8') as f:
                yaml.dump({'drift_detections': drift_log}, f, default_flow_style=False, indent=2)
                
        except Exception as e:
            print(f"⚠️ Failed to log drift detections: {e}")
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA-256 hash of a file."""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    def _calculate_content_hash(self, content: str) -> str:
        """Calculate SHA-256 hash of content string."""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    def _load_template_file(self, file_path: Path) -> Dict[str, Any]:
        """Load template file as dictionary."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            print(f"⚠️ Failed to load template file {file_path}: {e}")
            return {}
    
    def _get_nested_value(self, data: Dict[str, Any], path: str) -> Any:
        """Get nested dictionary value using dot notation."""
        if not data:
            return None
            
        keys = path.split('.')
        current = data
        
        try:
            for key in keys:
                current = current[key]
            return current
        except (KeyError, TypeError):
            return None
    
    def _is_version_newer(self, version1: str, version2: str) -> bool:
        """Check if version1 is newer than version2."""
        def version_tuple(v):
            return tuple(map(int, (v.split("."))))
        
        try:
            return version_tuple(version1) > version_tuple(version2)
        except:
            return version1 > version2  # Fallback to string comparison
    
    def _is_breaking_change(self, old_version: str, new_version: str) -> bool:
        """Check if version change is a breaking change (major version bump)."""
        try:
            old_major = int(old_version.split('.')[0])
            new_major = int(new_version.split('.')[0])
            return new_major > old_major
        except:
            return False
    
    def get_sync_status(self) -> Dict[str, Any]:
        """Get overall synchronization status."""
        recent_syncs = [result for result in self.sync_history 
                       if self._is_recent_sync(result.sync_timestamp)]
        
        status_counts = {}
        for result in recent_syncs:
            status = result.status.value
            status_counts[status] = status_counts.get(status, 0) + 1
        
        return {
            'last_sync_check': datetime.utcnow().isoformat() + 'Z',
            'total_templates': len(self.sync_config['templates']),
            'recent_sync_results': status_counts,
            'sync_enabled': self.sync_config['sync_settings'].get('auto_sync_enabled', True),
            'sync_interval_hours': self.sync_config['sync_settings'].get('sync_interval_hours', 24)
        }
    
    def _is_recent_sync(self, sync_timestamp: str, hours: int = 24) -> bool:
        """Check if sync timestamp is within recent hours."""
        try:
            sync_time = datetime.fromisoformat(sync_timestamp.rstrip('Z'))
            time_diff = datetime.utcnow() - sync_time
            return time_diff < timedelta(hours=hours)
        except:
            return False


def main():
    """Main CLI entry point for template synchronization."""
    parser = argparse.ArgumentParser(
        description='Synchronize constitutional templates with remote sources'
    )
    
    parser.add_argument('--config-dir', type=Path, default=Path('.kittify/config'),
                       help='Configuration directory (default: .kittify/config)')
    parser.add_argument('--templates-dir', type=Path, default=Path('.kittify/templates'),
                       help='Templates directory (default: .kittify/templates)')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Detect drift command
    drift_parser = subparsers.add_parser('detect-drift', help='Detect template drift')
    
    # Sync command
    sync_parser = subparsers.add_parser('sync', help='Synchronize templates')
    sync_parser.add_argument('--templates', nargs='*', help='Specific templates to sync')
    sync_parser.add_argument('--auto-resolve', action='store_true',
                            help='Automatically resolve conflicts')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Show synchronization status')
    
    # History command
    history_parser = subparsers.add_parser('history', help='Show synchronization history')
    history_parser.add_argument('--limit', type=int, default=10, help='Number of results to show')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Initialize synchronizer
    synchronizer = TemplateSynchronizer(args.config_dir, args.templates_dir)
    
    try:
        if args.command == 'detect-drift':
            drift_detections = synchronizer.detect_template_drift()
            
            if drift_detections:
                print(f"\n📊 Drift Detection Summary ({len(drift_detections)} templates):")
                for drift in drift_detections:
                    severity_icon = {
                        DriftSeverity.LOW: "🟢",
                        DriftSeverity.MEDIUM: "🟡", 
                        DriftSeverity.HIGH: "🟠",
                        DriftSeverity.CRITICAL: "🔴"
                    }.get(drift.severity, "❓")
                    
                    print(f"  {severity_icon} {drift.template_name}: {drift.changes_description}")
                    print(f"    Version: {drift.local_version} → {drift.remote_version}")
                    print(f"    Auto-fixable: {'Yes' if drift.auto_fixable else 'No'}")
            else:
                print("✅ No template drift detected")
        
        elif args.command == 'sync':
            results = synchronizer.synchronize_templates(
                args.templates, args.auto_resolve
            )
            
            print(f"\n📊 Synchronization Summary ({len(results)} templates):")
            for result in results:
                print(f"  • {result.template_name}: {result.status.value}")
                if result.changes_applied:
                    print(f"    Changes: {', '.join(result.changes_applied)}")
                if result.conflicts:
                    print(f"    Conflicts: {', '.join(result.conflicts)}")
        
        elif args.command == 'status':
            status = synchronizer.get_sync_status()
            print("📊 Synchronization Status:")
            print(f"  Total Templates: {status['total_templates']}")
            print(f"  Auto-sync: {'Enabled' if status['sync_enabled'] else 'Disabled'}")
            print(f"  Sync Interval: {status['sync_interval_hours']} hours")
            print(f"  Last Check: {status['last_sync_check']}")
            
            if status['recent_sync_results']:
                print("  Recent Results:")
                for status_type, count in status['recent_sync_results'].items():
                    print(f"    {status_type}: {count}")
        
        elif args.command == 'history':
            history = synchronizer.sync_history[-args.limit:]
            
            if history:
                print(f"📚 Synchronization History (last {len(history)} entries):")
                for result in reversed(history):
                    print(f"  • {result.sync_timestamp}: {result.template_name} ({result.status.value})")
                    if result.changes_applied:
                        print(f"    Changes: {', '.join(result.changes_applied[:2])}")
            else:
                print("📚 No synchronization history found")
    
    except Exception as e:
        print(f"❌ Command failed: {e}")


if __name__ == '__main__':
    main()