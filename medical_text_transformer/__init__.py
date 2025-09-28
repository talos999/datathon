"""
Medical Text Transformer Package
A tool for transforming and augmenting medical text data with configurable variations.
"""

__version__ = "1.0.0"
__author__ = "Datathon Team"

from .transformer import MedicalTextTransformer
from .config import TransformationConfig

__all__ = ['MedicalTextTransformer', 'TransformationConfig']