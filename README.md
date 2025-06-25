# Book-to-Zettelkasten AI Pipeline

A Python-based system that processes PDF books, uses Large Language Models to identify key concepts, and generates a network of interlinked atomic notes in Markdown format.

## Features

- **PDF Text Extraction**: Extract clean text from specific chapters or page ranges
- **AI-Powered Analysis**: Use OpenAI, Anthropic, or Google AI to identify atomic concepts
- **Zettelkasten Generation**: Create interlinked Markdown notes with wikilinks
- **Multiple LLM Providers**: Support for OpenAI GPT, Anthropic Claude, and Google Gemini
- **Customizable Templates**: Use your own note templates
- **CLI Interface**: Easy command-line operation

## Installation

1. Clone or download this repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env and add your API keys
   ```

## Usage

### Basic Usage

Process a chapter from a PDF book:

```bash
python src/main.py data/your-book.pdf --start-page 10 --end-page 25 --output notes/
```

### Advanced Usage

```bash
# Use Anthropic Claude instead of OpenAI
python src/main.py data/book.pdf -s 10 -e 25 -o notes/ --provider anthropic

# Use custom template and create index
python src/main.py data/book.pdf -s 10 -e 25 -o notes/ --template note_template.md --create-index

# Add chapter information and verbose output
python src/main.py data/book.pdf -s 10 -e 25 -o notes/ --chapter "Chapter 3" --verbose
```

### API Keys

You need at least one of these API keys in your `.env` file:

- `OPENAI_API_KEY` - for OpenAI GPT models
- `ANTHROPIC_API_KEY` - for Anthropic Claude models  
- `GOOGLE_API_KEY` - for Google Gemini models

## Project Structure

```
book-to-zettelkasten/
├── data/                 # Input PDF files
├── notes/                # Generated markdown notes
├── src/                  # Source code
│   ├── pdf_extractor.py  # PDF text extraction
│   ├── llm_service.py    # LLM API integration
│   ├── note_generator.py # Markdown note creation
│   └── main.py          # CLI orchestrator
├── note_template.md     # Default note template
├── requirements.txt     # Python dependencies
└── .env.example        # Environment variables template
```

## How It Works

1. **Extract**: Read text from specified pages of a PDF book
2. **Analyze**: Send text to an LLM to identify atomic concepts and relationships
3. **Generate**: Create individual Markdown files with wikilinks between concepts

## Example Output

The system generates atomic notes like this:

```markdown
# Efficient Market Hypothesis

## Summary
The Efficient Market Hypothesis (EMH) asserts that financial markets are 'informationally efficient,' meaning prices fully reflect all available information. This theory is built upon the [[Random Walk Theory]] and challenges traditional [[Technical Analysis]] approaches.

---
## Related Concepts
- [[Random Walk Theory]]
- [[Technical Analysis]]
- [[Market Efficiency]]

---
**Source:** "A Random Walk Down Wall Street", Chapter 3
**Tags:** #finance #investing #market-theory #investment-theory
```

## Customization

### Custom Templates

Create your own note template by copying `note_template.md` and modifying it. Use these placeholders:

- `{{TITLE}}` - Note title
- `{{SUMMARY}}` - Note content with wikilinks
- `{{LINKS}}` - Extracted wikilinks as bullet list
- `{{CHAPTER}}` - Chapter information
- `{{TAGS}}` - Formatted tags

### LLM Providers

The system supports multiple LLM providers:

- **OpenAI**: `gpt-4o-mini` (default), `gpt-4o`, `gpt-3.5-turbo`
- **Anthropic**: `claude-3-5-haiku-20241022` (default), `claude-3-5-sonnet-20241022`
- **Google**: `gemini-1.5-flash` (default), `gemini-1.5-pro`

## Troubleshooting

### Common Issues

1. **No text extracted**: Check page numbers are correct (0-indexed)
2. **API errors**: Verify API keys are set correctly in `.env`
3. **Import errors**: Ensure all dependencies are installed with `pip install -r requirements.txt`

### Getting Help

Run with `--help` to see all available options:

```bash
python src/main.py --help
```

## Future Enhancements

- Batch processing for entire books
- Vector embeddings for semantic linking
- Real-time filesystem monitoring
- Knowledge graph visualization
- Iterative note refinement