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
    size_group: Optional[bool]
    author: Optional[bool]
    title: Optional[bool]
    isbn: Optional[bool]

@dataclass
class FieldTypeInfo:
    """Information about field type (Upload Form + Filters, Upload Form Only, Filters Only)"""
    field_name: str
    is_upload_form: bool
    is_filter: bool

@dataclass
class CategoryData:
    category_id: str
    is_leaf_category: bool  # Add this field to match the new Kotlin model
    path: str  # Add path field for category hierarchy
    attributes: CategoryAttributes
    field_types: Dict[str, FieldTypeInfo]  # Field type information (Upload Form + Filters, etc.)
    package_size: str
    shipping_sizes: List[str]
    statuses_count: Dict[str, int]
    category_level: int

@dataclass
class Config:
    csv_file_path: str
    csv_encoding: str
    delimiter: str = ","
    columns: Dict[str, str] = None
    output_kotlin_file: str = ""
    condition_mapping: Dict[str, str] = None
    package_size_mapping: Dict[str, List[str]] = None