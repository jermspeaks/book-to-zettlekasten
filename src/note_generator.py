"""Note generation module for creating Markdown files from atomic notes."""

import re
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
            return """# {{TITLE}}

## Summary
{{SUMMARY}}

---
## Related Concepts
{{LINKS}}

---
**Source:** "A Random Walk Down Wall Street", Chapter {{CHAPTER}}
**Tags:** #finance #investing {{TAGS}}
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
    
    def _create_single_note(self, note_data: Dict, chapter_info: Optional[str] = None) -> Path:
        """Create a single Markdown note file."""
        title = note_data["title"]
        summary = note_data["summary"]
        tags = note_data.get("tags", [])
        
        # Create sanitized filename
        filename = self.sanitize_filename(title)
        file_path = self.output_dir / f"{filename}.md"
        
        # Check if file already exists
        if file_path.exists():
            print(f"Note already exists: {filename}.md (skipping)")
            return file_path
        
        # Extract wikilinks from summary
        links = self._extract_wikilinks(summary)
        
        # Populate template
        content = self.template.replace("{{TITLE}}", title)
        content = content.replace("{{SUMMARY}}", summary)
        content = content.replace("{{LINKS}}", self._format_links(links))
        content = content.replace("{{CHAPTER}}", chapter_info or "Unknown")
        content = content.replace("{{TAGS}}", self._format_tags(tags))
        
        # Write file
        file_path.write_text(content, encoding='utf-8')
        
        return file_path
    
    def sanitize_filename(self, title: str) -> str:
        """
        Convert title to filesystem-safe filename.
        
        Args:
            title: Note title
            
        Returns:
            Sanitized filename (without extension)
        """
        # Convert to lowercase
        filename = title.lower()
        
        # Replace spaces and special characters with hyphens
        filename = re.sub(r'[^\w\s-]', '', filename)
        filename = re.sub(r'[-\s]+', '-', filename)
        
        # Remove leading/trailing hyphens
        filename = filename.strip('-')
        
        # Ensure it's not empty
        if not filename:
            filename = "untitled-note"
        
        return filename
    
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
            filename = self.sanitize_filename(title)
            content += f"- [[{filename}]] - {title}\n"
        
        content += f"\n---\n**Generated:** {Path(__file__).name}\n"
        
        index_path.write_text(content, encoding='utf-8')
        return index_path


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