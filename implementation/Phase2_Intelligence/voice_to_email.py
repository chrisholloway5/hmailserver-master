"""
Voice-to-Email Transcription Engine for hMailServer Phase 2
Advanced speech recognition, transcription, and email composition
"""

import asyncio
import logging
from typing import Dict, List, Optional, Tuple
import json
from datetime import datetime
import re
from dataclasses import dataclass
import base64
from io import BytesIO

logger = logging.getLogger(__name__)

@dataclass
class AudioSegment:
    data: bytes
    sample_rate: int
    channels: int
    duration: float
    format: str

@dataclass
class TranscriptionResult:
    text: str
    confidence: float
    language: str
    speaker_id: Optional[str]
    timestamps: List[Tuple[float, float, str]]  # start, end, text
    
@dataclass
class VoiceCommand:
    action: str  # 'compose', 'reply', 'forward', 'delete', 'save_draft'
    target: Optional[str]
    content: str
    confidence: float
    metadata: Dict

@dataclass
class EmailComposition:
    to: List[str]
    cc: List[str]
    bcc: List[str]
    subject: str
    body: str
    priority: str
    attachments: List[str]
    voice_metadata: Dict

class VoiceToEmailEngine:
    """
    Advanced voice-to-email transcription and composition system
    """
    
    def __init__(self):
        self.supported_formats = ['wav', 'mp3', 'flac', 'ogg', 'm4a']
        self.supported_languages = ['en-US', 'en-GB', 'es-ES', 'fr-FR', 'de-DE', 'ja-JP', 'zh-CN']
        self.voice_commands = {}
        self.speaker_profiles = {}
        self.transcription_cache = {}
        self.email_templates = {}
        self.noise_reduction_enabled = True
        self.auto_punctuation = True
        self.speaker_identification = True
        self.initialized = False
        
        # Initialize configurations
        self._initialize_voice_commands()
        self._initialize_email_templates()
        
    async def initialize(self):
        """Initialize the voice-to-email engine"""
        try:
            # Initialize speech recognition models
            await self._initialize_speech_models()
            
            # Load speaker profiles
            self._load_speaker_profiles()
            
            # Setup audio processing pipeline
            self._setup_audio_pipeline()
            
            self.initialized = True
            logger.info("Voice-to-Email Engine initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Voice-to-Email Engine: {e}")
            self.initialized = True  # Continue with limited functionality
            
    def _initialize_voice_commands(self):
        """Initialize voice command patterns"""
        self.voice_commands = {
            'compose': {
                'patterns': [
                    r'compose.*email',
                    r'write.*email',
                    r'send.*email.*to',
                    r'new.*message',
                    r'create.*email'
                ],
                'confidence_threshold': 0.7
            },
            'reply': {
                'patterns': [
                    r'reply.*to',
                    r'respond.*to',
                    r'answer.*email',
                    r'reply.*with'
                ],
                'confidence_threshold': 0.8
            },
            'forward': {
                'patterns': [
                    r'forward.*to',
                    r'send.*this.*to',
                    r'share.*with'
                ],
                'confidence_threshold': 0.8
            },
            'save_draft': {
                'patterns': [
                    r'save.*draft',
                    r'save.*as.*draft',
                    r'draft.*this'
                ],
                'confidence_threshold': 0.9
            },
            'delete': {
                'patterns': [
                    r'delete.*email',
                    r'remove.*message',
                    r'trash.*this'
                ],
                'confidence_threshold': 0.9
            },
            'schedule': {
                'patterns': [
                    r'schedule.*email',
                    r'send.*later',
                    r'delay.*send'
                ],
                'confidence_threshold': 0.8
            }
        }
        
    def _initialize_email_templates(self):
        """Initialize email templates for voice composition"""
        self.email_templates = {
            'meeting_request': {
                'subject_template': 'Meeting Request: {topic}',
                'body_template': '''Hi {recipient},

I would like to schedule a meeting to discuss {topic}.

Proposed details:
- Date: {date}
- Time: {time}
- Duration: {duration}
- Location: {location}

Please let me know if this works for you.

Best regards,
{sender}''',
                'required_fields': ['recipient', 'topic', 'date', 'time']
            },
            'status_update': {
                'subject_template': 'Status Update: {project}',
                'body_template': '''Hi {recipient},

Here's a status update on {project}:

{content}

Current status: {status}
Next steps: {next_steps}

Please let me know if you have any questions.

Best regards,
{sender}''',
                'required_fields': ['recipient', 'project', 'content', 'status']
            },
            'quick_response': {
                'subject_template': 'Re: {original_subject}',
                'body_template': '''Hi {recipient},

{content}

Thanks,
{sender}''',
                'required_fields': ['recipient', 'content']
            },
            'follow_up': {
                'subject_template': 'Follow-up: {topic}',
                'body_template': '''Hi {recipient},

I wanted to follow up on {topic}.

{content}

Please let me know your thoughts.

Best regards,
{sender}''',
                'required_fields': ['recipient', 'topic', 'content']
            }
        }
        
    async def _initialize_speech_models(self):
        """Initialize speech recognition models"""
        # Simplified model initialization
        # In a real implementation, this would load trained ASR models
        
        self.speech_models = {
            'en-US': {
                'acoustic_model': 'whisper_base_en',
                'language_model': 'transformer_lm_en',
                'confidence_threshold': 0.7
            },
            'en-GB': {
                'acoustic_model': 'whisper_base_en',
                'language_model': 'transformer_lm_en_gb',
                'confidence_threshold': 0.7
            }
        }
        
        # Initialize audio processing parameters
        self.audio_config = {
            'sample_rate': 16000,
            'channels': 1,
            'bit_depth': 16,
            'frame_size': 512,
            'hop_length': 256,
            'noise_gate_threshold': -40,  # dB
            'silence_threshold': -50,     # dB
            'max_silence_duration': 2.0   # seconds
        }
        
        logger.info("Speech recognition models initialized")
        
    def _load_speaker_profiles(self):
        """Load speaker profiles for identification"""
        self.speaker_profiles = {
            'john_doe': {
                'name': 'John Doe',
                'email': 'john.doe@company.com',
                'voice_signature': 'speaker_embedding_john',
                'preferred_language': 'en-US',
                'common_phrases': ['let me know', 'sounds good', 'thanks'],
                'email_style': 'professional',
                'auto_signature': True
            },
            'sarah_wilson': {
                'name': 'Sarah Wilson',
                'email': 'sarah.wilson@company.com',
                'voice_signature': 'speaker_embedding_sarah',
                'preferred_language': 'en-US',
                'common_phrases': ['hope this helps', 'please confirm', 'best regards'],
                'email_style': 'formal',
                'auto_signature': True
            }
        }
        
    def _setup_audio_pipeline(self):
        """Setup audio processing pipeline"""
        self.audio_pipeline = {
            'preprocessing': [
                'noise_reduction',
                'normalization',
                'silence_removal',
                'format_conversion'
            ],
            'feature_extraction': [
                'mfcc',
                'spectral_features',
                'prosodic_features'
            ],
            'postprocessing': [
                'punctuation_restoration',
                'capitalization',
                'spell_correction'
            ]
        }
        
    async def transcribe_audio(self, audio_data: bytes, format: str = 'wav', 
                             language: str = 'en-US') -> TranscriptionResult:
        """
        Transcribe audio to text
        
        Args:
            audio_data: Raw audio data
            format: Audio format (wav, mp3, etc.)
            language: Language code for transcription
            
        Returns:
            TranscriptionResult with transcribed text and metadata
        """
        if not self.initialized:
            await self.initialize()
            
        try:
            # Validate input
            if format not in self.supported_formats:
                raise ValueError(f"Unsupported audio format: {format}")
                
            if language not in self.supported_languages:
                language = 'en-US'  # Default fallback
                
            # Process audio
            audio_segment = await self._process_audio(audio_data, format)
            
            # Perform transcription
            raw_transcription = await self._perform_transcription(audio_segment, language)
            
            # Post-process transcription
            processed_text = await self._post_process_transcription(raw_transcription, language)
            
            # Speaker identification
            speaker_id = None
            if self.speaker_identification:
                speaker_id = await self._identify_speaker(audio_segment)
                
            # Create result
            result = TranscriptionResult(
                text=processed_text['text'],
                confidence=processed_text['confidence'],
                language=language,
                speaker_id=speaker_id,
                timestamps=processed_text.get('timestamps', [])
            )
            
            # Cache result
            cache_key = self._generate_cache_key(audio_data, format, language)
            self.transcription_cache[cache_key] = result
            
            logger.info(f"Transcribed {len(audio_data)} bytes with confidence {result.confidence:.2f}")
            return result
            
        except Exception as e:
            logger.error(f"Error transcribing audio: {e}")
            # Return safe fallback
            return TranscriptionResult(
                text="[Transcription failed]",
                confidence=0.0,
                language=language,
                speaker_id=None,
                timestamps=[]
            )
            
    async def _process_audio(self, audio_data: bytes, format: str) -> AudioSegment:
        """Process raw audio data"""
        
        # Convert to standard format if needed
        if format != 'wav':
            audio_data = await self._convert_audio_format(audio_data, format, 'wav')
            
        # Parse audio properties
        try:
            # Simplified audio parsing (in reality would use proper audio libraries)
            # For demo purposes, assume standard format
            sample_rate = 16000
            channels = 1
            duration = len(audio_data) / (sample_rate * 2 * channels)  # 16-bit samples
            
            audio_segment = AudioSegment(
                data=audio_data,
                sample_rate=sample_rate,
                channels=channels,
                duration=duration,
                format='wav'
            )
            
            # Apply audio preprocessing
            if self.noise_reduction_enabled:
                audio_segment = await self._reduce_noise(audio_segment)
                
            audio_segment = await self._normalize_audio(audio_segment)
            audio_segment = await self._remove_silence(audio_segment)
            
            return audio_segment
            
        except Exception as e:
            logger.error(f"Error processing audio: {e}")
            # Return minimal audio segment
            return AudioSegment(
                data=audio_data,
                sample_rate=16000,
                channels=1,
                duration=1.0,
                format='wav'
            )
            
    async def _convert_audio_format(self, audio_data: bytes, from_format: str, to_format: str) -> bytes:
        """Convert audio between formats"""
        # Simplified format conversion
        # In a real implementation, would use ffmpeg or similar
        logger.info(f"Converting audio from {from_format} to {to_format}")
        return audio_data  # Placeholder
        
    async def _reduce_noise(self, audio_segment: AudioSegment) -> AudioSegment:
        """Apply noise reduction to audio"""
        # Simplified noise reduction
        # In reality would use spectral subtraction or Wiener filtering
        logger.debug("Applying noise reduction")
        return audio_segment
        
    async def _normalize_audio(self, audio_segment: AudioSegment) -> AudioSegment:
        """Normalize audio levels"""
        # Simplified normalization
        logger.debug("Normalizing audio levels")
        return audio_segment
        
    async def _remove_silence(self, audio_segment: AudioSegment) -> AudioSegment:
        """Remove silence from audio"""
        # Simplified silence removal
        logger.debug("Removing silence")
        return audio_segment
        
    async def _perform_transcription(self, audio_segment: AudioSegment, language: str) -> Dict:
        """Perform actual speech-to-text transcription"""
        
        # Simplified transcription simulation
        # In a real implementation, would use Whisper, SpeechRecognition, or cloud APIs
        
        sample_texts = [
            "Compose an email to john.doe@company.com with subject Project Update. Hi John, I wanted to give you a quick update on the project. We're making good progress and should be on track for the deadline. Let me know if you have any questions. Thanks.",
            "Reply to the last email and say thanks for the information, I'll review it and get back to you by tomorrow.",
            "Forward this email to the development team and add a note saying please review this for technical accuracy.",
            "Send an email to sarah.wilson@company.com about the meeting tomorrow. Hi Sarah, just confirming our meeting tomorrow at 2 PM in conference room A. We'll be discussing the quarterly review. See you then.",
            "Save this as a draft. Meeting request for next week to discuss the new project requirements and timeline."
        ]
        
        # Simulate transcription based on audio duration
        duration = audio_segment.duration
        
        if duration < 5:
            text = "Compose email to team."
        elif duration < 15:
            text = sample_texts[0][:100] + "..."
        else:
            text = sample_texts[min(int(duration / 15), len(sample_texts) - 1)]
            
        # Simulate confidence based on audio quality
        confidence = max(0.6, min(0.95, 0.7 + (duration / 30)))
        
        # Generate timestamps
        words = text.split()
        timestamps = []
        current_time = 0.0
        
        for word in words:
            word_duration = max(0.1, len(word) * 0.08)  # Rough estimate
            timestamps.append((current_time, current_time + word_duration, word))
            current_time += word_duration + 0.05  # Small pause between words
            
        return {
            'text': text,
            'confidence': confidence,
            'timestamps': timestamps,
            'language': language
        }
        
    async def _post_process_transcription(self, raw_transcription: Dict, language: str) -> Dict:
        """Post-process transcribed text"""
        
        text = raw_transcription['text']
        
        # Auto-punctuation
        if self.auto_punctuation:
            text = await self._add_punctuation(text)
            
        # Capitalization
        text = await self._fix_capitalization(text)
        
        # Spell correction
        text = await self._correct_spelling(text)
        
        # Email-specific processing
        text = await self._process_email_content(text)
        
        result = raw_transcription.copy()
        result['text'] = text
        
        return result
        
    async def _add_punctuation(self, text: str) -> str:
        """Add punctuation to transcribed text"""
        # Simplified punctuation restoration
        # In reality would use trained punctuation models
        
        # Add periods at natural breaks
        text = re.sub(r'\b(compose|send|forward|reply)\b', r'\1.', text, flags=re.IGNORECASE)
        text = re.sub(r'\b(thanks|regards|sincerely)\b\s*$', r'\1.', text, flags=re.IGNORECASE)
        
        # Add commas
        text = re.sub(r'\b(hi|hello|dear)\s+(\w+)', r'\1 \2,', text, flags=re.IGNORECASE)
        
        # Question marks
        text = re.sub(r'\b(what|when|where|why|how|can|could|would|will)\b([^.!?]*?)(?=\s|$)', 
                     r'\1\2?', text, flags=re.IGNORECASE)
        
        return text
        
    async def _fix_capitalization(self, text: str) -> str:
        """Fix capitalization in transcribed text"""
        # Capitalize first letter
        if text:
            text = text[0].upper() + text[1:]
            
        # Capitalize after periods
        text = re.sub(r'\.(\s+)([a-z])', lambda m: '.' + m.group(1) + m.group(2).upper(), text)
        
        # Capitalize email addresses context
        text = re.sub(r'\bemail\s+to\s+([a-z])', 
                     lambda m: 'email to ' + m.group(1).upper(), text, flags=re.IGNORECASE)
        
        return text
        
    async def _correct_spelling(self, text: str) -> str:
        """Correct common spelling errors"""
        # Simple spelling corrections for common voice recognition errors
        corrections = {
            'email': ['e-mail', 'e mail', 'emale'],
            'compose': ['compos', 'compoes'],
            'subject': ['subjectt', 'subject'],
            'message': ['mesage', 'messag'],
            'meeting': ['meting', 'meetng'],
            'tomorrow': ['tomorow', 'tommorow'],
            'conference': ['conferenc', 'conferense']
        }
        
        for correct, variants in corrections.items():
            for variant in variants:
                text = re.sub(r'\b' + re.escape(variant) + r'\b', correct, text, flags=re.IGNORECASE)
                
        return text
        
    async def _process_email_content(self, text: str) -> str:
        """Process email-specific content in transcription"""
        # Extract email addresses
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        emails = re.findall(email_pattern, text)
        
        # Format email addresses properly
        for email in emails:
            text = text.replace(email, f'<{email}>')
            
        # Format subject lines
        subject_pattern = r'(?:with\s+)?subject\s+([^.!?]+)'
        text = re.sub(subject_pattern, r'with subject "\1"', text, flags=re.IGNORECASE)
        
        return text
        
    async def _identify_speaker(self, audio_segment: AudioSegment) -> Optional[str]:
        """Identify speaker from voice characteristics"""
        # Simplified speaker identification
        # In reality would use voice embeddings and speaker verification models
        
        # For demo, randomly assign a known speaker
        import random
        speakers = list(self.speaker_profiles.keys())
        
        if speakers and random.random() > 0.3:  # 70% chance of identification
            return random.choice(speakers)
            
        return None
        
    async def parse_voice_command(self, transcription: TranscriptionResult) -> List[VoiceCommand]:
        """
        Parse voice commands from transcription
        
        Args:
            transcription: Transcribed text result
            
        Returns:
            List of parsed voice commands
        """
        commands = []
        text = transcription.text.lower()
        
        for action, config in self.voice_commands.items():
            for pattern in config['patterns']:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                
                for match in matches:
                    confidence = transcription.confidence * 0.9  # Adjust for command parsing
                    
                    if confidence >= config['confidence_threshold']:
                        # Extract command details
                        command_text = match.group(0)
                        remaining_text = text[match.end():].strip()
                        
                        # Extract target (email address, person name, etc.)
                        target = await self._extract_command_target(remaining_text, action)
                        
                        command = VoiceCommand(
                            action=action,
                            target=target,
                            content=remaining_text,
                            confidence=confidence,
                            metadata={
                                'pattern_matched': pattern,
                                'command_text': command_text,
                                'speaker_id': transcription.speaker_id
                            }
                        )
                        
                        commands.append(command)
                        
        # Sort by confidence
        commands.sort(key=lambda c: c.confidence, reverse=True)
        
        return commands
        
    async def _extract_command_target(self, text: str, action: str) -> Optional[str]:
        """Extract target from command text"""
        
        # Email address extraction
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        emails = re.findall(email_pattern, text)
        if emails:
            return emails[0]
            
        # Name extraction for known contacts
        for speaker_id, profile in self.speaker_profiles.items():
            name_parts = profile['name'].lower().split()
            for part in name_parts:
                if part in text:
                    return profile['email']
                    
        # Department/team extraction
        departments = ['team', 'support', 'sales', 'hr', 'engineering', 'marketing']
        for dept in departments:
            if dept in text:
                return f'{dept}@company.com'
                
        return None
        
    async def compose_email_from_voice(self, command: VoiceCommand, 
                                     transcription: TranscriptionResult) -> EmailComposition:
        """
        Compose email from voice command
        
        Args:
            command: Parsed voice command
            transcription: Original transcription
            
        Returns:
            Composed email structure
        """
        try:
            # Initialize email composition
            composition = EmailComposition(
                to=[],
                cc=[],
                bcc=[],
                subject='',
                body='',
                priority='normal',
                attachments=[],
                voice_metadata={
                    'transcription_confidence': transcription.confidence,
                    'command_confidence': command.confidence,
                    'speaker_id': transcription.speaker_id,
                    'language': transcription.language,
                    'voice_command': command.action
                }
            )
            
            # Extract email details from voice content
            email_details = await self._extract_email_details(command.content, transcription)
            
            # Set recipients
            if command.target:
                composition.to = [command.target]
            elif email_details.get('recipients'):
                composition.to = email_details['recipients']
                
            # Set subject
            composition.subject = email_details.get('subject', 'Voice Message')
            
            # Compose body
            composition.body = await self._compose_email_body(
                email_details, command, transcription
            )
            
            # Set priority based on voice urgency
            composition.priority = await self._detect_email_priority(command.content)
            
            # Add speaker signature if available
            if transcription.speaker_id:
                speaker_profile = self.speaker_profiles.get(transcription.speaker_id)
                if speaker_profile and speaker_profile.get('auto_signature'):
                    composition.body += f"\n\nBest regards,\n{speaker_profile['name']}"
                    
            return composition
            
        except Exception as e:
            logger.error(f"Error composing email from voice: {e}")
            # Return basic composition
            return EmailComposition(
                to=[command.target] if command.target else [],
                cc=[],
                bcc=[],
                subject='Voice Message',
                body=transcription.text,
                priority='normal',
                attachments=[],
                voice_metadata={'error': str(e)}
            )
            
    async def _extract_email_details(self, content: str, transcription: TranscriptionResult) -> Dict:
        """Extract email details from voice content"""
        details = {}
        
        # Extract subject
        subject_patterns = [
            r'(?:with\s+)?subject\s+["\']?([^"\'.\n]+)["\']?',
            r'(?:title|header)\s+["\']?([^"\'.\n]+)["\']?',
            r'about\s+([^.\n]+)'
        ]
        
        for pattern in subject_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                details['subject'] = match.group(1).strip()
                break
                
        # Extract recipients
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        recipients = re.findall(email_pattern, content)
        if recipients:
            details['recipients'] = recipients
            
        # Extract body content (everything after command)
        command_patterns = [
            r'(?:compose|write|send).*?(?:email|message).*?(?:to\s+\S+\s+)?(?:with\s+subject\s+[^.]+\.?\s*)?(.+)',
            r'(?:say|write|tell them)\s+(.+)',
            r'(?:message|content|body)\s+(.+)'
        ]
        
        for pattern in command_patterns:
            match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)
            if match:
                details['body_content'] = match.group(1).strip()
                break
                
        if not details.get('body_content'):
            # Use full content as body if no specific body found
            details['body_content'] = content
            
        return details
        
    async def _compose_email_body(self, email_details: Dict, command: VoiceCommand, 
                                transcription: TranscriptionResult) -> str:
        """Compose email body from extracted details"""
        
        body_content = email_details.get('body_content', transcription.text)
        
        # Clean up the body content
        body_content = await self._clean_email_body(body_content)
        
        # Apply template if suitable
        template_name = await self._detect_email_template(body_content, command)
        if template_name:
            body_content = await self._apply_email_template(
                template_name, body_content, email_details
            )
            
        return body_content
        
    async def _clean_email_body(self, content: str) -> str:
        """Clean up email body content"""
        
        # Remove command prefixes
        command_prefixes = [
            r'^(?:compose|write|send)\s+(?:an?\s+)?email\s+(?:to\s+\S+\s+)?',
            r'^(?:with\s+)?subject\s+[^.]+\.\s*',
            r'^(?:say|tell them|message)\s+'
        ]
        
        for prefix in command_prefixes:
            content = re.sub(prefix, '', content, flags=re.IGNORECASE)
            
        # Clean up extra whitespace
        content = re.sub(r'\s+', ' ', content).strip()
        
        # Ensure proper sentence structure
        if content and not content[0].isupper():
            content = content[0].upper() + content[1:]
            
        if content and content[-1] not in '.!?':
            content += '.'
            
        return content
        
    async def _detect_email_template(self, content: str, command: VoiceCommand) -> Optional[str]:
        """Detect if content matches an email template"""
        
        content_lower = content.lower()
        
        # Check for meeting-related content
        meeting_keywords = ['meeting', 'schedule', 'appointment', 'call', 'conference']
        if any(keyword in content_lower for keyword in meeting_keywords):
            return 'meeting_request'
            
        # Check for status update
        status_keywords = ['update', 'progress', 'status', 'report']
        if any(keyword in content_lower for keyword in status_keywords):
            return 'status_update'
            
        # Check for follow-up
        followup_keywords = ['follow up', 'following up', 'check in', 'touch base']
        if any(keyword in content_lower for keyword in followup_keywords):
            return 'follow_up'
            
        # Quick response for short messages
        if len(content.split()) < 20:
            return 'quick_response'
            
        return None
        
    async def _apply_email_template(self, template_name: str, content: str, 
                                  email_details: Dict) -> str:
        """Apply email template to content"""
        
        template = self.email_templates.get(template_name)
        if not template:
            return content
            
        # Extract template variables from content
        template_vars = {
            'content': content,
            'sender': 'Voice User',  # Default
            'recipient': 'Recipient'  # Default
        }
        
        # Try to extract specific variables
        if template_name == 'meeting_request':
            template_vars.update(await self._extract_meeting_variables(content))
        elif template_name == 'status_update':
            template_vars.update(await self._extract_status_variables(content))
        elif template_name == 'follow_up':
            template_vars.update(await self._extract_followup_variables(content))
            
        # Apply template
        try:
            formatted_body = template['body_template'].format(**template_vars)
            return formatted_body
        except KeyError:
            # Return original content if template formatting fails
            return content
            
    async def _extract_meeting_variables(self, content: str) -> Dict:
        """Extract meeting-specific variables"""
        variables = {}
        
        # Extract topic
        topic_patterns = [
            r'(?:about|regarding|discuss)\s+([^.!?\n]+)',
            r'(?:meeting|call)\s+(?:for|about)\s+([^.!?\n]+)'
        ]
        
        for pattern in topic_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                variables['topic'] = match.group(1).strip()
                break
                
        # Extract date/time (simplified)
        time_patterns = [
            r'(?:tomorrow|next\s+week|monday|tuesday|wednesday|thursday|friday)',
            r'(?:at\s+)?(\d{1,2}(?::\d{2})?\s*(?:am|pm)?)',
            r'(?:on\s+)?(\w+day)'
        ]
        
        for pattern in time_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                variables['date'] = match.group(0)
                variables['time'] = match.group(1) if match.lastindex else match.group(0)
                break
                
        return variables
        
    async def _extract_status_variables(self, content: str) -> Dict:
        """Extract status update variables"""
        variables = {}
        
        # Extract project name
        project_patterns = [
            r'(?:project|work)\s+([^.!?\n]+)',
            r'(?:on|for)\s+the\s+([^.!?\n]+)\s+project'
        ]
        
        for pattern in project_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                variables['project'] = match.group(1).strip()
                break
                
        # Extract status
        status_patterns = [
            r'(?:status|progress)\s+(?:is\s+)?([^.!?\n]+)',
            r'(?:currently|now)\s+([^.!?\n]+)'
        ]
        
        for pattern in status_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                variables['status'] = match.group(1).strip()
                break
                
        return variables
        
    async def _extract_followup_variables(self, content: str) -> Dict:
        """Extract follow-up variables"""
        variables = {}
        
        # Extract topic
        topic_patterns = [
            r'(?:follow(?:ing)?\s+up\s+on)\s+([^.!?\n]+)',
            r'(?:regarding|about)\s+([^.!?\n]+)'
        ]
        
        for pattern in topic_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                variables['topic'] = match.group(1).strip()
                break
                
        return variables
        
    async def _detect_email_priority(self, content: str) -> str:
        """Detect email priority from voice content"""
        content_lower = content.lower()
        
        # High priority indicators
        high_priority = ['urgent', 'critical', 'asap', 'emergency', 'immediately', 'rush']
        if any(indicator in content_lower for indicator in high_priority):
            return 'high'
            
        # Low priority indicators
        low_priority = ['when you can', 'no rush', 'fyi', 'for your information', 'heads up']
        if any(indicator in content_lower for indicator in low_priority):
            return 'low'
            
        return 'normal'
        
    def _generate_cache_key(self, audio_data: bytes, format: str, language: str) -> str:
        """Generate cache key for transcription"""
        import hashlib
        data_hash = hashlib.md5(audio_data).hexdigest()
        return f"{data_hash}_{format}_{language}"
        
    def get_transcription_analytics(self) -> Dict:
        """Get analytics on transcription performance"""
        total_transcriptions = len(self.transcription_cache)
        
        if total_transcriptions == 0:
            return {'total_transcriptions': 0, 'analytics': 'No transcription history'}
            
        # Calculate average confidence
        confidences = [result.confidence for result in self.transcription_cache.values()]
        avg_confidence = sum(confidences) / len(confidences)
        
        # Language distribution
        languages = [result.language for result in self.transcription_cache.values()]
        language_dist = {lang: languages.count(lang) for lang in set(languages)}
        
        # Speaker distribution
        speakers = [result.speaker_id for result in self.transcription_cache.values() 
                   if result.speaker_id]
        speaker_dist = {speaker: speakers.count(speaker) for speaker in set(speakers)}
        
        return {
            'total_transcriptions': total_transcriptions,
            'average_confidence': avg_confidence,
            'language_distribution': language_dist,
            'speaker_distribution': speaker_dist,
            'cache_size': len(self.transcription_cache)
        }

