"""Batch Processor - Orchestrates OCR + LLM + Output pipeline"""
import time
from pathlib import Path
from typing import List, Callable, Optional
from datetime import datetime

from ..interfaces.ocr_provider import OCRProvider
from ..interfaces.llm_provider import LLMProvider
from ..interfaces.output_generator import OutputGenerator
from ..utils.logger import get_logger


class ProcessingStats:
    """Statistics for batch processing"""
    
    def __init__(self):
        self.total_files = 0
        self.successful_files = 0
        self.empty_files = 0
        self.failed_files = 0
        self.start_time = None
        self.end_time = None
    
    def get_elapsed_time(self) -> float:
        """Get elapsed time in seconds"""
        if self.start_time is None:
            return 0.0
        end = self.end_time or time.time()
        return end - self.start_time
    
    def get_summary(self) -> str:
        """Get summary string"""
        elapsed = self.get_elapsed_time()
        return (
            f"📊 PROCESSING RESULTS:\n"
            f"   ✅ Successful: {self.successful_files} pages\n"
            f"   📭 Empty: {self.empty_files} pages\n"
            f"   ❌ Failed: {self.failed_files} pages\n"
            f"   ⏱️  Time: {elapsed:.1f}s ({elapsed/60:.1f} min)"
        )


class BatchProcessor:
    """
    Orchestrates the OCR -> LLM -> Output pipeline.
    
    Processes files in batches for optimal AI performance.
    """
    
    def __init__(
        self,
        ocr_provider: OCRProvider,
        llm_provider: LLMProvider,
        output_generator: OutputGenerator,
        batch_size: int = 7,
        system_prompt: str = "",
        temperature: float = 0.0
    ):
        """
        Initialize batch processor.
        
        Args:
            ocr_provider: OCR provider instance
            llm_provider: LLM provider instance
            output_generator: Output generator instance
            batch_size: Number of pages to process before AI cleanup
            system_prompt: System prompt for LLM
            temperature: LLM temperature
        """
        self.ocr_provider = ocr_provider
        self.llm_provider = llm_provider
        self.output_generator = output_generator
        self.batch_size = batch_size
        self.system_prompt = system_prompt
        self.temperature = temperature
        self.logger = get_logger()
        
        self.stats = ProcessingStats()
        self._should_stop = False
        self._is_paused = False
    
    def process_files(
        self,
        file_paths: List[str],
        output_path: str,
        progress_callback: Optional[Callable[[int, int, str], None]] = None
    ) -> ProcessingStats:
        """
        Process multiple files through OCR -> LLM -> Output pipeline.
        
        Args:
            file_paths: List of file paths to process
            output_path: Output file path
            progress_callback: Optional callback(current, total, status_message)
            
        Returns:
            Processing statistics
        """
        self.stats = ProcessingStats()
        self.stats.total_files = len(file_paths)
        self.stats.start_time = time.time()
        self._should_stop = False
        
        self.logger.info(f"🤖 Starting batch processing with AI cleanup")
        self.logger.info(f"📦 Batch size: {self.batch_size} pages per cleanup")
        self.logger.info(f"📁 Total files: {len(file_paths)}")
        
        full_content = ""
        batch_buffer = []
        batch_filenames = []
        
        for index, file_path in enumerate(file_paths):
            # Check if should stop
            if self._should_stop:
                self.logger.warning("Processing stopped by user")
                break
            
            # Handle pause
            while self._is_paused:
                time.sleep(0.1)
                if self._should_stop:
                    break
            
            filename = Path(file_path).name
            self.logger.info(f"🔄 [{index+1}/{len(file_paths)}] OCR: {filename}")
            
            if progress_callback:
                progress_callback(index + 1, len(file_paths), f"Processing: {filename}")
            
            # Step 1: OCR the page
            try:
                raw_text = self.ocr_provider.extract_text(file_path)
                
                if raw_text:
                    batch_buffer.append(raw_text)
                    batch_filenames.append(filename)
                else:
                    self.logger.info(f"  ℹ️  Empty page, skipping")
                    self.stats.empty_files += 1
                    
            except Exception as e:
                self.logger.error(f"  ❌ OCR failed: {str(e)}")
                self.stats.failed_files += 1
                continue
            
            # Step 2: Check if batch is ready for cleanup
            is_last_file = (index == len(file_paths) - 1)
            should_cleanup = len(batch_buffer) >= self.batch_size or (is_last_file and batch_buffer)
            
            if should_cleanup:
                self.logger.info(
                    f"\n🧹 Cleaning batch ({len(batch_buffer)} pages: "
                    f"{', '.join(batch_filenames)})"
                )
                
                if progress_callback:
                    progress_callback(
                        index + 1, len(file_paths),
                        f"AI cleaning batch ({len(batch_buffer)} pages)..."
                    )
                
                # Combine batch
                combined_raw = "\n\n---PAGE BREAK---\n\n".join(batch_buffer)
                
                # Clean with AI
                try:
                    cleaned_batch = self.llm_provider.clean_text(
                        combined_raw,
                        self.system_prompt,
                        self.temperature
                    )
                    
                    if cleaned_batch:
                        full_content += cleaned_batch + "\n\n"
                        self.stats.successful_files += len(batch_buffer)
                        self.logger.info("  ✅ Batch cleaned successfully\n")
                    
                except Exception as e:
                    self.logger.error(f"  ❌ LLM cleanup failed: {str(e)}")
                    # Use raw text as fallback
                    full_content += combined_raw + "\n\n"
                    self.stats.failed_files += len(batch_buffer)
                
                # Reset batch
                batch_buffer = []
                batch_filenames = []
        
        self.stats.end_time = time.time()
        
        # Step 3: Generate output
        if full_content.strip() and not self._should_stop:
            self.logger.info(f"\n💾 Generating output: {Path(output_path).name}")
            
            if progress_callback:
                progress_callback(len(file_paths), len(file_paths), "Generating output file...")
            
            try:
                self.output_generator.generate(full_content, output_path)
            except Exception as e:
                self.logger.error(f"❌ Output generation failed: {str(e)}")
        
        # Log summary
        self.logger.info(f"\n{self.stats.get_summary()}")
        
        return self.stats
    
    def stop(self):
        """Stop processing"""
        self._should_stop = True
        self._is_paused = False
    
    def pause(self):
        """Pause processing"""
        self._is_paused = True
    
    def resume(self):
        """Resume processing"""
        self._is_paused = False
