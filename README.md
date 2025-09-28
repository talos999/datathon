# Medical Text Transformer

A comprehensive tool for transforming and augmenting medical text data with configurable variations. Developed for the Poland healthcare datathon.

## Features

- **Multi-language Support**: Process medical texts in English, Polish, German, French, and Spanish
- **Configurable Variation Strength**: Choose from low, medium, or high variation intensity
- **Multiple Transformation Types**:
  - Synonym replacement with medical terminology
  - Sentence restructuring
  - Medical terminology variations
  - Paraphrasing
- **Flexible Export Options**: Export results to JSON, CSV, Excel, YAML, and plain text formats
- **Batch Processing**: Process multiple texts from files
- **Medical Domain Awareness**: Preserves medical accuracy while generating variations
- **Command Line Interface**: Easy-to-use CLI for all operations

## Installation

1. Clone the repository:
```bash
git clone https://github.com/talos999/datathon.git
cd datathon
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Install the package:
```bash
pip install -e .
```

## Quick Start

### Basic Usage

Transform a single medical text:
```bash
medical-transformer transform "Patient complains of severe chest pain radiating to the left arm."
```

### With Custom Options

```bash
medical-transformer transform "Patient has chronic headache." \
  --strength high \
  --variations 10 \
  --output results \
  --format json csv excel
```

### Batch Processing

Process multiple texts from a file:
```bash
medical-transformer batch examples/sample_texts.json \
  --output-dir ./output \
  --strength medium \
  --format json csv
```

## Configuration

Generate a default configuration file:
```bash
medical-transformer generate-config --output my_config.yaml
```

Use custom configuration:
```bash
medical-transformer transform "Medical text here" --config my_config.yaml
```

### Configuration Options

- `variation_strength`: low, medium, high
- `num_variations`: Number of variations to generate
- `transformation_types`: List of transformation types to apply
- `supported_languages`: Languages to support
- `export_formats`: Default export formats
- `strength_params`: Fine-tune transformation parameters

## Examples

### Example 1: Basic Transformation

```bash
medical-transformer transform "Doctor prescribed medication for hypertension."
```

Output:
```
Variation 1:
  Language: en
  Transformed: Physician prescribed medicine for high blood pressure.
  
Variation 2:
  Language: en
  Transformed: Clinician prescribed therapeutic agent for hypertension.
```

### Example 2: High Variation Strength

```bash
medical-transformer transform "Patient presents with acute dyspnea." --strength high
```

### Example 3: Specific Transformations

```bash
medical-transformer transform "Individual has severe pain." \
  --transformations synonym_replacement medical_terminology_variation
```

### Example 4: Multiple Export Formats

```bash
medical-transformer transform "Patient complains of headache." \
  --output results \
  --format json csv excel yaml txt
```

## API Usage

```python
from medical_text_transformer import MedicalTextTransformer, TransformationConfig

# Create configuration
config = TransformationConfig(
    variation_strength='medium',
    num_variations=5,
    transformation_types=['synonym_replacement', 'paraphrasing']
)

# Initialize transformer
transformer = MedicalTextTransformer(config)

# Transform text
results = transformer.transform_text("Patient has severe chest pain.")

# Export results
from medical_text_transformer.exporter import ExportManager
ExportManager.export(results, 'output/results', 'json')
```

## Supported Languages

- English (en)
- Polish (pl) 
- German (de)
- French (fr)
- Spanish (es)

View supported languages:
```bash
medical-transformer supported-languages
```

## Export Formats

- **JSON**: Structured data with full metadata
- **CSV**: Tabular format for analysis
- **Excel**: Multi-sheet workbook with summary
- **YAML**: Human-readable configuration format
- **TXT**: Plain text for easy reading

## Transformation Types

### 1. Synonym Replacement
Replaces medical terms with appropriate synonyms:
- "pain" → "discomfort", "ache"
- "doctor" → "physician", "clinician"
- "medication" → "medicine", "drug"

### 2. Sentence Restructuring
Restructures sentences while preserving meaning:
- "Patient has fever" → "Fever is present in the patient"
- "Pain is severe" → "Severe pain is observed"

### 3. Medical Terminology Variation
Converts between formal and common medical terms:
- "myocardial infarction" ↔ "heart attack"
- "hypertension" ↔ "high blood pressure"
- "dyspnea" ↔ "shortness of breath"

### 4. Paraphrasing
Rephrases expressions with equivalent meanings:
- "complains of" → "reports"
- "presents with" → "shows"
- "experiences" → "has"

## Variation Strength Levels

### Low Strength
- 20% synonym replacement probability
- 10% sentence restructuring probability
- Minimal changes, high similarity to original

### Medium Strength (Default)
- 40% synonym replacement probability
- 30% sentence restructuring probability
- Balanced variation and similarity

### High Strength
- 70% synonym replacement probability
- 50% sentence restructuring probability
- Maximum variation while preserving medical accuracy

## Use Cases

- **Data Augmentation**: Generate diverse training data for ML models
- **Text Analysis**: Create variations for robustness testing
- **Medical NLP**: Develop language models with varied medical text
- **Research**: Study text variation impact on medical information systems
- **Education**: Create diverse medical case examples

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

For issues and questions:
- Open an issue on GitHub
- Check the examples directory for usage patterns
- Review the configuration options in config/default.yaml
