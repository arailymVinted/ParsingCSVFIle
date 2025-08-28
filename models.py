# models.py
from dataclasses import dataclass
from typing import Dict, List, Optional, Set
from enum import Enum

class FieldType(Enum):
    BRAND = "VintedUploadItemFieldTypes.BRAND_VISIBLE"
    COLOUR = "VintedUploadItemFieldTypes.COLOR_VISIBLE"
    MATERIAL = "VintedUploadItemFieldTypes.MATERIAL_VISIBLE"
    CONDITION = "VintedUploadItemFieldTypes.CONDITION_VISIBLE"

@dataclass
class CategoryAttributes:
    brand: Optional[bool]
    colour: Optional[bool]
    material: Optional[bool]

@dataclass
class CategoryData:
    category_id: str
    attributes: CategoryAttributes
    package_size: str
    shipping_sizes: List[str]
    statuses_count: Dict[str, int]
    category_level: int

@dataclass
class Config:
    csv_file_path: str
    csv_encoding: str
    columns: Dict[str, str]
    output_kotlin_file: str
    condition_mapping: Dict[str, str]
    package_size_mapping: Dict[str, List[str]]