#!/usr/bin/env python3
"""
Export inscription data with transcription to CSV.
"""

import os
import sys
import csv
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
    
    if inscriptions.count() == 0:
        print("No inscriptions found with transcription data.")
        return None
    
    # Create CSV file
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    csv_filename = f'inscriptions_{timestamp}.csv'
    
    with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        
        # Write header
        writer.writerow(['id', 'transcription', 'panel_title'])
        
        # Write data
        for inscription in inscriptions:
            writer.writerow([
                inscription.id,
                inscription.transcription,
                inscription.panel.title if inscription.panel else ''
            ])
    
    print(f"✓ Exported {inscriptions.count()} inscriptions to {csv_filename}")
    return csv_filename


if __name__ == "__main__":
    result = export_inscriptions()
    if result:
        print(f"\nNext step: Use this file to download annotations:")
        print(f"  python download_annotations.py {result}")
    else:
        print("\nNo data to export.")
