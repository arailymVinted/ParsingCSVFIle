# csv_processor.py
import csv
import logging
from pathlib import Path
from typing import List, Dict, Optional
from models import CategoryData, CategoryAttributes, Config, FieldTypeInfo

logger = logging.getLogger(__name__)


class CSVProcessor:
    def __init__(self, config: Config):
        self.config = config
        self._column_indices: Dict[str, int] = {}

    def _find_header_row(self, csv_data: List[List[str]]) -> int:
        """Find the row that contains the actual column headers"""
        # Look for a row that contains expected column names
        expected_columns = ['ID', 'Code', 'Name', 'Path', 'Level', 'Leaf']
        
        for i, row in enumerate(csv_data):
            if all(col in row for col in expected_columns):
                return i
        
        # Fallback to first row if no match found
        return 0

    def _validate_csv_structure(self, headers: List[str]) -> None:
        """Validate that required columns exist in CSV"""
        required_columns = [
            self.config.columns['leaf'],
            self.config.columns['category_id'],
            self.config.columns['path'],
            self.config.columns['brand'],
            self.config.columns['colour'],
            self.config.columns['level']
        ]
        
        # Add new required columns
        new_columns = ['material', 'size_group', 'author', 'title', 'isbn']
        for col in new_columns:
            if col in self.config.columns:
                required_columns.append(self.config.columns[col])
        
        # Add package_size column if it exists in config
        if 'package_size' in self.config.columns:
            required_columns.append(self.config.columns['package_size'])

        missing_columns = [col for col in required_columns if col not in headers]
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")

        # Store column indices for efficient access
        for col_name in required_columns:
            self._column_indices[col_name] = headers.index(col_name)

        # Store condition column indices
        for condition in self.config.columns['conditions']:
            if condition in headers:
                self._column_indices[condition] = headers.index(condition)
            else:
                logger.warning(f"Condition column '{condition}' not found in CSV")

        # Store package size boolean column indices
        package_size_columns = ['All shippable', 'Heavy shipping', 'Light bulky', 'Heavy bulky']
        for col_name in package_size_columns:
            if col_name in headers:
                self._column_indices[col_name] = headers.index(col_name)
            else:
                logger.warning(f"Package size column '{col_name}' not found in CSV")

    def _extract_attributes(self, row: List[str]) -> CategoryAttributes:
        """Extract category attributes from CSV row"""
        brand_col = self.config.columns['brand']
        colour_col = self.config.columns['colour']
        material_col = self.config.columns['material']
        size_group_col = self.config.columns['size_group']
        author_col = self.config.columns['author']
        title_col = self.config.columns['title']
        isbn_col = self.config.columns['isbn']

        # Get column indices
        brand_idx = self._column_indices.get(brand_col)
        colour_idx = self._column_indices.get(colour_col)
        material_idx = self._column_indices.get(material_col)
        size_group_idx = self._column_indices.get(size_group_col)
        author_idx = self._column_indices.get(author_col)
        title_idx = self._column_indices.get(title_col)
        isbn_idx = self._column_indices.get(isbn_col)

        # Extract values safely
        def safe_extract(idx, default=""):
            return row[idx].strip() if idx is not None and idx < len(row) else default

        brand_value = safe_extract(brand_idx)
        colour_value = safe_extract(colour_idx)
        material_value = safe_extract(material_idx)
        size_group_value = safe_extract(size_group_idx)
        author_value = safe_extract(author_idx)
        title_value = safe_extract(title_idx)
        isbn_value = safe_extract(isbn_idx)

        return CategoryAttributes(
            brand=True if brand_value == 'TRUE' else None if brand_value == '' else brand_value,
            colour=True if colour_value == 'TRUE' else None if colour_value == '' else colour_value,
            material=True if material_value == 'TRUE' else None if material_value == '' else material_value,
            size_group=True if size_group_value == 'TRUE' else None if size_group_value == '' else size_group_value,
            author=True if author_value == 'TRUE' else None if author_value == '' else author_value,
            title=True if title_value == 'TRUE' else None if title_value == '' else title_value,
            isbn=True if isbn_value == 'TRUE' else None if isbn_value == '' else isbn_value,
        )

    def _extract_path(self, row: List[str]) -> str:
        """Extract path from CSV row"""
        path_col = self.config.columns['path']
        path_idx = self._column_indices.get(path_col)
        
        if path_idx is None or path_idx >= len(row):
            return ""
        
        return row[path_idx].strip()

    def _extract_package_size(self, row: List[str]) -> str:
        """Extract package size from CSV row by checking boolean columns first, then Package size column"""
        # Check boolean package size columns in order of preference
        package_size_columns = [
            ('All shippable', 'All shippable'),
            ('Heavy shipping', 'Heavy'),
            ('Light bulky', 'Light bulky'),
            ('Heavy bulky', 'Heavy bulky')
        ]
        
        for col_name, package_type in package_size_columns:
            col_idx = self._column_indices.get(col_name)
            if col_idx is not None and col_idx < len(row):
                value = row[col_idx].strip().upper()
                if value == 'TRUE':
                    return package_type
        
        # Fallback to the Package size column if no boolean columns are TRUE
        package_size_col = self.config.columns.get('package_size')
        if package_size_col:
            package_size_idx = self._column_indices.get(package_size_col)
            if package_size_idx is not None and package_size_idx < len(row):
                package_size_value = row[package_size_idx].strip()
                if package_size_value and package_size_value != '-':
                    # Map the Package size column value to the correct package type
                    if package_size_value == 'Light bulky':
                        return 'Light bulky'
                    elif package_size_value == 'Heavy':
                        return 'Heavy'
                    elif package_size_value == 'Heavy bulky':
                        return 'Heavy bulky'
                    elif package_size_value == 'All shippable':
                        return 'All shippable'
                    else:
                        return package_size_value
        
        return "All shippable"

    def _extract_status_counts(self, row: List[str]) -> Dict[str, int]:
        """Extract status counts from CSV row"""
        statuses_count = {}

        for condition in self.config.columns['conditions']:
            condition_idx = self._column_indices.get(condition)
            if condition_idx is not None and condition_idx < len(row):
                value = row[condition_idx].strip().upper()
                statuses_count[condition] = 1 if value == 'TRUE' else 0
            else:
                statuses_count[condition] = 0

        return statuses_count

    def _extract_field_types(self, row: List[str]) -> Dict[str, FieldTypeInfo]:
        """Extract field type information based on the field type row (row 3 in CSV)"""
        field_types = {}
        
        # Field mappings based on the CSV structure
        field_mappings = {
            'brand': {'upload_form': True, 'filter': True},      # Upload Form + Filters
            'colour': {'upload_form': True, 'filter': True},     # Upload Form + Filters  
            'material': {'upload_form': True, 'filter': True},   # Upload Form + Filters
            'size_group': {'upload_form': True, 'filter': True}, # Upload Form + Filters
            'author': {'upload_form': True, 'filter': False},    # Upload Form Only
            'title': {'upload_form': True, 'filter': False},     # Upload Form Only
            'isbn': {'upload_form': True, 'filter': False},      # Upload Form Only
        }
        
        # Check if each field is enabled (TRUE) in the CSV
        for field_name, mapping in field_mappings.items():
            col_name = self.config.columns.get(field_name)
            if col_name:
                col_idx = self._column_indices.get(col_name)
                if col_idx is not None and col_idx < len(row):
                    value = row[col_idx].strip().upper()
                    if value == 'TRUE':
                        field_types[field_name] = FieldTypeInfo(
                            field_name=field_name,
                            is_upload_form=mapping['upload_form'],
                            is_filter=mapping['filter']
                        )
        
        return field_types

    def process_csv(self) -> List[CategoryData]:
        """Process CSV file and return structured category data"""
        csv_path = Path(self.config.csv_file_path)

        if not csv_path.exists():
            raise FileNotFoundError(f"CSV file not found: {csv_path}")

        logger.info(f"Processing CSV file: {csv_path}")

        try:
            # Get delimiter from config, fallback to comma
            delimiter = getattr(self.config, 'delimiter', ',')
            with open(csv_path, 'r', encoding=self.config.csv_encoding) as f:
                reader = csv.reader(f, delimiter=delimiter)
                csv_data = list(reader)
        except Exception as e:
            raise RuntimeError(f"Failed to read CSV file: {e}")

        if len(csv_data) < 2:
            raise ValueError("CSV file must have at least a header row and one data row")

        # Find the actual header row
        header_row_index = self._find_header_row(csv_data)
        headers = csv_data[header_row_index]
        self._validate_csv_structure(headers)

        logger.info(f"CSV structure validated. Header row: {header_row_index + 1}. Total rows: {len(csv_data)}")

        categories = []
        total_count = 0

        # Start processing from the row after the header
        for row_index, row in enumerate(csv_data[header_row_index + 1:], header_row_index + 1):
            try:
                category_data = self._process_row(row, row_index)
                if category_data:
                    categories.append(category_data)
                    total_count += 1
            except Exception as e:
                logger.warning(f"Failed to process row {row_index}: {e}")
                continue

        logger.info(f"Successfully processed {total_count} categories (including both leaf and non-leaf)")
        return categories

    def _process_row(self, row: List[str], row_index: int) -> Optional[CategoryData]:
        """Process a single CSV row"""
        # Extract the Leaf value for the data model (but don't filter by it)
        leaf_col = self.config.columns['leaf']
        leaf_idx = self._column_indices[leaf_col]

        if leaf_idx >= len(row):
            logger.warning(f"Row {row_index}: Leaf column out of bounds")
            return None

        # Extract the actual Leaf value for the data model
        leaf_value = row[leaf_idx].strip().upper() == 'TRUE'

        # Extract category ID
        category_id_col = self.config.columns['category_id']
        category_id_idx = self._column_indices[category_id_col]

        if category_id_idx >= len(row):
            logger.warning(f"Row {row_index}: Category ID column out of bounds")
            return None

        try:
            category_id = int(row[category_id_idx].strip())
        except ValueError:
            logger.warning(f"Row {row_index}: Invalid category ID '{row[category_id_idx]}'")
            return None

        # Extract category level
        level_col = self.config.columns['level']
        level_idx = self._column_indices[level_col]

        if level_idx >= len(row):
            logger.warning(f"Row {row_index}: Level column out of bounds")
            return None

        try:
            category_level = int(row[level_idx].strip())
        except ValueError:
            logger.warning(f"Row {row_index}: Invalid level '{row[level_idx]}'")
            return None

        # Extract all data
        path = self._extract_path(row)
        attributes = self._extract_attributes(row)
        field_types = self._extract_field_types(row)
        package_size = self._extract_package_size(row)
        statuses_count = self._extract_status_counts(row)

        # Map package size to shipping IDs
        shipping_sizes = self.config.package_size_mapping.get(
            package_size,
            self.config.package_size_mapping['All shippable']
        )

        return CategoryData(
            category_id=category_id,
            is_leaf_category=leaf_value,  # Add the Leaf column value
            path=path,  # Add the path value
            attributes=attributes,
            field_types=field_types,  # Add field type information
            package_size=package_size,
            shipping_sizes=shipping_sizes,
            statuses_count=statuses_count,
            category_level=category_level
        )