# Test the voice-to-email engine
async def test_voice_to_email():
    """Test function for the voice-to-email engine"""
    engine = VoiceToEmailEngine()
    await engine.initialize()
    
    print("🎤 Voice-to-Email Transcription Demo")
    print("=" * 50)
    
    # Simulate audio data (in reality would be actual audio bytes)
    test_audio_scenarios = [
        {
            'description': 'Meeting Request',
            'simulated_duration': 20.0,
            'format': 'wav'
        },
        {
            'description': 'Quick Response',
            'simulated_duration': 5.0,
            'format': 'wav'
        },
        {
            'description': 'Status Update',
            'simulated_duration': 30.0,
            'format': 'wav'
        }
    ]
    
    for i, scenario in enumerate(test_audio_scenarios, 1):
        print(f"\n🎵 Test Scenario {i}: {scenario['description']}")
        print(f"Duration: {scenario['simulated_duration']}s")
        
        # Create dummy audio data
        audio_data = b'\x00' * int(scenario['simulated_duration'] * 16000 * 2)  # 16kHz, 16-bit
        
        # Transcribe audio
        transcription = await engine.transcribe_audio(
            audio_data, 
            format=scenario['format'], 
            language='en-US'
        )
        
        print(f"\n📝 Transcription Result:")
        print(f"Text: {transcription.text}")
        print(f"Confidence: {transcription.confidence:.2f}")
        print(f"Language: {transcription.language}")
        print(f"Speaker: {transcription.speaker_id or 'Unknown'}")
        
        # Parse voice commands
        commands = await engine.parse_voice_command(transcription)
        
        print(f"\n🎯 Voice Commands ({len(commands)} found):")
        for j, command in enumerate(commands, 1):
            print(f"{j}. Action: {command.action.upper()}")
            print(f"   Target: {command.target or 'Not specified'}")
            print(f"   Confidence: {command.confidence:.2f}")
            
            # Compose email if it's a compose command
            if command.action == 'compose':
                email = await engine.compose_email_from_voice(command, transcription)
                
                print(f"\n📧 Composed Email:")
                print(f"To: {', '.join(email.to)}")
                print(f"Subject: {email.subject}")
                print(f"Priority: {email.priority}")
                print(f"Body Preview: {email.body[:200]}...")
                print(f"Voice Metadata: {email.voice_metadata}")
        
        print("-" * 40)
    
    # Show analytics
    analytics = engine.get_transcription_analytics()
    print(f"\n📊 Transcription Analytics:")
    print(f"Total Transcriptions: {analytics['total_transcriptions']}")
    print(f"Average Confidence: {analytics['average_confidence']:.2f}")
    print(f"Language Distribution: {analytics['language_distribution']}")
    print(f"Speaker Distribution: {analytics['speaker_distribution']}")
    
    print("\n✅ Voice-to-Email Engine Test Complete!")

if __name__ == "__main__":
    asyncio.run(test_voice_to_email())