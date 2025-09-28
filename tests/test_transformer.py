"""
Basic tests for the Medical Text Transformer.
"""

import unittest
import tempfile
import os
from medical_text_transformer import MedicalTextTransformer, TransformationConfig
from medical_text_transformer.exporter import ExportManager


class TestMedicalTextTransformer(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = TransformationConfig(
            variation_strength='medium',
            num_variations=3,
            include_metadata=True
        )
        self.transformer = MedicalTextTransformer(self.config)
    
    def test_transformer_initialization(self):
        """Test transformer initialization."""
        self.assertIsNotNone(self.transformer)
        self.assertEqual(self.transformer.config.variation_strength, 'medium')
        self.assertEqual(self.transformer.config.num_variations, 3)
    
    def test_language_detection(self):
        """Test language detection functionality."""
        english_text = "Patient has severe chest pain."
        detected_lang = self.transformer.detect_language(english_text)
        self.assertEqual(detected_lang, 'en')
    
    def test_text_transformation(self):
        """Test basic text transformation."""
        test_text = "Patient complains of severe chest pain."
        results = self.transformer.transform_text(test_text)
        
        # Check basic structure
        self.assertEqual(len(results), 3)  # num_variations = 3
        
        for result in results:
            self.assertIn('variation_id', result)
            self.assertIn('original_text', result)
            self.assertIn('transformed_text', result)
            self.assertIn('language', result)
            self.assertIn('variation_strength', result)
            self.assertEqual(result['original_text'], test_text)
            self.assertEqual(result['language'], 'en')
            self.assertEqual(result['variation_strength'], 'medium')
    
    def test_synonym_replacement(self):
        """Test synonym replacement functionality."""
        test_text = "Patient has pain."
        transformed_text, transformations = self.transformer._apply_synonym_replacement(test_text, 1.0)  # 100% probability
        
        # Should have some transformation with high probability
        self.assertIsNotNone(transformed_text)
        self.assertIsInstance(transformations, list)
    
    def test_sentence_restructuring(self):
        """Test sentence restructuring functionality."""
        test_text = "Patient has fever."
        transformed_text, transformations = self.transformer._apply_sentence_restructuring(test_text, 1.0)
        
        self.assertIsNotNone(transformed_text)
        self.assertIsInstance(transformations, list)
    
    def test_medical_terminology_variation(self):
        """Test medical terminology variation."""
        test_text = "Patient has hypertension."
        transformed_text, transformations = self.transformer._apply_terminology_variation(test_text, 1.0)
        
        self.assertIsNotNone(transformed_text)
        self.assertIsInstance(transformations, list)
    
    def test_similarity_calculation(self):
        """Test similarity calculation."""
        original = "Patient has severe pain."
        transformed = "Individual has intense discomfort."
        
        similarity = self.transformer._calculate_similarity(original, transformed)
        self.assertIsInstance(similarity, float)
        self.assertGreaterEqual(similarity, 0.0)
        self.assertLessEqual(similarity, 1.0)
    
    def test_configuration_validation(self):
        """Test configuration validation."""
        # Test invalid language
        with self.assertRaises(ValueError):
            self.transformer.transform_text("Test text", language='invalid')
    
    def test_export_json(self):
        """Test JSON export functionality."""
        test_text = "Patient has headache."
        results = self.transformer.transform_text(test_text)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = f.name
        
        try:
            ExportManager.export_to_json(results, temp_path)
            self.assertTrue(os.path.exists(temp_path))
            
            # Verify file is not empty
            self.assertGreater(os.path.getsize(temp_path), 0)
            
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_export_csv(self):
        """Test CSV export functionality."""
        test_text = "Patient has fever."
        results = self.transformer.transform_text(test_text)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            temp_path = f.name
        
        try:
            ExportManager.export_to_csv(results, temp_path)
            self.assertTrue(os.path.exists(temp_path))
            self.assertGreater(os.path.getsize(temp_path), 0)
            
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)


class TestTransformationConfig(unittest.TestCase):
    
    def test_default_config(self):
        """Test default configuration."""
        config = TransformationConfig()
        
        self.assertEqual(config.variation_strength, 'medium')
        self.assertEqual(config.num_variations, 5)
        self.assertTrue(config.preserve_medical_accuracy)
        self.assertTrue(config.include_metadata)
    
    def test_strength_params(self):
        """Test strength parameter retrieval."""
        config = TransformationConfig(variation_strength='high')
        params = config.get_strength_params()
        
        self.assertIn('synonym_probability', params)
        self.assertIn('restructure_probability', params)
        self.assertIsInstance(params['synonym_probability'], float)
    
    def test_config_to_dict(self):
        """Test configuration serialization."""
        config = TransformationConfig()
        config_dict = config.to_dict()
        
        self.assertIsInstance(config_dict, dict)
        self.assertIn('variation_strength', config_dict)
        self.assertIn('num_variations', config_dict)


if __name__ == '__main__':
    unittest.main()