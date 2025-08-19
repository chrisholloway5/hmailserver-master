"""
Production AI Bridge for hMailServer
Unified service that coordinates all Phase 2 AI modules for production deployment
"""

import asyncio
import time
import json
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor
import grpc
from grpc import aio

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class EmailProcessingRequest:
    """Standardized email processing request"""
    sender: str
    recipient: str
    subject: str
    content: str
    timestamp: str
    has_attachments: bool = False
    language: Optional[str] = None
    priority: str = "normal"
    thread_id: Optional[str] = None

@dataclass
class IntegratedAIResult:
    """Comprehensive AI processing result"""
    suggestions: List[str]
    summary: str
    routing_decisions: List[str]
    translation: Optional[str]
    key_points: List[str]
    confidence_scores: Dict[str, float]
    processing_time_ms: float
    status: str
    errors: List[str]

class ProductionAIBridge:
    """Production-ready AI service bridge for hMailServer"""
    
    def __init__(self):
        self.initialized = False
        self.services = {}
        self.thread_pool = ThreadPoolExecutor(max_workers=4)
        self.stats = {
            'requests_processed': 0,
            'average_processing_time': 0.0,
            'errors_encountered': 0,
            'uptime_start': time.time()
        }
        
    async def initialize(self) -> bool:
        """Initialize all AI services for production use"""
        logger.info("Initializing Production AI Bridge...")
        
        try:
            # Initialize AI services with error handling
            self.services = await self._initialize_ai_services()
            
            # Validate service health
            health_check = await self._perform_health_check()
            
            if health_check['healthy_services'] >= 3:  # At least 3 services working
                self.initialized = True
                logger.info(f"AI Bridge initialized successfully. {health_check['healthy_services']}/5 services online.")
                return True
            else:
                logger.warning(f"AI Bridge partially initialized. {health_check['healthy_services']}/5 services online.")
                self.initialized = True  # Allow partial initialization
                return True
                
        except Exception as e:
            logger.error(f"AI Bridge initialization failed: {e}")
            return False
    
    async def _initialize_ai_services(self) -> Dict[str, Any]:
        """Initialize individual AI services with fallback handling"""
        services = {}
        
        # Initialize Predictive Composer
        try:
            from predictive_composer import PredictiveComposer
            composer = PredictiveComposer()
            await composer.initialize()
            services['composer'] = composer
            logger.info("✅ Predictive Composer initialized")
        except Exception as e:
            logger.warning(f"Predictive Composer initialization failed: {e}")
            services['composer'] = None
            
        # Initialize Smart Summarizer
        try:
            from smart_summarizer import SmartSummarizer
            summarizer = SmartSummarizer()
            await summarizer.initialize()
            services['summarizer'] = summarizer
            logger.info("✅ Smart Summarizer initialized")
        except Exception as e:
            logger.warning(f"Smart Summarizer initialization failed: {e}")
            services['summarizer'] = None
            
        # Initialize Intelligent Router
        try:
            from intelligent_router import IntelligentRouter
            router = IntelligentRouter()
            await router.initialize()
            services['router'] = router
            logger.info("✅ Intelligent Router initialized")
        except Exception as e:
            logger.warning(f"Intelligent Router initialization failed: {e}")
            services['router'] = None
            
        # Initialize Voice-to-Email Engine
        try:
            from voice_to_email import VoiceToEmailEngine
            voice_engine = VoiceToEmailEngine()
            await voice_engine.initialize()
            services['voice'] = voice_engine
            logger.info("✅ Voice-to-Email Engine initialized")
        except Exception as e:
            logger.warning(f"Voice-to-Email Engine initialization failed: {e}")
            services['voice'] = None
            
        # Initialize Dynamic Translator
        try:
            from dynamic_translator import DynamicTranslationEngine
            translator = DynamicTranslationEngine()
            await translator.initialize()
            services['translator'] = translator
            logger.info("✅ Dynamic Translator initialized")
        except Exception as e:
            logger.warning(f"Dynamic Translator initialization failed: {e}")
            services['translator'] = None
            
        return services
    
    async def _perform_health_check(self) -> Dict[str, Any]:
        """Perform health check on all services"""
        healthy_services = 0
        service_status = {}
        
        for service_name, service in self.services.items():
            try:
                if service and hasattr(service, 'initialized') and service.initialized:
                    service_status[service_name] = 'healthy'
                    healthy_services += 1
                else:
                    service_status[service_name] = 'unhealthy'
            except Exception as e:
                service_status[service_name] = f'error: {e}'
                
        return {
            'healthy_services': healthy_services,
            'total_services': len(self.services),
            'service_status': service_status
        }
    
    async def process_email_integrated(
        self, 
        request: EmailProcessingRequest
    ) -> IntegratedAIResult:
        """Main email processing method with full AI integration"""
        
        if not self.initialized:
            return IntegratedAIResult(
                suggestions=[], summary="", routing_decisions=[],
                translation=None, key_points=[], confidence_scores={},
                processing_time_ms=0, status="error",
                errors=["AI Bridge not initialized"]
            )
        
        start_time = time.time()
        errors = []
        
        try:
            # Update statistics
            self.stats['requests_processed'] += 1
            
            # Convert request to processing format
            email_data = {
                'sender': request.sender,
                'recipient': request.recipient,
                'subject': request.subject,
                'content': request.content,
                'timestamp': request.timestamp,
                'has_attachments': request.has_attachments,
                'language': request.language,
                'priority': request.priority
            }
            
            # Run AI processing tasks concurrently
            tasks = []
            
            # Predictive Composition
            if self.services.get('composer'):
                tasks.append(self._get_composition_suggestions(email_data))
            else:
                tasks.append(asyncio.create_task(self._return_empty_list()))
                
            # Smart Summarization
            if self.services.get('summarizer'):
                tasks.append(self._generate_summary(email_data))
            else:
                tasks.append(asyncio.create_task(self._return_empty_string()))
                
            # Intelligent Routing
            if self.services.get('router'):
                tasks.append(self._get_routing_decisions(email_data))
            else:
                tasks.append(asyncio.create_task(self._return_empty_list()))
                
            # Translation (if needed)
            if self.services.get('translator') and request.language:
                tasks.append(self._translate_content(email_data, request.language))
            else:
                tasks.append(asyncio.create_task(self._return_none()))
                
            # Extract key points
            if self.services.get('summarizer'):
                tasks.append(self._extract_key_points(email_data))
            else:
                tasks.append(asyncio.create_task(self._return_empty_list()))
            
            # Execute all tasks with timeout
            try:
                results = await asyncio.wait_for(
                    asyncio.gather(*tasks, return_exceptions=True),
                    timeout=30.0  # 30 second timeout
                )
            except asyncio.TimeoutError:
                logger.warning("AI processing timeout - returning partial results")
                results = [[] for _ in tasks]  # Empty results for timeout
                errors.append("Processing timeout")
            
            # Extract results with error handling
            suggestions = results[0] if not isinstance(results[0], Exception) else []
            summary = results[1] if not isinstance(results[1], Exception) else ""
            routing_decisions = results[2] if not isinstance(results[2], Exception) else []
            translation = results[3] if not isinstance(results[3], Exception) else None
            key_points = results[4] if not isinstance(results[4], Exception) else []
            
            # Collect any errors from results
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    errors.append(f"Task {i} failed: {str(result)}")
            
            # Calculate confidence scores
            confidence_scores = self._calculate_confidence_scores(
                suggestions, summary, routing_decisions, translation, key_points
            )
            
            # Calculate processing time
            processing_time_ms = (time.time() - start_time) * 1000
            
            # Update statistics
            self.stats['average_processing_time'] = (
                (self.stats['average_processing_time'] * (self.stats['requests_processed'] - 1) +
                 processing_time_ms) / self.stats['requests_processed']
            )
            
            if errors:
                self.stats['errors_encountered'] += 1
            
            # Create result
            result = IntegratedAIResult(
                suggestions=suggestions if isinstance(suggestions, list) else [],
                summary=summary if isinstance(summary, str) else "",
                routing_decisions=routing_decisions if isinstance(routing_decisions, list) else [],
                translation=translation if isinstance(translation, str) else None,
                key_points=key_points if isinstance(key_points, list) else [],
                confidence_scores=confidence_scores,
                processing_time_ms=processing_time_ms,
                status="success" if not errors else "partial_success",
                errors=errors
            )
            
            logger.info(f"Email processed successfully in {processing_time_ms:.2f}ms")
            return result
            
        except Exception as e:
            processing_time_ms = (time.time() - start_time) * 1000
            self.stats['errors_encountered'] += 1
            
            logger.error(f"Email processing failed: {e}")
            return IntegratedAIResult(
                suggestions=[], summary="", routing_decisions=[],
                translation=None, key_points=[], confidence_scores={},
                processing_time_ms=processing_time_ms, status="error",
                errors=[str(e)]
            )
    
    async def _get_composition_suggestions(self, email_data: Dict[str, Any]) -> List[str]:
        """Get predictive composition suggestions"""
        try:
            composer = self.services['composer']
            context = {
                'recipient': email_data.get('recipient'),
                'subject': email_data.get('subject'),
                'current_text': email_data.get('content', '')[:100]  # First 100 chars
            }
            
            suggestions = await composer.get_composition_suggestions(
                context['current_text'], context
            )
            
            return [s.text for s in suggestions if hasattr(s, 'text')]
            
        except Exception as e:
            logger.warning(f"Composition suggestions failed: {e}")
            return []
    
    async def _generate_summary(self, email_data: Dict[str, Any]) -> str:
        """Generate smart summary"""
        try:
            summarizer = self.services['summarizer']
            
            # Create a simple thread structure for summarization
            thread = [{
                'sender': email_data['sender'],
                'subject': email_data['subject'],
                'body': email_data['content'],
                'timestamp': email_data['timestamp']
            }]
            
            summary_result = await summarizer.summarize_email_thread(thread)
            return summary_result.summary_text if hasattr(summary_result, 'summary_text') else ""
            
        except Exception as e:
            logger.warning(f"Summary generation failed: {e}")
            return ""
    
    async def _get_routing_decisions(self, email_data: Dict[str, Any]) -> List[str]:
        """Get intelligent routing decisions"""
        try:
            router = self.services['router']
            decisions = await router.route_email(email_data)
            return [d.destination for d in decisions if hasattr(d, 'destination')]
            
        except Exception as e:
            logger.warning(f"Routing decisions failed: {e}")
            return []
    
    async def _translate_content(self, email_data: Dict[str, Any], target_language: str) -> Optional[str]:
        """Translate email content if needed"""
        try:
            translator = self.services['translator']
            
            # Detect source language
            source_lang, confidence = await translator.detect_language(email_data['content'])
            
            # Only translate if source language is different from target
            if source_lang != target_language and confidence > 0.5:
                result = await translator.translate_text(
                    email_data['content'], 
                    source_language=source_lang,
                    target_language=target_language
                )
                return result.translated_text if hasattr(result, 'translated_text') else None
            
            return None
            
        except Exception as e:
            logger.warning(f"Translation failed: {e}")
            return None
    
    async def _extract_key_points(self, email_data: Dict[str, Any]) -> List[str]:
        """Extract key points from email content"""
        try:
            summarizer = self.services['summarizer']
            key_points = summarizer._extract_key_points(email_data['content'])
            return key_points if isinstance(key_points, list) else []
            
        except Exception as e:
            logger.warning(f"Key points extraction failed: {e}")
            return []
    
    def _calculate_confidence_scores(
        self, 
        suggestions: List[str], 
        summary: str, 
        routing_decisions: List[str],
        translation: Optional[str],
        key_points: List[str]
    ) -> Dict[str, float]:
        """Calculate confidence scores for each AI operation"""
        
        scores = {}
        
        # Composition confidence
        scores['composition'] = min(0.9, len(suggestions) * 0.3) if suggestions else 0.0
        
        # Summary confidence
        scores['summary'] = min(0.95, len(summary) / 100) if summary else 0.0
        
        # Routing confidence
        scores['routing'] = min(0.9, len(routing_decisions) * 0.4) if routing_decisions else 0.0
        
        # Translation confidence
        scores['translation'] = 0.8 if translation else 0.0
        
        # Key points confidence
        scores['key_points'] = min(0.9, len(key_points) * 0.3) if key_points else 0.0
        
        # Overall confidence
        scores['overall'] = sum(scores.values()) / len(scores)
        
        return scores
    
    # Helper methods for fallback scenarios
    async def _return_empty_list(self) -> List[str]:
        return []
    
    async def _return_empty_string(self) -> str:
        return ""
    
    async def _return_none(self) -> None:
        return None
    
    def get_service_stats(self) -> Dict[str, Any]:
        """Get service statistics"""
        uptime = time.time() - self.stats['uptime_start']
        
        return {
            'uptime_seconds': uptime,
            'requests_processed': self.stats['requests_processed'],
            'average_processing_time_ms': self.stats['average_processing_time'],
            'errors_encountered': self.stats['errors_encountered'],
            'error_rate': (
                self.stats['errors_encountered'] / max(1, self.stats['requests_processed'])
            ),
            'requests_per_second': self.stats['requests_processed'] / max(1, uptime),
            'initialized': self.initialized
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform comprehensive health check"""
        service_health = await self._perform_health_check()
        stats = self.get_service_stats()
        
        overall_health = (
            self.initialized and 
            service_health['healthy_services'] >= 3 and
            stats['error_rate'] < 0.1
        )
        
        return {
            'healthy': overall_health,
            'service_health': service_health,
            'statistics': stats,
            'timestamp': time.time()
        }

# Global bridge instance
_bridge_instance = None

async def get_bridge_instance() -> ProductionAIBridge:
    """Get or create the global bridge instance"""
    global _bridge_instance
    
    if _bridge_instance is None:
        _bridge_instance = ProductionAIBridge()
        await _bridge_instance.initialize()
    
    return _bridge_instance

# REST API endpoints (for integration with web services)
async def process_email_endpoint(email_data: Dict[str, Any]) -> Dict[str, Any]:
    """REST endpoint for email processing"""
    try:
        bridge = await get_bridge_instance()
        
        # Convert dict to EmailProcessingRequest
        request = EmailProcessingRequest(
            sender=email_data.get('sender', ''),
            recipient=email_data.get('recipient', ''),
            subject=email_data.get('subject', ''),
            content=email_data.get('content', ''),
            timestamp=email_data.get('timestamp', str(time.time())),
            has_attachments=email_data.get('has_attachments', False),
            language=email_data.get('language'),
            priority=email_data.get('priority', 'normal')
        )
        
        result = await bridge.process_email_integrated(request)
        return asdict(result)
        
    except Exception as e:
        logger.error(f"Email processing endpoint failed: {e}")
        return {
            'status': 'error',
            'errors': [str(e)],
            'suggestions': [],
            'summary': '',
            'routing_decisions': [],
            'translation': None,
            'key_points': [],
            'confidence_scores': {},
            'processing_time_ms': 0
        }

async def health_endpoint() -> Dict[str, Any]:
    """Health check endpoint"""
    try:
        bridge = await get_bridge_instance()
        return await bridge.health_check()
    except Exception as e:
        return {
            'healthy': False,
            'error': str(e),
            'timestamp': time.time()
        }

async def stats_endpoint() -> Dict[str, Any]:
    """Statistics endpoint"""
    try:
        bridge = await get_bridge_instance()
        return bridge.get_service_stats()
    except Exception as e:
        return {
            'error': str(e),
            'timestamp': time.time()
        }

if __name__ == "__main__":
    # Simple test
    async def test_bridge():
        bridge = ProductionAIBridge()
        success = await bridge.initialize()
        
        if success:
            # Test email processing
            test_request = EmailProcessingRequest(
                sender="test@example.com",
                recipient="user@company.com",
                subject="Test Email",
                content="This is a test email for the production AI bridge.",
                timestamp=str(time.time())
            )
            
            result = await bridge.process_email_integrated(test_request)
            print(f"Processing result: {result.status}")
            print(f"Processing time: {result.processing_time_ms:.2f}ms")
            print(f"Confidence: {result.confidence_scores.get('overall', 0):.2f}")
            
            # Health check
            health = await bridge.health_check()
            print(f"System health: {health['healthy']}")
            
        else:
            print("Bridge initialization failed")
    
    asyncio.run(test_bridge())