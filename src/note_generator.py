"""Note generation module for creating Markdown files from atomic notes."""

import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class NoteGenerator:
    """Generates Markdown notes from structured atomic note data."""
    
    def __init__(self, output_dir: str, template_path: Optional[str] = None):
        """
        Initialize note generator.
        
        Args:
            output_dir: Directory to save generated notes
            template_path: Path to note template file (optional)
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.template_path = Path(template_path) if template_path else None
        self.template = self._load_template()
    
    def _load_template(self) -> str:
        """Load note template from file or use default."""
        if self.template_path and self.template_path.exists():
            return self.template_path.read_text(encoding='utf-8')
        else:
            # Default template
            return """---
created: {{CREATED}}
in: "[[{{BOOK_TITLE}}]]"
chapter: {{CHAPTER}}
tags: [{{TAGS}}]
---

# {{TITLE}}

## Summary
{{SUMMARY}}

## Examples and Elaboration
{{EXAMPLES}}

## Related Concepts
{{LINKS}}

**Source:** {{BOOK_TITLE}}, {{CHAPTER}}
"""
    
    def create_notes_from_data(self, notes_data: List[Dict], chapter_info: Optional[str] = None) -> List[str]:
        """
        Create Markdown notes from atomic note data.
        
        Args:
            notes_data: List of note dictionaries from LLM
            chapter_info: Chapter information to include in notes
            
        Returns:
            List of created file paths
        """
        created_files = []
        
        for note_data in notes_data:
            try:
                file_path = self._create_single_note(note_data, chapter_info)
                created_files.append(str(file_path))
            except Exception as e:
                print(f"Error creating note '{note_data.get('title', 'Unknown')}': {e}")
                continue
        
        return created_files
    
    def _create_single_note(self, note_data: Dict, chapter_info: Optional[str] = None, book_title: str = "A Random Walk Down Wall Street") -> Path:
        """Create a single Markdown note file."""
        title = note_data["title"]
        summary = note_data["summary"]
        tags = note_data.get("tags", [])
        examples = note_data.get("examples", "*No specific examples provided in the source material.*")
        
        # Create Capital Case filename
        filename = self.capital_case_filename(title)
        file_path = self.output_dir / f"{filename}.md"
        
        # Check if file already exists
        if file_path.exists():
            print(f"Note already exists: {filename}.md (skipping)")
            return file_path
        
        # Extract wikilinks from summary
        links = self._extract_wikilinks(summary)
        
        # Create timestamp
        created_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Populate template
        content = self.template.replace("{{TITLE}}", title)
        content = content.replace("{{SUMMARY}}", summary)
        content = content.replace("{{EXAMPLES}}", examples)
        content = content.replace("{{LINKS}}", self._format_links(links))
        content = content.replace("{{CHAPTER}}", chapter_info or "Unknown")
        content = content.replace("{{TAGS}}", self._format_tags_yaml(tags))
        content = content.replace("{{BOOK_TITLE}}", book_title)
        content = content.replace("{{CREATED}}", created_timestamp)
        
        # Write file
        file_path.write_text(content, encoding='utf-8')
        
        return file_path
    
    def capital_case_filename(self, title: str) -> str:
        """
        Convert title to Capital Case filename with spaces.
        
        Args:
            title: Note title
            
        Returns:
            Capital Case filename (without extension)
        """
        # Remove special characters but keep spaces and alphanumeric
        filename = re.sub(r'[^\w\s]', '', title)
        
        # Clean up multiple spaces
        filename = re.sub(r'\s+', ' ', filename)
        
        # Strip leading/trailing spaces
        filename = filename.strip()
        
        # Convert to title case
        filename = filename.title()
        
        # Ensure it's not empty
        if not filename:
            filename = "Untitled Note"
        
        return filename
    
    def sanitize_filename(self, title: str) -> str:
        """
        Legacy method for backward compatibility.
        Now redirects to capital_case_filename.
        """
        return self.capital_case_filename(title)
    
    def _extract_wikilinks(self, text: str) -> List[str]:
        """Extract wikilinks from text."""
        pattern = r'\[\[([^\]]+)\]\]'
        matches = re.findall(pattern, text)
        return sorted(set(matches))  # Remove duplicates and sort
    
    def _format_links(self, links: List[str]) -> str:
        """Format wikilinks as bullet list."""
        if not links:
            return "- No direct links identified"
        
        formatted_links = []
        for link in links:
            formatted_links.append(f"- [[{link}]]")
        
        return "\n".join(formatted_links)
    
    def _format_tags(self, tags: List[str]) -> str:
        """Format tags with # prefix."""
        if not tags:
            return ""
        
        formatted_tags = []
        for tag in tags:
            # Ensure tag doesn't already have #
            tag_clean = tag.strip().lstrip('#')
            if tag_clean:
                formatted_tags.append(f"#{tag_clean}")
        
        return " ".join(formatted_tags)
    
    def _format_tags_yaml(self, tags: List[str]) -> str:
        """Format tags for YAML frontmatter."""
        if not tags:
            return "finance, investing"
        
        formatted_tags = []
        for tag in tags:
            # Clean tag and ensure no # prefix for YAML
            tag_clean = tag.strip().lstrip('#')
            if tag_clean:
                formatted_tags.append(tag_clean)
        
        # Add default tags if not present
        default_tags = ["finance", "investing"]
        for default_tag in default_tags:
            if default_tag not in formatted_tags:
                formatted_tags.insert(0, default_tag)
        
        return ", ".join(formatted_tags)
    
    def get_existing_notes(self) -> List[str]:
        """Get list of existing note filenames."""
        if not self.output_dir.exists():
            return []
        
        return [f.stem for f in self.output_dir.glob("*.md")]
    
    def create_index_note(self, notes_data: List[Dict], chapter_info: Optional[str] = None) -> Optional[Path]:
        """
        Create an index note that links to all generated notes.
        
        Args:
            notes_data: List of note dictionaries
            chapter_info: Chapter information
            
        Returns:
            Path to created index file
        """
        if not notes_data:
            return None
        
        index_filename = f"index-{chapter_info.lower().replace(' ', '-')}" if chapter_info else "index"
        index_path = self.output_dir / f"{index_filename}.md"
        
        # Create index content
        content = f"# Index: {chapter_info or 'Generated Notes'}\n\n"
        content += f"Generated {len(notes_data)} atomic notes from this chapter.\n\n"
        content += "## Notes\n\n"
        
        for note_data in notes_data:
            title = note_data["title"]
            filename = self.capital_case_filename(title)
            content += f"- [[{filename}]] - {title}\n"
        
        content += f"\n---\n**Generated:** {Path(__file__).name}\n"
        
        index_path.write_text(content, encoding='utf-8')
        return index_path
    
    def create_book_moc(self, book_title: str = "A Random Walk Down Wall Street", author: str = "Burton G. Malkiel", notes_data: Optional[List[Dict]] = None, chapter_info: Optional[str] = None) -> Path:
        """
        Create a comprehensive Map of Content (MOC) for the book.
        
        Args:
            book_title: Title of the book
            author: Author of the book
            notes_data: Optional list of note dictionaries for this session
            chapter_info: Optional chapter information
            
        Returns:
            Path to created MOC file
        """
        # Create MOC filename from book title
        moc_filename = self.capital_case_filename(book_title)
        moc_path = self.output_dir / f"{moc_filename}.md"
        
        # Get current timestamp
        created_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Start building MOC content
        content = f"""---
created: {created_timestamp}
type: map-of-content
book: "{book_title}"
author: "{author}"
tags: [moc, book, finance, investing]
---

# {book_title}

**Author:** {author}  
**Type:** Map of Content (MOC)  
**Created:** {created_timestamp}

## Book Overview

*{book_title}* is a comprehensive guide to investing that challenges conventional wisdom about stock market prediction and active management. The book argues for the efficiency of markets and advocates for passive index fund investing over active stock picking or market timing.

## Key Themes

- **Market Efficiency**: The idea that stock prices reflect all available information
- **Random Walk Theory**: Stock price movements are essentially unpredictable
- **Index Fund Investing**: Passive investment strategies outperform active management
- **Behavioral Finance**: How psychological biases affect investment decisions
- **Risk and Return**: The fundamental relationship between investment risk and expected returns

## Book Structure

### Part I: Stocks and Their Value
- Historical perspective on stock market speculation
- Analysis of technical and fundamental analysis
- Introduction to efficient market theory

### Part II: How the Pros Play the Biggest Game in Town
- Institutional investment strategies
- Performance analysis of professional fund managers
- The rise of index funds

### Part III: The New Investment Technology
- Modern portfolio theory
- Asset allocation strategies
- International diversification

### Part IV: A Practical Guide for Random Walkers
- Practical investment advice for individual investors
- Life-cycle investing strategies
- Specific fund recommendations
"""

        # Add chapter-specific content if provided
        if chapter_info and notes_data:
            content += f"\n## Chapter Notes: {chapter_info}\n\n"
            content += f"Generated {len(notes_data)} atomic notes from {chapter_info}:\n\n"
            
            # Group notes by theme if possible
            for note_data in notes_data:
                title = note_data["title"]
                filename = self.capital_case_filename(title)
                summary = note_data["summary"][:100] + "..." if len(note_data["summary"]) > 100 else note_data["summary"]
                content += f"- **[[{filename}]]** - {summary}\n"

        # Add existing notes section
        existing_notes = self.get_existing_notes()
        if existing_notes:
            content += "\n## All Generated Notes\n\n"
            content += "*This section will be automatically updated as more notes are generated.*\n\n"
            
            for note_filename in sorted(existing_notes):
                if note_filename != moc_filename:  # Don't include the MOC itself
                    content += f"- [[{note_filename}]]\n"

        content += f"""

## Related Books and Resources

- *The Intelligent Investor* by Benjamin Graham
- *Common Sense on Mutual Funds* by John C. Bogle
- *The Little Book of Common Sense Investing* by John C. Bogle
- *Your Money or Your Life* by Vicki Robin

## Navigation

- 🏠 [[Home]] - Return to main knowledge base
- 📚 Books MOC - Other book notes
- 💰 Finance MOC - Financial concepts and strategies

---

**Last Updated:** {created_timestamp}  
**Note Count:** {len(notes_data) if notes_data else 0} concepts from {chapter_info or 'various chapters'}
"""

        # Write the MOC file
        moc_path.write_text(content, encoding='utf-8')
        return moc_path


def create_notes_from_data(notes_data: List[Dict], output_dir: str, template_path: Optional[str] = None, chapter_info: Optional[str] = None) -> List[str]:
    """
    Convenience function for creating notes from data.
    
    Args:
        notes_data: List of note dictionaries from LLM
        output_dir: Directory to save notes
        template_path: Optional path to template file
        chapter_info: Optional chapter information
        
    Returns:
        List of created file paths
    """
    generator = NoteGenerator(output_dir, template_path)
    return generator.create_notes_from_data(notes_data, chapter_info)