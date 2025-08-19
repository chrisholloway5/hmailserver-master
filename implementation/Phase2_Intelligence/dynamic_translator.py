"""
Dynamic Translation Engine for hMailServer Phase 2
Real-time multi-language email translation with context awareness
"""

import asyncio
import logging
from typing import Dict, List, Optional, Tuple, Set
import json
from datetime import datetime
import re
from dataclasses import dataclass
from collections import defaultdict
import hashlib

logger = logging.getLogger(__name__)

@dataclass
class LanguageProfile:
    code: str
    name: str
    native_name: str
    script: str
    direction: str  # 'ltr' or 'rtl'
    confidence_threshold: float

@dataclass
class TranslationResult:
    original_text: str
    translated_text: str
    source_language: str
    target_language: str
    confidence: float
    translation_method: str
    metadata: Dict

@dataclass
class ContextualTranslation:
    text: str
    context_type: str  # 'business', 'technical', 'casual', 'formal'
    domain: str       # 'email', 'legal', 'medical', 'finance'
    tone: str         # 'professional', 'friendly', 'urgent', 'polite'
    formality: str    # 'formal', 'informal', 'neutral'

@dataclass
class TranslationQuality:
    fluency_score: float
    adequacy_score: float
    context_preservation: float
    tone_preservation: float
    overall_score: float

