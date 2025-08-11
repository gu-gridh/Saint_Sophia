# Inscription Data Export Scripts

This repository contains two scripts to export inscription data to CSV format where at least one field in the "graffiti data" section is not empty.

## Graffiti Data Fields

The scripts filter inscriptions based on the following fields from the "graffiti data" section:
- `transcription` (RichTextField)
- `interpretative_edition` (RichTextField)
- `romanisation` (RichTextField)
- `mentioned_person` (ManyToManyField)
- `inscriber` (ForeignKey)
- `translation_eng` (RichTextField)
- `translation_ukr` (RichTextField)
- `comments_eng` (RichTextField)
- `comments_ukr` (RichTextField)

## Option 1: Django Management Command

Use this if you're working within the Django project environment.

```bash
# Basic usage - exports to timestamped file
python manage.py export_inscriptions_csv

# Specify output file
python manage.py export_inscriptions_csv --output my_inscriptions.csv

# Include inscriptions with empty text fields but with related objects
python manage.py export_inscriptions_csv --include-empty-text-fields
```

## Option 2: Standalone Script

Use this if you want to run the script independently.

```bash
# Basic usage - exports to timestamped file
python export_inscriptions_standalone.py

# Specify output file
python export_inscriptions_standalone.py --output my_inscriptions.csv

# Include inscriptions with empty text fields but with related objects
python export_inscriptions_standalone.py --include-empty-text-fields
```

## Output

The CSV file will contain all fields from the Inscription model, including:

### Basic Information
- id, title, position_on_surface
- panel_title, panel_room

### Inscription Metadata
- type_of_inscription, genres, tags
- elevation, height, width
- language, writing_system
- min_year, max_year, dating_criteria

### Graffiti Data (the filtered fields)
- transcription, interpretative_edition, romanisation
- mentioned_persons, inscriber
- translation_eng, translation_ukr
- comments_eng, comments_ukr

### Material Metadata
- conditions, alignments, extra_alphabetical_signs

### Bibliography and Contributions
- bibliography_items, authors

### Timestamps
- created_at, updated_at

## Notes

- The script uses UTF-8 encoding to handle Unicode characters properly
- Many-to-many relationships are joined with semicolons (;)
- Empty fields are represented as empty strings
- Rich text fields may contain HTML markup
- File names include timestamps by default to avoid overwriting
