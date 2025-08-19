"""
Predictive Scaler - Phase 3 Core Component
==========================================

This module implements predictive scaling capabilities that use machine learning
to anticipate email traffic patterns and automatically scale resources before
demand peaks occur.

Features:
- Email traffic prediction
- Automatic resource scaling
- Load forecasting
- Performance optimization
- Cost-aware scaling decisions
- Multi-dimensional scaling
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import statistics
import threading
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ScalingDirection(Enum):
    """Scaling direction"""
    SCALE_UP = "scale_up"
    SCALE_DOWN = "scale_down"
    MAINTAIN = "maintain"

class ResourceType(Enum):
    """Resource types for scaling"""
    CPU = "cpu"
    MEMORY = "memory"
    STORAGE = "storage"
    NETWORK = "network"
    CONNECTIONS = "connections"
    THREADS = "threads"

@dataclass
class TrafficPattern:
    """Email traffic pattern data"""
    timestamp: datetime
    email_volume: int
    peak_concurrent_users: int
    average_email_size: float
    connection_count: int
    cpu_usage: float
    memory_usage: float
    response_time: float

@dataclass
class ScalingPrediction:
    """Scaling prediction result"""
    resource_type: ResourceType
    current_value: float
    predicted_demand: float
    recommended_action: ScalingDirection
    confidence: float
    time_to_scale: timedelta
    reasoning: str
    cost_impact: float

@dataclass
class ScalingAction:
    """Scaling action record"""
    action_id: str
    resource_type: ResourceType
    direction: ScalingDirection
    from_value: float
    to_value: float
    executed_at: datetime
    success: bool
    performance_impact: Optional[float] = None

class PredictiveScaler:
    """
    Predictive Scaling System
    
    Uses machine learning to predict email traffic patterns and automatically
    scale resources to maintain optimal performance while minimizing costs.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize predictive scaler"""
        self.config_path = config_path or "config/predictive_scaler.json"
        self.is_active = False
        self.traffic_history: List[TrafficPattern] = []
        self.scaling_history: List[ScalingAction] = []
        self.current_resources: Dict[ResourceType, float] = {}
        self.prediction_interval = 300  # 5 minutes
        self.scaling_lock = threading.Lock()
        
        # Resource limits and thresholds
        self.resource_limits = {
            ResourceType.CPU: {'min': 1, 'max': 64, 'current': 8},
            ResourceType.MEMORY: {'min': 2048, 'max': 131072, 'current': 16384},  # MB
            ResourceType.STORAGE: {'min': 100, 'max': 10240, 'current': 1024},  # GB
            ResourceType.NETWORK: {'min': 100, 'max': 10000, 'current': 1000},  # Mbps
            ResourceType.CONNECTIONS: {'min': 100, 'max': 50000, 'current': 5000},
            ResourceType.THREADS: {'min': 10, 'max': 1000, 'current': 100}
        }
        
        # Scaling thresholds
        self.scaling_thresholds = {
            'cpu_usage': {'scale_up': 75.0, 'scale_down': 30.0},
            'memory_usage': {'scale_up': 80.0, 'scale_down': 40.0},
            'response_time': {'scale_up': 500.0, 'scale_down': 100.0},
            'connection_utilization': {'scale_up': 85.0, 'scale_down': 50.0}
        }
        
        # Cost factors for different resources
        self.resource_costs = {
            ResourceType.CPU: 0.10,  # $ per core per hour
            ResourceType.MEMORY: 0.02,  # $ per GB per hour
            ResourceType.STORAGE: 0.01,  # $ per GB per hour
            ResourceType.NETWORK: 0.05,  # $ per Mbps per hour
            ResourceType.CONNECTIONS: 0.001,  # $ per connection per hour
            ResourceType.THREADS: 0.005   # $ per thread per hour
        }
        
        # Initialize current resources
        for resource_type in ResourceType:
            self.current_resources[resource_type] = self.resource_limits[resource_type]['current']
        
        logger.info("Predictive Scaler initialized")
    
    async def initialize(self):
        """Initialize the predictive scaler"""
        try:
            await self._load_config()
            await self._load_historical_data()
            
            logger.info("Predictive scaler initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize predictive scaler: {e}")
            return False
    
    async def start_prediction(self):
        """Start predictive scaling process"""
        if self.is_active:
            logger.warning("Predictive scaling is already active")
            return
        
        self.is_active = True
        logger.info("Starting predictive scaling...")
        
        try:
            while self.is_active:
                # Collect current traffic data
                current_pattern = await self._collect_traffic_data()
                
                with self.scaling_lock:
                    self.traffic_history.append(current_pattern)
                    
                    # Keep only last 1000 patterns
                    if len(self.traffic_history) > 1000:
                        self.traffic_history = self.traffic_history[-1000:]
                
                # Generate predictions if we have enough history
                if len(self.traffic_history) >= 20:
                    predictions = await self._generate_predictions(current_pattern)
                    
                    # Execute scaling actions based on predictions
                    for prediction in predictions:
                        if prediction.recommended_action != ScalingDirection.MAINTAIN:
                            await self._execute_scaling_action(prediction)
                
                # Wait for next prediction cycle
                await asyncio.sleep(self.prediction_interval)
                
        except Exception as e:
            logger.error(f"Error in prediction loop: {e}")
        finally:
            self.is_active = False
            logger.info("Predictive scaling stopped")
    
    async def stop_prediction(self):
        """Stop predictive scaling"""
        self.is_active = False
        logger.info("Stopping predictive scaling...")
    
    async def _collect_traffic_data(self) -> TrafficPattern:
        """Collect current email traffic and system metrics"""
        try:
            # Simulate traffic data collection (in production, this would come from actual monitoring)
            current_time = datetime.now()
            
            # Generate realistic traffic patterns based on time of day
            hour = current_time.hour
            day_of_week = current_time.weekday()
            
            # Base traffic varies by time of day
            base_volume = self._get_base_volume_for_time(hour, day_of_week)
            
            pattern = TrafficPattern(
                timestamp=current_time,
                email_volume=self._simulate_email_volume(base_volume),
                peak_concurrent_users=self._simulate_concurrent_users(base_volume),
                average_email_size=self._simulate_email_size(),
                connection_count=self._simulate_connection_count(),
                cpu_usage=self._simulate_cpu_usage(),
                memory_usage=self._simulate_memory_usage(),
                response_time=self._simulate_response_time()
            )
            
            logger.debug(f"Collected traffic data: volume={pattern.email_volume}, users={pattern.peak_concurrent_users}")
            return pattern
            
        except Exception as e:
            logger.error(f"Failed to collect traffic data: {e}")
            # Return default pattern if collection fails
            return TrafficPattern(
                timestamp=datetime.now(),
                email_volume=1000, peak_concurrent_users=100, average_email_size=1.5,
                connection_count=500, cpu_usage=50.0, memory_usage=60.0, response_time=200.0
            )
    
    def _get_base_volume_for_time(self, hour: int, day_of_week: int) -> int:
        """Get base email volume for specific time"""
        # Weekend has lower traffic
        weekend_factor = 0.3 if day_of_week >= 5 else 1.0
        
        # Traffic patterns throughout the day
        if 0 <= hour < 6:
            time_factor = 0.1  # Very low traffic
        elif 6 <= hour < 9:
            time_factor = 0.8  # Morning ramp-up
        elif 9 <= hour < 12:
            time_factor = 1.0  # Peak morning
        elif 12 <= hour < 14:
            time_factor = 0.7  # Lunch dip
        elif 14 <= hour < 17:
            time_factor = 1.0  # Peak afternoon
        elif 17 <= hour < 20:
            time_factor = 0.6  # Evening decline
        else:
            time_factor = 0.2  # Night
        
        base_volume = int(5000 * time_factor * weekend_factor)
        return base_volume
    
    def _simulate_email_volume(self, base_volume: int) -> int:
        """Simulate email volume with realistic variation"""
        import random
        variation = random.uniform(0.8, 1.3)
        spike_chance = random.random()
        
        # Occasional traffic spikes
        if spike_chance < 0.05:  # 5% chance of spike
            variation *= random.uniform(2.0, 5.0)
        elif spike_chance < 0.1:  # 5% chance of moderate increase
            variation *= random.uniform(1.5, 2.0)
        
        return max(0, int(base_volume * variation))
    
    def _simulate_concurrent_users(self, base_volume: int) -> int:
        """Simulate concurrent users based on email volume"""
        import random
        # Roughly 1 user per 50 emails
        base_users = base_volume // 50
        variation = random.uniform(0.7, 1.4)
        return max(1, int(base_users * variation))
    
    def _simulate_email_size(self) -> float:
        """Simulate average email size in MB"""
        import random
        # Typical email size between 0.5MB and 5MB
        return random.uniform(0.5, 5.0)
    
    def _simulate_connection_count(self) -> int:
        """Simulate active connection count"""
        import random
        base_connections = 1000
        variation = random.uniform(0.6, 1.8)
        return max(10, int(base_connections * variation))
    
    def _simulate_cpu_usage(self) -> float:
        """Simulate CPU usage percentage"""
        import random
        base_cpu = 45.0
        variation = random.uniform(-20, 40)
        return max(0.0, min(100.0, base_cpu + variation))
    
    def _simulate_memory_usage(self) -> float:
        """Simulate memory usage percentage"""
        import random
        base_memory = 55.0
        variation = random.uniform(-15, 35)
        return max(0.0, min(100.0, base_memory + variation))
    
    def _simulate_response_time(self) -> float:
        """Simulate response time in milliseconds"""
        import random
        base_time = 150.0
        variation = random.uniform(-50, 200)
        return max(10.0, base_time + variation)
    
    async def _generate_predictions(self, current_pattern: TrafficPattern) -> List[ScalingPrediction]:
        """Generate scaling predictions based on traffic patterns"""
        predictions = []
        
        try:
            with self.scaling_lock:
                recent_patterns = self.traffic_history[-20:] if len(self.traffic_history) >= 20 else self.traffic_history
            
            # Predict CPU scaling needs
            cpu_prediction = await self._predict_cpu_scaling(current_pattern, recent_patterns)
            if cpu_prediction:
                predictions.append(cpu_prediction)
            
            # Predict memory scaling needs
            memory_prediction = await self._predict_memory_scaling(current_pattern, recent_patterns)
            if memory_prediction:
                predictions.append(memory_prediction)
            
            # Predict connection scaling needs
            connection_prediction = await self._predict_connection_scaling(current_pattern, recent_patterns)
            if connection_prediction:
                predictions.append(connection_prediction)
            
            # Predict thread scaling needs
            thread_prediction = await self._predict_thread_scaling(current_pattern, recent_patterns)
            if thread_prediction:
                predictions.append(thread_prediction)
            
            logger.info(f"Generated {len(predictions)} scaling predictions")
            return predictions
            
        except Exception as e:
            logger.error(f"Error generating predictions: {e}")
            return []
    
    async def _predict_cpu_scaling(self, current: TrafficPattern, history: List[TrafficPattern]) -> Optional[ScalingPrediction]:
        """Predict CPU scaling requirements"""
        try:
            # Calculate CPU usage trend
            cpu_values = [p.cpu_usage for p in history[-10:]]
            cpu_trend = self._calculate_trend(cpu_values)
            
            current_cpu_cores = self.current_resources[ResourceType.CPU]
            predicted_cpu_usage = current.cpu_usage + (cpu_trend * 5)  # 5-step ahead prediction
            
            # Determine scaling action
            if predicted_cpu_usage > self.scaling_thresholds['cpu_usage']['scale_up']:
                # Scale up CPU
                new_cpu_cores = min(
                    self.resource_limits[ResourceType.CPU]['max'],
                    current_cpu_cores * 1.5
                )
                
                return ScalingPrediction(
                    resource_type=ResourceType.CPU,
                    current_value=current_cpu_cores,
                    predicted_demand=predicted_cpu_usage,
                    recommended_action=ScalingDirection.SCALE_UP,
                    confidence=min(0.9, abs(cpu_trend) / 10 + 0.5),
                    time_to_scale=timedelta(minutes=2),
                    reasoning=f"CPU usage predicted to reach {predicted_cpu_usage:.1f}%, trend: {cpu_trend:.2f}%/period",
                    cost_impact=self.resource_costs[ResourceType.CPU] * (new_cpu_cores - current_cpu_cores)
                )
            
            elif predicted_cpu_usage < self.scaling_thresholds['cpu_usage']['scale_down'] and current_cpu_cores > self.resource_limits[ResourceType.CPU]['min']:
                # Scale down CPU
                new_cpu_cores = max(
                    self.resource_limits[ResourceType.CPU]['min'],
                    current_cpu_cores * 0.8
                )
                
                return ScalingPrediction(
                    resource_type=ResourceType.CPU,
                    current_value=current_cpu_cores,
                    predicted_demand=predicted_cpu_usage,
                    recommended_action=ScalingDirection.SCALE_DOWN,
                    confidence=min(0.8, abs(cpu_trend) / 10 + 0.4),
                    time_to_scale=timedelta(minutes=5),
                    reasoning=f"CPU usage predicted to drop to {predicted_cpu_usage:.1f}%, can scale down",
                    cost_impact=self.resource_costs[ResourceType.CPU] * (current_cpu_cores - new_cpu_cores)
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Error predicting CPU scaling: {e}")
            return None
    
    async def _predict_memory_scaling(self, current: TrafficPattern, history: List[TrafficPattern]) -> Optional[ScalingPrediction]:
        """Predict memory scaling requirements"""
        try:
            # Calculate memory usage trend
            memory_values = [p.memory_usage for p in history[-10:]]
            memory_trend = self._calculate_trend(memory_values)
            
            current_memory = self.current_resources[ResourceType.MEMORY]
            predicted_memory_usage = current.memory_usage + (memory_trend * 5)
            
            # Determine scaling action
            if predicted_memory_usage > self.scaling_thresholds['memory_usage']['scale_up']:
                # Scale up memory
                new_memory = min(
                    self.resource_limits[ResourceType.MEMORY]['max'],
                    current_memory * 1.3
                )
                
                return ScalingPrediction(
                    resource_type=ResourceType.MEMORY,
                    current_value=current_memory,
                    predicted_demand=predicted_memory_usage,
                    recommended_action=ScalingDirection.SCALE_UP,
                    confidence=min(0.85, abs(memory_trend) / 15 + 0.5),
                    time_to_scale=timedelta(minutes=1),
                    reasoning=f"Memory usage predicted to reach {predicted_memory_usage:.1f}%, trend: {memory_trend:.2f}%/period",
                    cost_impact=self.resource_costs[ResourceType.MEMORY] * (new_memory - current_memory) / 1024
                )
            
            elif predicted_memory_usage < self.scaling_thresholds['memory_usage']['scale_down'] and current_memory > self.resource_limits[ResourceType.MEMORY]['min']:
                # Scale down memory
                new_memory = max(
                    self.resource_limits[ResourceType.MEMORY]['min'],
                    current_memory * 0.9
                )
                
                return ScalingPrediction(
                    resource_type=ResourceType.MEMORY,
                    current_value=current_memory,
                    predicted_demand=predicted_memory_usage,
                    recommended_action=ScalingDirection.SCALE_DOWN,
                    confidence=min(0.75, abs(memory_trend) / 15 + 0.4),
                    time_to_scale=timedelta(minutes=3),
                    reasoning=f"Memory usage predicted to drop to {predicted_memory_usage:.1f}%, can scale down",
                    cost_impact=self.resource_costs[ResourceType.MEMORY] * (current_memory - new_memory) / 1024
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Error predicting memory scaling: {e}")
            return None
    
    async def _predict_connection_scaling(self, current: TrafficPattern, history: List[TrafficPattern]) -> Optional[ScalingPrediction]:
        """Predict connection pool scaling requirements"""
        try:
            # Calculate connection utilization
            current_connections = self.current_resources[ResourceType.CONNECTIONS]
            connection_utilization = (current.connection_count / current_connections) * 100
            
            # Get connection trend
            connection_values = [p.connection_count for p in history[-5:]]
            connection_trend = self._calculate_trend(connection_values)
            
            predicted_connections = current.connection_count + (connection_trend * 3)
            predicted_utilization = (predicted_connections / current_connections) * 100
            
            # Determine scaling action
            if predicted_utilization > self.scaling_thresholds['connection_utilization']['scale_up']:
                # Scale up connections
                new_connections = min(
                    self.resource_limits[ResourceType.CONNECTIONS]['max'],
                    current_connections * 1.4
                )
                
                return ScalingPrediction(
                    resource_type=ResourceType.CONNECTIONS,
                    current_value=current_connections,
                    predicted_demand=predicted_connections,
                    recommended_action=ScalingDirection.SCALE_UP,
                    confidence=min(0.8, abs(connection_trend) / 100 + 0.6),
                    time_to_scale=timedelta(seconds=30),
                    reasoning=f"Connection utilization predicted to reach {predicted_utilization:.1f}%",
                    cost_impact=self.resource_costs[ResourceType.CONNECTIONS] * (new_connections - current_connections)
                )
            
            elif predicted_utilization < self.scaling_thresholds['connection_utilization']['scale_down'] and current_connections > self.resource_limits[ResourceType.CONNECTIONS]['min']:
                # Scale down connections
                new_connections = max(
                    self.resource_limits[ResourceType.CONNECTIONS]['min'],
                    current_connections * 0.9
                )
                
                return ScalingPrediction(
                    resource_type=ResourceType.CONNECTIONS,
                    current_value=current_connections,
                    predicted_demand=predicted_connections,
                    recommended_action=ScalingDirection.SCALE_DOWN,
                    confidence=min(0.7, abs(connection_trend) / 100 + 0.5),
                    time_to_scale=timedelta(minutes=2),
                    reasoning=f"Connection utilization predicted to drop to {predicted_utilization:.1f}%",
                    cost_impact=self.resource_costs[ResourceType.CONNECTIONS] * (current_connections - new_connections)
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Error predicting connection scaling: {e}")
            return None
    
    async def _predict_thread_scaling(self, current: TrafficPattern, history: List[TrafficPattern]) -> Optional[ScalingPrediction]:
        """Predict thread pool scaling requirements"""
        try:
            # Estimate thread demand based on concurrent users and response time
            current_threads = self.current_resources[ResourceType.THREADS]
            
            # More users and slower response time = need more threads
            thread_demand_factor = (current.peak_concurrent_users / 100) * (current.response_time / 200)
            predicted_thread_demand = current_threads * thread_demand_factor
            
            # Response time trend
            response_values = [p.response_time for p in history[-5:]]
            response_trend = self._calculate_trend(response_values)
            
            # Determine scaling action
            if current.response_time > self.scaling_thresholds['response_time']['scale_up'] or response_trend > 50:
                # Scale up threads
                new_threads = min(
                    self.resource_limits[ResourceType.THREADS]['max'],
                    current_threads * 1.25
                )
                
                return ScalingPrediction(
                    resource_type=ResourceType.THREADS,
                    current_value=current_threads,
                    predicted_demand=predicted_thread_demand,
                    recommended_action=ScalingDirection.SCALE_UP,
                    confidence=min(0.75, abs(response_trend) / 100 + 0.5),
                    time_to_scale=timedelta(seconds=10),
                    reasoning=f"Response time {current.response_time:.1f}ms indicates thread bottleneck",
                    cost_impact=self.resource_costs[ResourceType.THREADS] * (new_threads - current_threads)
                )
            
            elif current.response_time < self.scaling_thresholds['response_time']['scale_down'] and current_threads > self.resource_limits[ResourceType.THREADS]['min']:
                # Scale down threads
                new_threads = max(
                    self.resource_limits[ResourceType.THREADS]['min'],
                    current_threads * 0.95
                )
                
                return ScalingPrediction(
                    resource_type=ResourceType.THREADS,
                    current_value=current_threads,
                    predicted_demand=predicted_thread_demand,
                    recommended_action=ScalingDirection.SCALE_DOWN,
                    confidence=min(0.65, abs(response_trend) / 100 + 0.4),
                    time_to_scale=timedelta(minutes=1),
                    reasoning=f"Low response time {current.response_time:.1f}ms allows thread reduction",
                    cost_impact=self.resource_costs[ResourceType.THREADS] * (current_threads - new_threads)
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Error predicting thread scaling: {e}")
            return None
    
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
    
    async def _execute_scaling_action(self, prediction: ScalingPrediction):
        """Execute a scaling action based on prediction"""
        try:
            action_id = f"scale_{prediction.resource_type.value}_{int(time.time())}"
            
            logger.info(f"Executing scaling action: {prediction.recommended_action.value} "
                       f"{prediction.resource_type.value} from {prediction.current_value} "
                       f"(confidence: {prediction.confidence:.2f})")
            
            # Calculate new resource value
            if prediction.recommended_action == ScalingDirection.SCALE_UP:
                new_value = min(
                    self.resource_limits[prediction.resource_type]['max'],
                    prediction.current_value * 1.2
                )
            elif prediction.recommended_action == ScalingDirection.SCALE_DOWN:
                new_value = max(
                    self.resource_limits[prediction.resource_type]['min'],
                    prediction.current_value * 0.9
                )
            else:
                new_value = prediction.current_value
            
            # Simulate scaling action execution
            success = await self._simulate_scaling_execution(prediction.resource_type, new_value)
            
            # Create scaling action record
            scaling_action = ScalingAction(
                action_id=action_id,
                resource_type=prediction.resource_type,
                direction=prediction.recommended_action,
                from_value=prediction.current_value,
                to_value=new_value,
                executed_at=datetime.now(),
                success=success
            )
            
            if success:
                # Update current resource value
                self.current_resources[prediction.resource_type] = new_value
                logger.info(f"Scaling successful: {prediction.resource_type.value} scaled to {new_value}")
            else:
                logger.warning(f"Scaling failed for {prediction.resource_type.value}")
            
            self.scaling_history.append(scaling_action)
            
            # Monitor performance impact
            await self._monitor_scaling_impact(scaling_action)
            
        except Exception as e:
            logger.error(f"Failed to execute scaling action: {e}")
    
    async def _simulate_scaling_execution(self, resource_type: ResourceType, new_value: float) -> bool:
        """Simulate scaling action execution"""
        # Simulate scaling delay
        scaling_delays = {
            ResourceType.CPU: 2.0,
            ResourceType.MEMORY: 1.0,
            ResourceType.STORAGE: 5.0,
            ResourceType.NETWORK: 3.0,
            ResourceType.CONNECTIONS: 0.5,
            ResourceType.THREADS: 0.1
        }
        
        delay = scaling_delays.get(resource_type, 1.0)
        await asyncio.sleep(delay)
        
        # Simulate success rate (in production, this would depend on actual scaling capability)
        import random
        success_rates = {
            ResourceType.CPU: 0.95,
            ResourceType.MEMORY: 0.98,
            ResourceType.STORAGE: 0.90,
            ResourceType.NETWORK: 0.85,
            ResourceType.CONNECTIONS: 0.99,
            ResourceType.THREADS: 0.99
        }
        
        success_rate = success_rates.get(resource_type, 0.9)
        success = random.random() < success_rate
        
        logger.debug(f"Scaling {resource_type.value} to {new_value}: {'success' if success else 'failed'}")
        return success
    
    async def _monitor_scaling_impact(self, scaling_action: ScalingAction):
        """Monitor the performance impact of scaling action"""
        try:
            # Wait for scaling to take effect
            await asyncio.sleep(30)
            
            # Collect post-scaling metrics
            post_scaling_pattern = await self._collect_traffic_data()
            
            # Calculate performance impact (simplified)
            baseline_response_time = 200.0  # ms
            performance_impact = (baseline_response_time - post_scaling_pattern.response_time) / baseline_response_time
            
            scaling_action.performance_impact = performance_impact
            
            logger.info(f"Scaling impact for {scaling_action.action_id}: {performance_impact:.2f}")
            
        except Exception as e:
            logger.error(f"Failed to monitor scaling impact: {e}")
    
    async def _load_config(self):
        """Load predictive scaler configuration"""
        try:
            config_file = Path(self.config_path)
            if config_file.exists():
                with open(config_file, 'r') as f:
                    config = json.load(f)
                    self.resource_limits.update(config.get('resource_limits', {}))
                    self.scaling_thresholds.update(config.get('scaling_thresholds', {}))
                    self.prediction_interval = config.get('prediction_interval', self.prediction_interval)
                    logger.info("Predictive scaler configuration loaded successfully")
            else:
                logger.info("No existing configuration found, using defaults")
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
    
    async def _load_historical_data(self):
        """Load historical traffic data if available"""
        try:
            # In production, this would load actual historical data
            logger.info("Historical data loading skipped (using simulated data)")
        except Exception as e:
            logger.error(f"Failed to load historical data: {e}")
    
    def get_scaling_report(self) -> Dict[str, Any]:
        """Generate comprehensive scaling report"""
        try:
            with self.scaling_lock:
                recent_traffic = self.traffic_history[-10:] if len(self.traffic_history) >= 10 else self.traffic_history
                recent_actions = [a for a in self.scaling_history 
                                if a.executed_at > datetime.now() - timedelta(hours=24)]
            
            return {
                'scaler_status': {
                    'is_active': self.is_active,
                    'traffic_data_points': len(self.traffic_history),
                    'scaling_actions_total': len(self.scaling_history),
                    'recent_actions': len(recent_actions)
                },
                'current_resources': {
                    resource_type.value: value for resource_type, value in self.current_resources.items()
                },
                'resource_utilization': {
                    'cpu_usage': recent_traffic[-1].cpu_usage if recent_traffic else 0,
                    'memory_usage': recent_traffic[-1].memory_usage if recent_traffic else 0,
                    'connection_count': recent_traffic[-1].connection_count if recent_traffic else 0,
                    'response_time': recent_traffic[-1].response_time if recent_traffic else 0
                },
                'recent_scaling_actions': [
                    {
                        'resource': action.resource_type.value,
                        'direction': action.direction.value,
                        'from_value': action.from_value,
                        'to_value': action.to_value,
                        'success': action.success,
                        'performance_impact': action.performance_impact,
                        'executed_at': action.executed_at.isoformat()
                    }
                    for action in recent_actions
                ],
                'cost_analysis': {
                    'current_hourly_cost': sum(
                        self.current_resources[rt] * cost 
                        for rt, cost in self.resource_costs.items()
                    ),
                    'cost_saved_by_scaling': sum(
                        action.performance_impact or 0 for action in recent_actions 
                        if action.direction == ScalingDirection.SCALE_DOWN
                    )
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating scaling report: {e}")
            return {'error': str(e)}

# Example usage and testing
async def main():
    """Main function for testing predictive scaler"""
    scaler = PredictiveScaler()
    
    # Initialize scaler
    success = await scaler.initialize()
    if not success:
        print("Failed to initialize predictive scaler")
        return
    
    print("Predictive Scaler initialized successfully!")
    print("Starting predictive scaling...")
    
    # Start scaling in background
    scaling_task = asyncio.create_task(scaler.start_prediction())
    
    # Run for demonstration period
    await asyncio.sleep(150)  # Run for 2.5 minutes
    
    # Stop scaling
    await scaler.stop_prediction()
    await scaling_task
    
    # Generate report
    report = scaler.get_scaling_report()
    print("\nScaling Report:")
    print(json.dumps(report, indent=2, default=str))
    
    print("\nPredictive scaling demonstration complete!")

if __name__ == "__main__":
    asyncio.run(main())