class DynamicTranslationEngine:
    """
    Advanced multi-language translation engine with context awareness
    """
    
    def __init__(self):
        self.supported_languages = {}
        self.translation_models = {}
        self.context_analyzers = {}
        self.quality_assessors = {}
        self.translation_cache = {}
        self.user_preferences = {}
        self.domain_dictionaries = {}
        self.phrase_patterns = {}
        self.cultural_adaptations = {}
        self.initialized = False
        
        # Initialize language configurations
        self._initialize_language_profiles()
        self._initialize_domain_dictionaries()
        self._initialize_cultural_adaptations()
        
    async def initialize(self):
        """Initialize the translation engine"""
        try:
            # Load translation models
            await self._load_translation_models()
            
            # Initialize context analyzers
            await self._initialize_context_analyzers()
            
            # Setup quality assessment
            self._initialize_quality_assessors()
            
            # Load user preferences
            self._load_user_preferences()
            
            self.initialized = True
            logger.info("Dynamic Translation Engine initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Translation Engine: {e}")
            self.initialized = True  # Continue with limited functionality
            
    def _initialize_language_profiles(self):
        """Initialize supported language profiles"""
        self.supported_languages = {
            'en': LanguageProfile('en', 'English', 'English', 'Latin', 'ltr', 0.8),
            'es': LanguageProfile('es', 'Spanish', 'Español', 'Latin', 'ltr', 0.8),
            'fr': LanguageProfile('fr', 'French', 'Français', 'Latin', 'ltr', 0.8),
            'de': LanguageProfile('de', 'German', 'Deutsch', 'Latin', 'ltr', 0.8),
            'it': LanguageProfile('it', 'Italian', 'Italiano', 'Latin', 'ltr', 0.8),
            'pt': LanguageProfile('pt', 'Portuguese', 'Português', 'Latin', 'ltr', 0.8),
            'nl': LanguageProfile('nl', 'Dutch', 'Nederlands', 'Latin', 'ltr', 0.8),
            'ru': LanguageProfile('ru', 'Russian', 'Русский', 'Cyrillic', 'ltr', 0.75),
            'zh': LanguageProfile('zh', 'Chinese', '中文', 'Chinese', 'ltr', 0.75),
            'ja': LanguageProfile('ja', 'Japanese', '日本語', 'Japanese', 'ltr', 0.75),
            'ko': LanguageProfile('ko', 'Korean', '한국어', 'Korean', 'ltr', 0.75),
            'ar': LanguageProfile('ar', 'Arabic', 'العربية', 'Arabic', 'rtl', 0.7),
            'he': LanguageProfile('he', 'Hebrew', 'עברית', 'Hebrew', 'rtl', 0.7),
            'hi': LanguageProfile('hi', 'Hindi', 'हिन्दी', 'Devanagari', 'ltr', 0.7),
            'th': LanguageProfile('th', 'Thai', 'ไทย', 'Thai', 'ltr', 0.7),
            'vi': LanguageProfile('vi', 'Vietnamese', 'Tiếng Việt', 'Latin', 'ltr', 0.75),
            'tr': LanguageProfile('tr', 'Turkish', 'Türkçe', 'Latin', 'ltr', 0.75),
            'pl': LanguageProfile('pl', 'Polish', 'Polski', 'Latin', 'ltr', 0.75),
            'sv': LanguageProfile('sv', 'Swedish', 'Svenska', 'Latin', 'ltr', 0.8),
            'no': LanguageProfile('no', 'Norwegian', 'Norsk', 'Latin', 'ltr', 0.8),
            'da': LanguageProfile('da', 'Danish', 'Dansk', 'Latin', 'ltr', 0.8),
            'fi': LanguageProfile('fi', 'Finnish', 'Suomi', 'Latin', 'ltr', 0.75),
            'cs': LanguageProfile('cs', 'Czech', 'Čeština', 'Latin', 'ltr', 0.75),
            'hu': LanguageProfile('hu', 'Hungarian', 'Magyar', 'Latin', 'ltr', 0.75),
            'el': LanguageProfile('el', 'Greek', 'Ελληνικά', 'Greek', 'ltr', 0.75)
        }
        
    def _initialize_domain_dictionaries(self):
        """Initialize domain-specific dictionaries"""
        self.domain_dictionaries = {
            'business': {
                'en': {
                    'meeting': ['meeting', 'conference', 'call', 'appointment'],
                    'proposal': ['proposal', 'offer', 'suggestion', 'recommendation'],
                    'deadline': ['deadline', 'due date', 'target date', 'completion date'],
                    'contract': ['contract', 'agreement', 'terms', 'conditions'],
                    'budget': ['budget', 'cost', 'expense', 'financial'],
                    'project': ['project', 'initiative', 'task', 'assignment']
                },
                'es': {
                    'meeting': ['reunión', 'conferencia', 'llamada', 'cita'],
                    'proposal': ['propuesta', 'oferta', 'sugerencia', 'recomendación'],
                    'deadline': ['fecha límite', 'fecha de vencimiento', 'plazo'],
                    'contract': ['contrato', 'acuerdo', 'términos', 'condiciones'],
                    'budget': ['presupuesto', 'costo', 'gasto', 'financiero'],
                    'project': ['proyecto', 'iniciativa', 'tarea', 'asignación']
                }
            },
            'technical': {
                'en': {
                    'server': ['server', 'host', 'machine', 'system'],
                    'database': ['database', 'db', 'data store', 'repository'],
                    'error': ['error', 'issue', 'problem', 'bug'],
                    'security': ['security', 'authentication', 'authorization', 'access'],
                    'performance': ['performance', 'speed', 'optimization', 'efficiency'],
                    'backup': ['backup', 'restore', 'recovery', 'archive']
                },
                'es': {
                    'server': ['servidor', 'host', 'máquina', 'sistema'],
                    'database': ['base de datos', 'bd', 'almacén de datos', 'repositorio'],
                    'error': ['error', 'problema', 'fallo', 'bug'],
                    'security': ['seguridad', 'autenticación', 'autorización', 'acceso'],
                    'performance': ['rendimiento', 'velocidad', 'optimización', 'eficiencia'],
                    'backup': ['copia de seguridad', 'restaurar', 'recuperación', 'archivo']
                }
            },
            'legal': {
                'en': {
                    'liability': ['liability', 'responsibility', 'obligation', 'duty'],
                    'compliance': ['compliance', 'adherence', 'conformity', 'observance'],
                    'confidential': ['confidential', 'private', 'restricted', 'classified'],
                    'intellectual_property': ['intellectual property', 'IP', 'copyright', 'patent'],
                    'indemnity': ['indemnity', 'compensation', 'reimbursement', 'damages']
                }
            }
        }
        
    def _initialize_cultural_adaptations(self):
        """Initialize cultural adaptation rules"""
        self.cultural_adaptations = {
            'formality_levels': {
                'en': {'formal': 'Sir/Madam', 'neutral': 'Hello', 'informal': 'Hi'},
                'de': {'formal': 'Sehr geehrte Damen und Herren', 'neutral': 'Hallo', 'informal': 'Hi'},
                'fr': {'formal': 'Monsieur/Madame', 'neutral': 'Bonjour', 'informal': 'Salut'},
                'es': {'formal': 'Estimado/a Señor/a', 'neutral': 'Hola', 'informal': 'Hola'},
                'ja': {'formal': 'いつもお世話になっております', 'neutral': 'こんにちは', 'informal': 'やあ'},
                'zh': {'formal': '尊敬的先生/女士', 'neutral': '您好', 'informal': '你好'}
            },
            'time_formats': {
                'en': '12h',  # 12-hour format
                'de': '24h',  # 24-hour format
                'fr': '24h',
                'es': '24h',
                'ja': '24h',
                'zh': '24h'
            },
            'date_formats': {
                'en': 'MM/DD/YYYY',
                'de': 'DD.MM.YYYY',
                'fr': 'DD/MM/YYYY',
                'es': 'DD/MM/YYYY',
                'ja': 'YYYY/MM/DD',
                'zh': 'YYYY年MM月DD日'
            },
            'business_customs': {
                'ja': {
                    'email_opening': 'いつもお世話になっております。',
                    'email_closing': 'よろしくお願いいたします。',
                    'honorifics': True
                },
                'ko': {
                    'email_opening': '안녕하세요.',
                    'email_closing': '감사합니다.',
                    'honorifics': True
                },
                'de': {
                    'formal_address': True,
                    'title_usage': True
                },
                'fr': {
                    'formal_address': True,
                    'courtesy_expressions': True
                }
            }
        }
        
    async def _load_translation_models(self):
        """Load translation models for supported languages"""
        # Simplified model loading - in reality would load actual ML models
        self.translation_models = {
            'neural_mt': {
                'model_type': 'transformer',
                'supported_pairs': [],
                'confidence_baseline': 0.8
            },
            'statistical_mt': {
                'model_type': 'phrase_based',
                'supported_pairs': [],
                'confidence_baseline': 0.6
            },
            'rule_based': {
                'model_type': 'rule_based',
                'supported_pairs': [],
                'confidence_baseline': 0.4
            }
        }
        
        # Generate supported language pairs
        languages = list(self.supported_languages.keys())
        for source in languages:
            for target in languages:
                if source != target:
                    pair = f"{source}-{target}"
                    self.translation_models['neural_mt']['supported_pairs'].append(pair)
                    
        logger.info(f"Loaded translation models for {len(languages)} languages")
        
    async def _initialize_context_analyzers(self):
        """Initialize context analysis components"""
        self.context_analyzers = {
            'domain_classifier': {
                'business_indicators': ['meeting', 'proposal', 'deadline', 'budget', 'contract'],
                'technical_indicators': ['server', 'database', 'error', 'security', 'API'],
                'legal_indicators': ['compliance', 'liability', 'confidential', 'terms'],
                'medical_indicators': ['patient', 'diagnosis', 'treatment', 'medical'],
                'academic_indicators': ['research', 'study', 'publication', 'academic']
            },
            'tone_analyzer': {
                'formal_indicators': ['dear sir', 'yours faithfully', 'please find attached'],
                'informal_indicators': ['hey', 'thanks', 'no worries', 'catch up'],
                'urgent_indicators': ['urgent', 'asap', 'immediately', 'critical'],
                'polite_indicators': ['please', 'thank you', 'appreciate', 'kindly']
            },
            'formality_detector': {
                'formal_patterns': [
                    r'\b(?:dear|sincerely|faithfully|respectfully)\b',
                    r'\b(?:please find|attached herewith|enclosed)\b',
                    r'\b(?:kindly|would you|could you)\b'
                ],
                'informal_patterns': [
                    r'\b(?:hey|hi|thanks|cheers)\b',
                    r'\b(?:gonna|wanna|kinda)\b',
                    r'[!]{2,}|\?{2,}'
                ]
            }
        }
        
    def _initialize_quality_assessors(self):
        """Initialize translation quality assessment"""
        self.quality_assessors = {
            'fluency_metrics': {
                'perplexity_threshold': 100,
                'grammar_weight': 0.4,
                'naturalness_weight': 0.6
            },
            'adequacy_metrics': {
                'semantic_similarity_threshold': 0.7,
                'content_preservation_weight': 0.8,
                'meaning_accuracy_weight': 0.2
            },
            'context_metrics': {
                'domain_consistency_weight': 0.5,
                'tone_preservation_weight': 0.3,
                'cultural_appropriateness_weight': 0.2
            }
        }
        
    def _load_user_preferences(self):
        """Load user translation preferences"""
        self.user_preferences = {
            'default_target_language': 'en',
            'formality_level': 'neutral',
            'domain_specialization': 'business',
            'cultural_adaptation': True,
            'preserve_formatting': True,
            'auto_detect_language': True,
            'confidence_threshold': 0.7,
            'fallback_to_alternative': True
        }
        
    async def detect_language(self, text: str) -> Tuple[str, float]:
        """
        Detect the language of the input text
        
        Args:
            text: Text to analyze
            
        Returns:
            Tuple of (language_code, confidence)
        """
        if not text.strip():
            return 'unknown', 0.0
            
        try:
            # Simplified language detection
            # In reality would use language detection libraries
            
            # Check for common language indicators
            language_indicators = {
                'en': ['the', 'and', 'is', 'are', 'you', 'to', 'of', 'a', 'in', 'that'],
                'es': ['el', 'la', 'de', 'que', 'y', 'en', 'un', 'es', 'se', 'no'],
                'fr': ['le', 'de', 'et', 'à', 'un', 'il', 'être', 'et', 'en', 'avoir'],
                'de': ['der', 'die', 'und', 'in', 'den', 'von', 'zu', 'das', 'mit', 'sich'],
                'it': ['il', 'di', 'che', 'e', 'la', 'per', 'un', 'in', 'con', 'non'],
                'pt': ['o', 'de', 'e', 'que', 'do', 'da', 'em', 'um', 'para', 'com'],
                'ru': ['в', 'и', 'не', 'на', 'я', 'быть', 'тот', 'он', 'оно', 'с'],
                'zh': ['的', '一', '是', '在', '有', '了', '我', '不', '人', '也'],
                'ja': ['の', 'に', 'は', 'を', 'た', 'が', 'で', 'て', 'と', 'し'],
                'ar': ['في', 'من', 'إلى', 'على', 'هذا', 'هذه', 'التي', 'الذي', 'أن', 'كان'],
                'ko': ['이', '그', '저', '의', '를', '에', '는', '은', '도', '만']
            }
            
            text_lower = text.lower()
            word_count = len(text.split())
            
            language_scores = {}
            
            for lang, indicators in language_indicators.items():
                score = 0
                for indicator in indicators:
                    score += text_lower.count(indicator)
                    
                # Normalize by text length
                if word_count > 0:
                    language_scores[lang] = score / word_count
                else:
                    language_scores[lang] = 0
                    
            if language_scores:
                best_language = max(language_scores, key=language_scores.get)
                confidence = min(0.95, language_scores[best_language] * 5)  # Scale confidence
                
                # Minimum confidence threshold
                if confidence < 0.2:
                    return 'unknown', confidence
                    
                return best_language, confidence
            else:
                return 'unknown', 0.0
                
        except Exception as e:
            logger.error(f"Error detecting language: {e}")
            return 'unknown', 0.0
            
    async def analyze_context(self, text: str, metadata: Dict = None) -> ContextualTranslation:
        """
        Analyze text context for better translation
        
        Args:
            text: Text to analyze
            metadata: Additional context metadata
            
        Returns:
            ContextualTranslation with analysis results
        """
        try:
            # Detect domain
            domain = await self._detect_domain(text)
            
            # Analyze tone
            tone = await self._analyze_tone(text)
            
            # Detect formality level
            formality = await self._detect_formality(text)
            
            # Determine context type
            context_type = await self._determine_context_type(text, metadata)
            
            return ContextualTranslation(
                text=text,
                context_type=context_type,
                domain=domain,
                tone=tone,
                formality=formality
            )
            
        except Exception as e:
            logger.error(f"Error analyzing context: {e}")
            return ContextualTranslation(
                text=text,
                context_type='general',
                domain='general',
                tone='neutral',
                formality='neutral'
            )
            
    async def _detect_domain(self, text: str) -> str:
        """Detect the domain/subject area of the text"""
        text_lower = text.lower()
        
        domain_scores = {}
        
        for domain, languages in self.domain_dictionaries.items():
            score = 0
            
            # Check English indicators (most comprehensive)
            if 'en' in languages:
                for category, terms in languages['en'].items():
                    for term in terms:
                        if term in text_lower:
                            score += 1
                            
            domain_scores[domain] = score
            
        if domain_scores:
            best_domain = max(domain_scores, key=domain_scores.get)
            if domain_scores[best_domain] > 0:
                return best_domain
                
        return 'general'
        
    async def _analyze_tone(self, text: str) -> str:
        """Analyze the tone of the text"""
        text_lower = text.lower()
        
        tone_scores = {
            'formal': 0,
            'informal': 0,
            'urgent': 0,
            'polite': 0,
            'neutral': 1  # Base score for neutral
        }
        
        for tone, indicators in self.context_analyzers['tone_analyzer'].items():
            for indicator in indicators:
                if indicator in text_lower:
                    tone_scores[tone.replace('_indicators', '')] += 1
                    
        # Analyze punctuation patterns
        if '!' in text:
            tone_scores['urgent'] += text.count('!')
            
        if '?' in text and text.count('?') > 2:
            tone_scores['informal'] += 1
            
        best_tone = max(tone_scores, key=tone_scores.get)
        return best_tone
        
    async def _detect_formality(self, text: str) -> str:
        """Detect formality level of the text"""
        text_lower = text.lower()
        
        formal_score = 0
        informal_score = 0
        
        # Check formal patterns
        for pattern in self.context_analyzers['formality_detector']['formal_patterns']:
            matches = re.findall(pattern, text_lower)
            formal_score += len(matches)
            
        # Check informal patterns
        for pattern in self.context_analyzers['formality_detector']['informal_patterns']:
            matches = re.findall(pattern, text_lower)
            informal_score += len(matches)
            
        # Additional heuristics
        if any(word in text_lower for word in ['dear sir', 'yours sincerely', 'respectfully']):
            formal_score += 2
            
        if any(word in text_lower for word in ['hey', 'sup', 'yeah', 'nah']):
            informal_score += 2
            
        if formal_score > informal_score:
            return 'formal'
        elif informal_score > formal_score:
            return 'informal'
        else:
            return 'neutral'
            
    async def _determine_context_type(self, text: str, metadata: Dict = None) -> str:
        """Determine the overall context type"""
        if metadata:
            if metadata.get('email_type') == 'business':
                return 'business'
            elif metadata.get('sender_domain', '').endswith('.edu'):
                return 'academic'
                
        # Analyze text content
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['meeting', 'deadline', 'project', 'budget']):
            return 'business'
        elif any(word in text_lower for word in ['server', 'database', 'code', 'API']):
            return 'technical'
        elif any(word in text_lower for word in ['thanks', 'friend', 'weekend', 'party']):
            return 'casual'
        else:
            return 'general'
            
    async def translate_text(self, text: str, target_language: str, 
                           source_language: str = None, 
                           context: ContextualTranslation = None) -> TranslationResult:
        """
        Translate text to target language with context awareness
        
        Args:
            text: Text to translate
            target_language: Target language code
            source_language: Source language code (auto-detect if None)
            context: Contextual information for better translation
            
        Returns:
            TranslationResult with translated text and metadata
        """
        if not self.initialized:
            await self.initialize()
            
        try:
            # Detect source language if not provided
            if not source_language:
                source_language, lang_confidence = await self.detect_language(text)
                if source_language == 'unknown':
                    source_language = 'en'  # Default fallback
            else:
                lang_confidence = 1.0
                
            # Check if translation is needed
            if source_language == target_language:
                return TranslationResult(
                    original_text=text,
                    translated_text=text,
                    source_language=source_language,
                    target_language=target_language,
                    confidence=1.0,
                    translation_method='no_translation_needed',
                    metadata={'language_detection_confidence': lang_confidence}
                )
                
            # Check cache
            cache_key = self._generate_translation_cache_key(
                text, source_language, target_language, context
            )
            
            if cache_key in self.translation_cache:
                cached_result = self.translation_cache[cache_key]
                logger.debug(f"Using cached translation for {source_language}->{target_language}")
                return cached_result
                
            # Analyze context if not provided
            if not context:
                context = await self.analyze_context(text)
                
            # Perform translation
            translated_text = await self._perform_translation(
                text, source_language, target_language, context
            )
            
            # Apply cultural adaptations
            if self.user_preferences.get('cultural_adaptation', True):
                translated_text = await self._apply_cultural_adaptations(
                    translated_text, source_language, target_language, context
                )
                
            # Assess translation quality
            quality = await self._assess_translation_quality(
                text, translated_text, source_language, target_language, context
            )
            
            # Create result
            result = TranslationResult(
                original_text=text,
                translated_text=translated_text,
                source_language=source_language,
                target_language=target_language,
                confidence=quality.overall_score,
                translation_method='contextual_neural_mt',
                metadata={
                    'language_detection_confidence': lang_confidence,
                    'context': context.__dict__ if context else {},
                    'quality_metrics': quality.__dict__,
                    'cultural_adaptations_applied': True
                }
            )
            
            # Cache result
            self.translation_cache[cache_key] = result
            
            logger.info(f"Translated text from {source_language} to {target_language} "
                       f"with confidence {result.confidence:.2f}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error translating text: {e}")
            # Return safe fallback
            return TranslationResult(
                original_text=text,
                translated_text=f"[Translation failed: {text}]",
                source_language=source_language or 'unknown',
                target_language=target_language,
                confidence=0.0,
                translation_method='error_fallback',
                metadata={'error': str(e)}
            )
            
    async def _perform_translation(self, text: str, source_lang: str, 
                                 target_lang: str, context: ContextualTranslation) -> str:
        """Perform the actual translation"""
        
        # Simplified translation simulation
        # In a real implementation, this would use actual translation models
        
        # Sample translations for demonstration
        sample_translations = {
            'en-es': {
                'hello': 'hola',
                'good morning': 'buenos días',
                'thank you': 'gracias',
                'please': 'por favor',
                'meeting': 'reunión',
                'project': 'proyecto',
                'deadline': 'fecha límite',
                'urgent': 'urgente',
                'important': 'importante',
                'email': 'correo electrónico'
            },
            'en-fr': {
                'hello': 'bonjour',
                'good morning': 'bonjour',
                'thank you': 'merci',
                'please': 's\'il vous plaît',
                'meeting': 'réunion',
                'project': 'projet',
                'deadline': 'échéance',
                'urgent': 'urgent',
                'important': 'important',
                'email': 'email'
            },
            'en-de': {
                'hello': 'hallo',
                'good morning': 'guten Morgen',
                'thank you': 'danke',
                'please': 'bitte',
                'meeting': 'Besprechung',
                'project': 'Projekt',
                'deadline': 'Frist',
                'urgent': 'dringend',
                'important': 'wichtig',
                'email': 'E-Mail'
            }
        }
        
        translation_key = f"{source_lang}-{target_lang}"
        
        if translation_key in sample_translations:
            # Simple word-by-word translation for demo
            words = text.lower().split()
            translated_words = []
            
            for word in words:
                # Remove punctuation for lookup
                clean_word = re.sub(r'[^\w\s]', '', word)
                
                if clean_word in sample_translations[translation_key]:
                    translated_word = sample_translations[translation_key][clean_word]
                    
                    # Preserve original capitalization pattern
                    if word.isupper():
                        translated_word = translated_word.upper()
                    elif word.istitle():
                        translated_word = translated_word.capitalize()
                        
                    translated_words.append(translated_word)
                else:
                    # Keep original word if no translation found
                    translated_words.append(word)
                    
            translated_text = ' '.join(translated_words)
            
            # Adjust for context and formality
            if context.formality == 'formal':
                translated_text = await self._apply_formal_style(translated_text, target_lang)
            elif context.formality == 'informal':
                translated_text = await self._apply_informal_style(translated_text, target_lang)
                
            return translated_text
        else:
            # Fallback: return original text with language indicator
            return f"[{target_lang.upper()}] {text}"
            
    async def _apply_formal_style(self, text: str, language: str) -> str:
        """Apply formal style to translated text"""
        
        formal_replacements = {
            'es': {
                'hola': 'estimado/a',
                'gracias': 'le agradezco',
            },
            'fr': {
                'salut': 'monsieur/madame',
                'merci': 'je vous remercie',
            },
            'de': {
                'hallo': 'sehr geehrte damen und herren',
                'danke': 'vielen dank',
            }
        }
        
        if language in formal_replacements:
            for informal, formal in formal_replacements[language].items():
                text = text.replace(informal, formal)
                
        return text
        
    async def _apply_informal_style(self, text: str, language: str) -> str:
        """Apply informal style to translated text"""
        
        informal_replacements = {
            'es': {
                'estimado/a': 'hola',
                'le agradezco': 'gracias',
            },
            'fr': {
                'monsieur/madame': 'salut',
                'je vous remercie': 'merci',
            },
            'de': {
                'sehr geehrte damen und herren': 'hallo',
                'vielen dank': 'danke',
            }
        }
        
        if language in informal_replacements:
            for formal, informal in informal_replacements[language].items():
                text = text.replace(formal, informal)
                
        return text
        
    async def _apply_cultural_adaptations(self, text: str, source_lang: str, 
                                        target_lang: str, context: ContextualTranslation) -> str:
        """Apply cultural adaptations to translation"""
        
        # Apply business customs
        if context.context_type == 'business' and target_lang in self.cultural_adaptations['business_customs']:
            customs = self.cultural_adaptations['business_customs'][target_lang]
            
            # Add appropriate opening for Japanese business emails
            if target_lang == 'ja' and context.formality == 'formal':
                if not text.startswith(customs['email_opening']):
                    text = customs['email_opening'] + ' ' + text
                    
            # Add appropriate closing
            if 'email_closing' in customs and not any(
                closing in text.lower() for closing in ['regards', 'sincerely', 'thank']
            ):
                text += '\n\n' + customs['email_closing']
                
        # Apply date and time format adaptations
        if target_lang in self.cultural_adaptations['date_formats']:
            date_format = self.cultural_adaptations['date_formats'][target_lang]
            # This would typically involve parsing and reformatting dates
            # For demo purposes, just note the requirement
            pass
            
        return text
        
    async def _assess_translation_quality(self, original: str, translated: str,
                                        source_lang: str, target_lang: str,
                                        context: ContextualTranslation) -> TranslationQuality:
        """Assess the quality of the translation"""
        
        # Simplified quality assessment
        # In reality would use BLEU, METEOR, or other MT evaluation metrics
        
        # Basic fluency assessment
        fluency_score = 0.8  # Default good fluency
        
        # Check for obvious errors
        if '[' in translated and ']' in translated:
            fluency_score -= 0.3  # Penalty for untranslated content
            
        if len(translated.split()) == 0:
            fluency_score = 0.0
            
        # Adequacy assessment (content preservation)
        word_ratio = len(translated.split()) / max(1, len(original.split()))
        adequacy_score = max(0.3, min(1.0, 1.0 - abs(1.0 - word_ratio)))
        
        # Context preservation
        context_preservation = 0.9  # Assume good context preservation
        
        # Tone preservation
        tone_preservation = 0.85
        
        # Overall score
        overall_score = (
            fluency_score * 0.3 +
            adequacy_score * 0.3 +
            context_preservation * 0.2 +
            tone_preservation * 0.2
        )
        
        return TranslationQuality(
            fluency_score=fluency_score,
            adequacy_score=adequacy_score,
            context_preservation=context_preservation,
            tone_preservation=tone_preservation,
            overall_score=overall_score
        )
        
    async def translate_email(self, email_data: Dict, target_language: str) -> Dict:
        """
        Translate an entire email with context awareness
        
        Args:
            email_data: Email content and metadata
            target_language: Target language code
            
        Returns:
            Dictionary with translated email content
        """
        try:
            # Extract email components
            subject = email_data.get('subject', '')
            body = email_data.get('body', '')
            sender = email_data.get('sender', '')
            
            # Analyze email context
            email_context = await self.analyze_context(
                subject + ' ' + body,
                metadata={
                    'email_type': 'business',
                    'sender_domain': sender.split('@')[-1] if '@' in sender else ''
                }
            )
            
            # Translate subject
            subject_result = await self.translate_text(
                subject, target_language, context=email_context
            )
            
            # Translate body
            body_result = await self.translate_text(
                body, target_language, context=email_context
            )
            
            # Prepare translated email
            translated_email = {
                'original_subject': subject,
                'translated_subject': subject_result.translated_text,
                'original_body': body,
                'translated_body': body_result.translated_text,
                'source_language': subject_result.source_language,
                'target_language': target_language,
                'translation_confidence': (subject_result.confidence + body_result.confidence) / 2,
                'context_analysis': email_context.__dict__,
                'translation_metadata': {
                    'subject_metadata': subject_result.metadata,
                    'body_metadata': body_result.metadata,
                    'cultural_adaptations': True,
                    'timestamp': datetime.now().isoformat()
                }
            }
            
            return translated_email
            
        except Exception as e:
            logger.error(f"Error translating email: {e}")
            return {
                'original_subject': email_data.get('subject', ''),
                'translated_subject': f"[Translation failed] {email_data.get('subject', '')}",
                'original_body': email_data.get('body', ''),
                'translated_body': f"[Translation failed] {email_data.get('body', '')}",
                'source_language': 'unknown',
                'target_language': target_language,
                'translation_confidence': 0.0,
                'error': str(e)
            }
            
    def _generate_translation_cache_key(self, text: str, source_lang: str, 
                                      target_lang: str, context: ContextualTranslation = None) -> str:
        """Generate cache key for translation"""
        
        context_str = ''
        if context:
            context_str = f"{context.domain}_{context.tone}_{context.formality}"
            
        key_content = f"{text}_{source_lang}_{target_lang}_{context_str}"
        return hashlib.md5(key_content.encode()).hexdigest()
        
    def get_supported_languages(self) -> List[Dict]:
        """Get list of supported languages"""
        return [
            {
                'code': profile.code,
                'name': profile.name,
                'native_name': profile.native_name,
                'script': profile.script,
                'direction': profile.direction
            }
            for profile in self.supported_languages.values()
        ]
        
    def get_translation_analytics(self) -> Dict:
        """Get analytics on translation performance"""
        if not self.translation_cache:
            return {'total_translations': 0, 'analytics': 'No translation history'}
            
        total_translations = len(self.translation_cache)
        
        # Calculate average confidence
        confidences = [result.confidence for result in self.translation_cache.values()]
        avg_confidence = sum(confidences) / len(confidences)
        
        # Language pair distribution
        language_pairs = {}
        for result in self.translation_cache.values():
            pair = f"{result.source_language}-{result.target_language}"
            language_pairs[pair] = language_pairs.get(pair, 0) + 1
            
        # Domain distribution
        domains = {}
        for result in self.translation_cache.values():
            context = result.metadata.get('context', {})
            domain = context.get('domain', 'unknown')
            domains[domain] = domains.get(domain, 0) + 1
            
        return {
            'total_translations': total_translations,
            'average_confidence': avg_confidence,
            'top_language_pairs': sorted(language_pairs.items(), key=lambda x: x[1], reverse=True)[:5],
            'domain_distribution': domains,
            'cache_efficiency': len(self.translation_cache) / max(1, total_translations)
        }

