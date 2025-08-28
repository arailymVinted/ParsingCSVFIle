# csv_processor.py
import csv
import logging
from pathlib import Path
from typing import List, Dict, Optional
from models import CategoryData, CategoryAttributes, Config

logger = logging.getLogger(__name__)


class CSVProcessor:
    def __init__(self, config: Config):
        self.config = config
        self._column_indices: Dict[str, int] = {}

    def _validate_csv_structure(self, headers: List[str]) -> None:
        """Validate that required columns exist in CSV"""
        required_columns = [
            self.config.columns['leaf'],
            self.config.columns['category_id'],
            self.config.columns['brand'],
            self.config.columns['colour'],
            self.config.columns['level']
        ]

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

    def _extract_attributes(self, row: List[str]) -> CategoryAttributes:
        """Extract category attributes from CSV row"""
        brand_col = self.config.columns['brand']
        colour_col = self.config.columns['colour']

        brand_idx = self._column_indices.get(brand_col)
        colour_idx = self._column_indices.get(colour_col)

        if brand_idx is None or colour_idx is None:
            raise ValueError("Required attribute columns not found")

        brand_value = row[brand_idx].strip() if brand_idx < len(row) else ""
        colour_value = row[colour_idx].strip() if colour_idx < len(row) else ""

        return CategoryAttributes(
            brand=True if brand_value == 'x' else None if brand_value == '' else brand_value,
            colour=True if colour_value == 'x' else None if colour_value == '' else colour_value,
            material=None  # Not present in current CSV
        )

    def _extract_package_size(self, row: List[str]) -> str:
        """Extract package size from CSV row"""
        package_size_col = self.config.columns.get('package_size')
        if not package_size_col:
            return "All shippable"

        package_size_idx = self._column_indices.get(package_size_col)
        if package_size_idx is None or package_size_idx >= len(row):
            return "All shippable"

        package_size_value = row[package_size_idx].strip()
        return package_size_value if package_size_value else "All shippable"

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

    def process_csv(self) -> List[CategoryData]:
        """Process CSV file and return structured category data"""
        csv_path = Path(self.config.csv_file_path)

        if not csv_path.exists():
            raise FileNotFoundError(f"CSV file not found: {csv_path}")

        logger.info(f"Processing CSV file: {csv_path}")

        try:
            with open(csv_path, 'r', encoding=self.config.csv_encoding) as f:
                reader = csv.reader(f, delimiter=';')
                csv_data = list(reader)
        except Exception as e:
            raise RuntimeError(f"Failed to read CSV file: {e}")

        if len(csv_data) < 2:
            raise ValueError("CSV file must have at least a header row and one data row")

        headers = csv_data[0]
        self._validate_csv_structure(headers)

        logger.info(f"CSV structure validated. Total rows: {len(csv_data)}")

        categories = []
        leaf_count = 0

        for row_index, row in enumerate(csv_data[1:], 1):
            try:
                category_data = self._process_row(row, row_index)
                if category_data:
                    categories.append(category_data)
                    leaf_count += 1
            except Exception as e:
                logger.warning(f"Failed to process row {row_index}: {e}")
                continue

        logger.info(f"Successfully processed {leaf_count} leaf categories")
        return categories

    def _process_row(self, row: List[str], row_index: int) -> Optional[CategoryData]:
        """Process a single CSV row"""
        # Check if this is a leaf category
        leaf_col = self.config.columns['leaf']
        leaf_idx = self._column_indices[leaf_col]

        if leaf_idx >= len(row) or row[leaf_idx].strip().upper() != 'TRUE':
            return None

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
        attributes = self._extract_attributes(row)
        package_size = self._extract_package_size(row)
        statuses_count = self._extract_status_counts(row)

        # Map package size to shipping IDs
        shipping_sizes = self.config.package_size_mapping.get(
            package_size,
            self.config.package_size_mapping['All shippable']
        )

        return CategoryData(
            category_id=category_id,
            attributes=attributes,
            package_size=package_size,
            shipping_sizes=shipping_sizes,
            statuses_count=statuses_count,
            category_level=category_level
        )