#!/usr/bin/env python3
"""
Download annotation data for inscriptions from CSV file.
"""

import os
import csv
import json
import requests
import time
import sys
from datetime import datetime


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
            print(f"    Error {response.status_code} for surface {surface_id}")
            return None
    except Exception as e:
        print(f"    Request failed for {surface_id}: {e}")
        return None


def download_annotations(csv_filename):
    """Download annotations for all inscriptions in CSV."""
    if not os.path.exists(csv_filename):
        print(f"Error: File {csv_filename} not found")
        return False
    
    print(f"Downloading annotations from {csv_filename}...")
    
    # Create output directory
    output_dir = 'annotations'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created {output_dir}/ directory")
    
    successful = 0
    failed = 0
    no_panel = 0
    
    with open(csv_filename, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            inscription_id = row['id']
            panel_title = row['panel_title']
            
            if not panel_title:
                print(f"  Inscription {inscription_id}: No panel title")
                no_panel += 1
                continue
            
            print(f"  Inscription {inscription_id} → Surface {panel_title}", end="")
            
            annotation_data = download_annotation(panel_title)
            
            if annotation_data:
                # Save to file
                filename = f"annotation_{inscription_id}.json"
                filepath = os.path.join(output_dir, filename)
                
                with open(filepath, 'w', encoding='utf-8') as af:
                    json.dump(annotation_data, af, indent=2, ensure_ascii=False)
                
                num_items = len(annotation_data) if isinstance(annotation_data, list) else 1
                print(f" ✓ ({num_items} annotation(s))")
                successful += 1
            else:
                print(" ✗ (no annotation)")
                failed += 1
            
            time.sleep(0.5)  # Be nice to the server
    
    print(f"\nDownload summary:")
    print(f"  ✓ Successful: {successful}")
    print(f"  ✗ Failed/No annotation: {failed}")
    print(f"  ⚠ No panel title: {no_panel}")
    print(f"  📁 Files saved in '{output_dir}/' folder")
    
    return successful > 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python download_annotations.py <inscriptions_csv_file>")
        print("Example: python download_annotations.py inscriptions_20240812_123456.csv")
        sys.exit(1)
    
    csv_file = sys.argv[1]
    success = download_annotations(csv_file)
    
    if success:
        print(f"\nNext step: Create combined dataset:")
        print(f"  python create_dataset.py {csv_file}")
    else:
        print("\nNo annotations downloaded.")
