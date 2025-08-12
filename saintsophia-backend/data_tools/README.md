# Data Collection Tools

Simple tools for collecting Saint Sophia inscription data and annotations.

## Files

### `export_inscriptions.py` - Export inscription data
Exports inscriptions with transcription data from the database to CSV.

**Usage:**
```bash
python export_inscriptions.py
```

### `download_annotations.py` - Download annotation data
Downloads annotation data from the API for each inscription in the CSV.

**Usage:**
```bash
python download_annotations.py inscriptions_TIMESTAMP.csv
```

### `create_dataset.py` - Create ML dataset
Combines inscription and annotation data into a single CSV for machine learning.

**Usage:**
```bash
python create_dataset.py inscriptions_TIMESTAMP.csv
```

### `test_api.py` - Test script
Tests if the Saint Sophia API is working.

**Usage:**
```bash
python test_api.py
```

### `collect_data.py` - All-in-one script
Does all three steps above in one command (if you prefer that).

### `upload_cooments.py` - Update database from CSV
Updates inscription data in the database from a CSV file. Automatically detects CSV columns and matches them to model fields.

**Usage:**
```bash
python upload_cooments.py data.csv
```

**CSV Requirements:**
- Must have an `id` column with inscription IDs
- Column names must match model field names exactly
- Common fields: `transcription`, `comments_eng`, `comments_ukr`, `interpretative_edition`, `romanisation`

**Example CSV:**
```csv
id,transcription,comments_eng,romanisation
123,"Ancient text","Good condition","Romanized version"
124,"More text","Partially damaged","Another romanization"
```

## Step-by-step workflow

```bash
# 1. Test API connection (optional)
python test_api.py

# 2. Export inscriptions from database
python export_inscriptions.py
# → Creates: inscriptions_TIMESTAMP.csv

# 3. Download annotations from API
python download_annotations.py inscriptions_TIMESTAMP.csv
# → Creates: annotations/ folder with JSON files

# 4. Create combined ML dataset
python create_dataset.py inscriptions_TIMESTAMP.csv
# → Creates: combined_dataset_TIMESTAMP.csv
```

## What you get

The final dataset includes:
- `inscription_id` - Database ID
- `transcription` - The actual text
- `panel_title` - Surface identifier  
- `has_annotation` - Whether annotation data exists
- `num_annotations` - Number of annotation objects
- `annotation_types` - Types of annotations found
- `transcription_length` - Length of transcription in characters
- `transcription_words` - Number of words in transcription
