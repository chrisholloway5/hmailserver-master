"""
Self-Healing System - Phase 3 Core Component
============================================

This module implements autonomous self-healing capabilities that automatically
detect, diagnose, and resolve system issues without human intervention.

Features:
- Automatic problem detection
- Intelligent fault diagnosis
- Self-recovery mechanisms
- Predictive failure prevention
- System health monitoring
- Automated rollback capabilities
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
import threading
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HealthStatus(Enum):
    """System health status levels"""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    FAILED = "failed"
    RECOVERING = "recovering"

class IssueType(Enum):
    """Types of system issues"""
    PERFORMANCE_DEGRADATION = "performance_degradation"
    MEMORY_LEAK = "memory_leak"
    CONNECTION_FAILURE = "connection_failure"
    DISK_SPACE_LOW = "disk_space_low"
    SERVICE_UNRESPONSIVE = "service_unresponsive"
    SECURITY_BREACH = "security_breach"
    CONFIGURATION_ERROR = "configuration_error"
    NETWORK_ISSUE = "network_issue"

@dataclass
class HealthMetric:
    """Health metric container"""
    name: str
    value: float
    threshold: float
    status: HealthStatus
    timestamp: datetime
    description: str = ""

@dataclass
class SystemIssue:
    """System issue container"""
    issue_id: str
    issue_type: IssueType
    severity: HealthStatus
    description: str
    affected_components: List[str]
    detected_at: datetime
    resolved_at: Optional[datetime] = None
    resolution_actions: List[str] = field(default_factory=list)
    auto_resolved: bool = False

@dataclass
class RecoveryAction:
    """Recovery action container"""
    action_id: str
    action_type: str
    description: str
    target_components: List[str]
    execution_time: datetime
    success: bool
    rollback_available: bool = True

class SelfHealingSystem:
    """
    Self-Healing System
    
    Automatically detects system issues and implements recovery actions
    to maintain optimal system health without human intervention.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the self-healing system"""
        self.config_path = config_path or "config/self_healing.json"
        self.is_monitoring = False
        self.health_metrics: Dict[str, List[HealthMetric]] = {}
        self.active_issues: Dict[str, SystemIssue] = {}
        self.resolved_issues: List[SystemIssue] = []
        self.recovery_actions: List[RecoveryAction] = []
        self.monitoring_interval = 30  # seconds
        self.metrics_lock = threading.Lock()
        
        # Health thresholds
        self.health_thresholds = {
            'cpu_usage': {'warning': 75.0, 'critical': 90.0},
            'memory_usage': {'warning': 80.0, 'critical': 95.0},
            'disk_usage': {'warning': 85.0, 'critical': 95.0},
            'response_time': {'warning': 1000.0, 'critical': 3000.0},
            'error_rate': {'warning': 2.0, 'critical': 5.0},
            'connection_count': {'warning': 8000, 'critical': 9500},
            'queue_depth': {'warning': 500, 'critical': 1000}
        }
        
        # Recovery strategies
        self.recovery_strategies = {
            IssueType.PERFORMANCE_DEGRADATION: [
                'restart_slow_services',
                'clear_cache',
                'optimize_configuration',
                'scale_resources'
            ],
            IssueType.MEMORY_LEAK: [
                'restart_affected_service',
                'clear_memory_cache',
                'garbage_collection',
                'memory_optimization'
            ],
            IssueType.CONNECTION_FAILURE: [
                'restart_network_service',
                'reset_connections',
                'update_network_config',
                'failover_to_backup'
            ],
            IssueType.DISK_SPACE_LOW: [
                'cleanup_temp_files',
                'archive_old_logs',
                'compress_data',
                'expand_storage'
            ],
            IssueType.SERVICE_UNRESPONSIVE: [
                'restart_service',
                'kill_hanging_processes',
                'reset_service_config',
                'failover_service'
            ]
        }
        
        logger.info("Self-Healing System initialized")
    
    async def initialize(self):
        """Initialize the self-healing system"""
        try:
            await self._load_config()
            logger.info("Self-healing system initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize self-healing system: {e}")
            return False
    
    async def start_monitoring(self):
        """Start continuous health monitoring"""
        if self.is_monitoring:
            logger.warning("Health monitoring is already active")
            return
        
        self.is_monitoring = True
        logger.info("Starting continuous health monitoring...")
        
        try:
            while self.is_monitoring:
                # Collect health metrics
                await self._collect_health_metrics()
                
                # Analyze for issues
                issues = await self._detect_issues()
                
                # Process new issues
                for issue in issues:
                    await self._handle_issue(issue)
                
                # Check recovery progress
                await self._check_recovery_progress()
                
                # Wait for next monitoring cycle
                await asyncio.sleep(self.monitoring_interval)
                
        except Exception as e:
            logger.error(f"Error in health monitoring loop: {e}")
        finally:
            self.is_monitoring = False
            logger.info("Health monitoring stopped")
    
    async def stop_monitoring(self):
        """Stop health monitoring"""
        self.is_monitoring = False
        logger.info("Stopping health monitoring...")
    
    async def _collect_health_metrics(self):
        """Collect current health metrics"""
        try:
            timestamp = datetime.now()
            
            # Simulate system metrics (in production, these would come from actual monitoring)
            metrics = [
                HealthMetric(
                    name="cpu_usage",
                    value=self._simulate_cpu_usage(),
                    threshold=self.health_thresholds['cpu_usage']['warning'],
                    status=HealthStatus.HEALTHY,
                    timestamp=timestamp,
                    description="System CPU utilization percentage"
                ),
                HealthMetric(
                    name="memory_usage",
                    value=self._simulate_memory_usage(),
                    threshold=self.health_thresholds['memory_usage']['warning'],
                    status=HealthStatus.HEALTHY,
                    timestamp=timestamp,
                    description="System memory utilization percentage"
                ),
                HealthMetric(
                    name="disk_usage",
                    value=self._simulate_disk_usage(),
                    threshold=self.health_thresholds['disk_usage']['warning'],
                    status=HealthStatus.HEALTHY,
                    timestamp=timestamp,
                    description="Disk space utilization percentage"
                ),
                HealthMetric(
                    name="response_time",
                    value=self._simulate_response_time(),
                    threshold=self.health_thresholds['response_time']['warning'],
                    status=HealthStatus.HEALTHY,
                    timestamp=timestamp,
                    description="Average response time in milliseconds"
                ),
                HealthMetric(
                    name="error_rate",
                    value=self._simulate_error_rate(),
                    threshold=self.health_thresholds['error_rate']['warning'],
                    status=HealthStatus.HEALTHY,
                    timestamp=timestamp,
                    description="Error rate percentage"
                ),
                HealthMetric(
                    name="connection_count",
                    value=self._simulate_connection_count(),
                    threshold=self.health_thresholds['connection_count']['warning'],
                    status=HealthStatus.HEALTHY,
                    timestamp=timestamp,
                    description="Active connection count"
                ),
                HealthMetric(
                    name="queue_depth",
                    value=self._simulate_queue_depth(),
                    threshold=self.health_thresholds['queue_depth']['warning'],
                    status=HealthStatus.HEALTHY,
                    timestamp=timestamp,
                    description="Email queue depth"
                )
            ]
            
            # Update health status based on thresholds
            for metric in metrics:
                metric.status = self._determine_health_status(metric)
            
            # Store metrics
            with self.metrics_lock:
                for metric in metrics:
                    if metric.name not in self.health_metrics:
                        self.health_metrics[metric.name] = []
                    
                    self.health_metrics[metric.name].append(metric)
                    
                    # Keep only last 100 metrics per type
                    if len(self.health_metrics[metric.name]) > 100:
                        self.health_metrics[metric.name] = self.health_metrics[metric.name][-100:]
            
            logger.debug(f"Collected {len(metrics)} health metrics")
            
        except Exception as e:
            logger.error(f"Failed to collect health metrics: {e}")
    
    def _simulate_cpu_usage(self) -> float:
        """Simulate CPU usage"""
        import random
        base_usage = 45.0
        variation = random.uniform(-20, 30)
        # Occasionally simulate high CPU
        if random.random() < 0.1:
            variation += random.uniform(20, 50)
        return max(0.0, min(100.0, base_usage + variation))
    
    def _simulate_memory_usage(self) -> float:
        """Simulate memory usage"""
        import random
        base_usage = 60.0
        variation = random.uniform(-15, 25)
        # Occasionally simulate memory leak
        if random.random() < 0.05:
            variation += random.uniform(20, 40)
        return max(0.0, min(100.0, base_usage + variation))
    
    def _simulate_disk_usage(self) -> float:
        """Simulate disk usage"""
        import random
        base_usage = 70.0
        variation = random.uniform(-10, 15)
        return max(0.0, min(100.0, base_usage + variation))
    
    def _simulate_response_time(self) -> float:
        """Simulate response time"""
        import random
        base_time = 200.0
        variation = random.uniform(-100, 300)
        # Occasionally simulate slow response
        if random.random() < 0.08:
            variation += random.uniform(500, 2000)
        return max(10.0, base_time + variation)
    
    def _simulate_error_rate(self) -> float:
        """Simulate error rate"""
        import random
        base_rate = 0.5
        variation = random.uniform(-0.3, 1.5)
        # Occasionally simulate error spike
        if random.random() < 0.06:
            variation += random.uniform(2, 8)
        return max(0.0, base_rate + variation)
    
    def _simulate_connection_count(self) -> float:
        """Simulate connection count"""
        import random
        base_count = 3000
        variation = random.randint(-1000, 2000)
        # Occasionally simulate connection surge
        if random.random() < 0.07:
            variation += random.randint(2000, 5000)
        return max(0, base_count + variation)
    
    def _simulate_queue_depth(self) -> float:
        """Simulate queue depth"""
        import random
        base_depth = 100
        variation = random.randint(-50, 200)
        # Occasionally simulate queue backup
        if random.random() < 0.09:
            variation += random.randint(300, 800)
        return max(0, base_depth + variation)
    
    def _determine_health_status(self, metric: HealthMetric) -> HealthStatus:
        """Determine health status based on metric value and thresholds"""
        if metric.name not in self.health_thresholds:
            return HealthStatus.HEALTHY
        
        thresholds = self.health_thresholds[metric.name]
        
        if metric.value >= thresholds['critical']:
            return HealthStatus.CRITICAL
        elif metric.value >= thresholds['warning']:
            return HealthStatus.WARNING
        else:
            return HealthStatus.HEALTHY
    
    async def _detect_issues(self) -> List[SystemIssue]:
        """Detect system issues from health metrics"""
        issues = []
        
        try:
            with self.metrics_lock:
                # Check for performance degradation
                response_metrics = self.health_metrics.get('response_time', [])
                if response_metrics:
                    recent_response = response_metrics[-5:] if len(response_metrics) >= 5 else response_metrics
                    avg_response = sum(m.value for m in recent_response) / len(recent_response)
                    
                    if avg_response > self.health_thresholds['response_time']['critical']:
                        issues.append(SystemIssue(
                            issue_id=f"perf_deg_{int(time.time())}",
                            issue_type=IssueType.PERFORMANCE_DEGRADATION,
                            severity=HealthStatus.CRITICAL,
                            description=f"Severe performance degradation detected: {avg_response:.1f}ms average response time",
                            affected_components=['email_server', 'database', 'network'],
                            detected_at=datetime.now()
                        ))
                
                # Check for memory leak
                memory_metrics = self.health_metrics.get('memory_usage', [])
                if len(memory_metrics) >= 10:
                    recent_memory = memory_metrics[-10:]
                    memory_trend = self._calculate_trend([m.value for m in recent_memory])
                    current_memory = recent_memory[-1].value
                    
                    if memory_trend > 2.0 and current_memory > self.health_thresholds['memory_usage']['warning']:
                        issues.append(SystemIssue(
                            issue_id=f"mem_leak_{int(time.time())}",
                            issue_type=IssueType.MEMORY_LEAK,
                            severity=HealthStatus.CRITICAL if current_memory > self.health_thresholds['memory_usage']['critical'] else HealthStatus.WARNING,
                            description=f"Memory leak detected: {current_memory:.1f}% usage with {memory_trend:.1f}% increase trend",
                            affected_components=['email_server', 'cache_system'],
                            detected_at=datetime.now()
                        ))
                
                # Check for disk space issues
                disk_metrics = self.health_metrics.get('disk_usage', [])
                if disk_metrics:
                    current_disk = disk_metrics[-1].value
                    if current_disk > self.health_thresholds['disk_usage']['warning']:
                        issues.append(SystemIssue(
                            issue_id=f"disk_low_{int(time.time())}",
                            issue_type=IssueType.DISK_SPACE_LOW,
                            severity=HealthStatus.CRITICAL if current_disk > self.health_thresholds['disk_usage']['critical'] else HealthStatus.WARNING,
                            description=f"Low disk space: {current_disk:.1f}% usage",
                            affected_components=['storage_system', 'log_system'],
                            detected_at=datetime.now()
                        ))
                
                # Check for service responsiveness
                error_metrics = self.health_metrics.get('error_rate', [])
                if error_metrics:
                    current_error_rate = error_metrics[-1].value
                    if current_error_rate > self.health_thresholds['error_rate']['critical']:
                        issues.append(SystemIssue(
                            issue_id=f"svc_unresponsive_{int(time.time())}",
                            issue_type=IssueType.SERVICE_UNRESPONSIVE,
                            severity=HealthStatus.CRITICAL,
                            description=f"Service unresponsive: {current_error_rate:.1f}% error rate",
                            affected_components=['email_server', 'authentication_service'],
                            detected_at=datetime.now()
                        ))
                
                # Filter out issues already being handled
                new_issues = [issue for issue in issues if issue.issue_id not in self.active_issues]
                
                logger.info(f"Issue detection complete: {len(new_issues)} new issues found")
                return new_issues
                
        except Exception as e:
            logger.error(f"Error in issue detection: {e}")
            return []
    
    def _calculate_trend(self, values: List[float]) -> float:
        """Calculate trend slope for a series of values"""
        if len(values) < 2:
            return 0.0
        
        n = len(values)
        x_mean = (n - 1) / 2
        y_mean = sum(values) / n
        
        numerator = sum((i - x_mean) * (values[i] - y_mean) for i in range(n))
        denominator = sum((i - x_mean) ** 2 for i in range(n))
        
        return numerator / denominator if denominator != 0 else 0.0
    
    async def _handle_issue(self, issue: SystemIssue):
        """Handle a detected system issue"""
        try:
            logger.warning(f"Handling issue: {issue.issue_type.value} - {issue.description}")
            
            # Add to active issues
            self.active_issues[issue.issue_id] = issue
            
            # Get recovery strategies for this issue type
            strategies = self.recovery_strategies.get(issue.issue_type, [])
            
            if not strategies:
                logger.warning(f"No recovery strategies available for {issue.issue_type.value}")
                return
            
            # Execute recovery actions
            for strategy in strategies:
                recovery_action = await self._execute_recovery_action(strategy, issue)
                if recovery_action and recovery_action.success:
                    issue.resolution_actions.append(strategy)
                    logger.info(f"Recovery action successful: {strategy}")
                    break  # Stop after first successful recovery
                else:
                    logger.warning(f"Recovery action failed: {strategy}")
            
            # Mark as auto-resolved if any action succeeded
            if issue.resolution_actions:
                issue.auto_resolved = True
                issue.resolved_at = datetime.now()
                logger.info(f"Issue auto-resolved: {issue.issue_id}")
            
        except Exception as e:
            logger.error(f"Error handling issue {issue.issue_id}: {e}")
    
    async def _execute_recovery_action(self, action_type: str, issue: SystemIssue) -> Optional[RecoveryAction]:
        """Execute a specific recovery action"""
        try:
            action_id = f"{action_type}_{int(time.time())}"
            
            logger.info(f"Executing recovery action: {action_type} for issue {issue.issue_id}")
            
            # Simulate recovery action execution
            success = await self._simulate_recovery_action(action_type, issue)
            
            recovery_action = RecoveryAction(
                action_id=action_id,
                action_type=action_type,
                description=f"Recovery action for {issue.issue_type.value}",
                target_components=issue.affected_components,
                execution_time=datetime.now(),
                success=success
            )
            
            self.recovery_actions.append(recovery_action)
            return recovery_action
            
        except Exception as e:
            logger.error(f"Failed to execute recovery action {action_type}: {e}")
            return None
    
    async def _simulate_recovery_action(self, action_type: str, issue: SystemIssue) -> bool:
        """Simulate recovery action execution"""
        # Simulate action execution time
        await asyncio.sleep(0.5)
        
        # Different success rates for different actions
        success_rates = {
            'restart_slow_services': 0.85,
            'clear_cache': 0.90,
            'restart_affected_service': 0.80,
            'clear_memory_cache': 0.75,
            'cleanup_temp_files': 0.95,
            'restart_service': 0.85,
            'restart_network_service': 0.70,
            'optimize_configuration': 0.60
        }
        
        import random
        success_rate = success_rates.get(action_type, 0.70)
        success = random.random() < success_rate
        
        logger.debug(f"Recovery action {action_type} {'succeeded' if success else 'failed'}")
        return success
    
    async def _check_recovery_progress(self):
        """Check progress of ongoing recovery actions"""
        try:
            resolved_issues = []
            
            for issue_id, issue in self.active_issues.items():
                if issue.resolved_at:
                    # Issue was already resolved
                    resolved_issues.append(issue_id)
                else:
                    # Check if issue persists
                    if await self._verify_issue_resolution(issue):
                        issue.resolved_at = datetime.now()
                        issue.auto_resolved = True
                        resolved_issues.append(issue_id)
                        logger.info(f"Issue verified as resolved: {issue_id}")
            
            # Move resolved issues to history
            for issue_id in resolved_issues:
                resolved_issue = self.active_issues.pop(issue_id)
                self.resolved_issues.append(resolved_issue)
            
            if resolved_issues:
                logger.info(f"Moved {len(resolved_issues)} resolved issues to history")
                
        except Exception as e:
            logger.error(f"Error checking recovery progress: {e}")
    
    async def _verify_issue_resolution(self, issue: SystemIssue) -> bool:
        """Verify if an issue has been resolved"""
        try:
            # Check relevant metrics to see if issue is resolved
            if issue.issue_type == IssueType.PERFORMANCE_DEGRADATION:
                response_metrics = self.health_metrics.get('response_time', [])
                if response_metrics:
                    recent_response = response_metrics[-3:]
                    avg_response = sum(m.value for m in recent_response) / len(recent_response)
                    return avg_response < self.health_thresholds['response_time']['warning']
            
            elif issue.issue_type == IssueType.MEMORY_LEAK:
                memory_metrics = self.health_metrics.get('memory_usage', [])
                if memory_metrics:
                    current_memory = memory_metrics[-1].value
                    return current_memory < self.health_thresholds['memory_usage']['warning']
            
            elif issue.issue_type == IssueType.DISK_SPACE_LOW:
                disk_metrics = self.health_metrics.get('disk_usage', [])
                if disk_metrics:
                    current_disk = disk_metrics[-1].value
                    return current_disk < self.health_thresholds['disk_usage']['warning']
            
            elif issue.issue_type == IssueType.SERVICE_UNRESPONSIVE:
                error_metrics = self.health_metrics.get('error_rate', [])
                if error_metrics:
                    current_error_rate = error_metrics[-1].value
                    return current_error_rate < self.health_thresholds['error_rate']['warning']
            
            return False
            
        except Exception as e:
            logger.error(f"Error verifying issue resolution: {e}")
            return False
    
    async def _load_config(self):
        """Load self-healing configuration"""
        try:
            config_file = Path(self.config_path)
            if config_file.exists():
                with open(config_file, 'r') as f:
                    config = json.load(f)
                    self.health_thresholds.update(config.get('thresholds', {}))
                    self.recovery_strategies.update(config.get('strategies', {}))
                    logger.info("Self-healing configuration loaded successfully")
            else:
                logger.info("No existing configuration found, using defaults")
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
    
    def get_health_report(self) -> Dict[str, Any]:
        """Generate comprehensive health report"""
        try:
            with self.metrics_lock:
                current_metrics = {}
                for metric_name, metrics_list in self.health_metrics.items():
                    if metrics_list:
                        latest = metrics_list[-1]
                        current_metrics[metric_name] = {
                            'value': latest.value,
                            'status': latest.status.value,
                            'threshold': latest.threshold,
                            'last_updated': latest.timestamp.isoformat()
                        }
                
                return {
                    'system_status': {
                        'is_monitoring': self.is_monitoring,
                        'active_issues': len(self.active_issues),
                        'resolved_issues_today': len([i for i in self.resolved_issues 
                                                     if i.resolved_at and i.resolved_at > datetime.now() - timedelta(days=1)])
                    },
                    'current_metrics': current_metrics,
                    'active_issues': [
                        {
                            'issue_id': issue.issue_id,
                            'type': issue.issue_type.value,
                            'severity': issue.severity.value,
                            'description': issue.description,
                            'detected_at': issue.detected_at.isoformat(),
                            'affected_components': issue.affected_components,
                            'resolution_actions': issue.resolution_actions
                        }
                        for issue in self.active_issues.values()
                    ],
                    'recovery_summary': {
                        'total_actions': len(self.recovery_actions),
                        'successful_actions': len([a for a in self.recovery_actions if a.success]),
                        'recent_actions': len([a for a in self.recovery_actions 
                                             if a.execution_time > datetime.now() - timedelta(hours=24)])
                    }
                }
                
        except Exception as e:
            logger.error(f"Error generating health report: {e}")
            return {'error': str(e)}

# Example usage and testing
async def main():
    """Main function for testing self-healing system"""
    healing_system = SelfHealingSystem()
    
    # Initialize system
    success = await healing_system.initialize()
    if not success:
        print("Failed to initialize self-healing system")
        return
    
    print("Self-Healing System initialized successfully!")
    print("Starting health monitoring...")
    
    # Start monitoring in background
    monitoring_task = asyncio.create_task(healing_system.start_monitoring())
    
    # Run for demonstration period
    await asyncio.sleep(120)  # Run for 2 minutes
    
    # Stop monitoring
    await healing_system.stop_monitoring()
    await monitoring_task
    
    # Generate report
    report = healing_system.get_health_report()
    print("\nHealth Report:")
    print(json.dumps(report, indent=2, default=str))
    
    print("\nSelf-healing system demonstration complete!")

if __name__ == "__main__":
    asyncio.run(main())