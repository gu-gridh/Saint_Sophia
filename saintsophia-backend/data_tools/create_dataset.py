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
            transcription = row['transcription']
            panel_title = row['panel_title']
            
            # Check if annotation file exists
            annotation_file = f"annotations/annotation_{inscription_id}.json"
            has_annotation = os.path.exists(annotation_file)
            
            num_annotations = 0
            annotation_types = []
            
            if has_annotation:
                try:
                    with open(annotation_file, 'r', encoding='utf-8') as af:
                        annotation_data = json.load(af)
                        
                        if isinstance(annotation_data, list):
                            num_annotations = len(annotation_data)
                            # Extract annotation types
                            for item in annotation_data:
                                if isinstance(item, dict) and 'properties' in item:
                                    if 'type' in item['properties']:
                                        annotation_types.append(item['properties']['type'])
                        else:
                            num_annotations = 1
                            if isinstance(annotation_data, dict) and 'properties' in annotation_data:
                                if 'type' in annotation_data['properties']:
                                    annotation_types.append(annotation_data['properties']['type'])
                except Exception as e:
                    print(f"  Warning: Could not read annotation file for inscription {inscription_id}: {e}")
            
            dataset.append({
                'inscription_id': inscription_id,
                'transcription': transcription,
                'panel_title': panel_title,
                'has_annotation': has_annotation,
                'num_annotations': num_annotations,
                'annotation_types': '; '.join(set(annotation_types)) if annotation_types else '',
                'transcription_length': len(transcription) if transcription else 0,
                'transcription_words': len(transcription.split()) if transcription else 0
            })
    
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
    
    print(f"✓ Combined dataset saved as {dataset_filename}")
    
    # Print summary
    total = len(dataset)
    with_annotations = len([d for d in dataset if d['has_annotation']])
    total_annotations = sum(d['num_annotations'] for d in dataset)
    
    print(f"\nDataset summary:")
    print(f"   Total inscriptions: {total}")
    print(f"   With annotations: {with_annotations} ({with_annotations/total*100:.1f}%)")
    print(f"   Total annotation objects: {total_annotations}")
    print(f"   Average transcription length: {sum(d['transcription_length'] for d in dataset)/total:.1f} characters")
    
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
