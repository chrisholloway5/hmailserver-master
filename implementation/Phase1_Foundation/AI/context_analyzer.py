"""
Context Analysis Module for hMailServer
Provides context-aware email processing and MCP integration
"""

import asyncio
import json
import logging
import aiohttp
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import re

logger = logging.getLogger(__name__)

class ContextAnalyzer:
    """
    Context-aware email analyzer that integrates with MCP servers
    """
    
    def __init__(self, mcp_config_path: str = "config/mcp/config.json"):
        """
        Initialize the context analyzer
        
        Args:
            mcp_config_path: Path to MCP configuration file
        """
        self.mcp_config_path = mcp_config_path
        self.mcp_servers = {}
        self.conversation_context = {}
        self.user_preferences = {}
        
    async def initialize(self):
        """Initialize MCP connections and load configuration"""
        try:
            # Load MCP configuration
            with open(self.mcp_config_path, 'r') as f:
                config = json.load(f)
                
            # Initialize MCP server connections
            for server_name, server_config in config.get('servers', {}).items():
                await self._connect_mcp_server(server_name, server_config)
                
            logger.info("Context analyzer initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize context analyzer: {e}")
            
    async def _connect_mcp_server(self, name: str, config: Dict):
        """Connect to an MCP server"""
        try:
            # For now, store the configuration
            # In a real implementation, this would establish actual MCP connections
            self.mcp_servers[name] = {
                'config': config,
                'status': 'connected',
                'last_ping': datetime.now()
            }
            logger.info(f"Connected to MCP server: {name}")
            
        except Exception as e:
            logger.error(f"Failed to connect to MCP server {name}: {e}")
            
    async def analyze_email_context(self, email_data: Dict) -> Dict:
        """
        Analyze email context using MCP integration
        
        Args:
            email_data: Dictionary containing email information
            
        Returns:
            Context analysis results
        """
        try:
            sender = email_data.get('sender', '')
            subject = email_data.get('subject', '')
            content = email_data.get('content', '')
            recipients = email_data.get('recipients', [])
            
            # Analyze conversation thread
            thread_context = await self._analyze_conversation_thread(sender, subject)
            
            # Extract entities and relationships
            entities = await self._extract_entities(content)
            
            # Analyze user behavior patterns
            behavior_analysis = await self._analyze_user_behavior(sender, recipients)
            
            # Get contextual recommendations
            recommendations = await self._get_contextual_recommendations(
                sender, subject, content, thread_context
            )
            
            # Calculate priority score
            priority_score = await self._calculate_priority_score(
                email_data, thread_context, behavior_analysis
            )
            
            context_result = {
                'thread_context': thread_context,
                'entities': entities,
                'behavior_analysis': behavior_analysis,
                'recommendations': recommendations,
                'priority_score': priority_score,
                'suggested_actions': await self._suggest_actions(email_data, priority_score),
                'contextual_metadata': {
                    'analysis_timestamp': datetime.now().isoformat(),
                    'mcp_servers_used': list(self.mcp_servers.keys()),
                    'confidence_level': self._calculate_confidence(entities, thread_context)
                }
            }
            
            return context_result
            
        except Exception as e:
            logger.error(f"Context analysis error: {e}")
            return {
                'error': str(e),
                'thread_context': {},
                'entities': [],
                'recommendations': [],
                'priority_score': 0.5
            }
            
    async def _analyze_conversation_thread(self, sender: str, subject: str) -> Dict:
        """Analyze conversation thread context"""
        thread_id = self._generate_thread_id(sender, subject)
        
        if thread_id in self.conversation_context:
            thread = self.conversation_context[thread_id]
            thread['message_count'] += 1
            thread['last_activity'] = datetime.now()
            
            # Calculate thread characteristics
            thread_age = (datetime.now() - thread['started']).days
            response_pattern = thread.get('response_pattern', 'unknown')
            
            return {
                'thread_id': thread_id,
                'message_count': thread['message_count'],
                'thread_age_days': thread_age,
                'response_pattern': response_pattern,
                'participants': thread.get('participants', [sender]),
                'is_ongoing': thread_age < 7 and thread['message_count'] > 1
            }
        else:
            # New conversation thread
            self.conversation_context[thread_id] = {
                'started': datetime.now(),
                'message_count': 1,
                'last_activity': datetime.now(),
                'participants': [sender],
                'response_pattern': 'new'
            }
            
            return {
                'thread_id': thread_id,
                'message_count': 1,
                'thread_age_days': 0,
                'response_pattern': 'new',
                'participants': [sender],
                'is_ongoing': False
            }
            
    def _generate_thread_id(self, sender: str, subject: str) -> str:
        """Generate a thread ID based on sender and subject"""
        # Remove Re: and Fwd: prefixes and normalize
        clean_subject = re.sub(r'^(re:|fwd?:)\s*', '', subject.lower()).strip()
        return f"{sender.lower()}:{clean_subject}"
        
    async def _extract_entities(self, content: str) -> List[Dict]:
        """Extract entities from email content"""
        entities = []
        
        # Extract email addresses
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, content)
        for email in emails:
            entities.append({'type': 'email', 'value': email, 'confidence': 0.9})
            
        # Extract phone numbers (multiple patterns)
        phone_patterns = [
            r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
            r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b',
            r'\(\d{3}\)\s?\d{3}[-.]?\d{4}\b'
        ]
        for pattern in phone_patterns:
            phones = re.findall(pattern, content)
            for phone in phones:
                entities.append({'type': 'phone', 'value': phone, 'confidence': 0.8})
            
        # Extract dates
        date_pattern = r'\b\d{1,2}/\d{1,2}/\d{4}\b|\b\d{4}-\d{2}-\d{2}\b'
        dates = re.findall(date_pattern, content)
        for date in dates:
            entities.append({'type': 'date', 'value': date, 'confidence': 0.7})
            
        # Extract URLs (improved pattern)
        url_patterns = [
            r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',
            r'www\.(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',
            r'\b[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(?:/[^\s]*)?\b'
        ]
        for pattern in url_patterns:
            urls = re.findall(pattern, content)
            for url in urls:
                if not any(e['value'] == url for e in entities):  # Avoid duplicates
                    entities.append({'type': 'url', 'value': url, 'confidence': 0.9})
                    
        # Extract money amounts
        money_pattern = r'\$\d+(?:,\d{3})*(?:\.\d{2})?'
        money_amounts = re.findall(money_pattern, content)
        for amount in money_amounts:
            entities.append({'type': 'money', 'value': amount, 'confidence': 0.8})
            
        # Extract time references
        time_patterns = [
            r'\b\d{1,2}:\d{2}\s*(?:AM|PM|am|pm)?\b',
            r'\b(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b',
            r'\b(?:january|february|march|april|may|june|july|august|september|october|november|december)\b'
        ]
        for pattern in time_patterns:
            times = re.findall(pattern, content, re.IGNORECASE)
            for time_ref in times:
                entities.append({'type': 'time', 'value': time_ref, 'confidence': 0.6})
            
        return entities
        
    async def _analyze_user_behavior(self, sender: str, recipients: List[str]) -> Dict:
        """Analyze user behavior patterns"""
        # In a real implementation, this would analyze historical data
        return {
            'sender_frequency': 'regular',  # daily, weekly, monthly, rare
            'response_likelihood': 0.7,     # Based on historical response rates
            'preferred_response_time': '2-4 hours',
            'interaction_pattern': 'professional',
            'trust_score': 0.8,             # Based on domain, history, etc.
            'relationship_type': 'colleague' # colleague, customer, vendor, unknown
        }
        
    async def _get_contextual_recommendations(self, sender: str, subject: str, 
                                            content: str, thread_context: Dict) -> List[Dict]:
        """Get contextual recommendations using MCP integration"""
        recommendations = []
        
        # Auto-reply suggestions
        if thread_context.get('response_pattern') == 'quick_response_expected':
            recommendations.append({
                'type': 'auto_reply',
                'suggestion': 'Send quick acknowledgment',
                'confidence': 0.8,
                'template': 'Thanks for your email. I\'ll review this and get back to you shortly.'
            })
            
        # Priority adjustment
        if any(keyword in subject.lower() for keyword in ['urgent', 'asap', 'important']):
            recommendations.append({
                'type': 'priority_adjustment',
                'suggestion': 'Mark as high priority',
                'confidence': 0.9
            })
            
        # Follow-up reminder
        if thread_context.get('message_count', 0) > 2:
            recommendations.append({
                'type': 'follow_up',
                'suggestion': 'Schedule follow-up reminder',
                'confidence': 0.7,
                'suggested_time': '24 hours'
            })
            
        return recommendations
        
    async def _calculate_priority_score(self, email_data: Dict, thread_context: Dict, 
                                      behavior_analysis: Dict) -> float:
        """Calculate email priority score"""
        score = 0.5  # Base score
        
        # Subject line indicators
        subject = email_data.get('subject', '').lower()
        if any(word in subject for word in ['urgent', 'asap', 'important']):
            score += 0.3
        if any(word in subject for word in ['fyi', 'info']):
            score -= 0.2
            
        # Sender trust score
        score += behavior_analysis.get('trust_score', 0.5) * 0.2
        
        # Thread context
        if thread_context.get('is_ongoing'):
            score += 0.1
        if thread_context.get('message_count', 0) > 3:
            score += 0.1
            
        # Response likelihood
        score += behavior_analysis.get('response_likelihood', 0.5) * 0.1
        
        return min(max(score, 0.0), 1.0)
        
    async def _suggest_actions(self, email_data: Dict, priority_score: float) -> List[str]:
        """Suggest actions based on analysis"""
        actions = []
        
        if priority_score > 0.8:
            actions.append('notify_immediately')
        elif priority_score > 0.6:
            actions.append('mark_important')
            
        # Check for attachments
        if email_data.get('has_attachments'):
            actions.append('scan_attachments')
            
        # Check for external sender
        sender_domain = email_data.get('sender', '').split('@')[-1]
        if sender_domain not in ['company.com']:  # Add your trusted domains
            actions.append('verify_sender')
            
        return actions
        
    def _calculate_confidence(self, entities: List[Dict], thread_context: Dict) -> float:
        """Calculate overall confidence in the analysis"""
        entity_confidence = sum(e.get('confidence', 0) for e in entities) / max(len(entities), 1)
        thread_confidence = 0.8 if thread_context.get('message_count', 0) > 1 else 0.5
        
        return (entity_confidence + thread_confidence) / 2

# Test the context analyzer
async def test_context_analyzer():
    """Test function for the context analyzer"""
    analyzer = ContextAnalyzer()
    await analyzer.initialize()
    
    # Test email
    test_email = {
        'sender': 'john.doe@company.com',
        'recipients': ['user@company.com'],
        'subject': 'Urgent: Quarterly Review Meeting',
        'content': '''Hi there,
        
        Can we schedule the quarterly review meeting for next week?
        I'm available Tuesday or Wednesday. Please let me know what works for you.
        
        My phone: 555-123-4567
        Meeting link: https://zoom.us/meeting/123
        
        Best regards,
        John''',
        'has_attachments': False
    }
    
    result = await analyzer.analyze_email_context(test_email)
    
    print("Context Analysis Result:")
    print(json.dumps(result, indent=2, default=str))

if __name__ == "__main__":
    # Run the test
    asyncio.run(test_context_analyzer())