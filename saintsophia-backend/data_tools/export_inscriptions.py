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
    print("Exporting inscriptions with transcription data.")
    
    # Get inscriptions with transcription
    query = Q(transcription__isnull=False) & ~Q(transcription__exact='')
    inscriptions = Inscription.objects.filter(query).select_related('panel')
    
    print(f"Found {inscriptions.count()} inscriptions with transcription")
    
    if inscriptions.count() == 0:
        print("No inscriptions found with transcription data.")
        return None
    
    # Create CSV file with time
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
    
    print(f"Exported {inscriptions.count()} inscriptions to {csv_filename}")
    return csv_filename


if __name__ == "__main__":
    result = export_inscriptions()
    if result:
        print(f"\nNext step: Use this file to download annotations:")
        print(f"  python download_annotations.py {result}")
    else:
        print("\nNo data to export.")
