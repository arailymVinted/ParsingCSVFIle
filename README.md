# CSV to Kotlin Converter

A powerful tool to convert CSV category data into Kotlin data provider models for Vinted category launches.

## Features

- **CSV Processing**: Automatically processes CSV files with category data
- **Kotlin Generation**: Generates clean, formatted Kotlin code
- **Web Interface**: User-friendly web UI for easy file conversion
- **Command Line**: CLI tool for batch processing and automation
- **Smart Mapping**: Automatic condition and package size mapping
- **Category Level Support**: Extracts and includes category hierarchy levels

## Requirements

- Python 3.8+
- Required Python packages (see requirements.txt)

## Installation

1. Clone or download this repository
2. Create a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Web Interface (Recommended)

1. Start the web server:
   ```bash
   # Option 1: Use the startup script
   ./start_web.sh
   
   # Option 2: Manual start
   source venv/bin/activate
   python app.py
   ```
2. Open your browser and go to `http://localhost:8080`
3. Drag and drop your CSV file or click to browse
4. Click "Convert to Kotlin"
5. Preview the generated code and download the Kotlin file

### Command Line Interface

1. Place your CSV file in the `data/` directory
2. Update `config.yaml` if needed
3. Run the converter:
   ```bash
   python main.py
   ```
4. Find the generated Kotlin file in `output/leaf_category_models.kt`

## CSV Format Requirements

Your CSV file should contain these columns:

| Column | Description | Required |
|--------|-------------|----------|
| `Leaf` | Boolean indicating if category is a leaf node | ✅ |
| `ID` | Unique category identifier | ✅ |
| `Level` | Category hierarchy level (1, 2, 3, etc.) | ✅ |
| `Brand` | Boolean indicating if brand field is visible | ✅ |
| `Colour` | Boolean indicating if colour field is visible | ✅ |
| `Package size` | Package size category (e.g., "All shippable") | ✅ |
| `New with tags` | Boolean for condition availability | ✅ |
| `New without tags` | Boolean for condition availability | ✅ |
| `Very good` | Boolean for condition availability | ✅ |
| `Good` | Boolean for condition availability | ✅ |
| `Satisfactory` | Boolean for condition availability | ✅ |
| `Not fully functional` | Boolean for condition availability | ✅ |

### Sample Data

Check `data/sample_data.csv` for an example of the expected CSV format. This file shows:
- How to structure your data
- Required column names
- Expected data types
- Sample category entries

## Generated Kotlin Output

The tool generates `CategoryLaunchDataProviderModel` entries with:

```kotlin
CategoryLaunchDataProviderModel(
    categoryId = 5429L,
    categoryLevel = 3L,
    expectedFieldsVisibility = listOf(...),
    expectedConditionTypeIds = setOf(...),
    expectedPackageSizeIds = setOf(...),
    expectedSizeGroupsIds = listOf(),
    brandId = supplyTestsHelper.getDefaultBrandId(5429L)
)
```

## Configuration

The `config.yaml` file allows you to customize:

- **CSV Settings**: File path, encoding, column mappings
- **Output Settings**: File paths for generated code
- **Condition Mappings**: Map CSV conditions to Vinted condition types
- **Package Size Mappings**: Map CSV package sizes to Vinted package types

## Project Structure

```
ParsingCSVFIle/
├── app.py                 # Flask web application
├── main.py               # Command-line entry point
├── start_web.sh          # Web interface startup script
├── config.yaml           # Configuration file
├── config_loader.py      # Configuration loader
├── csv_processor.py      # CSV processing logic
├── kotlin_generator.py   # Kotlin code generation
├── models.py             # Data models
├── templates/            # Web templates
│   └── index.html       # Main web interface
├── data/                 # Input CSV files
│   └── sample_data.csv  # Example CSV format
├── output/               # Generated output files
├── temp_uploads/         # Temporary upload storage
├── .gitignore           # Git ignore rules
└── requirements.txt      # Python dependencies
```

## Web Interface Features

- **Drag & Drop**: Easy file upload with visual feedback
- **Real-time Processing**: Live conversion status and progress
- **Preview Mode**: View generated Kotlin code before downloading
- **Responsive Design**: Works on desktop and mobile devices
- **Error Handling**: Clear error messages and validation
- **File Validation**: Ensures uploaded files are valid CSV

## GitHub Setup

### Initial Setup

1. **Initialize Git repository:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit: CSV to Kotlin converter"
   ```

2. **Create GitHub repository:**
   - Go to [GitHub](https://github.com) and create a new repository
   - Don't initialize with README (we already have one)
   - Copy the repository URL

3. **Connect to GitHub:**
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
   git branch -M main
   git push -u origin main
   ```

### Updating Your Repository

```bash
# After making changes
git add .
git commit -m "Description of your changes"
git push
```

## Troubleshooting

### Common Issues

1. **"No module named 'yaml'"**: Install PyYAML: `pip install pyyaml`
2. **"No leaf categories found"**: Check your CSV has `Leaf` column with `TRUE` values
3. **"Missing required columns"**: Ensure all required columns are present in your CSV
4. **File upload errors**: Check file size (max 16MB) and ensure it's a valid CSV
5. **Port already in use**: The web interface uses port 8080 by default. If you get a port conflict, modify `app.py` to use a different port.

### CSV Validation

- Ensure your CSV uses semicolon (`;`) as delimiter
- Check that boolean columns contain `TRUE`/`FALSE` values
- Verify category IDs are numeric
- Confirm category levels are numeric

## Contributing

Feel free to submit issues, feature requests, or pull requests to improve this tool.

## License

This project is open source and available under the MIT License.

