# app.py
from flask import Flask, render_template, request, send_file, jsonify
import re
import os
import tempfile
from pathlib import Path
import logging
from werkzeug.utils import secure_filename

from config_loader import ConfigLoader
from csv_processor import CSVProcessor
from kotlin_generator import KotlinGenerator
from models import Config

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'temp_uploads'

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def _split_kotlin_into_chunks(content: str, max_per_chunk: int = 150):
    """Split generated Kotlin into chunks by CategoryLaunchDataProviderModel entries.

    We detect each entry by occurrences of 'CategoryLaunchDataProviderModel(' and group
    up to max_per_chunk entries per returned chunk. Any header text (if present) is
    included at the beginning of the first chunk, and footer is added to every chunk.
    """
    try:
        # Find positions of each entry start
        pattern = r"CategoryLaunchDataProviderModel\("
        positions = [m.start() for m in re.finditer(pattern, content)]

        if not positions:
            return [content] if content.strip() else []

        # Split content into header (before first entry), entry blocks, and footer (after last entry)
        header = content[:positions[0]]
        
        # Extract footer - look for the closing pattern at the end: "        )\n    }\n}"
        # The footer pattern is: closing parenthesis for arrayOf, then function closing brace, then class closing brace
        footer_pattern = r'^\s+\)\s*\n\s+\}\s*\n\s*\}\s*$'
        footer_match = re.search(footer_pattern, content, re.MULTILINE)
        if footer_match:
            footer = content[footer_match.start():].strip()
            # Content without footer ends before footer starts
            content_without_footer = content[:footer_match.start()].rstrip()
        else:
            footer = ""
            content_without_footer = content
        
        # Extract each entry by slicing between start positions
        # Adjust positions to be relative to content_without_footer
        positions_in_content = [pos for pos in positions if pos < len(content_without_footer)]
        if not positions_in_content:
            positions_in_content = positions
        
        entries = []
        for i, start in enumerate(positions_in_content):
            if i + 1 < len(positions_in_content):
                end = positions_in_content[i + 1]
            else:
                end = len(content_without_footer)
            entries.append(content_without_footer[start:end].strip())

        # Group entries into chunks
        chunks = []
        header_text = header.strip() + "\n\n" if header.strip() else ""
        footer_text = "\n" + footer if footer else ""
        for i in range(0, len(entries), max_per_chunk):
            group = entries[i:i + max_per_chunk]
            chunk_body = "\n\n".join(group)
            # Add header and footer to every chunk
            chunks.append((header_text + chunk_body + footer_text).strip())
        return chunks
    except Exception as e:
        logger.error(f"Failed to split preview content: {e}")
        return [content]

def create_temp_config(csv_file_path: str) -> Config:
    """Create a temporary configuration for the uploaded CSV"""
    return Config(
        csv_file_path=csv_file_path,
        csv_encoding="utf-8",
        delimiter=",",
        columns={
            'leaf': 'Leaf',
            'category_id': 'ID',
            'level': 'Level',
            'path': 'Path',
            'brand': 'Brand',
            'colour': 'Colour',
            'material': 'Material',
            'pattern': 'Pattern',
            'size': 'Size',
            'size_group': 'Size group',
            'author': 'Author',
            'title': 'Title',
            'isbn': 'ISBN',
            'language_book': 'Language Book',
            'video_game_rating': 'Video Game Rating',
            'video_game_platform': 'Video Game Platform',
            'internal_memory_capacity': 'Internal memory capacity',
            'sim_lock': 'Sim Lock',
            'package_size': 'All shippable',
            'conditions': [
                'New with tags',
                'New without tags',
                'Very good',
                'Good',
                'Satisfactory',
                'Not fully functional'
            ]
        },
        output_kotlin_file="temp_output.kt",
        condition_mapping={
            "New with tags": "VintedConditionTypes.NEW_WITH_TAGS.id",
            "New without tags": "VintedConditionTypes.NEW_WITHOUT_TAGS.id",
            "Very good": "VintedConditionTypes.VERY_GOOD.id",
            "Good": "VintedConditionTypes.GOOD.id",
            "Satisfactory": "VintedConditionTypes.SATISFACTORY.id",
            "Not fully functional": "VintedConditionTypes.NOT_FULLY_FUNCTIONAL.id"
        },
        package_size_mapping={
            "All shippable": [
                "VintedPackageTypes.SMALL.id",
                "VintedPackageTypes.MEDIUM.id",
                "VintedPackageTypes.LARGE.id"
            ],
            "Light bulky": [
                "VintedPackageTypes.BULKY_SMALL.id",
                "VintedPackageTypes.BULKY_MEDIUM.id",
                "VintedPackageTypes.BULKY_LARGE.id",
                "VintedPackageTypes.BULKY_X_LARGE.id"
            ],
            "Heavy": [
                "VintedPackageTypes.HEAVY_SMALL.id",
                "VintedPackageTypes.HEAVY_MEDIUM.id",
                "VintedPackageTypes.HEAVY_LARGE.id"
            ],
            "Heavy bulky": [
                "VintedPackageTypes.HEAVY_BULKY_SMALL.id",
                "VintedPackageTypes.HEAVY_BULKY_MEDIUM.id",
                "VintedPackageTypes.HEAVY_BULKY_LARGE.id"
            ]
        }
    )

