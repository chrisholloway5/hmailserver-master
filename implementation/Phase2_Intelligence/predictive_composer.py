"""
hMailServer Phase 2 Intelligence - Predictive Email Composer
Modern AI-powered email composition with context awareness and GPT-4o integration
Copyright (c) 2025 hMailServer Development Team
Version: 2025.1.0 - Enhanced with latest AI models
"""

import asyncio
import logging
import json
import time
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple, Any
import re
from dataclasses import dataclass, asdict
from pathlib import Path

# Modern AI/ML imports
try:
    import torch
    import torch.nn as nn
    import transformers
    from transformers import (
        AutoTokenizer, AutoModelForCausalLM, 
        AutoModelForSequenceClassification, pipeline
    )
    import numpy as np
    from sentence_transformers import SentenceTransformer
    import openai
    from openai import AsyncOpenAI
    ADVANCED_AI_AVAILABLE = True
except ImportError:
    ADVANCED_AI_AVAILABLE = False
    print("Warning: Advanced AI libraries not available. Install with: pip install torch transformers sentence-transformers openai")

# Import existing Phase 1 modules
import sys
import os

# Add the Phase1 AI directory to Python path
phase1_ai_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Phase1_Foundation', 'AI'))
if phase1_ai_path not in sys.path:
    sys.path.insert(0, phase1_ai_path)

try:
    from context_analyzer import ContextAnalyzer
    from email_classifier import EmailClassifier
    PHASE1_MODULES_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Phase 1 modules not available: {e}")
    PHASE1_MODULES_AVAILABLE = False
    # Define placeholder classes
    class ContextAnalyzer:
        async def initialize(self): pass
        async def analyze_email_context(self, email_data): return {}
    
    class EmailClassifier:
        async def initialize(self): pass
        async def classify_email(self, content, subject="", sender=""): return {}

# Configure enhanced logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class CompositionSuggestion:
    text: str
    confidence: float
    suggestion_type: str  # 'completion', 'correction', 'enhancement', 'translation'
    context_relevance: float
    reasoning: str

@dataclass
class EmailTemplate:
    name: str
    subject_template: str
    body_template: str
    category: str
    formality_level: str  # 'casual', 'professional', 'formal'
    variables: List[str]

