"""
Export utilities for medical text transformation results.
"""

import json
import csv
import pandas as pd
from pathlib import Path
from typing import List, Dict, Any
import yaml


class ExportManager:
    """Handles exporting transformation results to various formats."""
    
    @staticmethod
    def export_to_json(results: List[Dict[str, Any]], output_path: str, indent: int = 2):
        """Export results to JSON format."""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=indent, ensure_ascii=False)
    
    @staticmethod
    def export_to_csv(results: List[Dict[str, Any]], output_path: str):
        """Export results to CSV format."""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Flatten the results for CSV export
        flattened_results = []
        for result in results:
            flat_result = {
                'variation_id': result['variation_id'],
                'original_text': result['original_text'],
                'transformed_text': result['transformed_text'],
                'language': result['language'],
                'variation_strength': result['variation_strength'],
                'transformations_applied': '; '.join(result.get('transformations_applied', [])),
            }
            
            # Add metadata if present
            if 'metadata' in result:
                for key, value in result['metadata'].items():
                    flat_result[f'metadata_{key}'] = value
            
            flattened_results.append(flat_result)
        
        df = pd.DataFrame(flattened_results)
        df.to_csv(output_path, index=False, encoding='utf-8')
    
    @staticmethod
    def export_to_excel(results: List[Dict[str, Any]], output_path: str):
        """Export results to Excel format."""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create multiple sheets for different views
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            # Main results sheet
            flattened_results = []
            for result in results:
                flat_result = {
                    'variation_id': result['variation_id'],
                    'original_text': result['original_text'],
                    'transformed_text': result['transformed_text'],
                    'language': result['language'],
                    'variation_strength': result['variation_strength'],
                    'transformations_applied': '; '.join(result.get('transformations_applied', [])),
                }
                
                # Add metadata if present
                if 'metadata' in result:
                    for key, value in result['metadata'].items():
                        flat_result[f'metadata_{key}'] = value
                
                flattened_results.append(flat_result)
            
            df_main = pd.DataFrame(flattened_results)
            df_main.to_excel(writer, sheet_name='Transformations', index=False)
            
            # Summary sheet
            summary_data = {
                'Total Variations': len(results),
                'Languages': list(set(r['language'] for r in results)),
                'Variation Strengths': list(set(r['variation_strength'] for r in results)),
                'Average Similarity': sum(r.get('metadata', {}).get('similarity_score', 0) for r in results) / len(results) if results else 0
            }
            
            summary_df = pd.DataFrame([summary_data])
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
    
    @staticmethod
    def export_to_yaml(results: List[Dict[str, Any]], output_path: str):
        """Export results to YAML format."""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            yaml.dump(results, f, default_flow_style=False, indent=2, allow_unicode=True)
    
    @staticmethod
    def export_to_txt(results: List[Dict[str, Any]], output_path: str):
        """Export results to plain text format."""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("Medical Text Transformation Results\n")
            f.write("=" * 50 + "\n\n")
            
            for i, result in enumerate(results, 1):
                f.write(f"Variation {result['variation_id']}:\n")
                f.write(f"Language: {result['language']}\n")
                f.write(f"Strength: {result['variation_strength']}\n")
                f.write(f"Original: {result['original_text']}\n")
                f.write(f"Transformed: {result['transformed_text']}\n")
                
                if result.get('transformations_applied'):
                    f.write(f"Transformations: {'; '.join(result['transformations_applied'])}\n")
                
                if result.get('metadata'):
                    f.write(f"Metadata: {result['metadata']}\n")
                
                f.write("-" * 30 + "\n\n")
    
    @classmethod
    def export(cls, results: List[Dict[str, Any]], output_path: str, format_type: str):
        """
        Export results to specified format.
        
        Args:
            results: List of transformation results
            output_path: Output file path (without extension)
            format_type: Format type ('json', 'csv', 'excel', 'yaml', 'txt')
        """
        format_map = {
            'json': (cls.export_to_json, '.json'),
            'csv': (cls.export_to_csv, '.csv'),
            'excel': (cls.export_to_excel, '.xlsx'),
            'xlsx': (cls.export_to_excel, '.xlsx'),
            'yaml': (cls.export_to_yaml, '.yaml'),
            'yml': (cls.export_to_yaml, '.yml'),
            'txt': (cls.export_to_txt, '.txt'),
        }
        
        if format_type not in format_map:
            raise ValueError(f"Unsupported format: {format_type}. Supported: {list(format_map.keys())}")
        
        export_func, extension = format_map[format_type]
        full_output_path = f"{output_path}{extension}"
        
        export_func(results, full_output_path)
        return full_output_path