"""
Intelligent Email Routing Engine for hMailServer Phase 2
ML-based email categorization, auto-forwarding, and smart distribution
"""

import asyncio
import logging
from typing import Dict, List, Optional, Tuple, Set
import json
from datetime import datetime, timedelta
import re
from dataclasses import dataclass
from collections import defaultdict, Counter
import math

logger = logging.getLogger(__name__)

@dataclass
class RoutingRule:
    name: str
    priority: int
    conditions: Dict
    actions: Dict
    confidence_threshold: float
    active: bool
    
@dataclass
class RoutingDecision:
    destination: str
    action: str  # 'forward', 'folder', 'priority', 'delegate', 'auto_reply'
    confidence: float
    reasoning: str
    metadata: Dict

@dataclass
class UserProfile:
    email: str
    department: str
    role: str
    expertise_areas: List[str]
    workload_score: float
    availability: str
    response_time_avg: float
    success_rate: float

class IntelligentRouter:
    """
    Advanced email routing system with machine learning capabilities
    """
    
    def __init__(self):
        self.routing_rules = {}
        self.user_profiles = {}
        self.routing_history = []
        self.category_models = {}
        self.keyword_weights = {}
        self.department_mapping = {}
        self.expertise_keywords = {}
        self.performance_metrics = {}
        self.initialized = False
        
        # Initialize default configuration
        self._initialize_default_config()
        
    async def initialize(self):
        """Initialize the intelligent router"""
        try:
            # Load user profiles and routing rules
            self._load_default_user_profiles()
            self._load_default_routing_rules()
            
            # Initialize ML models (simplified for demo)
            await self._initialize_ml_models()
            
            self.initialized = True
            logger.info("Intelligent Router initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Intelligent Router: {e}")
            self.initialized = True  # Continue with limited functionality
            
    def _initialize_default_config(self):
        """Initialize default configuration"""
        self.department_mapping = {
            'sales': ['sales', 'revenue', 'customer', 'deal', 'quote', 'proposal'],
            'support': ['issue', 'problem', 'help', 'bug', 'error', 'ticket'],
            'hr': ['employee', 'hiring', 'benefit', 'policy', 'leave', 'payroll'],
            'finance': ['budget', 'expense', 'invoice', 'payment', 'cost', 'financial'],
            'engineering': ['technical', 'development', 'code', 'system', 'api', 'bug'],
            'marketing': ['campaign', 'promotion', 'brand', 'social', 'content', 'lead'],
            'legal': ['contract', 'compliance', 'legal', 'terms', 'agreement', 'liability']
        }
        
        self.expertise_keywords = {
            'database_admin': ['database', 'sql', 'query', 'backup', 'performance'],
            'network_admin': ['network', 'firewall', 'router', 'connection', 'bandwidth'],
            'security_specialist': ['security', 'vulnerability', 'breach', 'encryption', 'threat'],
            'project_manager': ['project', 'timeline', 'milestone', 'deadline', 'resource'],
            'business_analyst': ['requirements', 'analysis', 'process', 'workflow', 'optimization'],
            'quality_assurance': ['testing', 'quality', 'defect', 'validation', 'verification']
        }
        
    def _load_default_user_profiles(self):
        """Load default user profiles"""
        self.user_profiles = {
            'john.doe@company.com': UserProfile(
                email='john.doe@company.com',
                department='engineering',
                role='senior_developer',
                expertise_areas=['database_admin', 'security_specialist'],
                workload_score=0.7,
                availability='available',
                response_time_avg=2.5,  # hours
                success_rate=0.95
            ),
            'sarah.wilson@company.com': UserProfile(
                email='sarah.wilson@company.com',
                department='support',
                role='support_manager',
                expertise_areas=['customer_service', 'troubleshooting'],
                workload_score=0.8,
                availability='busy',
                response_time_avg=1.0,
                success_rate=0.92
            ),
            'mike.chen@company.com': UserProfile(
                email='mike.chen@company.com',
                department='sales',
                role='sales_representative',
                expertise_areas=['customer_relations', 'product_knowledge'],
                workload_score=0.6,
                availability='available',
                response_time_avg=0.5,
                success_rate=0.88
            )
        }
        
    def _load_default_routing_rules(self):
        """Load default routing rules"""
        self.routing_rules = {
            'urgent_to_manager': RoutingRule(
                name='Urgent emails to department manager',
                priority=1,
                conditions={
                    'urgency_level': 'high',
                    'confidence_min': 0.8
                },
                actions={
                    'action': 'escalate',
                    'target': 'department_manager'
                },
                confidence_threshold=0.8,
                active=True
            ),
            'expertise_routing': RoutingRule(
                name='Route by expertise match',
                priority=2,
                conditions={
                    'has_expertise_match': True,
                    'confidence_min': 0.7
                },
                actions={
                    'action': 'forward',
                    'target': 'best_expert'
                },
                confidence_threshold=0.7,
                active=True
            ),
            'department_routing': RoutingRule(
                name='Route by department',
                priority=3,
                conditions={
                    'department_match': True,
                    'confidence_min': 0.6
                },
                actions={
                    'action': 'forward',
                    'target': 'department_available'
                },
                confidence_threshold=0.6,
                active=True
            ),
            'auto_reply_faq': RoutingRule(
                name='Auto-reply for FAQ',
                priority=4,
                conditions={
                    'is_common_question': True,
                    'confidence_min': 0.9
                },
                actions={
                    'action': 'auto_reply',
                    'template': 'faq_response'
                },
                confidence_threshold=0.9,
                active=True
            )
        }
        
    async def _initialize_ml_models(self):
        """Initialize machine learning models for routing"""
        # Simplified ML model initialization
        # In a real implementation, this would load trained models
        
        # Category classification weights
        self.category_models = {
            'urgency': {
                'high': ['urgent', 'critical', 'asap', 'emergency', 'immediately'],
                'medium': ['soon', 'quickly', 'priority', 'important'],
                'low': ['when possible', 'no rush', 'fyi', 'info']
            },
            'complexity': {
                'high': ['complex', 'advanced', 'technical', 'detailed', 'comprehensive'],
                'medium': ['moderate', 'standard', 'typical', 'regular'],
                'low': ['simple', 'basic', 'quick', 'easy', 'straightforward']
            },
            'sentiment': {
                'angry': ['frustrated', 'angry', 'upset', 'disappointed', 'unacceptable'],
                'concerned': ['worried', 'concerned', 'issue', 'problem', 'trouble'],
                'neutral': ['request', 'question', 'information', 'update'],
                'positive': ['thank', 'appreciate', 'excellent', 'good', 'pleased']
            }
        }
        
        logger.info("ML models initialized for intelligent routing")
        
    async def route_email(self, email_data: Dict) -> List[RoutingDecision]:
        """
        Determine optimal routing for an email
        
        Args:
            email_data: Dictionary containing email information
            
        Returns:
            List of routing decisions with confidence scores
        """
        if not self.initialized:
            await self.initialize()
            
        try:
            # Extract email features
            features = await self._extract_email_features(email_data)
            
            # Classify email characteristics
            classifications = await self._classify_email(email_data, features)
            
            # Find expertise matches
            expertise_matches = self._find_expertise_matches(features, classifications)
            
            # Assess user availability and workload
            availability_scores = self._assess_user_availability(expertise_matches)
            
            # Generate routing decisions
            routing_decisions = []
            
            # Apply routing rules in priority order
            for rule_name, rule in sorted(self.routing_rules.items(), 
                                        key=lambda x: x[1].priority):
                if not rule.active:
                    continue
                    
                decision = await self._apply_routing_rule(
                    rule, email_data, features, classifications, 
                    expertise_matches, availability_scores
                )
                
                if decision and decision.confidence >= rule.confidence_threshold:
                    routing_decisions.append(decision)
                    
            # If no rules matched, use default routing
            if not routing_decisions:
                default_decision = await self._get_default_routing(
                    email_data, features, classifications
                )
                routing_decisions.append(default_decision)
                
            # Sort by confidence
            routing_decisions.sort(key=lambda d: d.confidence, reverse=True)
            
            # Log routing decision
            self._log_routing_decision(email_data, routing_decisions[0] if routing_decisions else None)
            
            return routing_decisions
            
        except Exception as e:
            logger.error(f"Error routing email: {e}")
            # Return safe default
            return [RoutingDecision(
                destination='admin@company.com',
                action='forward',
                confidence=0.1,
                reasoning=f"Error in routing: {e}",
                metadata={}
            )]
            
    async def _extract_email_features(self, email_data: Dict) -> Dict:
        """Extract features from email for routing analysis"""
        content = email_data.get('content', '')
        subject = email_data.get('subject', '')
        sender = email_data.get('sender', '')
        
        features = {
            'word_count': len(content.split()),
            'has_attachments': email_data.get('has_attachments', False),
            'sender_domain': sender.split('@')[-1] if '@' in sender else '',
            'is_external': not sender.endswith('@company.com'),
            'time_sent': email_data.get('timestamp', datetime.now()),
            'subject_length': len(subject),
            'urgency_indicators': [],
            'technical_indicators': [],
            'department_indicators': [],
            'question_indicators': []
        }
        
        # Analyze content for indicators
        content_lower = (subject + ' ' + content).lower()
        
        # Urgency indicators
        urgency_words = ['urgent', 'asap', 'critical', 'emergency', 'immediately', 'rush']
        features['urgency_indicators'] = [word for word in urgency_words if word in content_lower]
        
        # Technical indicators
        technical_words = ['error', 'bug', 'system', 'server', 'database', 'api', 'code']
        features['technical_indicators'] = [word for word in technical_words if word in content_lower]
        
        # Department indicators
        for dept, keywords in self.department_mapping.items():
            dept_matches = [word for word in keywords if word in content_lower]
            if dept_matches:
                features['department_indicators'].append({
                    'department': dept,
                    'matches': dept_matches,
                    'score': len(dept_matches)
                })
                
        # Question indicators
        question_patterns = [
            r'\?',
            r'\bhow\b',
            r'\bwhat\b',
            r'\bwhen\b',
            r'\bwhere\b',
            r'\bwhy\b',
            r'\bcan you\b',
            r'\bcould you\b'
        ]
        
        for pattern in question_patterns:
            if re.search(pattern, content_lower):
                features['question_indicators'].append(pattern)
                
        return features
        
    async def _classify_email(self, email_data: Dict, features: Dict) -> Dict:
        """Classify email characteristics"""
        content = email_data.get('content', '') + ' ' + email_data.get('subject', '')
        content_lower = content.lower()
        
        classifications = {}
        
        # Classify each dimension
        for dimension, categories in self.category_models.items():
            scores = {}
            
            for category, keywords in categories.items():
                score = sum(1 for keyword in keywords if keyword in content_lower)
                if score > 0:
                    scores[category] = score
                    
            if scores:
                best_category = max(scores, key=scores.get)
                confidence = scores[best_category] / sum(scores.values())
                classifications[dimension] = {
                    'category': best_category,
                    'confidence': confidence,
                    'scores': scores
                }
            else:
                classifications[dimension] = {
                    'category': 'unknown',
                    'confidence': 0.0,
                    'scores': {}
                }
                
        return classifications
        
    def _find_expertise_matches(self, features: Dict, classifications: Dict) -> List[Dict]:
        """Find users with matching expertise"""
        matches = []
        
        # Extract technical keywords from email
        all_indicators = (
            features.get('technical_indicators', []) +
            [match['department'] for match in features.get('department_indicators', [])]
        )
        
        # Score each user based on expertise match
        for user_email, profile in self.user_profiles.items():
            match_score = 0.0
            matched_areas = []
            
            # Check expertise area matches
            for expertise in profile.expertise_areas:
                expertise_keywords = self.expertise_keywords.get(expertise, [])
                
                # Count keyword matches
                keyword_matches = sum(1 for keyword in expertise_keywords 
                                    if any(keyword in indicator for indicator in all_indicators))
                
                if keyword_matches > 0:
                    match_score += keyword_matches * 0.3
                    matched_areas.append(expertise)
                    
            # Check department match
            dept_indicators = features.get('department_indicators', [])
            for dept_match in dept_indicators:
                if dept_match['department'] == profile.department:
                    match_score += dept_match['score'] * 0.4
                    matched_areas.append(f"department_{profile.department}")
                    
            if match_score > 0:
                matches.append({
                    'user': user_email,
                    'profile': profile,
                    'score': match_score,
                    'matched_areas': matched_areas
                })
                
        # Sort by match score
        matches.sort(key=lambda m: m['score'], reverse=True)
        
        return matches
        
    def _assess_user_availability(self, expertise_matches: List[Dict]) -> Dict:
        """Assess user availability and workload"""
        availability_scores = {}
        
        for match in expertise_matches:
            user_email = match['user']
            profile = match['profile']
            
            # Calculate availability score
            availability_score = 1.0
            
            # Workload factor (lower workload = higher availability)
            availability_score *= (1.0 - profile.workload_score)
            
            # Availability status factor
            status_factors = {
                'available': 1.0,
                'busy': 0.5,
                'away': 0.2,
                'do_not_disturb': 0.1
            }
            availability_score *= status_factors.get(profile.availability, 0.5)
            
            # Response time factor (faster response = higher score)
            response_factor = max(0.1, 1.0 / (1.0 + profile.response_time_avg))
            availability_score *= response_factor
            
            # Success rate factor
            availability_score *= profile.success_rate
            
            availability_scores[user_email] = {
                'score': availability_score,
                'factors': {
                    'workload': (1.0 - profile.workload_score),
                    'availability': status_factors.get(profile.availability, 0.5),
                    'response_time': response_factor,
                    'success_rate': profile.success_rate
                }
            }
            
        return availability_scores
        
    async def _apply_routing_rule(self, rule: RoutingRule, email_data: Dict, 
                                features: Dict, classifications: Dict,
                                expertise_matches: List[Dict], 
                                availability_scores: Dict) -> Optional[RoutingDecision]:
        """Apply a specific routing rule"""
        
        # Check rule conditions
        conditions_met = True
        confidence = 1.0
        
        # Check urgency condition
        if 'urgency_level' in rule.conditions:
            required_urgency = rule.conditions['urgency_level']
            email_urgency = classifications.get('urgency', {}).get('category', 'low')
            
            if email_urgency != required_urgency:
                if not (required_urgency == 'high' and email_urgency in ['high', 'medium']):
                    conditions_met = False
                    
        # Check expertise match condition
        if 'has_expertise_match' in rule.conditions:
            if not expertise_matches:
                conditions_met = False
            else:
                confidence *= min(1.0, expertise_matches[0]['score'] / 2.0)
                
        # Check department match condition
        if 'department_match' in rule.conditions:
            dept_indicators = features.get('department_indicators', [])
            if not dept_indicators:
                conditions_met = False
            else:
                best_dept_score = max(d['score'] for d in dept_indicators)
                confidence *= min(1.0, best_dept_score / 3.0)
                
        # Check FAQ condition
        if 'is_common_question' in rule.conditions:
            # Simplified FAQ detection
            question_indicators = features.get('question_indicators', [])
            common_questions = ['password', 'login', 'access', 'how to', 'reset']
            content_lower = email_data.get('content', '').lower()
            
            has_common_question = any(q in content_lower for q in common_questions)
            if not (has_common_question and question_indicators):
                conditions_met = False
            else:
                confidence *= 0.9
                
        if not conditions_met or confidence < rule.confidence_threshold:
            return None
            
        # Generate routing decision based on rule action
        action = rule.actions.get('action', 'forward')
        target = rule.actions.get('target', 'admin@company.com')
        
        if target == 'best_expert' and expertise_matches:
            # Find best available expert
            best_match = None
            best_combined_score = 0.0
            
            for match in expertise_matches:
                user_email = match['user']
                expertise_score = match['score']
                availability = availability_scores.get(user_email, {}).get('score', 0.1)
                
                combined_score = expertise_score * 0.7 + availability * 0.3
                
                if combined_score > best_combined_score:
                    best_combined_score = combined_score
                    best_match = match
                    
            if best_match:
                destination = best_match['user']
                reasoning = f"Best expert match: {', '.join(best_match['matched_areas'])}"
            else:
                destination = 'admin@company.com'
                reasoning = "No suitable expert available"
                
        elif target == 'department_manager':
            # Route to department manager
            dept_indicators = features.get('department_indicators', [])
            if dept_indicators:
                dept = dept_indicators[0]['department']
                destination = f"{dept}_manager@company.com"
                reasoning = f"Escalated to {dept} department manager"
            else:
                destination = 'admin@company.com'
                reasoning = "Escalated to admin (no department identified)"
                
        elif target == 'department_available':
            # Route to available person in department
            dept_indicators = features.get('department_indicators', [])
            if dept_indicators:
                dept = dept_indicators[0]['department']
                # Find available person in department
                dept_users = [user for user, profile in self.user_profiles.items() 
                            if profile.department == dept]
                
                if dept_users:
                    # Pick user with best availability
                    best_user = max(dept_users, 
                                  key=lambda u: availability_scores.get(u, {}).get('score', 0))
                    destination = best_user
                    reasoning = f"Routed to available {dept} team member"
                else:
                    destination = f"{dept}@company.com"
                    reasoning = f"Routed to {dept} department"
            else:
                destination = 'admin@company.com'
                reasoning = "Routed to admin (no department match)"
                
        else:
            destination = target
            reasoning = f"Routed by rule: {rule.name}"
            
        return RoutingDecision(
            destination=destination,
            action=action,
            confidence=confidence,
            reasoning=reasoning,
            metadata={
                'rule_applied': rule.name,
                'rule_priority': rule.priority,
                'conditions_met': rule.conditions
            }
        )
        
    async def _get_default_routing(self, email_data: Dict, features: Dict, 
                                 classifications: Dict) -> RoutingDecision:
        """Get default routing when no rules match"""
        
        # Default to general inbox or admin
        destination = 'admin@company.com'
        reasoning = "Default routing - no specific rules matched"
        
        # Check if there's a department match
        dept_indicators = features.get('department_indicators', [])
        if dept_indicators:
            dept = dept_indicators[0]['department']
            destination = f"{dept}@company.com"
            reasoning = f"Default department routing to {dept}"
            
        return RoutingDecision(
            destination=destination,
            action='forward',
            confidence=0.3,
            reasoning=reasoning,
            metadata={'routing_type': 'default'}
        )
        
    def _log_routing_decision(self, email_data: Dict, decision: Optional[RoutingDecision]):
        """Log routing decision for analytics"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'sender': email_data.get('sender', ''),
            'subject': email_data.get('subject', ''),
            'decision': {
                'destination': decision.destination if decision else None,
                'action': decision.action if decision else None,
                'confidence': decision.confidence if decision else 0.0,
                'reasoning': decision.reasoning if decision else 'No decision made'
            }
        }
        
        self.routing_history.append(log_entry)
        
        # Keep only last 1000 entries
        if len(self.routing_history) > 1000:
            self.routing_history = self.routing_history[-1000:]
            
    def get_routing_analytics(self) -> Dict:
        """Get analytics on routing performance"""
        if not self.routing_history:
            return {'total_routed': 0, 'analytics': 'No routing history available'}
            
        total_routed = len(self.routing_history)
        
        # Analyze routing patterns
        destinations = Counter(entry['decision']['destination'] for entry in self.routing_history)
        actions = Counter(entry['decision']['action'] for entry in self.routing_history)
        
        # Calculate average confidence
        avg_confidence = sum(entry['decision']['confidence'] for entry in self.routing_history) / total_routed
        
        # Recent activity (last 24 hours)
        recent_cutoff = datetime.now() - timedelta(hours=24)
        recent_entries = [
            entry for entry in self.routing_history 
            if datetime.fromisoformat(entry['timestamp']) > recent_cutoff
        ]
        
        return {
            'total_routed': total_routed,
            'average_confidence': avg_confidence,
            'top_destinations': destinations.most_common(5),
            'action_distribution': dict(actions),
            'recent_activity_24h': len(recent_entries),
            'routing_accuracy': avg_confidence  # Simplified metric
        }

# Test the intelligent router
async def test_intelligent_router():
    """Test function for the intelligent router"""
    router = IntelligentRouter()
    await router.initialize()
    
    # Test email scenarios
    test_emails = [
        {
            'sender': 'customer@external.com',
            'subject': 'URGENT: Database connection error',
            'content': '''Hi,
            
            We're experiencing critical database connection errors in production. 
            Our application cannot connect to the database server and customers 
            are unable to access their accounts.
            
            This is urgent - please help immediately!
            
            Error details:
            - Connection timeout after 30 seconds
            - Database server appears to be running
            - No recent configuration changes
            
            Can someone from your technical team help us resolve this ASAP?
            
            Thanks,
            Customer Support Team''',
            'timestamp': datetime.now(),
            'has_attachments': False
        },
        {
            'sender': 'employee@company.com',
            'subject': 'Question about vacation policy',
            'content': '''Hello HR,
            
            I have a question about the vacation policy. How many vacation days 
            do I have available this year? Also, what's the process for requesting 
            time off during the holidays?
            
            Thanks for your help!
            
            Best regards,
            John''',
            'timestamp': datetime.now(),
            'has_attachments': False
        },
        {
            'sender': 'partner@business.com',
            'subject': 'New project proposal - collaboration opportunity',
            'content': '''Dear Team,
            
            We have an exciting collaboration opportunity that could benefit both 
            our companies. We'd like to propose a joint project for developing 
            a new product line.
            
            Key details:
            - Estimated budget: $500,000
            - Timeline: 6 months
            - Revenue potential: $2M in first year
            
            Would someone from your business development team be available for 
            a meeting next week to discuss this further?
            
            Best regards,
            Business Partner''',
            'timestamp': datetime.now(),
            'has_attachments': True
        }
    ]
    
    print("🎯 Intelligent Email Routing Demo")
    print("=" * 50)
    
    for i, email in enumerate(test_emails, 1):
        print(f"\n📧 Test Email {i}:")
        print(f"From: {email['sender']}")
        print(f"Subject: {email['subject']}")
        print(f"Has Attachments: {email['has_attachments']}")
        
        # Get routing decisions
        decisions = await router.route_email(email)
        
        print(f"\n🎯 Routing Decisions ({len(decisions)} options):")
        for j, decision in enumerate(decisions, 1):
            print(f"{j}. {decision.action.upper()} → {decision.destination}")
            print(f"   Confidence: {decision.confidence:.2f}")
            print(f"   Reasoning: {decision.reasoning}")
            if decision.metadata:
                print(f"   Metadata: {decision.metadata}")
        
        print("-" * 40)
    
    # Show routing analytics
    analytics = router.get_routing_analytics()
    print(f"\n📊 Routing Analytics:")
    print(f"Total Emails Routed: {analytics['total_routed']}")
    print(f"Average Confidence: {analytics['average_confidence']:.2f}")
    print(f"Top Destinations: {analytics['top_destinations']}")
    print(f"Recent Activity (24h): {analytics['recent_activity_24h']}")
    
    print("\n✅ Intelligent Router Test Complete!")

if __name__ == "__main__":
    asyncio.run(test_intelligent_router())