# Test the dynamic translation engine
async def test_dynamic_translation():
    """Test function for the dynamic translation engine"""
    engine = DynamicTranslationEngine()
    await engine.initialize()
    
    print("🌍 Dynamic Translation Engine Demo")
    print("=" * 50)
    
    # Test language detection
    test_texts = [
        "Hello, how are you today?",
        "Bonjour, comment allez-vous?",
        "Hola, ¿cómo estás?",
        "Guten Tag, wie geht es Ihnen?",
        "Meeting tomorrow at 2 PM in conference room A."
    ]
    
    print("\n🔍 Language Detection Test:")
    for text in test_texts:
        lang, confidence = await engine.detect_language(text)
        print(f"'{text}' -> {lang} (confidence: {confidence:.2f})")
    
    # Test context analysis
    business_email = """
    Dear Mr. Johnson,
    
    I hope this email finds you well. I wanted to follow up on our meeting 
    yesterday regarding the Q4 budget proposal. As discussed, we need to 
    finalize the numbers by Friday to meet our deadline.
    
    Please let me know if you need any additional information.
    
    Best regards,
    Sarah Wilson
    """
    
    print(f"\n📊 Context Analysis Test:")
    context = await engine.analyze_context(business_email)
    print(f"Domain: {context.domain}")
    print(f"Tone: {context.tone}")
    print(f"Formality: {context.formality}")
    print(f"Context Type: {context.context_type}")
    
    # Test translations
    test_translations = [
        {
            'text': "Hello, how are you?",
            'target': 'es',
            'description': 'Simple greeting to Spanish'
        },
        {
            'text': "Urgent: Server maintenance required",
            'target': 'fr',
            'description': 'Technical urgent message to French'
        },
        {
            'text': "Thank you for your proposal. We will review it carefully.",
            'target': 'de',
            'description': 'Business response to German'
        }
    ]
    
    print(f"\n🔄 Translation Test:")
    for i, test in enumerate(test_translations, 1):
        print(f"\n{i}. {test['description']}")
        print(f"Original: {test['text']}")
        
        result = await engine.translate_text(test['text'], test['target'])
        
        print(f"Translated: {result.translated_text}")
        print(f"Source Language: {result.source_language}")
        print(f"Confidence: {result.confidence:.2f}")
        print(f"Method: {result.translation_method}")
    
    # Test email translation
    test_email = {
        'subject': 'Project Update - Q4 Budget Review',
        'body': business_email,
        'sender': 'sarah.wilson@company.com'
    }
    
    print(f"\n📧 Email Translation Test:")
    translated_email = await engine.translate_email(test_email, 'es')
    
    print(f"Original Subject: {translated_email['original_subject']}")
    print(f"Translated Subject: {translated_email['translated_subject']}")
    print(f"Body Preview: {translated_email['translated_body'][:200]}...")
    print(f"Translation Confidence: {translated_email['translation_confidence']:.2f}")
    
    # Show supported languages
    print(f"\n🌐 Supported Languages ({len(engine.get_supported_languages())} total):")
    for lang in engine.get_supported_languages()[:10]:  # Show first 10
        print(f"  {lang['code']}: {lang['name']} ({lang['native_name']}) - {lang['script']}")
    
    # Show analytics
    analytics = engine.get_translation_analytics()
    print(f"\n📈 Translation Analytics:")
    print(f"Total Translations: {analytics['total_translations']}")
    print(f"Average Confidence: {analytics['average_confidence']:.2f}")
    print(f"Top Language Pairs: {analytics['top_language_pairs']}")
    print(f"Domain Distribution: {analytics['domain_distribution']}")
    
    print("\n✅ Dynamic Translation Engine Test Complete!")

if __name__ == "__main__":
    asyncio.run(test_dynamic_translation())