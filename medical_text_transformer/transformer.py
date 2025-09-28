"""
Core medical text transformation engine.
"""

import random
import re
from typing import List, Dict, Tuple, Optional
from langdetect import detect
import nltk
from nltk.corpus import wordnet
from nltk.tokenize import sent_tokenize, word_tokenize
from .config import TransformationConfig


class MedicalTextTransformer:
    """Main class for transforming medical text prompts."""
    
    def __init__(self, config: TransformationConfig = None):
        self.config = config or TransformationConfig()
        self._download_nltk_data()
        self._medical_synonyms = self._load_medical_synonyms()
        self._medical_terms = self._load_medical_terms()
    
    def _download_nltk_data(self):
        """Download required NLTK data."""
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt', quiet=True)
        
        try:
            nltk.data.find('tokenizers/punkt_tab')
        except LookupError:
            nltk.download('punkt_tab', quiet=True)
        
        try:
            nltk.data.find('corpora/wordnet')
        except LookupError:
            nltk.download('wordnet', quiet=True)
            
        try:
            nltk.data.find('corpora/omw-1.4')
        except LookupError:
            nltk.download('omw-1.4', quiet=True)
    
    def _load_medical_synonyms(self) -> Dict[str, List[str]]:
        """Load medical synonym mappings."""
        return {
            # Common medical terms and their variations
            'pain': ['discomfort', 'ache', 'soreness', 'tenderness'],
            'severe': ['acute', 'intense', 'extreme', 'serious'],
            'mild': ['slight', 'minor', 'gentle', 'moderate'],
            'patient': ['individual', 'person', 'case', 'subject'],
            'doctor': ['physician', 'clinician', 'medical practitioner', 'healthcare provider'],
            'treatment': ['therapy', 'intervention', 'management', 'care'],
            'medication': ['drug', 'medicine', 'pharmaceutical', 'therapeutic agent'],
            'symptom': ['sign', 'manifestation', 'indication', 'feature'],
            'diagnosis': ['assessment', 'evaluation', 'determination', 'identification'],
            'examination': ['assessment', 'evaluation', 'inspection', 'check-up'],
            'infection': ['contamination', 'sepsis', 'inflammatory condition'],
            'inflammation': ['swelling', 'irritation', 'inflammatory response'],
            'chronic': ['long-term', 'persistent', 'ongoing', 'prolonged'],
            'acute': ['sudden', 'rapid-onset', 'severe', 'immediate'],
            'fever': ['pyrexia', 'elevated temperature', 'hyperthermia'],
            'nausea': ['queasiness', 'sick feeling', 'gastric discomfort'],
            'headache': ['cephalgia', 'head pain', 'cranial discomfort'],
            'fatigue': ['tiredness', 'exhaustion', 'weakness', 'lethargy']
        }
    
    def _load_medical_terms(self) -> Dict[str, str]:
        """Load medical term mappings and entity types."""
        return {
            # Medical entities patterns for recognition
            'MEDICATION_PATTERN': r'\b(?:mg|mcg|ml|tablet|capsule|injection)\b',
            'DOSAGE_PATTERN': r'\b\d+(?:\.\d+)?\s*(?:mg|mcg|ml|units?)\b',
            'TIME_PATTERN': r'\b(?:daily|twice|three times|morning|evening|bedtime)\b',
            'DURATION_PATTERN': r'\b\d+\s*(?:days?|weeks?|months?|years?)\b'
        }
    
    def detect_language(self, text: str) -> str:
        """Detect the language of input text."""
        try:
            return detect(text)
        except:
            return 'en'  # Default to English
    
    def transform_text(self, text: str, language: str = None) -> List[Dict[str, any]]:
        """
        Transform medical text with variations.
        
        Args:
            text: Input medical text
            language: Language code (auto-detected if None)
            
        Returns:
            List of transformation results with metadata
        """
        if language is None:
            language = self.detect_language(text)
        
        if language not in self.config.supported_languages:
            raise ValueError(f"Language '{language}' not supported. Supported: {self.config.supported_languages}")
        
        results = []
        strength_params = self.config.get_strength_params()
        
        for i in range(self.config.num_variations):
            transformed_text = text
            transformations_applied = []
            
            # Apply different transformation types based on configuration
            if 'synonym_replacement' in self.config.transformation_types:
                transformed_text, syns = self._apply_synonym_replacement(
                    transformed_text, strength_params['synonym_probability']
                )
                if syns:
                    transformations_applied.extend(syns)
            
            if 'sentence_restructuring' in self.config.transformation_types:
                transformed_text, structs = self._apply_sentence_restructuring(
                    transformed_text, strength_params['restructure_probability']
                )
                if structs:
                    transformations_applied.extend(structs)
            
            if 'medical_terminology_variation' in self.config.transformation_types:
                transformed_text, terms = self._apply_terminology_variation(
                    transformed_text, strength_params['terminology_variation_probability']
                )
                if terms:
                    transformations_applied.extend(terms)
            
            if 'paraphrasing' in self.config.transformation_types:
                transformed_text, paraphrases = self._apply_paraphrasing(
                    transformed_text, strength_params.get('paraphrase_probability', 0.3)
                )
                if paraphrases:
                    transformations_applied.extend(paraphrases)
            
            result = {
                'variation_id': i + 1,
                'original_text': text,
                'transformed_text': transformed_text,
                'language': language,
                'variation_strength': self.config.variation_strength,
                'transformations_applied': transformations_applied,
                'metadata': {
                    'word_count': len(word_tokenize(transformed_text)),
                    'sentence_count': len(sent_tokenize(transformed_text)),
                    'similarity_score': self._calculate_similarity(text, transformed_text)
                } if self.config.include_metadata else {}
            }
            
            results.append(result)
        
        return results
    
    def _apply_synonym_replacement(self, text: str, probability: float) -> Tuple[str, List[str]]:
        """Apply medical synonym replacements."""
        words = word_tokenize(text)
        applied_transformations = []
        
        for i, word in enumerate(words):
            if random.random() < probability:
                word_lower = word.lower()
                if word_lower in self._medical_synonyms:
                    synonym = random.choice(self._medical_synonyms[word_lower])
                    # Preserve original case
                    if word.isupper():
                        synonym = synonym.upper()
                    elif word.istitle():
                        synonym = synonym.capitalize()
                    
                    words[i] = synonym
                    applied_transformations.append(f"synonym_replacement: {word} -> {synonym}")
        
        return ' '.join(words), applied_transformations
    
    def _apply_sentence_restructuring(self, text: str, probability: float) -> Tuple[str, List[str]]:
        """Apply sentence restructuring transformations."""
        sentences = sent_tokenize(text)
        applied_transformations = []
        
        for i, sentence in enumerate(sentences):
            if random.random() < probability:
                # Simple restructuring patterns
                restructured = self._restructure_sentence(sentence)
                if restructured != sentence:
                    sentences[i] = restructured
                    applied_transformations.append(f"sentence_restructuring: modified sentence {i+1}")
        
        return ' '.join(sentences), applied_transformations
    
    def _restructure_sentence(self, sentence: str) -> str:
        """Apply simple sentence restructuring rules."""
        # Pattern: "Patient has X" -> "X is present in the patient"
        has_pattern = re.compile(r'(\w+)\s+has\s+(.+)', re.IGNORECASE)
        match = has_pattern.match(sentence.strip())
        if match:
            subject, condition = match.groups()
            return f"{condition.capitalize()} is present in the {subject.lower()}."
        
        # Pattern: "X is severe" -> "Severe X is observed"  
        is_adj_pattern = re.compile(r'(.+?)\s+is\s+(severe|mild|acute|chronic)\s*\.?$', re.IGNORECASE)
        match = is_adj_pattern.match(sentence.strip())
        if match:
            condition, severity = match.groups()
            return f"{severity.capitalize()} {condition.lower()} is observed."
        
        return sentence
    
    def _apply_terminology_variation(self, text: str, probability: float) -> Tuple[str, List[str]]:
        """Apply medical terminology variations."""
        applied_transformations = []
        modified_text = text
        
        # Replace formal terms with more common ones or vice versa
        terminology_variations = {
            'myocardial infarction': 'heart attack',
            'heart attack': 'myocardial infarction',
            'hypertension': 'high blood pressure',
            'high blood pressure': 'hypertension',
            'dyspnea': 'shortness of breath',
            'shortness of breath': 'dyspnea',
            'pyrexia': 'fever',
            'cephalgia': 'headache',
            'gastric': 'stomach'
        }
        
        for formal_term, common_term in terminology_variations.items():
            if random.random() < probability:
                pattern = re.compile(re.escape(formal_term), re.IGNORECASE)
                if pattern.search(modified_text):
                    modified_text = pattern.sub(common_term, modified_text)
                    applied_transformations.append(f"terminology_variation: {formal_term} -> {common_term}")
        
        return modified_text, applied_transformations
    
    def _apply_paraphrasing(self, text: str, probability: float) -> Tuple[str, List[str]]:
        """Apply paraphrasing transformations."""
        applied_transformations = []
        
        if random.random() < probability:
            # Simple paraphrasing patterns
            paraphrase_patterns = [
                (r'complains? of (.+)', r'reports \1'),
                (r'presents? with (.+)', r'shows \1'),
                (r'experiences? (.+)', r'has \1'),
                (r'develops? (.+)', r'manifests \1')
            ]
            
            modified_text = text
            for pattern, replacement in paraphrase_patterns:
                if re.search(pattern, modified_text, re.IGNORECASE):
                    modified_text = re.sub(pattern, replacement, modified_text, flags=re.IGNORECASE)
                    applied_transformations.append(f"paraphrasing: applied pattern transformation")
                    break
            
            return modified_text, applied_transformations
        
        return text, applied_transformations
    
    def _calculate_similarity(self, original: str, transformed: str) -> float:
        """Calculate simple similarity score between original and transformed text."""
        original_words = set(word_tokenize(original.lower()))
        transformed_words = set(word_tokenize(transformed.lower()))
        
        if not original_words:
            return 1.0
        
        intersection = len(original_words.intersection(transformed_words))
        union = len(original_words.union(transformed_words))
        
        return intersection / union if union > 0 else 0.0