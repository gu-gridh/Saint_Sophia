#!/usr/bin/env python3
"""
Simple script to update inscription data from CSV file.
Automatically detects columns and updates matching model fields.
"""

import os
import sys
import csv

# Add Django to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'saintsophia.settings')

import django
django.setup()

from apps.inscriptions.models import Inscription


def update_inscriptions_from_csv(csv_file):
    """Update inscriptions from CSV file. Automatically detects columns."""
    
    if not os.path.exists(csv_file):
        print(f"Error: File '{csv_file}' not found")
        return
    
    print(f"Reading CSV file: {csv_file}")
    
    # Get available model fields
    model_fields = [field.name for field in Inscription._meta.get_fields() 
                   if not field.many_to_many and not field.one_to_many]
    
    updated_count = 0
    error_count = 0
    
    with open(csv_file, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        csv_columns = reader.fieldnames
        
        print(f"CSV columns: {csv_columns}")
        
        # Find matching columns
        matching_fields = []
        for col in csv_columns:
            if col in model_fields:
                matching_fields.append(col)
        
        print(f"Matching model fields: {matching_fields}")
        
        if 'id' not in csv_columns:
            print("Error: CSV must have 'id' column")
            return
        
        if not matching_fields:
            print("Error: No matching model fields found in CSV")
            return
        
        for row_num, row in enumerate(reader, start=2):
            try:
                inscription_id = row['id']
                if not inscription_id:
                    print(f"Row {row_num}: Missing ID, skipping")
                    error_count += 1
                    continue
                
                # Get inscription
                try:
                    inscription = Inscription.objects.get(id=inscription_id)
                except Inscription.DoesNotExist:
                    print(f"Row {row_num}: Inscription {inscription_id} not found")
                    error_count += 1
                    continue
                
                # Update matching fields
                updated = False
                for field in matching_fields:
                    if field != 'id' and field in row:
                        new_value = row[field].strip() if row[field] else ''
                        old_value = getattr(inscription, field, '') or ''
                        
                        if str(new_value) != str(old_value):
                            setattr(inscription, field, new_value)
                            updated = True
                            print(f"Row {row_num}: Updated {field} for inscription {inscription_id}")
                
                if updated:
                    inscription.save()
                    updated_count += 1
                
            except Exception as e:
                print(f"Row {row_num}: Error - {e}")
                error_count += 1
    
    print(f"\nFinished!")
    print(f"Updated: {updated_count}")
    print(f"Errors: {error_count}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python upload_cooments.py <csv_file>")
        print("Example: python upload_cooments.py comments.csv")
        sys.exit(1)
    
    csv_file = sys.argv[1]
    update_inscriptions_from_csv(csv_file)