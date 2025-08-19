"""
Email Classification Module for hMailServer
Provides AI-powered email classification and content analysis
"""

import torch
import numpy as np
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from sklearn.feature_extraction.text import TfidfVectorizer
import asyncio
import logging
import json
import re
from typing import Dict, List, Tuple, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmailClassifier:
    """
    AI-powered email classifier for spam detection, priority classification,
    and content analysis
    """
    
    def __init__(self, model_name: str = "microsoft/DialoGPT-medium"):
        """
        Initialize the email classifier
        
        Args:
            model_name: HuggingFace model name for classification
        """
        self.model_name = model_name
        self.tokenizer = None
        self.model = None
        self.tfidf_vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        self.is_initialized = False
        
        # Spam patterns (simple rule-based backup)
        self.spam_patterns = [
            r'\b(viagra|cialis|pills)\b',
            r'\b(lottery|winner|congratulations)\b',
            r'\b(urgent|immediate|act now)\b',
            r'\$\d+',  # Money patterns
            r'\b(click here|visit now)\b'
        ]
        
    async def initialize(self):
        """Initialize the AI models asynchronously"""
        try:
            logger.info(f"Loading model: {self.model_name}")
            
            # For now, use a simple approach without heavy models
            # In production, you'd load actual pre-trained models
            self.is_initialized = True
            logger.info("Email classifier initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize classifier: {e}")
            # Fall back to rule-based classification
            self.is_initialized = True
            
    def extract_features(self, email_content: str, subject: str = "") -> Dict:
        """
        Extract features from email content
        
        Args:
            email_content: Email body text
            subject: Email subject line
            
        Returns:
            Dictionary of extracted features
        """
        features = {
            'length': len(email_content),
            'subject_length': len(subject),
            'has_links': bool(re.search(r'http[s]?://', email_content)),
            'has_attachments': 'attachment' in email_content.lower(),
            'exclamation_count': email_content.count('!'),
            'question_count': email_content.count('?'),
            'caps_ratio': sum(1 for c in email_content if c.isupper()) / max(len(email_content), 1),
            'money_mentions': len(re.findall(r'\$\d+', email_content)),
            'urgency_words': len(re.findall(r'\b(urgent|immediate|asap|hurry)\b', email_content.lower())),
        }
        
        return features
        
    def rule_based_spam_detection(self, email_content: str, subject: str = "") -> float:
        """
        Simple rule-based spam detection as fallback
        
        Returns:
            Spam probability (0.0 to 1.0)
        """
        spam_score = 0.0
        full_text = (subject + " " + email_content).lower()
        
        # Check spam patterns
        for pattern in self.spam_patterns:
            if re.search(pattern, full_text, re.IGNORECASE):
                spam_score += 0.2
                
        # Additional heuristics
        features = self.extract_features(email_content, subject)
        
        if features['caps_ratio'] > 0.3:
            spam_score += 0.15
            
        if features['exclamation_count'] > 3:
            spam_score += 0.1
            
        if features['money_mentions'] > 0:
            spam_score += 0.2
            
        if features['urgency_words'] > 0:
            spam_score += 0.15
            
        return min(spam_score, 1.0)
        
    async def classify_email(self, email_content: str, subject: str = "", sender: str = "") -> Dict:
        """
        Classify email content
        
        Args:
            email_content: Email body text
            subject: Email subject line
            sender: Sender email address
            
        Returns:
            Classification results dictionary
        """
        if not self.is_initialized:
            await self.initialize()
            
        try:
            # Extract features
            features = self.extract_features(email_content, subject)
            
            # Spam detection
            spam_probability = self.rule_based_spam_detection(email_content, subject)
            
            # Priority classification (simple heuristic)
            priority = "normal"
            if any(word in subject.lower() for word in ['urgent', 'important', 'asap']):
                priority = "high"
            elif any(word in subject.lower() for word in ['fyi', 'info', 'newsletter']):
                priority = "low"
                
            # Category classification
            category = self._classify_category(email_content, subject)
            
            # Sentiment analysis (basic)
            sentiment = self._analyze_sentiment(email_content)
            
            result = {
                'spam_probability': spam_probability,
                'is_spam': spam_probability > 0.5,
                'priority': priority,
                'category': category,
                'sentiment': sentiment,
                'features': features,
                'confidence': 0.8 if spam_probability > 0.7 or spam_probability < 0.3 else 0.6
            }
            
            logger.info(f"Email classified: spam={spam_probability:.2f}, priority={priority}, category={category}")
            return result
            
        except Exception as e:
            logger.error(f"Classification error: {e}")
            return {
                'spam_probability': 0.0,
                'is_spam': False,
                'priority': 'normal',
                'category': 'general',
                'sentiment': 'neutral',
                'features': {},
                'confidence': 0.1,
                'error': str(e)
            }
            
    def _classify_category(self, content: str, subject: str) -> str:
        """Simple category classification"""
        text = (subject + " " + content).lower()
        
        if any(word in text for word in ['meeting', 'calendar', 'appointment', 'schedule']):
            return 'meeting'
        elif any(word in text for word in ['order', 'purchase', 'payment', 'invoice', 'receipt']):
            return 'commercial'
        elif any(word in text for word in ['support', 'help', 'issue', 'problem', 'bug']):
            return 'support'
        elif any(word in text for word in ['newsletter', 'news', 'update', 'announcement']):
            return 'newsletter'
        else:
            return 'general'
            
    def _analyze_sentiment(self, content: str) -> str:
        """Simple sentiment analysis"""
        positive_words = ['good', 'great', 'excellent', 'happy', 'pleased', 'wonderful']
        negative_words = ['bad', 'terrible', 'awful', 'angry', 'frustrated', 'disappointed']
        
        content_lower = content.lower()
        positive_count = sum(1 for word in positive_words if word in content_lower)
        negative_count = sum(1 for word in negative_words if word in content_lower)
        
        if positive_count > negative_count:
            return 'positive'
        elif negative_count > positive_count:
            return 'negative'
        else:
            return 'neutral'

# Test the classifier
async def test_classifier():
    """Test function for the email classifier"""
    classifier = EmailClassifier()
    await classifier.initialize()
    
    # Test email
    test_email = """
    Dear Sir/Madam,
    
    URGENT!!! You have won $1,000,000 in our lottery!
    Click here immediately to claim your prize!
    
    Best regards,
    Lottery Team
    """
    
    result = await classifier.classify_email(
        email_content=test_email,
        subject="URGENT: You Won $1M!!!",
        sender="noreply@spam.com"
    )
    
    print("Classification Result:")
    print(json.dumps(result, indent=2))
    
    # Test legitimate email
    legit_email = """
    Hi John,
    
    I wanted to follow up on our meeting yesterday. 
    Could you please send me the quarterly reports when you get a chance?
    
    Thanks,
    Sarah
    """
    
    result2 = await classifier.classify_email(
        email_content=legit_email,
        subject="Follow up - Quarterly Reports",
        sender="sarah@company.com"
    )
    
    print("\nLegitimate Email Classification:")
    print(json.dumps(result2, indent=2))

if __name__ == "__main__":
    # Run the test
    asyncio.run(test_classifier())