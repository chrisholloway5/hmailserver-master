"""
Smart Email Summarization Engine for hMailServer Phase 2
Automatic email thread and attachment summarization with intelligent insights
"""

import asyncio
import logging
from typing import Dict, List, Optional, Tuple
import json
from datetime import datetime, timedelta
import re
from dataclasses import dataclass
from collections import defaultdict

logger = logging.getLogger(__name__)

@dataclass
class EmailSummary:
    thread_id: str
    summary_text: str
    key_points: List[str]
    action_items: List[str]
    participants: List[str]
    timeline: List[Dict]
    sentiment: str
    priority_level: str
    word_count: int
    original_count: int
    compression_ratio: float

@dataclass
class AttachmentSummary:
    filename: str
    file_type: str
    content_summary: str
    key_information: List[str]
    metadata: Dict
    security_assessment: str

class SmartSummarizer:
    """
    Advanced email and attachment summarization with AI-powered insights
    """
    
    def __init__(self):
        self.thread_summaries = {}
        self.summarization_templates = {}
        self.extraction_patterns = {}
        self.initialized = False
        
        # Initialize extraction patterns
        self._initialize_extraction_patterns()
        
    async def initialize(self):
        """Initialize the smart summarizer"""
        try:
            # Load summarization templates
            self._load_summarization_templates()
            
            self.initialized = True
            logger.info("Smart Summarizer initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Smart Summarizer: {e}")
            self.initialized = True  # Continue with limited functionality
            
    def _initialize_extraction_patterns(self):
        """Initialize regex patterns for information extraction"""
        self.extraction_patterns = {
            'action_items': [
                r'(?:please|can you|could you|need to|must|should|will)\s+([^.!?]+)',
                r'(?:action item|todo|task):\s*([^.!?\n]+)',
                r'(?:by|before|due)\s+([^.!?\n]+)',
            ],
            'dates': [
                r'\b(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b',
                r'\b(?:january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2}',
                r'\d{1,2}/\d{1,2}/\d{4}',
                r'\d{4}-\d{2}-\d{2}',
            ],
            'deadlines': [
                r'(?:deadline|due date|by|before)\s+([^.!?\n]+)',
                r'(?:asap|urgent|immediately|soon)',
            ],
            'decisions': [
                r'(?:decided|decision|agreed|concluded)\s+([^.!?\n]+)',
                r'(?:we will|we have decided|it was agreed)\s+([^.!?\n]+)',
            ],
            'questions': [
                r'([^.!?\n]*\?)',
                r'(?:question|query|wondering)\s+([^.!?\n]+)',
            ],
            'attachments_mentioned': [
                r'(?:attached|attachment|see attached|enclosed)\s+([^.!?\n]+)',
                r'(?:document|file|report|spreadsheet)\s+([^.!?\n]+)',
            ]
        }
        
    def _load_summarization_templates(self):
        """Load templates for different types of summaries"""
        self.summarization_templates = {
            'meeting_summary': {
                'structure': ['participants', 'agenda_items', 'decisions', 'action_items', 'next_steps'],
                'intro': 'Meeting Summary:',
                'sections': {
                    'participants': 'Participants: {participants}',
                    'agenda_items': 'Topics Discussed:\n{agenda_items}',
                    'decisions': 'Decisions Made:\n{decisions}',
                    'action_items': 'Action Items:\n{action_items}',
                    'next_steps': 'Next Steps:\n{next_steps}'
                }
            },
            'project_update': {
                'structure': ['status', 'progress', 'blockers', 'next_milestones'],
                'intro': 'Project Update Summary:',
                'sections': {
                    'status': 'Current Status: {status}',
                    'progress': 'Progress Made:\n{progress}',
                    'blockers': 'Issues/Blockers:\n{blockers}',
                    'next_milestones': 'Upcoming Milestones:\n{next_milestones}'
                }
            },
            'general': {
                'structure': ['main_topic', 'key_points', 'action_items', 'follow_up'],
                'intro': 'Email Thread Summary:',
                'sections': {
                    'main_topic': 'Main Topic: {main_topic}',
                    'key_points': 'Key Points:\n{key_points}',
                    'action_items': 'Action Items:\n{action_items}',
                    'follow_up': 'Follow-up Required:\n{follow_up}'
                }
            }
        }
        
    async def summarize_email_thread(self, emails: List[Dict], thread_id: str = None) -> EmailSummary:
        """
        Summarize an email thread with intelligent insights
        
        Args:
            emails: List of email dictionaries with content, sender, timestamp, etc.
            thread_id: Optional thread identifier
            
        Returns:
            EmailSummary object with comprehensive summary
        """
        if not emails:
            raise ValueError("No emails provided for summarization")
            
        if thread_id is None:
            thread_id = self._generate_thread_id(emails[0])
            
        try:
            # Sort emails by timestamp
            sorted_emails = sorted(emails, key=lambda e: e.get('timestamp', datetime.now()))
            
            # Extract key information
            participants = self._extract_participants(sorted_emails)
            timeline = self._build_timeline(sorted_emails)
            
            # Combine all email content
            all_content = '\n\n'.join([
                f"From: {email.get('sender', 'Unknown')}\n"
                f"Date: {email.get('timestamp', 'Unknown')}\n"
                f"Subject: {email.get('subject', 'No Subject')}\n"
                f"Content: {email.get('content', '')}"
                for email in sorted_emails
            ])
            
            # Extract structured information
            key_points = self._extract_key_points(all_content)
            action_items = self._extract_action_items(all_content)
            
            # Determine thread category and sentiment
            category = self._classify_thread_category(all_content)
            sentiment = self._analyze_thread_sentiment(all_content)
            priority = self._assess_priority(all_content, sorted_emails)
            
            # Generate summary text
            summary_text = await self._generate_summary_text(
                all_content, category, key_points, action_items, participants
            )
            
            # Calculate compression metrics
            original_word_count = len(all_content.split())
            summary_word_count = len(summary_text.split())
            compression_ratio = summary_word_count / max(original_word_count, 1)
            
            summary = EmailSummary(
                thread_id=thread_id,
                summary_text=summary_text,
                key_points=key_points,
                action_items=action_items,
                participants=participants,
                timeline=timeline,
                sentiment=sentiment,
                priority_level=priority,
                word_count=summary_word_count,
                original_count=original_word_count,
                compression_ratio=compression_ratio
            )
            
            # Cache the summary
            self.thread_summaries[thread_id] = summary
            
            return summary
            
        except Exception as e:
            logger.error(f"Error summarizing email thread: {e}")
            raise
            
    def _generate_thread_id(self, email: Dict) -> str:
        """Generate a unique thread ID"""
        subject = email.get('subject', '')
        sender = email.get('sender', '')
        # Remove Re: and Fwd: prefixes
        clean_subject = re.sub(r'^(re:|fwd?:)\s*', '', subject.lower()).strip()
        return f"{sender}:{clean_subject}".replace(' ', '_')
        
    def _extract_participants(self, emails: List[Dict]) -> List[str]:
        """Extract unique participants from email thread"""
        participants = set()
        
        for email in emails:
            sender = email.get('sender', '')
            if sender:
                participants.add(sender)
                
            recipients = email.get('recipients', [])
            for recipient in recipients:
                participants.add(recipient)
                
        return list(participants)
        
    def _build_timeline(self, emails: List[Dict]) -> List[Dict]:
        """Build a timeline of email exchanges"""
        timeline = []
        
        for email in emails:
            timeline.append({
                'timestamp': email.get('timestamp', datetime.now()).isoformat() if isinstance(email.get('timestamp'), datetime) else str(email.get('timestamp', '')),
                'sender': email.get('sender', 'Unknown'),
                'subject': email.get('subject', 'No Subject'),
                'summary': self._create_brief_summary(email.get('content', ''))
            })
            
        return timeline
        
    def _create_brief_summary(self, content: str, max_words: int = 15) -> str:
        """Create a brief summary of email content"""
        if not content:
            return "No content"
            
        # Remove email headers and signatures
        clean_content = re.sub(r'^(From:|To:|Subject:|Date:).*$', '', content, flags=re.MULTILINE)
        clean_content = re.sub(r'^[-_=]+$', '', clean_content, flags=re.MULTILINE)
        
        # Get first meaningful sentence
        sentences = [s.strip() for s in clean_content.split('.') if s.strip()]
        if sentences:
            first_sentence = sentences[0]
            words = first_sentence.split()
            if len(words) > max_words:
                return ' '.join(words[:max_words]) + '...'
            return first_sentence
        else:
            words = clean_content.split()
            return ' '.join(words[:max_words]) + ('...' if len(words) > max_words else '')
            
    def _extract_key_points(self, content: str) -> List[str]:
        """Extract key points from email content"""
        key_points = []
        
        # Split into sentences
        sentences = [s.strip() for s in content.split('.') if s.strip()]
        
        # Look for important markers
        important_markers = [
            'important', 'key', 'critical', 'urgent', 'note that', 'please note',
            'significant', 'major', 'main', 'primary', 'essential'
        ]
        
        for sentence in sentences:
            sentence_lower = sentence.lower()
            
            # Check for importance markers
            if any(marker in sentence_lower for marker in important_markers):
                if len(sentence) > 20:  # Avoid very short sentences
                    key_points.append(sentence.strip())
                    
            # Check for numbered/bulleted points
            if re.match(r'^\s*[\d•\-\*]\s*', sentence):
                if len(sentence) > 20:
                    key_points.append(sentence.strip())
                    
        # Remove duplicates and limit
        seen = set()
        unique_points = []
        for point in key_points:
            if point not in seen and len(unique_points) < 10:
                seen.add(point)
                unique_points.append(point)
                
        return unique_points
        
    def _extract_action_items(self, content: str) -> List[str]:
        """Extract action items from email content"""
        action_items = []
        
        # Use predefined patterns
        for pattern in self.extraction_patterns['action_items']:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                if len(match.strip()) > 10:  # Meaningful action items
                    action_items.append(match.strip())
                    
        # Look for deadline patterns
        for pattern in self.extraction_patterns['deadlines']:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                if isinstance(match, str) and len(match.strip()) > 5:
                    action_items.append(f"Deadline: {match.strip()}")
                    
        # Remove duplicates
        return list(set(action_items))[:10]
        
    def _classify_thread_category(self, content: str) -> str:
        """Classify the email thread category"""
        content_lower = content.lower()
        
        # Category keywords
        categories = {
            'meeting': ['meeting', 'schedule', 'agenda', 'calendar', 'appointment'],
            'project': ['project', 'milestone', 'deliverable', 'deadline', 'progress'],
            'support': ['issue', 'problem', 'error', 'bug', 'help', 'support'],
            'announcement': ['announce', 'announcement', 'news', 'update', 'notice'],
            'decision': ['decision', 'decide', 'approve', 'approve', 'reject'],
            'information': ['fyi', 'information', 'inform', 'share', 'update']
        }
        
        category_scores = {}
        for category, keywords in categories.items():
            score = sum(1 for keyword in keywords if keyword in content_lower)
            if score > 0:
                category_scores[category] = score
                
        if category_scores:
            return max(category_scores, key=category_scores.get)
        else:
            return 'general'
            
    def _analyze_thread_sentiment(self, content: str) -> str:
        """Analyze overall sentiment of the email thread"""
        content_lower = content.lower()
        
        positive_words = [
            'good', 'great', 'excellent', 'awesome', 'fantastic', 'wonderful',
            'pleased', 'happy', 'satisfied', 'agree', 'perfect', 'thank'
        ]
        
        negative_words = [
            'bad', 'terrible', 'awful', 'horrible', 'disappointed', 'frustrated',
            'angry', 'upset', 'concern', 'problem', 'issue', 'disagree'
        ]
        
        urgent_words = [
            'urgent', 'critical', 'emergency', 'asap', 'immediately', 'rush'
        ]
        
        positive_count = sum(1 for word in positive_words if word in content_lower)
        negative_count = sum(1 for word in negative_words if word in content_lower)
        urgent_count = sum(1 for word in urgent_words if word in content_lower)
        
        if urgent_count > 0:
            return 'urgent'
        elif positive_count > negative_count * 1.5:
            return 'positive'
        elif negative_count > positive_count * 1.5:
            return 'negative'
        else:
            return 'neutral'
            
    def _assess_priority(self, content: str, emails: List[Dict]) -> str:
        """Assess the priority level of the email thread"""
        priority_score = 0
        content_lower = content.lower()
        
        # High priority indicators
        high_priority_words = ['urgent', 'critical', 'asap', 'emergency', 'important']
        priority_score += sum(2 for word in high_priority_words if word in content_lower)
        
        # Medium priority indicators
        medium_priority_words = ['deadline', 'soon', 'quickly', 'priority']
        priority_score += sum(1 for word in medium_priority_words if word in content_lower)
        
        # Thread characteristics
        if len(emails) > 5:  # Long thread
            priority_score += 1
            
        # Recent activity
        if emails:
            latest_email = max(emails, key=lambda e: e.get('timestamp', datetime.min))
            if isinstance(latest_email.get('timestamp'), datetime):
                hours_since = (datetime.now() - latest_email['timestamp']).total_seconds() / 3600
                if hours_since < 4:  # Recent activity
                    priority_score += 1
                    
        # Determine priority level
        if priority_score >= 4:
            return 'high'
        elif priority_score >= 2:
            return 'medium'
        else:
            return 'low'
            
    async def _generate_summary_text(self, content: str, category: str, 
                                   key_points: List[str], action_items: List[str],
                                   participants: List[str]) -> str:
        """Generate the summary text"""
        
        # Select appropriate template
        template_key = 'general'
        if category in self.summarization_templates:
            template_key = category
        elif category == 'meeting':
            template_key = 'meeting_summary'
        elif category == 'project':
            template_key = 'project_update'
            
        template = self.summarization_templates[template_key]
        
        # Build summary sections
        summary_parts = [template['intro']]
        
        # Participants
        if participants:
            summary_parts.append(f"Participants: {', '.join(participants[:5])}")
            
        # Key points
        if key_points:
            summary_parts.append("Key Points:")
            for i, point in enumerate(key_points[:5], 1):
                summary_parts.append(f"{i}. {point}")
                
        # Action items
        if action_items:
            summary_parts.append("Action Items:")
            for i, item in enumerate(action_items[:5], 1):
                summary_parts.append(f"{i}. {item}")
                
        return '\n'.join(summary_parts)
        
    async def summarize_attachment(self, attachment_data: Dict) -> AttachmentSummary:
        """
        Summarize an email attachment
        
        Args:
            attachment_data: Dictionary with filename, content, metadata
            
        Returns:
            AttachmentSummary object
        """
        filename = attachment_data.get('filename', 'unknown')
        content = attachment_data.get('content', '')
        file_type = attachment_data.get('type', self._detect_file_type(filename))
        
        try:
            # Extract key information based on file type
            if file_type in ['txt', 'doc', 'docx']:
                key_info = self._extract_document_info(content)
                summary = self._summarize_text_content(content)
            elif file_type in ['pdf']:
                key_info = self._extract_pdf_info(content)
                summary = "PDF document - content analysis limited"
            elif file_type in ['xls', 'xlsx', 'csv']:
                key_info = self._extract_spreadsheet_info(content)
                summary = "Spreadsheet data - numerical analysis performed"
            else:
                key_info = []
                summary = f"{file_type.upper()} file - binary content"
                
            # Security assessment
            security_assessment = self._assess_file_security(filename, file_type, content)
            
            return AttachmentSummary(
                filename=filename,
                file_type=file_type,
                content_summary=summary,
                key_information=key_info,
                metadata=attachment_data.get('metadata', {}),
                security_assessment=security_assessment
            )
            
        except Exception as e:
            logger.error(f"Error summarizing attachment {filename}: {e}")
            return AttachmentSummary(
                filename=filename,
                file_type=file_type,
                content_summary="Error processing attachment",
                key_information=[],
                metadata={},
                security_assessment="unknown"
            )
            
    def _detect_file_type(self, filename: str) -> str:
        """Detect file type from filename"""
        if '.' in filename:
            extension = filename.split('.')[-1].lower()
            return extension
        return 'unknown'
        
    def _extract_document_info(self, content: str) -> List[str]:
        """Extract key information from document content"""
        key_info = []
        
        # Look for headers/titles
        lines = content.split('\n')
        for line in lines[:10]:  # Check first 10 lines
            line = line.strip()
            if line and (line.isupper() or len(line.split()) <= 8):
                key_info.append(f"Heading: {line}")
                
        # Look for key data patterns
        dates = re.findall(r'\d{1,2}/\d{1,2}/\d{4}|\d{4}-\d{2}-\d{2}', content)
        if dates:
            key_info.append(f"Contains dates: {', '.join(dates[:3])}")
            
        numbers = re.findall(r'\$[\d,]+\.?\d*', content)
        if numbers:
            key_info.append(f"Financial figures: {', '.join(numbers[:3])}")
            
        return key_info[:10]
        
    def _summarize_text_content(self, content: str, max_sentences: int = 3) -> str:
        """Create a summary of text content"""
        if not content:
            return "Empty document"
            
        sentences = [s.strip() for s in content.split('.') if s.strip()]
        
        if len(sentences) <= max_sentences:
            return '. '.join(sentences)
        else:
            # Take first and last sentences, and one from middle
            summary_sentences = [
                sentences[0],
                sentences[len(sentences)//2],
                sentences[-1]
            ]
            return '. '.join(summary_sentences)
            
    def _extract_pdf_info(self, content: str) -> List[str]:
        """Extract basic info from PDF content (simplified)"""
        # In a real implementation, this would use PDF parsing libraries
        return ["PDF document - requires specialized parsing"]
        
    def _extract_spreadsheet_info(self, content: str) -> List[str]:
        """Extract info from spreadsheet content"""
        # In a real implementation, this would parse CSV/Excel data
        lines = content.split('\n')[:5]  # First 5 lines
        return [f"Data row: {line[:50]}..." for line in lines if line.strip()]
        
    def _assess_file_security(self, filename: str, file_type: str, content: str) -> str:
        """Assess the security risk of a file"""
        dangerous_types = ['exe', 'bat', 'scr', 'vbs', 'js']
        if file_type in dangerous_types:
            return 'high_risk'
            
        suspicious_patterns = ['script', 'macro', 'executable']
        if any(pattern in content.lower() for pattern in suspicious_patterns):
            return 'medium_risk'
            
        return 'low_risk'

# Test the smart summarizer
async def test_smart_summarizer():
    """Test function for the smart summarizer"""
    summarizer = SmartSummarizer()
    await summarizer.initialize()
    
    # Test email thread
    test_emails = [
        {
            'sender': 'john@company.com',
            'recipients': ['team@company.com'],
            'subject': 'Q4 Planning Meeting',
            'content': '''Hi team,

I wanted to schedule our Q4 planning meeting. We need to discuss budget allocation, project priorities, and resource planning.

Key topics:
1. Budget review for next quarter
2. New project proposals
3. Team restructuring

Please let me know your availability for next week. This is urgent as we need to finalize plans by Friday.

Best regards,
John''',
            'timestamp': datetime.now() - timedelta(hours=2)
        },
        {
            'sender': 'sarah@company.com',
            'recipients': ['john@company.com', 'team@company.com'],
            'subject': 'Re: Q4 Planning Meeting',
            'content': '''John,

Great idea! I'm available Tuesday or Wednesday afternoon. 

Regarding the budget review, I have some concerns about the current allocation for the marketing project. We might need to reallocate funds.

Action item: I'll prepare a detailed budget analysis by Monday.

Thanks,
Sarah''',
            'timestamp': datetime.now() - timedelta(hours=1)
        }
    ]
    
    print("📊 Smart Email Summarization Demo")
    print("=" * 50)
    
    # Test thread summarization
    summary = await summarizer.summarize_email_thread(test_emails)
    
    print(f"Thread ID: {summary.thread_id}")
    print(f"Participants: {', '.join(summary.participants)}")
    print(f"Priority: {summary.priority_level}")
    print(f"Sentiment: {summary.sentiment}")
    print(f"Compression: {summary.original_count} → {summary.word_count} words ({summary.compression_ratio:.1%})")
    print()
    print("Summary:")
    print(summary.summary_text)
    print()
    print("Key Points:")
    for i, point in enumerate(summary.key_points, 1):
        print(f"{i}. {point}")
    print()
    print("Action Items:")
    for i, item in enumerate(summary.action_items, 1):
        print(f"{i}. {item}")
    
    # Test attachment summarization
    test_attachment = {
        'filename': 'budget_report.txt',
        'content': '''Q4 Budget Report

Total Budget: $500,000
Allocated: $450,000
Remaining: $50,000

Department Allocations:
- Marketing: $200,000
- Development: $180,000
- Operations: $70,000

Key concerns:
1. Marketing budget may be insufficient
2. Development needs additional resources for new project
3. Operations running efficiently within budget''',
        'type': 'txt'
    }
    
    attachment_summary = await summarizer.summarize_attachment(test_attachment)
    
    print("\n📎 Attachment Summary:")
    print("=" * 30)
    print(f"File: {attachment_summary.filename}")
    print(f"Type: {attachment_summary.file_type}")
    print(f"Security: {attachment_summary.security_assessment}")
    print(f"Summary: {attachment_summary.content_summary}")
    print("Key Information:")
    for info in attachment_summary.key_information:
        print(f"- {info}")
    
    print("\n✅ Smart Summarizer Test Complete!")

if __name__ == "__main__":
    asyncio.run(test_smart_summarizer())