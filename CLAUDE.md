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
```bash
cd src
python main.py ../data/book.pdf -s START_PAGE -e END_PAGE -o ../notes/ --provider PROVIDER --verbose
```

**Working example:**
```bash
python main.py ../data/A\ Random\ Walk\ Down\ Wall\ Street\ -\ Burton\ G.\ Malkiel.pdf -s 18 -e 27 -o notes/ --provider google --verbose
```

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
- **JSON Response Cleaning**: Handles markdown code blocks from Google API
- **Comprehensive Logging**: Verbose mode with detailed debugging
- **Template System**: Customizable note templates
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
- `{{LINKS}}` - Extracted wikilinks as bullet list
- `{{CHAPTER}}` - Chapter information
- `{{TAGS}}` - Formatted tags

### Output Format
Generated notes include:
- Atomic concept titles
- Self-contained summaries with [[wikilinks]]
- Related concepts section
- Source attribution
- Topical tags

## Future Enhancements
- Batch processing for entire books
- Vector embeddings for semantic linking
- Real-time filesystem monitoring
- Knowledge graph visualization
- Iterative note refinement
- Configuration file support for batch operations