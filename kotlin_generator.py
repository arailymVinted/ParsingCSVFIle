# kotlin_generator.py
import logging
from pathlib import Path
from typing import List, Dict
from models import CategoryData, Config

logger = logging.getLogger(__name__)


class KotlinGenerator:
    def __init__(self, config: Config):
        self.config = config

    def _generate_field_types(self, field_types: Dict[str, 'FieldTypeInfo']) -> List[str]:
        """Generate field types based on field type information"""
        upload_form_fields = []

        # Only include fields that are enabled for upload form
        for field_name, field_info in field_types.items():
            if field_info.is_upload_form:
                if field_name == 'brand':
                    upload_form_fields.append('VintedUploadItemFieldTypes.BRAND_VISIBLE')
                elif field_name == 'colour':
                    upload_form_fields.append('VintedUploadItemFieldTypes.COLOR_VISIBLE')
                elif field_name == 'material':
                    upload_form_fields.append('VintedUploadItemFieldTypes.MATERIAL_VISIBLE')
                elif field_name == 'pattern':
                    upload_form_fields.append('VintedUploadItemFieldTypes.PATTERN_VISIBLE')
                elif field_name == 'size':
                    upload_form_fields.append('VintedUploadItemFieldTypes.SIZE_VISIBLE')
                elif field_name == 'size_group':
                    upload_form_fields.append('VintedUploadItemFieldTypes.SIZE_VISIBLE')
                elif field_name == 'author':
                    upload_form_fields.append('VintedUploadItemFieldTypes.AUTHOR_VISIBLE')
                elif field_name == 'isbn':
                    upload_form_fields.append('VintedUploadItemFieldTypes.ISBN_VISIBLE')
                elif field_name == 'video_game_rating':
                    upload_form_fields.append('VintedUploadItemFieldTypes.VIDEO_GAME_RATING_VISIBLE')
                elif field_name == 'video_game_platform':
                    upload_form_fields.append('VintedUploadItemFieldTypes.VIDEO_GAME_PLATFORM_VISIBLE')
                elif field_name == 'internal_memory_capacity':
                    upload_form_fields.append('VintedUploadItemFieldTypes.STORAGE_VISIBLE')
                elif field_name == 'sim_lock':
                    upload_form_fields.append('VintedUploadItemFieldTypes.SIM_LOCK_VISIBLE')

        # Always include condition field as it's always present
        upload_form_fields.append('VintedUploadItemFieldTypes.CONDITION_VISIBLE')

        return upload_form_fields

    def _generate_filter_types(self, field_types: Dict[str, 'FieldTypeInfo']) -> List[str]:
        """Generate filter types based on field type information"""
        filter_fields = []

        # Only include fields that are enabled for filters
        for field_name, field_info in field_types.items():
            if field_info.is_filter:
                if field_name == 'brand':
                    filter_fields.append('VintedFilterType.BRAND')
                elif field_name == 'colour':
                    filter_fields.append('VintedFilterType.COLOR')
                elif field_name == 'material':
                    filter_fields.append('VintedFilterType.MATERIAL')
                elif field_name == 'pattern':
                    filter_fields.append('VintedFilterType.PATTERNS')
                elif field_name == 'size':
                    filter_fields.append('VintedFilterType.SIZE')
                # Note: size_group does NOT add SIZE filter - only the 'size' field does
                elif field_name == 'language_book':
                    filter_fields.append('VintedFilterType.LANGUAGE')
                elif field_name == 'video_game_rating':
                    filter_fields.append('VintedFilterType.VIDEO_GAME_RATING')
                elif field_name == 'video_game_platform':
                    filter_fields.append('VintedFilterType.VIDEO_GAME_PLATFORM')
                elif field_name == 'internal_memory_capacity':
                    filter_fields.append('VintedFilterType.INTERNAL_MEMORY_CAPACITY')
                elif field_name == 'sim_lock':
                    filter_fields.append('VintedFilterType.SIM_LOCK')

        # Always include condition filter since condition is always visible in upload form
        filter_fields.append('VintedFilterType.STATUS')
        
        # Always include price filter by default
        filter_fields.append('VintedFilterType.PRICE')

        return filter_fields

    def _generate_condition_ids(self, statuses_count: Dict[str, int]) -> List[str]:
        """Generate condition IDs based on available statuses"""
        condition_ids = []

        for status, count in statuses_count.items():
            if count > 0 and status in self.config.condition_mapping:
                condition_ids.append(self.config.condition_mapping[status])

        # If no specific conditions found, use default conditions
        if not condition_ids:
            condition_ids = [
                'VintedConditionTypes.NEW_WITH_TAGS.id',
                'VintedConditionTypes.NEW_WITHOUT_TAGS.id',
                'VintedConditionTypes.VERY_GOOD.id',
                'VintedConditionTypes.GOOD.id',
                'VintedConditionTypes.SATISFACTORY.id'
            ]

        return sorted(condition_ids)

    def generate_kotlin_models(self, categories: List[CategoryData]) -> str:
        """Generate Kotlin CategoryLaunchDataProviderModel entries"""
        lines = []
        
        # Add header
        header = """package categoryLaunches.dataProviders

import api.data.models.categoryLaunch.VintedConditionTypes
import api.data.models.categoryLaunch.VintedPackageTypes
import api.data.models.categoryLaunch.VintedUploadItemFieldTypes
import commonUtil.data.enums.VintedFilterType
import helper.supply.SupplyTestsHelper
import org.testng.annotations.DataProvider

class CategoryLaunchDataProvider {
    private val supplyTestsHelper: SupplyTestsHelper get() = SupplyTestsHelper()
    @DataProvider(name = "leafCategoryDataForCategoryLaunches", parallel = true)
    fun getDataForLeafCategoriesOnly(): Array<CategoryLaunchDataProviderModel> {
        return getDataForEachCategory().filter { it.isLeafCategory }.toTypedArray()
    }

    @DataProvider(name = "dataForCategoryLaunches", parallel = true)
    fun getDataForEachCategory(): Array<CategoryLaunchDataProviderModel> {
        return arrayOf("""
        lines.append(header)

        for category in categories:
            upload_form_fields = self._generate_field_types(category.field_types)
            filter_fields = self._generate_filter_types(category.field_types)
            condition_ids = self._generate_condition_ids(category.statuses_count)

            # Format strings
            upload_form_fields_str = "listOf(" + ", ".join(upload_form_fields) + ")"
            filter_fields_str = "listOf(" + ", ".join(filter_fields) + ")" if filter_fields else "emptyList()"
            condition_ids_str = "setOf(" + ", ".join(condition_ids) + ")"
            shipping_sizes_str = "setOf(" + ", ".join(category.shipping_sizes) + ")"

            entry = f"""CategoryLaunchDataProviderModel(
    categoryId = {category.category_id}L,
    isLeafCategory = {str(category.is_leaf_category).lower()},
    categoryLevel = {category.category_level}L,
    categoryPath = "{category.path}",
    expectedFieldsVisibility = {upload_form_fields_str},
    expectedFiltersVisibility = {filter_fields_str},
    expectedConditionTypeIds = {condition_ids_str},
    expectedPackageSizeIds = {shipping_sizes_str},
    expectedSizeGroupsIds = null,
    brandId = supplyTestsHelper.getDefaultBrandId({category.category_id}L)
),"""

            lines.append(entry)
            lines.append("")

        # Remove the last blank line before adding footer
        if lines and lines[-1] == "":
            lines.pop()
        
        # Add footer
        footer = """        )
    }
}"""
        lines.append(footer)

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