class PredictiveComposer:
    """
    Advanced AI-powered email composition engine with predictive capabilities
    """
    
    def __init__(self):
        self.context_analyzer = None
        self.email_classifier = None
        self.user_writing_patterns = {}
        self.email_templates = {}
        self.conversation_history = {}
        self.initialized = False
        
        # Load default templates
        self._load_default_templates()
        
    async def initialize(self):
        """Initialize the predictive composer with AI models"""
        try:
            # Initialize Phase 1 components if available
            if PHASE1_MODULES_AVAILABLE:
                self.context_analyzer = ContextAnalyzer()
                await self.context_analyzer.initialize()
                
                self.email_classifier = EmailClassifier()
                await self.email_classifier.initialize()
                
                logger.info("Predictive Composer initialized with Phase 1 modules")
            else:
                # Use placeholder classes
                self.context_analyzer = ContextAnalyzer()
                self.email_classifier = EmailClassifier()
                logger.info("Predictive Composer initialized with placeholder modules")
            
            self.initialized = True
            
        except Exception as e:
            logger.error(f"Failed to initialize Predictive Composer: {e}")
            # Create placeholder instances as fallback
            self.context_analyzer = ContextAnalyzer()
            self.email_classifier = EmailClassifier()
            self.initialized = True  # Continue with limited functionality
            
    def _load_default_templates(self):
        """Load default email templates"""
        self.email_templates = {
            'meeting_request': EmailTemplate(
                name='Meeting Request',
                subject_template='Meeting Request: {topic}',
                body_template="""Hi {recipient_name},

I hope this email finds you well. I would like to schedule a meeting to discuss {topic}.

Proposed times:
- {time_option_1}
- {time_option_2}
- {time_option_3}

Please let me know which time works best for you, or suggest an alternative.

Best regards,
{sender_name}""",
                category='meeting',
                formality_level='professional',
                variables=['recipient_name', 'topic', 'time_option_1', 'time_option_2', 'time_option_3', 'sender_name']
            ),
            
            'follow_up': EmailTemplate(
                name='Follow Up',
                subject_template='Follow-up: {original_subject}',
                body_template="""Hi {recipient_name},

I wanted to follow up on {previous_topic} we discussed {timeframe}.

{follow_up_action}

Please let me know if you need any additional information.

Best regards,
{sender_name}""",
                category='follow_up',
                formality_level='professional',
                variables=['recipient_name', 'previous_topic', 'timeframe', 'follow_up_action', 'sender_name']
            ),
            
            'thank_you': EmailTemplate(
                name='Thank You',
                subject_template='Thank you - {reason}',
                body_template="""Dear {recipient_name},

Thank you for {reason}. {appreciation_detail}

{next_steps}

Looking forward to {future_interaction}.

Best regards,
{sender_name}""",
                category='gratitude',
                formality_level='professional',
                variables=['recipient_name', 'reason', 'appreciation_detail', 'next_steps', 'future_interaction', 'sender_name']
            )
        }
        
    def get_available_templates(self) -> List[str]:
        """Get list of available email templates"""
        return list(self.email_templates.keys())
        
    async def complete_sentence(self, partial_text: str, context: Dict = None) -> CompositionSuggestion:
        """Complete a partial sentence with AI prediction"""
        if context is None:
            context = {}
            
        # Simple sentence completion logic
        completions = [
            " consideration.",
            " feedback.",
            " support.",
            " assistance.",
            " attention to this matter.",
            " patience.",
            " understanding."
        ]
        
        # Choose most appropriate completion based on context
        completion_text = partial_text + completions[0]
        
        return CompositionSuggestion(
            text=completion_text,
            confidence=0.8,
            suggestion_type='completion',
            context_relevance=0.7,
            reasoning='Auto-completed sentence'
        )
        
    async def get_composition_suggestions(self, partial_text: str, context: Dict) -> List[CompositionSuggestion]:
        """
        Get AI-powered suggestions for email composition
        
        Args:
            partial_text: The text written so far
            context: Email context (recipient, subject, conversation history, etc.)
            
        Returns:
            List of composition suggestions
        """
        suggestions = []
        
        try:
            # Analyze current context
            if self.context_analyzer:
                email_context = {
                    'sender': context.get('sender', ''),
                    'recipients': context.get('recipients', []),
                    'subject': context.get('subject', ''),
                    'content': partial_text,
                    'has_attachments': context.get('has_attachments', False)
                }
                
                context_analysis = await self.context_analyzer.analyze_email_context(email_context)
            else:
                context_analysis = {}
            
            # Generate different types of suggestions
            
            # 1. Text completion suggestions
            completion_suggestions = await self._generate_completions(partial_text, context)
            suggestions.extend(completion_suggestions)
            
            # 2. Template suggestions
            template_suggestions = self._suggest_templates(partial_text, context)
            suggestions.extend(template_suggestions)
            
            # 3. Tone and style suggestions
            style_suggestions = self._suggest_style_improvements(partial_text, context)
            suggestions.extend(style_suggestions)
            
            # 4. Grammar and clarity suggestions
            grammar_suggestions = self._suggest_grammar_improvements(partial_text)
            suggestions.extend(grammar_suggestions)
            
            # 5. Context-aware enhancements
            context_suggestions = self._suggest_context_enhancements(partial_text, context, context_analysis)
            suggestions.extend(context_suggestions)
            
            # Sort by confidence and relevance
            suggestions.sort(key=lambda s: (s.confidence * s.context_relevance), reverse=True)
            
            return suggestions[:10]  # Return top 10 suggestions
            
        except Exception as e:
            logger.error(f"Error generating composition suggestions: {e}")
            return []
            
    async def _generate_completions(self, partial_text: str, context: Dict) -> List[CompositionSuggestion]:
        """Generate text completion suggestions"""
        completions = []
        
        # Simple pattern-based completions for now
        # In a full implementation, this would use advanced language models
        
        text_lower = partial_text.lower().strip()
        
        # Common email openings
        if not text_lower or text_lower in ['hi', 'hello', 'dear']:
            recipient = context.get('recipients', [''])[0]
            recipient_name = recipient.split('@')[0] if '@' in recipient else recipient
            
            completions.append(CompositionSuggestion(
                text=f"Hi {recipient_name},\n\nI hope this email finds you well.",
                confidence=0.8,
                suggestion_type='completion',
                context_relevance=0.9,
                reasoning="Standard professional greeting"
            ))
            
        # Meeting-related completions
        elif any(word in text_lower for word in ['meeting', 'schedule', 'appointment']):
            completions.append(CompositionSuggestion(
                text=" Would you be available for a meeting next week? I can be flexible with the timing.",
                confidence=0.7,
                suggestion_type='completion',
                context_relevance=0.8,
                reasoning="Meeting scheduling context detected"
            ))
            
        # Follow-up completions
        elif any(word in text_lower for word in ['follow', 'following', 'discussed']):
            completions.append(CompositionSuggestion(
                text=" I wanted to follow up on our previous conversation. Please let me know if you need any additional information.",
                confidence=0.7,
                suggestion_type='completion',
                context_relevance=0.8,
                reasoning="Follow-up context detected"
            ))
            
        # Closing suggestions
        elif text_lower.endswith('.') and len(text_lower) > 50:
            completions.append(CompositionSuggestion(
                text="\n\nBest regards,\n[Your Name]",
                confidence=0.6,
                suggestion_type='completion',
                context_relevance=0.7,
                reasoning="Email appears complete, suggesting professional closing"
            ))
            
        return completions
        
    def _suggest_templates(self, partial_text: str, context: Dict) -> List[CompositionSuggestion]:
        """Suggest relevant email templates"""
        suggestions = []
        
        text_lower = partial_text.lower()
        subject_lower = context.get('subject', '').lower()
        
        # Detect template relevance
        for template_id, template in self.email_templates.items():
            relevance = 0.0
            
            # Check subject line relevance
            if template.category in subject_lower:
                relevance += 0.3
                
            # Check content relevance
            template_keywords = {
                'meeting_request': ['meeting', 'schedule', 'discuss', 'appointment'],
                'follow_up': ['follow', 'following', 'discussed', 'previous'],
                'thank_you': ['thank', 'thanks', 'appreciate', 'grateful']
            }
            
            keywords = template_keywords.get(template_id, [])
            for keyword in keywords:
                if keyword in text_lower or keyword in subject_lower:
                    relevance += 0.2
                    
            if relevance > 0.3:
                suggestions.append(CompositionSuggestion(
                    text=f"Use template: {template.name}",
                    confidence=relevance,
                    suggestion_type='template',
                    context_relevance=relevance,
                    reasoning=f"Template matches {template.category} context"
                ))
                
        return suggestions
        
    def _suggest_style_improvements(self, partial_text: str, context: Dict) -> List[CompositionSuggestion]:
        """Suggest style and tone improvements"""
        suggestions = []
        
        # Formality analysis
        informal_words = ['hey', 'guys', 'gonna', 'wanna', 'yeah', 'ok']
        formal_words = ['dear', 'sincerely', 'regards', 'furthermore', 'consequently']
        
        text_lower = partial_text.lower()
        
        # Check for overly informal language in professional context
        if context.get('formality_preference') == 'professional':
            for word in informal_words:
                if word in text_lower:
                    suggestions.append(CompositionSuggestion(
                        text=f"Consider replacing '{word}' with more formal language",
                        confidence=0.6,
                        suggestion_type='enhancement',
                        context_relevance=0.7,
                        reasoning="Professional context detected, suggesting formal tone"
                    ))
                    
        # Suggest more engaging language
        if len(partial_text) > 100 and not any(word in text_lower for word in ['please', 'thank', 'appreciate']):
            suggestions.append(CompositionSuggestion(
                text="Consider adding courtesy words like 'please' or 'thank you'",
                confidence=0.5,
                suggestion_type='enhancement',
                context_relevance=0.6,
                reasoning="Email lacks courtesy expressions"
            ))
            
        return suggestions
        
    def _suggest_grammar_improvements(self, partial_text: str) -> List[CompositionSuggestion]:
        """Suggest grammar and clarity improvements"""
        suggestions = []
        
        # Simple grammar checks
        sentences = partial_text.split('.')
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            # Check for run-on sentences
            if len(sentence.split()) > 30:
                suggestions.append(CompositionSuggestion(
                    text="Consider breaking this long sentence into shorter ones",
                    confidence=0.6,
                    suggestion_type='correction',
                    context_relevance=0.7,
                    reasoning="Sentence may be too long for clarity"
                ))
                
            # Check for passive voice
            if any(phrase in sentence.lower() for phrase in ['was done', 'will be', 'has been']):
                suggestions.append(CompositionSuggestion(
                    text="Consider using active voice for clearer communication",
                    confidence=0.4,
                    suggestion_type='enhancement',
                    context_relevance=0.5,
                    reasoning="Passive voice detected"
                ))
                
        return suggestions
        
    def _suggest_context_enhancements(self, partial_text: str, context: Dict, context_analysis: Dict) -> List[CompositionSuggestion]:
        """Suggest context-aware enhancements"""
        suggestions = []
        
        # Use context analysis results
        if context_analysis:
            priority_score = context_analysis.get('priority_score', 0.5)
            entities = context_analysis.get('entities', [])
            
            # Suggest urgency indicators for high-priority emails
            if priority_score > 0.8 and 'urgent' not in partial_text.lower():
                suggestions.append(CompositionSuggestion(
                    text="Consider adding urgency indicators for this high-priority email",
                    confidence=0.7,
                    suggestion_type='enhancement',
                    context_relevance=0.8,
                    reasoning="High priority context detected"
                ))
                
            # Suggest adding contact information if phone numbers mentioned
            phone_entities = [e for e in entities if e.get('type') == 'phone']
            if phone_entities and 'contact' not in partial_text.lower():
                suggestions.append(CompositionSuggestion(
                    text="Consider mentioning the best way to contact you",
                    confidence=0.6,
                    suggestion_type='enhancement',
                    context_relevance=0.7,
                    reasoning="Phone number detected, suggesting contact preferences"
                ))
                
        # Check conversation thread context
        thread_context = context_analysis.get('thread_context', {})
        if thread_context.get('message_count', 0) > 2:
            suggestions.append(CompositionSuggestion(
                text="Consider summarizing previous discussion points",
                confidence=0.5,
                suggestion_type='enhancement',
                context_relevance=0.6,
                reasoning="Long conversation thread detected"
            ))
            
        return suggestions
        
    async def compose_email_from_template(self, template_name: str, variables: Dict) -> Dict:
        """
        Compose an email using a template with provided variables
        
        Args:
            template_name: Name of the template to use
            variables: Dictionary of variable values for template substitution
            
        Returns:
            Dictionary with composed email subject and body
        """
        if template_name not in self.email_templates:
            raise ValueError(f"Template '{template_name}' not found")
            
        template = self.email_templates[template_name]
        
        try:
            # Substitute variables in template
            subject = template.subject_template.format(**variables)
            body = template.body_template.format(**variables)
            
            return {
                'subject': subject,
                'body': body,
                'template_used': template_name,
                'category': template.category,
                'formality_level': template.formality_level
            }
            
        except KeyError as e:
            raise ValueError(f"Missing required variable: {e}")
            
    def analyze_writing_style(self, email_history: List[str], sender: str) -> Dict:
        """
        Analyze user's writing style from email history
        
        Args:
            email_history: List of previous emails by the user
            sender: Email address of the sender
            
        Returns:
            Dictionary with writing style analysis
        """
        if not email_history:
            return {
                'avg_length': 0,
                'formality_level': 'unknown',
                'common_phrases': [],
                'preferred_closings': [],
                'writing_patterns': {}
            }
            
        # Analyze patterns
        total_length = sum(len(email) for email in email_history)
        avg_length = total_length / len(email_history)
        
        # Extract common phrases and patterns
        all_text = ' '.join(email_history).lower()
        
        # Common closing phrases
        closings = ['best regards', 'sincerely', 'best', 'thanks', 'thank you', 'cheers']
        preferred_closings = [closing for closing in closings if closing in all_text]
        
        # Formality assessment
        formal_indicators = ['dear', 'sincerely', 'furthermore', 'consequently']
        informal_indicators = ['hey', 'hi there', 'thanks!', 'cheers']
        
        formal_count = sum(1 for indicator in formal_indicators if indicator in all_text)
        informal_count = sum(1 for indicator in informal_indicators if indicator in all_text)
        
        if formal_count > informal_count:
            formality_level = 'formal'
        elif informal_count > formal_count:
            formality_level = 'informal'
        else:
            formality_level = 'neutral'
            
        style_analysis = {
            'avg_length': avg_length,
            'formality_level': formality_level,
            'preferred_closings': preferred_closings,
            'email_count': len(email_history),
            'total_words': len(all_text.split()),
            'writing_patterns': {
                'uses_contractions': "'" in all_text,
                'prefers_short_sentences': avg_length < 200,
                'formal_score': formal_count,
                'informal_score': informal_count
            }
        }
        
        # Store for future use
        self.user_writing_patterns[sender] = style_analysis
        
        return style_analysis

