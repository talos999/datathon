"""
Command-line interface for the Medical Text Transformer.
"""

import click
import json
import sys
from pathlib import Path
from typing import List

from .transformer import MedicalTextTransformer
from .config import TransformationConfig
from .exporter import ExportManager


@click.group()
@click.version_option(version='1.0.0')
def cli():
    """Medical Text Transformer - Transform and augment medical text data."""
    pass


@cli.command()
@click.argument('text')
@click.option('--language', '-l', help='Language code (auto-detected if not specified)')
@click.option('--strength', '-s', 
              type=click.Choice(['low', 'medium', 'high']), 
              default='medium',
              help='Variation strength (default: medium)')
@click.option('--variations', '-n', 
              type=int, 
              default=5, 
              help='Number of variations to generate (default: 5)')
@click.option('--output', '-o', 
              help='Output file path (without extension)')
@click.option('--format', '-f', 
              type=click.Choice(['json', 'csv', 'excel', 'xlsx', 'yaml', 'txt']), 
              multiple=True,
              default=['json'],
              help='Export format(s) (default: json)')
@click.option('--config', '-c', 
              help='Path to configuration file')
@click.option('--transformations', '-t',
              multiple=True,
              type=click.Choice(['synonym_replacement', 'sentence_restructuring', 
                               'medical_terminology_variation', 'paraphrasing']),
              help='Specific transformation types to apply')
@click.option('--no-metadata', 
              is_flag=True, 
              help='Exclude metadata from results')
def transform(text, language, strength, variations, output, format, config, transformations, no_metadata):
    """Transform a medical text prompt with variations."""
    
    # Load configuration
    if config:
        try:
            config_obj = TransformationConfig.from_file(config)
        except Exception as e:
            click.echo(f"Error loading configuration: {e}", err=True)
            sys.exit(1)
    else:
        config_obj = TransformationConfig()
    
    # Override configuration with CLI options
    config_obj.variation_strength = strength
    config_obj.num_variations = variations
    config_obj.include_metadata = not no_metadata
    
    if transformations:
        config_obj.transformation_types = list(transformations)
    
    # Initialize transformer
    try:
        transformer = MedicalTextTransformer(config_obj)
    except Exception as e:
        click.echo(f"Error initializing transformer: {e}", err=True)
        sys.exit(1)
    
    # Transform text
    try:
        click.echo(f"Transforming text with {strength} variation strength...")
        results = transformer.transform_text(text, language)
        
        # Display results
        click.echo(f"\nGenerated {len(results)} variations:\n")
        for result in results:
            click.echo(f"Variation {result['variation_id']}:")
            click.echo(f"  Language: {result['language']}")
            click.echo(f"  Original: {result['original_text'][:100]}{'...' if len(result['original_text']) > 100 else ''}")
            click.echo(f"  Transformed: {result['transformed_text'][:100]}{'...' if len(result['transformed_text']) > 100 else ''}")
            if result.get('transformations_applied'):
                click.echo(f"  Transformations: {', '.join(result['transformations_applied'][:2])}{'...' if len(result['transformations_applied']) > 2 else ''}")
            click.echo()
        
        # Export results
        if output:
            exported_files = []
            for fmt in format:
                try:
                    exported_file = ExportManager.export(results, output, fmt)
                    exported_files.append(exported_file)
                    click.echo(f"Results exported to: {exported_file}")
                except Exception as e:
                    click.echo(f"Error exporting to {fmt}: {e}", err=True)
            
            if exported_files:
                click.echo(f"\nExported {len(exported_files)} file(s) successfully.")
        else:
            click.echo("Use --output to save results to file(s).")
            
    except Exception as e:
        click.echo(f"Error during transformation: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option('--output-dir', '-d', 
              default='./output',
              help='Output directory for results (default: ./output)')
@click.option('--strength', '-s', 
              type=click.Choice(['low', 'medium', 'high']), 
              default='medium',
              help='Variation strength (default: medium)')
@click.option('--variations', '-n', 
              type=int, 
              default=5, 
              help='Number of variations per text (default: 5)')
@click.option('--format', '-f', 
              type=click.Choice(['json', 'csv', 'excel', 'xlsx', 'yaml', 'txt']), 
              multiple=True,
              default=['json', 'csv'],
              help='Export format(s) (default: json, csv)')
@click.option('--config', '-c', 
              help='Path to configuration file')
def batch(input_file, output_dir, strength, variations, format, config):
    """Process multiple texts from a file (one per line or JSON array)."""
    
    # Load configuration
    if config:
        try:
            config_obj = TransformationConfig.from_file(config)
        except Exception as e:
            click.echo(f"Error loading configuration: {e}", err=True)
            sys.exit(1)
    else:
        config_obj = TransformationConfig()
    
    # Override configuration with CLI options
    config_obj.variation_strength = strength
    config_obj.num_variations = variations
    
    # Initialize transformer
    try:
        transformer = MedicalTextTransformer(config_obj)
    except Exception as e:
        click.echo(f"Error initializing transformer: {e}", err=True)
        sys.exit(1)
    
    # Read input file
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            
            # Try to parse as JSON first
            try:
                texts = json.loads(content)
                if not isinstance(texts, list):
                    texts = [texts]
            except json.JSONDecodeError:
                # Parse as line-separated texts
                texts = [line.strip() for line in content.split('\n') if line.strip()]
        
        if not texts:
            click.echo("No texts found in input file.", err=True)
            sys.exit(1)
            
    except Exception as e:
        click.echo(f"Error reading input file: {e}", err=True)
        sys.exit(1)
    
    # Process texts
    click.echo(f"Processing {len(texts)} text(s) with {strength} variation strength...")
    
    all_results = []
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        with click.progressbar(texts, label="Transforming texts") as progress_texts:
            for i, text in enumerate(progress_texts):
                results = transformer.transform_text(text)
                
                # Add source information
                for result in results:
                    result['source_text_id'] = i + 1
                    result['source_file'] = str(input_file)
                
                all_results.extend(results)
        
        click.echo(f"\nGenerated {len(all_results)} total variations from {len(texts)} source texts.")
        
        # Export results
        output_base = output_dir / f"batch_results_{strength}"
        exported_files = []
        
        for fmt in format:
            try:
                exported_file = ExportManager.export(all_results, str(output_base), fmt)
                exported_files.append(exported_file)
                click.echo(f"Results exported to: {exported_file}")
            except Exception as e:
                click.echo(f"Error exporting to {fmt}: {e}", err=True)
        
        if exported_files:
            click.echo(f"\nBatch processing completed successfully. Exported {len(exported_files)} file(s).")
            
    except Exception as e:
        click.echo(f"Error during batch processing: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--output', '-o', 
              default='config.yaml',
              help='Output configuration file path (default: config.yaml)')
def generate_config(output):
    """Generate a default configuration file."""
    try:
        config = TransformationConfig()
        config.save_to_file(output)
        click.echo(f"Default configuration saved to: {output}")
        click.echo("Edit this file to customize transformation parameters.")
    except Exception as e:
        click.echo(f"Error generating configuration: {e}", err=True)
        sys.exit(1)


@cli.command()
def supported_languages():
    """List supported languages."""
    config = TransformationConfig()
    click.echo("Supported languages:")
    for lang in config.supported_languages:
        click.echo(f"  - {lang}")


def main():
    """Entry point for the CLI."""
    cli()


if __name__ == '__main__':
    main()