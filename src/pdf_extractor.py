"""PDF text extraction module for the book-to-zettelkasten pipeline."""

import fitz  # PyMuPDF
import re
from pathlib import Path
from typing import Optional


class PDFExtractor:
    """Handles PDF text extraction with cleanup and preprocessing."""
    
    def __init__(self, pdf_path: str):
        """Initialize with path to PDF file."""
        self.pdf_path = Path(pdf_path)
        if not self.pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
    
    def extract_text_from_chapter(self, start_page: int, end_page: int) -> str:
        """
        Extract text from a specific page range (chapter).
        
        Args:
            start_page: Starting page number (0-indexed)
            end_page: Ending page number (0-indexed, inclusive)
            
        Returns:
            Cleaned text from the specified pages
        """
        try:
            doc = fitz.open(self.pdf_path)
            
            if start_page < 0 or end_page >= len(doc):
                raise ValueError(f"Page range {start_page}-{end_page} is invalid for PDF with {len(doc)} pages")
            
            text_chunks = []
            
            for page_num in range(start_page, end_page + 1):
                page = doc.load_page(page_num)
                text = page.get_text()
                text_chunks.append(text)
            
            doc.close()
            
            # Combine all text and clean it
            full_text = "\n".join(text_chunks)
            return self._clean_text(full_text)
            
        except Exception as e:
            raise Exception(f"Error extracting text from PDF: {str(e)}")
    
    def extract_text_from_pages(self, page_numbers: list[int]) -> str:
        """
        Extract text from specific page numbers.
        
        Args:
            page_numbers: List of page numbers (0-indexed)
            
        Returns:
            Cleaned text from the specified pages
        """
        try:
            doc = fitz.open(self.pdf_path)
            
            text_chunks = []
            
            for page_num in page_numbers:
                if page_num < 0 or page_num >= len(doc):
                    continue
                page = doc.load_page(page_num)
                text = page.get_text()
                text_chunks.append(text)
            
            doc.close()
            
            full_text = "\n".join(text_chunks)
            return self._clean_text(full_text)
            
        except Exception as e:
            raise Exception(f"Error extracting text from PDF: {str(e)}")
    
    def get_page_count(self) -> int:
        """Get the total number of pages in the PDF."""
        try:
            doc = fitz.open(self.pdf_path)
            count = len(doc)
            doc.close()
            return count
        except Exception as e:
            raise Exception(f"Error reading PDF: {str(e)}")
    
    def _clean_text(self, text: str) -> str:
        """
        Clean extracted text by removing excessive whitespace and formatting issues.
        
        Args:
            text: Raw text from PDF
            
        Returns:
            Cleaned text
        """
        # Remove excessive line breaks
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
        
        # Remove excessive spaces
        text = re.sub(r' +', ' ', text)
        
        # Remove hyphenation at line breaks
        text = re.sub(r'-\s*\n\s*', '', text)
        
        # Remove page numbers and headers/footers (basic heuristic)
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            # Skip very short lines that might be page numbers or headers
            if len(line) > 3 and not line.isdigit():
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines).strip()


def extract_text_from_chapter(pdf_path: str, chapter_page_start: int, chapter_page_end: int) -> str:
    """
    Convenience function for extracting text from a chapter.
    
    Args:
        pdf_path: Path to the PDF file
        chapter_page_start: Starting page number (0-indexed)  
        chapter_page_end: Ending page number (0-indexed, inclusive)
        
    Returns:
        Cleaned text from the chapter
    """
    extractor = PDFExtractor(pdf_path)
    return extractor.extract_text_from_chapter(chapter_page_start, chapter_page_end)