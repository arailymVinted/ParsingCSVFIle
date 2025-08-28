# kotlin_generator.py
import logging
from pathlib import Path
from typing import List, Dict
from models import CategoryData, Config

logger = logging.getLogger(__name__)


class KotlinGenerator:
    def __init__(self, config: Config):
        self.config = config

    def _generate_field_types(self, attributes) -> List[str]:
        """Generate field types based on category attributes"""
        field_types = []

        if attributes.brand:
            field_types.append('VintedUploadItemFieldTypes.BRAND_VISIBLE')
        if attributes.colour:
            field_types.append('VintedUploadItemFieldTypes.COLOR_VISIBLE')
        if attributes.material:
            field_types.append('VintedUploadItemFieldTypes.MATERIAL_VISIBLE')

        # Condition is always visible
        field_types.append('VintedUploadItemFieldTypes.CONDITION_VISIBLE')

        return field_types

    def _generate_condition_ids(self, statuses_count: Dict[str, int]) -> List[str]:
        """Generate condition IDs based on available statuses"""
        condition_ids = []

        for status, count in statuses_count.items():
            if count > 0 and status in self.config.condition_mapping:
                condition_ids.append(self.config.condition_mapping[status])

        return sorted(condition_ids)

    def generate_kotlin_models(self, categories: List[CategoryData]) -> str:
        """Generate Kotlin CategoryLaunchDataProviderModel entries"""
        lines = [
            "// Generated CategoryLaunchDataProviderModel entries",
            "// Based on Office supplies data (LEAF categories only)",
            f"// Total leaf categories: {len(categories)}",
            "",
            "// Category Level enum",
            "enum class CategoryLevel(val id: Long) {",
            "    ROOT_CATEGORY(1L),",
            "    L2(2L),",
            "    L3(3L),",
            "    L4(4L),",
            "    L5(5L),",
            "    L6(6L),",
            "    L7(7L)",
            "}",
            "",
            "// Condition mapping:",
            *[f"// {k} = {v}" for k, v in self.config.condition_mapping.items()],
            "",
            "// Package size mapping:",
            *[f"// {k} = setOf({', '.join(v)})" for k, v in self.config.package_size_mapping.items()],
            ""
        ]

        for category in categories:
            field_types = self._generate_field_types(category.attributes)
            condition_ids = self._generate_condition_ids(category.statuses_count)

            # Format strings
            field_types_str = "listOf(" + ", ".join(field_types) + ")"
            condition_ids_str = "setOf(" + ", ".join(condition_ids) + ")"
            shipping_sizes_str = "setOf(" + ", ".join(category.shipping_sizes) + ")"

            # Map category level to enum
            level_enum = self._get_level_enum(category.category_level)

            entry = f"""CategoryLaunchDataProviderModel(
    categoryId = {category.category_id}L,
    categoryLevel = {level_enum}.id,
    expectedFieldsVisibility = {field_types_str},
    expectedConditionTypeIds = {condition_ids_str},
    expectedPackageSizeIds = {shipping_sizes_str},
    expectedSizeGroupsIds = listOf(),
    brandId = supplyTestsHelper.getDefaultBrandId({category.category_id}L)
),"""

            lines.append(entry)
            lines.append("")

        return '\n'.join(lines)

    def _get_level_enum(self, level: int) -> str:
        """Convert numeric level to CategoryLevel enum reference"""
        level_mapping = {
            1: "CategoryLevel.ROOT_CATEGORY",
            2: "CategoryLevel.L2",
            3: "CategoryLevel.L3",
            4: "CategoryLevel.L4",
            5: "CategoryLevel.L5",
            6: "CategoryLevel.L6",
            7: "CategoryLevel.L7"
        }
        
        return level_mapping.get(level, f"CategoryLevel.L{level}")

    def save_kotlin_file(self, categories: List[CategoryData], output_path: str) -> None:
        """Generate and save Kotlin file"""
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        kotlin_content = self.generate_kotlin_models(categories)

        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(kotlin_content)
            logger.info(f"Kotlin file saved: {output_file}")
        except Exception as e:
            raise RuntimeError(f"Failed to save Kotlin file: {e}")