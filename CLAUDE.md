# Claude Code Project Memory

## Project Overview
This is a **Book-to-Zettelkasten AI Pipeline** - a Python system that processes PDF books, uses Large Language Models to identify key concepts, and generates interconnected atomic notes in Markdown format.

## Key Commands

### Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
cp .env.example .env
# Edit .env and add your API keys
```

### Running the Pipeline

**Basic Usage:**
```bash
python src/main.py data/book.pdf -s START_PAGE -e END_PAGE -o notes/ --provider PROVIDER --verbose
```

**Enhanced Usage with Phase 2 Features:**
```bash
# Create individual concept notes with Map of Content
python src/main.py data/book.pdf -s 18 -e 27 -o notes/ --provider google --create-moc --chapter "Chapter 3" --verbose

# Specify custom book metadata
python src/main.py data/book.pdf -s 18 -e 27 -o notes/ --create-moc --book-title "Your Book Title" --author "Author Name" --verbose
```

**Working example:**
```bash
python src/main.py data/A\ Random\ Walk\ Down\ Wall\ Street\ -\ Burton\ G.\ Malkiel.pdf -s 18 -e 27 -o notes/ --provider google --create-moc --chapter "Chapter 3" --verbose
```

### New Phase 2 CLI Arguments
- `--create-moc`: Create or update a comprehensive Map of Content for the book
- `--book-title`: Specify book title for MOC creation (default: "A Random Walk Down Wall Street")
- `--author`: Specify author for MOC creation (default: "Burton G. Malkiel")
- `--chapter`: Add chapter information to note metadata and MOC

### Testing and Linting
No specific test or lint commands configured yet. When adding them, update this section.

## Architecture

### Core Components
- **`src/pdf_extractor.py`** - PDF text extraction using PyMuPDF
- **`src/llm_service.py`** - Multi-LLM API integration (OpenAI, Anthropic, Google)
- **`src/note_generator.py`** - Markdown note creation with wikilinks
- **`src/main.py`** - CLI orchestrator and workflow management

### Key Features
- **Multi-LLM Support**: OpenAI GPT, Anthropic Claude, Google Gemini
- **Enhanced Note Structure**: YAML frontmatter with timestamps, book links, and metadata
- **Map of Content (MOC)**: Comprehensive book organization with automatic linking
- **Capital Case Filenames**: "Capital Case With Spaces.md" convention for better readability
- **Enhanced Content Extraction**: Examples, anecdotes, and elaborations from source material
- **JSON Response Cleaning**: Handles markdown code blocks from Google API
- **Comprehensive Logging**: Verbose mode with detailed debugging
- **Template System**: Customizable note templates with rich variable support
- **Error Handling**: Retry logic with exponential backoff

## API Keys Required
Set these in your `.env` file (at least one required):
- `OPENAI_API_KEY` - for OpenAI models
- `ANTHROPIC_API_KEY` - for Anthropic Claude models  
- `GOOGLE_API_KEY` - for Google Gemini models

## Common Issues and Solutions

### Google API JSON Parsing
**Issue**: Google API returns JSON wrapped in markdown code blocks (```json...```)
**Solution**: Implemented `_clean_json_response()` method in `llm_service.py`

### PDF Text Extraction
**Issue**: Page numbers are 0-indexed
**Solution**: Use `--verbose` to see extracted text length and verify correct pages

### Empty API Responses
**Issue**: Some APIs may block requests or return empty responses
**Solution**: Enhanced error handling with specific provider error messages

## Project Structure
```
book-to-zettelkasten/
├── data/                 # Input PDF files
├── notes/                # Generated markdown notes (output)
├── src/                  # Source code
│   ├── __init__.py
│   ├── pdf_extractor.py  # PDF text extraction
│   ├── llm_service.py    # LLM API integration
│   ├── note_generator.py # Markdown note creation
│   └── main.py          # CLI orchestrator
├── note_template.md     # Default note template
├── requirements.txt     # Python dependencies
├── .env.example        # Environment variables template
├── .gitignore          # Git ignore rules
├── README.md           # User documentation
└── CLAUDE.md           # This file
```

## Development Notes

### LLM Providers and Models
- **OpenAI**: `gpt-4o-mini` (default), `gpt-4o`, `gpt-3.5-turbo`
- **Anthropic**: `claude-3-5-haiku-20241022` (default), `claude-3-5-sonnet-20241022`
- **Google**: `gemini-2.0-flash` (default), `gemini-1.5-pro`

### Template Variables
Available in `note_template.md`:
- `{{TITLE}}` - Note title
- `{{SUMMARY}}` - Note content with wikilinks
- `{{EXAMPLES}}` - Examples, anecdotes, and elaborations from source material
- `{{LINKS}}` - Extracted wikilinks as bullet list
- `{{CHAPTER}}` - Chapter information
- `{{TAGS}}` - Formatted tags for YAML frontmatter
- `{{BOOK_TITLE}}` - Book title for MOC linking
- `{{CREATED}}` - Timestamp when note was created

### Output Format
Generated notes include:
- **YAML Frontmatter**: Structured metadata with timestamps, book links, and tags
- **Atomic Concept Titles**: Capital Case With Spaces.md filenames
- **Self-contained Summaries**: With [[wikilinks]] to related concepts
- **Examples and Elaboration**: Specific anecdotes and detailed explanations
- **Related Concepts Section**: Automatically extracted wikilinks
- **Source Attribution**: Book title and chapter information

### Map of Content (MOC) Features
Generated MOCs include:
- **Book Overview**: High-level summary and key themes
- **Book Structure**: Parts, chapters, and organizational hierarchy
- **Chapter Notes**: Links to all concept notes organized by chapter
- **All Generated Notes**: Comprehensive index of existing notes
- **Related Resources**: Additional books and materials
- **Navigation Links**: Integration with broader knowledge base

## Remaining Phase 2 Features
- **Book Metadata Lookup**: Automatic retrieval from external APIs (ISBN, publication details)
- **Chapter Summary System**: Generate comprehensive chapter-level summaries with cross-linking
- **Book Structure Analysis**: Enhanced hierarchical organization and thematic grouping

## Future Phase 3 Enhancements
- Batch processing for entire books
- Vector embeddings for semantic linking
- Real-time filesystem monitoring
- Knowledge graph visualization
- Iterative note refinement
- Configuration file support for batch operations