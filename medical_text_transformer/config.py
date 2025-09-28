"""
Configuration management for medical text transformations.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any
import yaml
import json


@dataclass
class TransformationConfig:
    """Configuration class for medical text transformations."""
    
    # Variation strength: 'low', 'medium', 'high'
    variation_strength: str = 'medium'
    
    # Supported languages
    supported_languages: List[str] = field(default_factory=lambda: ['en', 'pl', 'de', 'fr', 'es'])
    
    # Transformation types to apply
    transformation_types: List[str] = field(default_factory=lambda: [
        'synonym_replacement',
        'sentence_restructuring', 
        'medical_terminology_variation',
        'paraphrasing'
    ])
    
    # Number of variations to generate per input
    num_variations: int = 5
    
    # Medical domain specific settings
    preserve_medical_accuracy: bool = True
    medical_entity_types: List[str] = field(default_factory=lambda: [
        'DISEASE', 'SYMPTOM', 'MEDICATION', 'PROCEDURE', 'ANATOMY', 'DOSAGE'
    ])
    
    # Export settings
    export_formats: List[str] = field(default_factory=lambda: ['json', 'csv'])
    include_metadata: bool = True
    
    # Strength-specific parameters
    strength_params: Dict[str, Dict[str, float]] = field(default_factory=lambda: {
        'low': {
            'synonym_probability': 0.2,
            'restructure_probability': 0.1,
            'terminology_variation_probability': 0.15,
            'max_word_changes': 0.1
        },
        'medium': {
            'synonym_probability': 0.4,
            'restructure_probability': 0.3,
            'terminology_variation_probability': 0.3,
            'max_word_changes': 0.25
        },
        'high': {
            'synonym_probability': 0.7,
            'restructure_probability': 0.5,
            'terminology_variation_probability': 0.5,
            'max_word_changes': 0.4
        }
    })
    
    @classmethod
    def from_file(cls, config_path: str) -> 'TransformationConfig':
        """Load configuration from YAML or JSON file."""
        with open(config_path, 'r', encoding='utf-8') as f:
            if config_path.endswith('.yaml') or config_path.endswith('.yml'):
                data = yaml.safe_load(f)
            else:
                data = json.load(f)
        
        return cls(**data)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            'variation_strength': self.variation_strength,
            'supported_languages': self.supported_languages,
            'transformation_types': self.transformation_types,
            'num_variations': self.num_variations,
            'preserve_medical_accuracy': self.preserve_medical_accuracy,
            'medical_entity_types': self.medical_entity_types,
            'export_formats': self.export_formats,
            'include_metadata': self.include_metadata,
            'strength_params': self.strength_params
        }
    
    def save_to_file(self, config_path: str):
        """Save configuration to YAML file."""
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(self.to_dict(), f, default_flow_style=False, indent=2)
    
    def get_strength_params(self) -> Dict[str, float]:
        """Get parameters for current variation strength."""
        return self.strength_params.get(self.variation_strength, self.strength_params['medium'])