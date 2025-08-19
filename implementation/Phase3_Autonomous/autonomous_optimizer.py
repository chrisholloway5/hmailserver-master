"""
Autonomous Optimizer - Phase 3 Core Component
==============================================

This module implements autonomous performance optimization that continuously
monitors system performance and automatically adjusts configurations for
optimal operation without human intervention.

Features:
- Real-time performance monitoring
- AI-driven configuration optimization  
- Autonomous resource allocation
- Predictive performance tuning
- Self-learning optimization algorithms
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import statistics
import psutil
import threading
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetrics:
    """Performance metrics container"""
    timestamp: datetime
    cpu_usage: float
    memory_usage: float
    disk_io: float
    network_io: float
    email_throughput: int
    response_time: float
    error_rate: float
    queue_depth: int

@dataclass
class OptimizationAction:
    """Optimization action container"""
    action_type: str
    parameter: str
    old_value: Any
    new_value: Any
    expected_improvement: float
    confidence: float
    timestamp: datetime

class AutonomousOptimizer:
    """
    Autonomous Performance Optimizer
    
    Continuously monitors system performance and automatically optimizes
    configuration parameters using AI-driven algorithms.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the autonomous optimizer"""
        self.config_path = config_path or "config/autonomous_optimizer.json"
        self.is_running = False
        self.metrics_history: List[PerformanceMetrics] = []
        self.optimization_history: List[OptimizationAction] = []
        self.current_config = {}
        self.baseline_metrics = None
        self.learning_mode = True
        self.optimization_interval = 60  # seconds
        self.metrics_lock = threading.Lock()
        
        # Performance thresholds
        self.performance_thresholds = {
            'cpu_usage': 80.0,
            'memory_usage': 85.0,
            'response_time': 500.0,  # milliseconds
            'error_rate': 1.0,  # percentage
            'queue_depth': 100
        }
        
        # Optimization parameters
        self.optimization_parameters = {
            'max_connections': {'min': 100, 'max': 10000, 'current': 1000},
            'thread_pool_size': {'min': 10, 'max': 200, 'current': 50},
            'cache_size_mb': {'min': 64, 'max': 2048, 'current': 256},
            'timeout_seconds': {'min': 30, 'max': 300, 'current': 120},
            'batch_size': {'min': 10, 'max': 500, 'current': 100}
        }
        
        logger.info("Autonomous Optimizer initialized")
    
    async def initialize(self):
        """Initialize the optimizer with baseline measurements"""
        try:
            # Load existing configuration if available
            await self._load_config()
            
            # Establish baseline performance metrics
            logger.info("Establishing baseline performance metrics...")
            baseline_samples = []
            for _ in range(10):
                metrics = await self._collect_metrics()
                baseline_samples.append(metrics)
                await asyncio.sleep(5)
            
            self.baseline_metrics = self._calculate_baseline(baseline_samples)
            logger.info(f"Baseline established: CPU={self.baseline_metrics.cpu_usage:.1f}%, "
                       f"Memory={self.baseline_metrics.memory_usage:.1f}%, "
                       f"Response={self.baseline_metrics.response_time:.1f}ms")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize autonomous optimizer: {e}")
            return False
    
    async def start_optimization(self):
        """Start the autonomous optimization process"""
        if self.is_running:
            logger.warning("Optimizer is already running")
            return
        
        self.is_running = True
        logger.info("Starting autonomous optimization process...")
        
        try:
            while self.is_running:
                # Collect current performance metrics
                current_metrics = await self._collect_metrics()
                
                with self.metrics_lock:
                    self.metrics_history.append(current_metrics)
                    
                    # Keep only last 1000 metrics to prevent memory growth
                    if len(self.metrics_history) > 1000:
                        self.metrics_history = self.metrics_history[-1000:]
                
                # Analyze performance and determine optimizations
                if len(self.metrics_history) >= 10:  # Need minimum history
                    optimizations = await self._analyze_and_optimize(current_metrics)
                    
                    for optimization in optimizations:
                        await self._apply_optimization(optimization)
                
                # Wait for next optimization cycle
                await asyncio.sleep(self.optimization_interval)
                
        except Exception as e:
            logger.error(f"Error in optimization loop: {e}")
        finally:
            self.is_running = False
            logger.info("Autonomous optimization stopped")
    
    async def stop_optimization(self):
        """Stop the autonomous optimization process"""
        self.is_running = False
        logger.info("Stopping autonomous optimization...")
    
    async def _collect_metrics(self) -> PerformanceMetrics:
        """Collect current system performance metrics"""
        try:
            # System metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk_io = sum([d.read_bytes + d.write_bytes for d in psutil.disk_io_counters(perdisk=True).values()])
            network_io = sum([n.bytes_sent + n.bytes_recv for n in psutil.net_io_counters(pernic=True).values()])
            
            # Simulated email server metrics (in production, these would come from actual server)
            email_throughput = self._simulate_email_throughput()
            response_time = self._simulate_response_time()
            error_rate = self._simulate_error_rate()
            queue_depth = self._simulate_queue_depth()
            
            return PerformanceMetrics(
                timestamp=datetime.now(),
                cpu_usage=cpu_percent,
                memory_usage=memory.percent,
                disk_io=disk_io,
                network_io=network_io,
                email_throughput=email_throughput,
                response_time=response_time,
                error_rate=error_rate,
                queue_depth=queue_depth
            )
            
        except Exception as e:
            logger.error(f"Failed to collect metrics: {e}")
            # Return default metrics if collection fails
            return PerformanceMetrics(
                timestamp=datetime.now(),
                cpu_usage=0.0, memory_usage=0.0, disk_io=0, network_io=0,
                email_throughput=0, response_time=1000.0, error_rate=5.0, queue_depth=0
            )
    
    def _simulate_email_throughput(self) -> int:
        """Simulate email throughput (emails per minute)"""
        import random
        base_throughput = 1000
        variation = random.randint(-200, 300)
        return max(0, base_throughput + variation)
    
    def _simulate_response_time(self) -> float:
        """Simulate email response time in milliseconds"""
        import random
        base_time = 150.0
        variation = random.uniform(-50, 100)
        return max(10.0, base_time + variation)
    
    def _simulate_error_rate(self) -> float:
        """Simulate error rate as percentage"""
        import random
        base_rate = 0.5
        variation = random.uniform(-0.3, 2.0)
        return max(0.0, base_rate + variation)
    
    def _simulate_queue_depth(self) -> int:
        """Simulate email queue depth"""
        import random
        base_depth = 50
        variation = random.randint(-30, 80)
        return max(0, base_depth + variation)
    
    def _calculate_baseline(self, samples: List[PerformanceMetrics]) -> PerformanceMetrics:
        """Calculate baseline metrics from samples"""
        if not samples:
            raise ValueError("No samples provided for baseline calculation")
        
        return PerformanceMetrics(
            timestamp=datetime.now(),
            cpu_usage=statistics.mean([s.cpu_usage for s in samples]),
            memory_usage=statistics.mean([s.memory_usage for s in samples]),
            disk_io=statistics.mean([s.disk_io for s in samples]),
            network_io=statistics.mean([s.network_io for s in samples]),
            email_throughput=int(statistics.mean([s.email_throughput for s in samples])),
            response_time=statistics.mean([s.response_time for s in samples]),
            error_rate=statistics.mean([s.error_rate for s in samples]),
            queue_depth=int(statistics.mean([s.queue_depth for s in samples]))
        )
    
    async def _analyze_and_optimize(self, current_metrics: PerformanceMetrics) -> List[OptimizationAction]:
        """Analyze performance and determine optimization actions"""
        optimizations = []
        
        try:
            # Get recent metrics for trend analysis
            recent_metrics = self.metrics_history[-10:] if len(self.metrics_history) >= 10 else self.metrics_history
            
            # CPU optimization
            if current_metrics.cpu_usage > self.performance_thresholds['cpu_usage']:
                cpu_trend = statistics.mean([m.cpu_usage for m in recent_metrics[-5:]])
                if cpu_trend > self.baseline_metrics.cpu_usage * 1.2:
                    # High CPU usage - optimize thread pool
                    optimization = await self._optimize_thread_pool(current_metrics)
                    if optimization:
                        optimizations.append(optimization)
            
            # Memory optimization
            if current_metrics.memory_usage > self.performance_thresholds['memory_usage']:
                memory_trend = statistics.mean([m.memory_usage for m in recent_metrics[-5:]])
                if memory_trend > self.baseline_metrics.memory_usage * 1.2:
                    # High memory usage - optimize cache size
                    optimization = await self._optimize_cache_size(current_metrics)
                    if optimization:
                        optimizations.append(optimization)
            
            # Response time optimization
            if current_metrics.response_time > self.performance_thresholds['response_time']:
                response_trend = statistics.mean([m.response_time for m in recent_metrics[-5:]])
                if response_trend > self.baseline_metrics.response_time * 1.3:
                    # Slow response time - optimize connection handling
                    optimization = await self._optimize_connections(current_metrics)
                    if optimization:
                        optimizations.append(optimization)
            
            # Queue depth optimization
            if current_metrics.queue_depth > self.performance_thresholds['queue_depth']:
                queue_trend = statistics.mean([m.queue_depth for m in recent_metrics[-5:]])
                if queue_trend > self.baseline_metrics.queue_depth * 1.5:
                    # High queue depth - optimize batch processing
                    optimization = await self._optimize_batch_size(current_metrics)
                    if optimization:
                        optimizations.append(optimization)
            
            logger.info(f"Analysis complete: {len(optimizations)} optimizations identified")
            return optimizations
            
        except Exception as e:
            logger.error(f"Error in performance analysis: {e}")
            return []
    
    async def _optimize_thread_pool(self, metrics: PerformanceMetrics) -> Optional[OptimizationAction]:
        """Optimize thread pool size for CPU performance"""
        current_size = self.optimization_parameters['thread_pool_size']['current']
        max_size = self.optimization_parameters['thread_pool_size']['max']
        
        # Increase thread pool if CPU usage is high but we have headroom
        if current_size < max_size and metrics.cpu_usage > 70:
            new_size = min(max_size, int(current_size * 1.2))
            confidence = min(0.9, (metrics.cpu_usage - 70) / 30)
            
            return OptimizationAction(
                action_type='thread_pool_optimization',
                parameter='thread_pool_size',
                old_value=current_size,
                new_value=new_size,
                expected_improvement=15.0,
                confidence=confidence,
                timestamp=datetime.now()
            )
        
        return None
    
    async def _optimize_cache_size(self, metrics: PerformanceMetrics) -> Optional[OptimizationAction]:
        """Optimize cache size for memory performance"""
        current_size = self.optimization_parameters['cache_size_mb']['current']
        max_size = self.optimization_parameters['cache_size_mb']['max']
        min_size = self.optimization_parameters['cache_size_mb']['min']
        
        if metrics.memory_usage > 80:
            # Reduce cache size if memory usage is high
            new_size = max(min_size, int(current_size * 0.8))
            confidence = min(0.8, (metrics.memory_usage - 80) / 20)
            
            return OptimizationAction(
                action_type='cache_optimization',
                parameter='cache_size_mb',
                old_value=current_size,
                new_value=new_size,
                expected_improvement=10.0,
                confidence=confidence,
                timestamp=datetime.now()
            )
        
        return None
    
    async def _optimize_connections(self, metrics: PerformanceMetrics) -> Optional[OptimizationAction]:
        """Optimize connection handling for response time"""
        current_connections = self.optimization_parameters['max_connections']['current']
        max_connections = self.optimization_parameters['max_connections']['max']
        
        if metrics.response_time > 400 and current_connections < max_connections:
            # Increase max connections if response time is slow
            new_connections = min(max_connections, int(current_connections * 1.3))
            confidence = min(0.85, (metrics.response_time - 400) / 100)
            
            return OptimizationAction(
                action_type='connection_optimization',
                parameter='max_connections',
                old_value=current_connections,
                new_value=new_connections,
                expected_improvement=20.0,
                confidence=confidence,
                timestamp=datetime.now()
            )
        
        return None
    
    async def _optimize_batch_size(self, metrics: PerformanceMetrics) -> Optional[OptimizationAction]:
        """Optimize batch processing for queue management"""
        current_batch = self.optimization_parameters['batch_size']['current']
        max_batch = self.optimization_parameters['batch_size']['max']
        
        if metrics.queue_depth > 80 and current_batch < max_batch:
            # Increase batch size if queue is backing up
            new_batch = min(max_batch, int(current_batch * 1.4))
            confidence = min(0.9, (metrics.queue_depth - 80) / 50)
            
            return OptimizationAction(
                action_type='batch_optimization',
                parameter='batch_size',
                old_value=current_batch,
                new_value=new_batch,
                expected_improvement=25.0,
                confidence=confidence,
                timestamp=datetime.now()
            )
        
        return None
    
    async def _apply_optimization(self, optimization: OptimizationAction):
        """Apply an optimization action"""
        try:
            logger.info(f"Applying optimization: {optimization.action_type} - "
                       f"{optimization.parameter}: {optimization.old_value} → {optimization.new_value} "
                       f"(confidence: {optimization.confidence:.2f})")
            
            # Update parameter value
            if optimization.parameter in self.optimization_parameters:
                self.optimization_parameters[optimization.parameter]['current'] = optimization.new_value
            
            # Record the optimization
            self.optimization_history.append(optimization)
            
            # In production, this would trigger actual system configuration changes
            await self._simulate_config_update(optimization)
            
            logger.info(f"Optimization applied successfully: {optimization.parameter}")
            
        except Exception as e:
            logger.error(f"Failed to apply optimization {optimization.action_type}: {e}")
    
    async def _simulate_config_update(self, optimization: OptimizationAction):
        """Simulate configuration update (placeholder for actual implementation)"""
        # Simulate configuration update delay
        await asyncio.sleep(0.1)
        
        # In production, this would:
        # 1. Update hMailServer configuration files
        # 2. Trigger configuration reload
        # 3. Monitor impact of changes
        # 4. Rollback if performance degrades
        
        logger.debug(f"Configuration updated: {optimization.parameter} = {optimization.new_value}")
    
    async def _load_config(self):
        """Load optimizer configuration"""
        try:
            config_file = Path(self.config_path)
            if config_file.exists():
                with open(config_file, 'r') as f:
                    config = json.load(f)
                    self.optimization_parameters.update(config.get('parameters', {}))
                    self.performance_thresholds.update(config.get('thresholds', {}))
                    logger.info("Configuration loaded successfully")
            else:
                logger.info("No existing configuration found, using defaults")
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
    
    async def save_config(self):
        """Save current optimizer configuration"""
        try:
            config = {
                'parameters': self.optimization_parameters,
                'thresholds': self.performance_thresholds,
                'last_updated': datetime.now().isoformat()
            }
            
            config_file = Path(self.config_path)
            config_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
            
            logger.info("Configuration saved successfully")
            
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Generate performance report"""
        if not self.metrics_history:
            return {"error": "No metrics available"}
        
        recent_metrics = self.metrics_history[-10:] if len(self.metrics_history) >= 10 else self.metrics_history
        
        return {
            "current_status": {
                "is_optimizing": self.is_running,
                "metrics_collected": len(self.metrics_history),
                "optimizations_applied": len(self.optimization_history)
            },
            "performance_summary": {
                "avg_cpu_usage": statistics.mean([m.cpu_usage for m in recent_metrics]),
                "avg_memory_usage": statistics.mean([m.memory_usage for m in recent_metrics]),
                "avg_response_time": statistics.mean([m.response_time for m in recent_metrics]),
                "avg_throughput": statistics.mean([m.email_throughput for m in recent_metrics]),
                "avg_error_rate": statistics.mean([m.error_rate for m in recent_metrics])
            },
            "optimization_summary": {
                "recent_optimizations": len([o for o in self.optimization_history 
                                           if o.timestamp > datetime.now() - timedelta(hours=24)]),
                "avg_confidence": statistics.mean([o.confidence for o in self.optimization_history]) 
                                if self.optimization_history else 0.0
            },
            "current_parameters": self.optimization_parameters
        }

# Example usage and testing
async def main():
    """Main function for testing autonomous optimizer"""
    optimizer = AutonomousOptimizer()
    
    # Initialize optimizer
    success = await optimizer.initialize()
    if not success:
        print("Failed to initialize optimizer")
        return
    
    print("Autonomous Optimizer initialized successfully!")
    print("Starting optimization process...")
    
    # Start optimization in background
    optimization_task = asyncio.create_task(optimizer.start_optimization())
    
    # Run for demonstration period
    await asyncio.sleep(180)  # Run for 3 minutes
    
    # Stop optimization
    await optimizer.stop_optimization()
    await optimization_task
    
    # Generate report
    report = optimizer.get_performance_report()
    print("\nPerformance Report:")
    print(json.dumps(report, indent=2, default=str))
    
    # Save configuration
    await optimizer.save_config()
    print("\nAutonomous optimization demonstration complete!")

if __name__ == "__main__":
    asyncio.run(main())