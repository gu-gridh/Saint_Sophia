#!/usr/bin/env python3
"""
Create a combined dataset from inscriptions and annotations.
"""

import os
import sys
import csv
import json
from datetime import datetime


def create_dataset(csv_filename):
    """Create a combined dataset from inscriptions and annotations."""
    if not os.path.exists(csv_filename):
        print(f"Error: File {csv_filename} not found")
        return False
    
    print(f"Creating combined dataset from {csv_filename}...")
    
    dataset = []
    
    with open(csv_filename, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            inscription_id = row['id']
            
            # Check if annotation file exists
            annotation_file = f"annotations/annotation_{inscription_id}.json"
            
            if os.path.exists(annotation_file):
                try:
                    with open(annotation_file, 'r', encoding='utf-8') as af:
                        annotation_data = json.load(af)
                        
                        # Handle both single annotation and list of annotations
                        annotations = annotation_data if isinstance(annotation_data, list) else [annotation_data]
                        
                        # Create one row per annotation
                        for i, annotation in enumerate(annotations):
                            # Start with all inscription fields
                            dataset_entry = dict(row)
                            
                            # Add annotation-specific fields
                            dataset_entry['annotation_index'] = i
                            dataset_entry['total_annotations_for_inscription'] = len(annotations)
                            
                            # Extract annotation properties
                            if isinstance(annotation, dict):
                                # Add raw annotation data
                                dataset_entry['annotation_geometry_type'] = annotation.get('type', '')
                                
                                # Extract properties if they exist
                                props = annotation.get('properties', {})
                                for prop_key, prop_value in props.items():
                                    dataset_entry[f'annotation_{prop_key}'] = str(prop_value) if prop_value is not None else ''
                                
                                # Extract geometry info
                                geometry = annotation.get('geometry', {})
                                dataset_entry['annotation_geometry'] = geometry.get('type', '')
                                
                                # Add coordinates info (simplified)
                                coords = geometry.get('coordinates', [])
                                if coords:
                                    dataset_entry['annotation_has_coordinates'] = True
                                    if isinstance(coords, list) and len(coords) > 0:
                                        dataset_entry['annotation_coord_count'] = len(coords) if isinstance(coords[0], list) else 1
                                else:
                                    dataset_entry['annotation_has_coordinates'] = False
                                    dataset_entry['annotation_coord_count'] = 0
                            
                            dataset.append(dataset_entry)
                            
                except Exception as e:
                    print(f"  Warning: Could not read annotation file for inscription {inscription_id}: {e}")
                    # Add inscription without annotation data
                    dataset_entry = dict(row)
                    dataset_entry['annotation_index'] = -1
                    dataset_entry['total_annotations_for_inscription'] = 0
                    dataset_entry['annotation_error'] = str(e)
                    dataset.append(dataset_entry)
            else:
                # Add inscription without annotation data
                dataset_entry = dict(row)
                dataset_entry['annotation_index'] = -1
                dataset_entry['total_annotations_for_inscription'] = 0
                dataset_entry['annotation_missing'] = True
                dataset.append(dataset_entry)
    
    if not dataset:
        print("No data to process")
        return False
    
    # Save combined dataset
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    dataset_filename = f'combined_dataset_{timestamp}.csv'
    
    with open(dataset_filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=dataset[0].keys())
        writer.writeheader()
        writer.writerows(dataset)
    
    print(f"Combined dataset saved as {dataset_filename}")
    
    # Print summary
    total_rows = len(dataset)
    inscriptions_with_annotations = len(set(d['id'] for d in dataset if d.get('annotation_index', -1) >= 0))
    total_inscriptions = len(set(d['id'] for d in dataset))
    annotation_rows = len([d for d in dataset if d.get('annotation_index', -1) >= 0])
    
    print(f"\nDataset summary:")
    print(f"Total rows (one per annotation): {total_rows}")
    print(f"Total unique inscriptions: {total_inscriptions}")
    print(f"Inscriptions with annotations: {inscriptions_with_annotations}")
    print(f"Rows with annotation data: {annotation_rows}")
    if total_inscriptions > 0:
        print(f"Coverage: {inscriptions_with_annotations/total_inscriptions*100:.1f}% inscriptions have annotations")
    
    # Show some annotation types if available
    annotation_types = set()
    for d in dataset:
        for key, value in d.items():
            if key.startswith('annotation_type') and value:
                annotation_types.add(value)
    
    if annotation_types:
        print(f"Annotation types found: {', '.join(sorted(annotation_types))}")

    return True


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python create_dataset.py <inscriptions_csv_file>")
        print("Example: python create_dataset.py inscriptions_20240812_123456.csv")
        sys.exit(1)
    
    csv_file = sys.argv[1]
    success = create_dataset(csv_file)
    
    if success:
        print(f"\n All done! Your ML dataset is ready.")
    else:
        print("\nFailed to create dataset.")
