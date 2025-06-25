"""Main orchestrator for the book-to-zettelkasten pipeline."""

import argparse
import sys
from pathlib import Path
from typing import Optional

from pdf_extractor import PDFExtractor
from llm_service import LLMService
from note_generator import NoteGenerator


def main():
    """Main execution function with CLI interface."""
    parser = argparse.ArgumentParser(
        description="Convert book chapters to atomic Zettelkasten notes using AI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process pages 10-25 of a PDF
  python main.py book.pdf --start-page 10 --end-page 25 --output notes/

  # Process with specific LLM provider
  python main.py book.pdf -s 10 -e 25 -o notes/ --provider anthropic

  # Process with custom template
  python main.py book.pdf -s 10 -e 25 -o notes/ --template my_template.md
        """
    )
    
    # Required arguments
    parser.add_argument("pdf_path", help="Path to the PDF file")
    
    # Page range arguments
    parser.add_argument("-s", "--start-page", type=int, required=True,
                       help="Starting page number (0-indexed)")
    parser.add_argument("-e", "--end-page", type=int, required=True,
                       help="Ending page number (0-indexed, inclusive)")
    
    # Output arguments
    parser.add_argument("-o", "--output", default="notes",
                       help="Output directory for generated notes (default: notes)")
    
    # LLM arguments
    parser.add_argument("--provider", choices=["openai", "anthropic", "google"],
                       default="openai", help="LLM provider to use (default: openai)")
    parser.add_argument("--model", help="Specific model to use (optional)")
    
    # Template arguments
    parser.add_argument("--template", help="Path to note template file (optional)")
    
    # Chapter information
    parser.add_argument("--chapter", help="Chapter name/number for metadata")
    
    # Processing options
    parser.add_argument("--create-index", action="store_true",
                       help="Create an index note linking all generated notes")
    parser.add_argument("--create-moc", action="store_true",
                       help="Create or update a Map of Content (MOC) for the book")
    parser.add_argument("--book-title", default="A Random Walk Down Wall Street",
                       help="Title of the book for MOC creation")
    parser.add_argument("--author", default="Burton G. Malkiel",
                       help="Author of the book for MOC creation")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Enable verbose output")
    
    args = parser.parse_args()
    
    try:
        process_chapter(
            pdf_path=args.pdf_path,
            start_page=args.start_page,
            end_page=args.end_page,
            output_dir=args.output,
            provider=args.provider,
            model=args.model,
            template_path=args.template,
            chapter_info=args.chapter,
            create_index=args.create_index,
            create_moc=args.create_moc,
            book_title=args.book_title,
            author=args.author,
            verbose=args.verbose
        )
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def process_chapter(
    pdf_path: str,
    start_page: int,
    end_page: int,
    output_dir: str = "notes",
    provider: str = "openai",
    model: Optional[str] = None,
    template_path: Optional[str] = None,
    chapter_info: Optional[str] = None,
    create_index: bool = False,
    create_moc: bool = False,
    book_title: str = "A Random Walk Down Wall Street",
    author: str = "Burton G. Malkiel",
    verbose: bool = False
) -> dict:
    """
    Process a chapter of a book and generate atomic notes.
    
    Args:
        pdf_path: Path to PDF file
        start_page: Starting page (0-indexed)
        end_page: Ending page (0-indexed, inclusive)
        output_dir: Output directory for notes
        provider: LLM provider to use
        model: Specific model to use
        template_path: Path to note template
        chapter_info: Chapter information for metadata
        create_index: Whether to create index note
        create_moc: Whether to create/update Map of Content
        book_title: Title of the book for MOC
        author: Author of the book for MOC
        verbose: Enable verbose output
        
    Returns:
        Dictionary with processing results
    """
    
    def log(message: str):
        if verbose:
            print(f"[INFO] {message}")
    
    # Step 1: Extract text from PDF
    log(f"Extracting text from {pdf_path}, pages {start_page}-{end_page}")
    
    try:
        extractor = PDFExtractor(pdf_path)
        text = extractor.extract_text_from_chapter(start_page, end_page)
        
        if not text.strip():
            raise ValueError("No text extracted from specified pages")
        
        log(f"Extracted {len(text)} characters of text")
        
    except Exception as e:
        raise Exception(f"PDF extraction failed: {e}")
    
    # Step 2: Analyze text with LLM
    log(f"Sending text to {provider} for analysis...")
    
    try:
        llm_service = LLMService(provider=provider, model=model)
        log(f"Using {provider} with model: {llm_service.model}")
        
        notes_data = llm_service.get_atomic_notes_from_text(text, verbose=verbose)
        
        if not notes_data:
            raise ValueError("No notes generated by LLM")
        
        log(f"LLM generated {len(notes_data)} atomic notes")
        
    except Exception as e:
        print(f"[ERROR] LLM analysis failed: {e}")
        if verbose:
            import traceback
            print(f"[DEBUG] Full traceback:")
            traceback.print_exc()
        raise Exception(f"LLM analysis failed: {e}")
    
    # Step 3: Generate note files
    log(f"Creating markdown notes in {output_dir}/")
    
    try:
        generator = NoteGenerator(output_dir, template_path)
        created_files = generator.create_notes_from_data(notes_data, chapter_info)
        
        log(f"Created {len(created_files)} note files")
        
        # Optionally create index note
        index_path = None
        if create_index:
            index_path = generator.create_index_note(notes_data, chapter_info)
            if index_path:
                log(f"Created index note: {index_path.name}")
        
        # Optionally create/update Map of Content
        moc_path = None
        if create_moc:
            moc_path = generator.create_book_moc(book_title, author, notes_data, chapter_info)
            if moc_path:
                log(f"Created/updated Map of Content: {moc_path.name}")
        
    except Exception as e:
        raise Exception(f"Note generation failed: {e}")
    
    # Summary
    result = {
        "pdf_path": pdf_path,
        "pages_processed": f"{start_page}-{end_page}",
        "text_length": len(text),
        "notes_generated": len(notes_data),
        "files_created": created_files,
        "output_directory": output_dir,
        "index_created": str(index_path) if index_path else None,
        "moc_created": str(moc_path) if moc_path else None
    }
    
    print(f"\n✅ Success! Generated {len(notes_data)} atomic notes from pages {start_page}-{end_page}")
    print(f"📁 Notes saved to: {Path(output_dir).absolute()}")
    
    if verbose:
        print(f"\n📊 Processing Summary:")
        print(f"  • PDF: {pdf_path}")
        print(f"  • Pages: {start_page}-{end_page}")
        print(f"  • Text extracted: {len(text):,} characters")
        print(f"  • LLM provider: {provider} ({llm_service.model})")
        print(f"  • Notes generated: {len(notes_data)}")
        print(f"  • Files created: {len(created_files)}")
        
        if notes_data:
            print(f"\n📝 Generated Notes:")
            for i, note in enumerate(notes_data, 1):
                print(f"  {i:2d}. {note['title']}")
    
    return result


def batch_process_book(config_file: str):
    """
    Process entire book using a configuration file.
    
    Args:
        config_file: Path to JSON config file with chapter mappings
    """
    # TODO: Implement batch processing feature
    # Config file should contain: {"chapters": [{"name": "Chapter 1", "start": 10, "end": 25}, ...]}
    raise NotImplementedError("Batch processing feature not yet implemented")


if __name__ == "__main__":
    main()