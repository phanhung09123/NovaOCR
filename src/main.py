"""
Usage:
    # Launch GUI (default)
    python -m src.main
    
    # CLI mode
    python -m src.main --cli --input-folder ./scans --output-name output.docx
"""
import sys
import argparse
from pathlib import Path
from datetime import datetime

from src.core.config_manager import ConfigManager
from src.core.file_handler import FileHandler
from src.core.batch_processor import BatchProcessor
from src.providers.mistral_ocr import MistralOCRProvider
from src.providers.mistral_llm import MistralLLMProvider
from src.output.docx_generator import DOCXGenerator
from src.output.txt_generator import TXTGenerator
from src.utils.logger import Logger


def run_cli(args):
    """Run in CLI mode"""
    # Setup logger
    config = ConfigManager()
    log_level = args.log_level or config.get("logging.level", "INFO")
    log_file = config.get("logging.file_path", "logs/novaocr.log") if config.get("logging.file_enabled", True) else None
    logger = Logger.get_logger("NovaOCR", log_level, log_file)
    
    logger.info("=" * 60)
    logger.info("NovaOCR - CLI Mode")
    logger.info("=" * 60)
    
    # Get input folder
    if not args.input_folder:
        logger.error("❌ Error: --input-folder is required in CLI mode")
        sys.exit(1)
    
    input_folder = Path(args.input_folder)
    
    # Validate folder
    is_valid, message, file_count = FileHandler.validate_folder(str(input_folder))
    if not is_valid:
        logger.error(f"❌ {message}")
        sys.exit(1)
    
    logger.info(f"📁 Input folder: {input_folder}")
    logger.info(f"📄 Files found: {file_count}")
    
    if "Warning" in message:
        logger.warning(message)
    
    # Get file list
    file_paths = FileHandler.find_valid_files(str(input_folder))
    
    # Output path
    output_name = args.output_name or config.get("output.filename_template", "OUTPUT_{timestamp}.docx")
    if "{timestamp}" in output_name:
        output_name = output_name.replace("{timestamp}", datetime.now().strftime("%Y%m%d_%H%M%S"))
    
    output_path = input_folder / output_name
    
    # Check API key
    api_key = config.get("api.mistral.api_key")
    if not api_key:
        logger.error(
            "❌ Mistral API key not configured!\n"
            "   Set it in config/config.yaml or as MISTRAL_API_KEY environment variable"
        )
        sys.exit(1)
    
    # Initialize providers
    logger.info("🔧 Initializing providers...")
    
    try:
        ocr_provider = MistralOCRProvider(
            api_key=api_key,
            model=config.get("api.mistral.ocr_model", "mistral-ocr-latest")
        )
        
        llm_provider = MistralLLMProvider(
            api_key=api_key,
            model=config.get("api.mistral.llm_model", "mistral-large-latest"),
            max_retries=config.get("processing.max_retries", 3),
            backoff_base=config.get("processing.retry_backoff_base", 2)
        )
        
        # Select output generator
        output_format = config.get("output.format", "docx")
        if output_format == "docx" or output_name.endswith(".docx"):
            output_generator = DOCXGenerator()
        else:
            output_generator = TXTGenerator()
        
        # Create processor
        processor = BatchProcessor(
            ocr_provider=ocr_provider,
            llm_provider=llm_provider,
            output_generator=output_generator,
            batch_size=config.get("processing.batch_size", 7),
            system_prompt=config.get_prompt("text_cleanup", "system_prompt"),
            temperature=config.get_prompt("text_cleanup", "temperature")
        )
        
        logger.info(f"✅ Using OCR model: {ocr_provider.model}")
        logger.info(f"✅ Using LLM model: {llm_provider.model}")
        logger.info(f"✅ Output format: {output_generator.get_format_name()}")
        logger.info("")
        
        # Process files
        stats = processor.process_files(file_paths, str(output_path))
        
        logger.info("")
        logger.info("=" * 60)
        logger.info("Processing complete!")
        logger.info(f"Output saved to: {output_path}")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"❌ Fatal error: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)


def run_gui():
    """Run in GUI mode"""
    from src.gui.app import run_gui as launch_gui
    launch_gui()


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="NovaOCR - Professional OCR with AI text cleanup",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Launch GUI (default)
  python src/main.py
  
  # CLI mode
  python src/main.py --cli --input-folder ./scans
  
  # CLI with custom output
  python src/main.py --cli --input-folder ./scans --output-name mybook.docx
  
  # CLI with debug logging
  python src/main.py --cli --input-folder ./scans --log-level DEBUG
        """
    )
    
    parser.add_argument(
        '--cli',
        action='store_true',
        help='Run in CLI mode (default: GUI mode)'
    )
    
    parser.add_argument(
        '--input-folder',
        type=str,
        help='Input folder containing images/PDFs (required in CLI mode)'
    )
    
    parser.add_argument(
        '--output-name',
        type=str,
        help='Output filename (default: from config)'
    )
    
    parser.add_argument(
        '--config',
        type=str,
        help='Path to custom config file (optional)'
    )
    
    parser.add_argument(
        '--log-level',
        type=str,
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        help='Logging level (default: INFO)'
    )
    
    args = parser.parse_args()
    
    # Determine mode
    if args.cli:
        run_cli(args)
    else:
        # GUI mode
        if args.input_folder:
            print("Note: --input-folder is ignored in GUI mode")
        run_gui()


if __name__ == "__main__":
    main()
