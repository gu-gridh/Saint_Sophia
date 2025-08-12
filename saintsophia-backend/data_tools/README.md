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

**NEW: Each row represents one annotation** (not one inscription), so you get more detailed training data.

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

**Usage:**
```bash
python collect_data.py
```

**What it does:**
1. Exports inscriptions with transcription data
2. Downloads annotation data from API for each inscription
3. Creates a combined ML-ready dataset

**Output:**
- `inscriptions_TIMESTAMP.csv` - Raw inscription data
- `annotations/` folder - JSON files with annotation data  
- `combined_dataset_TIMESTAMP.csv` - Ready for ML training

**Use this if:** You want everything done automatically in one command.

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

## Quick Start

**Want everything in one command?**
```bash
python collect_data.py
```

**Want to control each step?**
```bash
python export_inscriptions.py
python download_annotations.py inscriptions_*.csv  
python create_dataset.py inscriptions_*.csv
```

**Want to update the database?**
```bash
python upload_cooments.py your_data.csv
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

The final dataset structure has changed! **Each row now represents one annotation** instead of one inscription.

### Inscription CSV (`inscriptions_TIMESTAMP.csv`)
Contains all 23 inscription fields including:
- Basic info: `id`, `title`, `transcription`, `panel_title`, `panel_room`
- Metadata: `type_of_inscription`, `elevation`, `height`, `width`, `language`, `writing_system`
- Dating: `min_year`, `max_year`
- Content: `interpretative_edition`, `romanisation`, `inscriber`
- Translations: `translation_eng`, `translation_ukr`
- Comments: `comments_eng`, `comments_ukr`
- Timestamps: `created_at`, `updated_at`

### Combined Dataset (`combined_dataset_TIMESTAMP.csv`)
**NEW STRUCTURE**: Each row = one annotation + full inscription context

**Columns include:**
- **All inscription fields** (23 fields from above)
- **Annotation metadata:**
  - `annotation_index` - Which annotation this is for the inscription (0, 1, 2...)
  - `total_annotations_for_inscription` - Total annotations for this inscription
- **Annotation properties** (dynamically extracted):
  - `annotation_geometry_type` - Shape type (Point, Polygon, etc.)
  - `annotation_type` - Type of annotation
  - `annotation_[property]` - All other annotation properties
  - `annotation_geometry` - Geometry info
  - `annotation_has_coordinates` - Boolean for coordinate existence
  - `annotation_coord_count` - Number of coordinate points
- **Special cases:**
  - Inscriptions without annotations: `annotation_index = -1`
  - Missing files: `annotation_missing = True`
  - Error cases: `annotation_error = "error message"`

**Benefits:**
- More training examples (5 annotations = 5 rows instead of 1)
- Individual annotation analysis
- Full inscription context for each annotation
- Ready for predicting annotation properties