@app.route('/')
def index():
    """Main page with file upload form"""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle CSV file upload and generate Kotlin"""
    try:
        if 'csv_file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['csv_file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not file.filename.lower().endswith('.csv'):
            return jsonify({'error': 'Please upload a CSV file'}), 400
        
        # Save uploaded file temporarily
        filename = secure_filename(file.filename)
        temp_csv_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(temp_csv_path)
        
        try:
            # Create configuration
            config = create_temp_config(temp_csv_path)
            
            # Process CSV
            csv_processor = CSVProcessor(config)
            categories = csv_processor.process_csv()
            
            if not categories:
                return jsonify({'error': 'No leaf categories found in CSV'}), 400
            
            # Generate Kotlin
            kotlin_generator = KotlinGenerator(config)
            kotlin_content = kotlin_generator.generate_kotlin_models(categories)
            
            # Create temporary Kotlin file
            temp_kotlin_path = os.path.join(app.config['UPLOAD_FOLDER'], 'generated_models.kt')
            with open(temp_kotlin_path, 'w', encoding='utf-8') as f:
                f.write(kotlin_content)
            
            # Return success with file info
            return jsonify({
                'success': True,
                'message': f'Successfully processed {len(categories)} categories',
                'categories_count': len(categories),
                'download_url': '/download'
            })
            
        finally:
            # Clean up temporary CSV file
            if os.path.exists(temp_csv_path):
                os.remove(temp_csv_path)
                
    except Exception as e:
        logger.error(f"Error processing file: {e}")
        return jsonify({'error': f'Error processing file: {str(e)}'}), 500

@app.route('/download')
def download_kotlin():
    """Download the generated Kotlin file"""
    try:
        kotlin_path = os.path.join(app.config['UPLOAD_FOLDER'], 'generated_models.kt')
        if not os.path.exists(kotlin_path):
            return jsonify({'error': 'No generated file found'}), 404
        
        return send_file(
            kotlin_path,
            as_attachment=True,
            download_name='leaf_category_models.kt',
            mimetype='text/plain'
        )
    except Exception as e:
        logger.error(f"Error downloading file: {e}")
        return jsonify({'error': f'Error downloading file: {str(e)}'}), 500

@app.route('/preview')
def preview_kotlin():
    """Preview the generated Kotlin content"""
    try:
        kotlin_path = os.path.join(app.config['UPLOAD_FOLDER'], 'generated_models.kt')
        if not os.path.exists(kotlin_path):
            return jsonify({'error': 'No generated file found'}), 404
        
        with open(kotlin_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Split content into chunks of up to 150 CategoryLaunchDataProviderModel entries
        chunks = _split_kotlin_into_chunks(content, max_per_chunk=150)
        return jsonify({'chunks': chunks, 'total_chunks': len(chunks)})
    except Exception as e:
        logger.error(f"Error reading preview: {e}")
        return jsonify({'error': f'Error reading preview: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