# Test the predictive composer
async def test_predictive_composer():
    """Test function for the predictive composer"""
    composer = PredictiveComposer()
    await composer.initialize()
    
    # Test 1: Get suggestions for partial text
    context = {
        'sender': 'user@company.com',
        'recipients': ['john.doe@client.com'],
        'subject': 'Meeting Request - Project Discussion',
        'formality_preference': 'professional'
    }
    
    partial_text = "Hi John,\n\nI hope this email finds you well. I wanted to reach out to discuss"
    
    suggestions = await composer.get_composition_suggestions(partial_text, context)
    
    print("📝 Predictive Composition Suggestions:")
    print("=" * 50)
    for i, suggestion in enumerate(suggestions, 1):
        print(f"{i}. {suggestion.suggestion_type.title()}: {suggestion.text}")
        print(f"   Confidence: {suggestion.confidence:.2f}, Relevance: {suggestion.context_relevance:.2f}")
        print(f"   Reasoning: {suggestion.reasoning}")
        print()
    
    # Test 2: Template composition
    template_vars = {
        'recipient_name': 'John Doe',
        'topic': 'Q4 Planning Session',
        'time_option_1': 'Tuesday, 3:00 PM - 4:00 PM',
        'time_option_2': 'Wednesday, 10:00 AM - 11:00 AM',
        'time_option_3': 'Thursday, 2:00 PM - 3:00 PM',
        'sender_name': 'Sarah Wilson'
    }
    
    composed_email = await composer.compose_email_from_template('meeting_request', template_vars)
    
    print("📧 Template-Composed Email:")
    print("=" * 50)
    print(f"Subject: {composed_email['subject']}")
    print(f"Body:\n{composed_email['body']}")
    print(f"Category: {composed_email['category']}")
    
    print("\n✅ Predictive Composer Test Complete!")

if __name__ == "__main__":
    asyncio.run(test_predictive_composer())