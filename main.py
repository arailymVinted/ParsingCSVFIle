# main.py
import logging
import sys
from pathlib import Path
from typing import List

from config_loader import ConfigLoader
from csv_processor import CSVProcessor
from kotlin_generator import KotlinGenerator
from models import CategoryData, Config


def setup_logging() -> None:
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('category_processor.log')
        ]
    )


def main():
    """Main application entry point"""
    setup_logging()
    logger = logging.getLogger(__name__)

    try:
        # Load configuration
        logger.info("Loading configuration...")
        config = ConfigLoader.load_config()

        # Process CSV
        logger.info("Processing CSV file...")
        csv_processor = CSVProcessor(config)
        categories = csv_processor.process_csv()

        if not categories:
            logger.warning("No categories found to process")
            return

        # Generate and save Kotlin code
        logger.info("Generating Kotlin code...")
        kotlin_generator = KotlinGenerator(config)
        kotlin_generator.save_kotlin_file(categories, config.output_kotlin_file)

        logger.info(f"Successfully processed {len(categories)} categories")
        logger.info(f"Output files:")
        logger.info(f"  - Kotlin: {config.output_kotlin_file}")

    except Exception as e:
        logger.error(f"Application failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()