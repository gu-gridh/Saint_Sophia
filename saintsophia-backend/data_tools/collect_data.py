#!/usr/bin/env python3
"""
Simple script to export inscription data and download annotations.
This script does everything in one place without complexity.
"""

import os
import sys
import csv
import json
import requests
import time
from datetime import datetime

# Add Django to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'saintsophia.settings')

import django
django.setup()

from apps.inscriptions.models import Inscription
from django.db.models import Q


def export_inscriptions():
    """Export inscriptions with transcription data to CSV."""
    print("Exporting inscriptions with transcription data...")
    
    # Get inscriptions with transcription
    query = Q(transcription__isnull=False) & ~Q(transcription__exact='')
    inscriptions = Inscription.objects.filter(query).select_related('panel')
    
    print(f"Found {inscriptions.count()} inscriptions with transcription")
    
    # Create CSV file
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    csv_filename = f'inscriptions_{timestamp}.csv'
    
    with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        
        # Define all fields to export
        headers = [
            'id', 'title', 'position_on_surface', 'panel_title', 'panel_room',
            'type_of_inscription', 'elevation', 'height', 'width', 'language', 
            'writing_system', 'min_year', 'max_year', 'transcription', 
            'interpretative_edition', 'romanisation', 'inscriber', 
            'translation_eng', 'translation_ukr', 'comments_eng', 'comments_ukr'
        ]
        
        writer.writerow(headers)
        
        # Write data for each inscription
        for inscription in inscriptions:
            row = [
                inscription.id,
                inscription.title or '',
                inscription.position_on_surface or '',
                inscription.panel.title if inscription.panel else '',
                inscription.panel.room if inscription.panel else '',
                str(inscription.type_of_inscription) if inscription.type_of_inscription else '',
                inscription.elevation or '',
                inscription.height or '',
                inscription.width or '',
                str(inscription.language) if inscription.language else '',
                str(inscription.writing_system) if inscription.writing_system else '',
                inscription.min_year or '',
                inscription.max_year or '',
                inscription.transcription or '',
                inscription.interpretative_edition or '',
                inscription.romanisation or '',
                str(inscription.inscriber) if inscription.inscriber else '',
                inscription.translation_eng or '',
                inscription.translation_ukr or '',
                inscription.comments_eng or '',
                inscription.comments_ukr or '',
            ]
            writer.writerow(row)
    
    print(f"Exported to {csv_filename}")
    return csv_filename


def download_annotation(surface_id):
    """Download annotation for a single surface."""
    url = f"https://saintsophia.dh.gu.se/api/inscriptions/annotation/?surface={surface_id}"
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            return None  # No annotation found
        else:
            print(f"Error {response.status_code} for surface {surface_id}")
            return None
    except Exception as e:
        print(f"Request failed for {surface_id}: {e}")
        return None


def download_all_annotations(csv_filename):
    """Download annotations for all inscriptions in CSV."""
    print("\nDownloading annotations.")
    
    # Create output directory
    output_dir = 'annotations'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    successful = 0
    failed = 0
    
    with open(csv_filename, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            inscription_id = row['id']
            panel_title = row['panel_title']
            
            if not panel_title:
                print(f"No panel title for inscription {inscription_id}")
                failed += 1
                continue

            print(f"Downloading annotation for inscription {inscription_id} (surface {panel_title})")

            annotation_data = download_annotation(panel_title)
            
            if annotation_data:
                # Save to file
                filename = f"annotation_{inscription_id}.json"
                filepath = os.path.join(output_dir, filename)
                
                with open(filepath, 'w', encoding='utf-8') as af:
                    json.dump(annotation_data, af, indent=2, ensure_ascii=False)
                
                print(f"Saved {filename}")
                successful += 1
            else:
                print(f"No annotation found")
                failed += 1
            
            time.sleep(0.5)  # Be nice to the server
    
    print(f"\nDownload complete: {successful} successful, {failed} failed")
    print(f"Annotation files saved in '{output_dir}' folder")


def create_simple_dataset(csv_filename):
    """Create a simple dataset combining inscriptions and annotations."""
    print("\nCreating combined dataset...")
    
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
            if has_annotation:
                try:
                    with open(annotation_file, 'r', encoding='utf-8') as af:
                        annotation_data = json.load(af)
                        num_annotations = len(annotation_data) if isinstance(annotation_data, list) else 1
                except:
                    pass
            
            # Create dataset entry with all original fields plus annotation info
            dataset_entry = dict(row)  # Copy all original fields
            dataset_entry.update({
                'has_annotation': has_annotation,
                'num_annotations': num_annotations,
                'transcription_length': len(transcription) if transcription else 0
            })
            
            dataset.append(dataset_entry)
    
    # Save combined dataset
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    dataset_filename = f'combined_dataset_{timestamp}.csv'
    
    with open(dataset_filename, 'w', newline='', encoding='utf-8') as f:
        if dataset:
            writer = csv.DictWriter(f, fieldnames=dataset[0].keys())
            writer.writeheader()
            writer.writerows(dataset)
    
    print(f"Combined dataset saved as {dataset_filename}")
    
    # Print summary
    total = len(dataset)
    with_annotations = len([d for d in dataset if d['has_annotation']])
    print(f"\nSummary:")
    print(f"  Total inscriptions: {total}")
    print(f"  With annotations: {with_annotations} ({with_annotations/total*100:.1f}%)")
    print(f"  Without annotations: {total-with_annotations}")


def main():
    print("Saint Sophia Data Collection Tool")
    print("=" * 40)
    
    # Step 1: Export inscriptions
    csv_filename = export_inscriptions()
    
    # Step 2: Download annotations
    download_all_annotations(csv_filename)
    
    # Step 3: Create combined dataset
    create_simple_dataset(csv_filename)
    
    print("\n" + "=" * 40)
    print("All done! Files created:")
    print(f"  - {csv_filename} (raw inscription data)")
    print("  - annotations/ (annotation JSON files)")
    print("  - combined_dataset_*.csv (ready for ML)")


if __name__ == "__main__":
    main()
