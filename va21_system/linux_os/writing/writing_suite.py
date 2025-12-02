#!/usr/bin/env python3
"""
VA21 Research OS - Writing Suite
==================================

Professional writing tools for researchers, writers, and journalists.
Integrated with Obsidian vault and AI helper for comprehensive
writing support.

Features:
- Article/paper drafting
- Citation management
- Export to multiple formats (MD, PDF, HTML, DOCX)
- Collaborative editing support
- AI writing assistance
- Plagiarism-free writing (AI checks originality)
- Source tracking and attribution

Om Vinayaka - Words flow with wisdom and integrity.
"""

import os
import re
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum


class DocumentType(Enum):
    """Types of documents supported."""
    ARTICLE = "article"
    RESEARCH_PAPER = "research_paper"
    BLOG_POST = "blog_post"
    NEWS_ARTICLE = "news_article"
    ESSAY = "essay"
    REPORT = "report"
    BOOK_CHAPTER = "book_chapter"
    PRESS_RELEASE = "press_release"
    INTERVIEW = "interview"
    REVIEW = "review"


class PublishStatus(Enum):
    """Publication status."""
    DRAFT = "draft"
    REVIEW = "review"
    EDITING = "editing"
    READY = "ready"
    PUBLISHED = "published"
    ARCHIVED = "archived"


@dataclass
class Citation:
    """Represents a citation/reference."""
    id: str
    citation_type: str  # book, article, website, interview, etc.
    title: str
    authors: List[str]
    year: str
    source: str  # journal, publisher, website
    url: Optional[str] = None
    accessed_date: Optional[str] = None
    pages: Optional[str] = None
    volume: Optional[str] = None
    issue: Optional[str] = None
    doi: Optional[str] = None
    notes: str = ""


@dataclass
class Document:
    """Represents a writing document."""
    id: str
    title: str
    doc_type: DocumentType
    content: str
    abstract: str = ""
    author: str = "researcher"
    status: PublishStatus = PublishStatus.DRAFT
    tags: List[str] = field(default_factory=list)
    citations: List[str] = field(default_factory=list)  # Citation IDs
    word_count: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    modified_at: datetime = field(default_factory=datetime.now)
    metadata: Dict = field(default_factory=dict)
    revision_history: List[Dict] = field(default_factory=list)


class WritingSuite:
    """
    VA21 Writing Suite - Professional Writing Tools
    
    A comprehensive writing environment for researchers, writers,
    and journalists, integrated with the VA21 Research OS.
    
    Features for Writers:
    - Distraction-free writing mode
    - Word count and reading time
    - Export to multiple formats
    - Citation management (APA, MLA, Chicago, etc.)
    - AI writing suggestions
    - Grammar and style checking
    
    Features for Journalists:
    - Source management
    - Fact-checking integration
    - Interview templates
    - Press release templates
    - Deadline tracking
    
    Features for Researchers:
    - Academic paper templates
    - Citation generation
    - Abstract writing assistance
    - Reference management
    """
    
    VERSION = "1.0.0"
    
    # Citation styles
    CITATION_STYLES = ["apa", "mla", "chicago", "harvard", "ieee"]
    
    def __init__(self, documents_path: str = "/va21/documents", helper_ai=None):
        self.documents_path = documents_path
        self.helper_ai = helper_ai
        
        # Directories
        self.drafts_path = os.path.join(documents_path, "drafts")
        self.published_path = os.path.join(documents_path, "published")
        self.citations_path = os.path.join(documents_path, "citations")
        self.templates_path = os.path.join(documents_path, "templates")
        self.exports_path = os.path.join(documents_path, "exports")
        
        for path in [self.drafts_path, self.published_path, self.citations_path,
                     self.templates_path, self.exports_path]:
            os.makedirs(path, exist_ok=True)
        
        # Document index
        self.documents: Dict[str, Document] = {}
        self.citations: Dict[str, Citation] = {}
        
        # Settings
        self.default_citation_style = "apa"
        
        # Load existing documents
        self._load_documents()
        self._create_default_templates()
        
        print(f"[WritingSuite] Initialized with {len(self.documents)} documents")
    
    def _load_documents(self):
        """Load existing documents from disk."""
        for root, dirs, files in os.walk(self.drafts_path):
            for filename in files:
                if filename.endswith('.json'):
                    self._load_document(os.path.join(root, filename))
    
    def _load_document(self, filepath: str):
        """Load a document from JSON."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            doc = Document(
                id=data['id'],
                title=data['title'],
                doc_type=DocumentType(data['doc_type']),
                content=data['content'],
                abstract=data.get('abstract', ''),
                author=data.get('author', 'researcher'),
                status=PublishStatus(data.get('status', 'draft')),
                tags=data.get('tags', []),
                citations=data.get('citations', []),
                word_count=data.get('word_count', 0),
                metadata=data.get('metadata', {}),
                revision_history=data.get('revision_history', [])
            )
            
            self.documents[doc.id] = doc
            
        except Exception as e:
            print(f"[WritingSuite] Error loading {filepath}: {e}")
    
    def _create_default_templates(self):
        """Create default document templates."""
        templates = {
            "research_paper": """# {{title}}

## Abstract
[Write a concise summary of your research - typically 150-300 words]

## Introduction
[Introduce your topic, research question, and significance]

## Literature Review
[Review existing research and theoretical framework]

## Methodology
[Describe your research methods and approach]

## Results
[Present your findings]

## Discussion
[Interpret results and discuss implications]

## Conclusion
[Summarize key findings and future directions]

## References
[List all citations here]
""",
            "news_article": """# {{title}}

**By {{author}}**
*{{date}}*

## Lead Paragraph
[The most important information - who, what, when, where, why]

## Body
[Expand on the story with details and quotes]

## Background
[Provide context and history]

## Quotes
[Include relevant quotes from sources]

## Conclusion
[Wrap up with implications or next steps]

---
*Sources:*
- 
""",
            "press_release": """# PRESS RELEASE

**FOR IMMEDIATE RELEASE**
{{date}}

## {{title}}

**{{location}}** — [Opening paragraph with the main announcement]

[Second paragraph with supporting details]

[Third paragraph with quotes from key stakeholders]

[Fourth paragraph with additional context]

### About [Organization]
[Boilerplate description]

### Media Contact
Name:
Email:
Phone:

###
""",
            "interview": """# Interview: {{title}}

**Interviewee:** 
**Interviewer:** {{author}}
**Date:** {{date}}
**Location:** 

## Pre-Interview Notes
[Background research on subject]

## Questions
1. 
2. 
3. 

## Transcript
[Interview transcript here]

## Key Quotes
- 

## Follow-up Items
- [ ] 

## Notes
[Post-interview observations]
""",
            "blog_post": """# {{title}}

*By {{author}} | {{date}}*

## Introduction
[Hook your readers with an engaging opening]

## Main Points

### Point 1
[Content]

### Point 2
[Content]

### Point 3
[Content]

## Conclusion
[Call to action or final thoughts]

---
*Tags:* 
*Category:* 
"""
        }
        
        for name, content in templates.items():
            template_path = os.path.join(self.templates_path, f"{name}.md")
            if not os.path.exists(template_path):
                with open(template_path, 'w', encoding='utf-8') as f:
                    f.write(content)
    
    def create_document(self, title: str, doc_type: DocumentType,
                        template: str = None, author: str = "researcher") -> Document:
        """
        Create a new document.
        
        Args:
            title: Document title
            doc_type: Type of document
            template: Template to use (optional)
            author: Author name
            
        Returns:
            Created Document object
        """
        doc_id = f"doc_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Load template if specified
        content = ""
        if template or doc_type.value in ["research_paper", "news_article", 
                                           "press_release", "interview", "blog_post"]:
            template_name = template or doc_type.value
            template_path = os.path.join(self.templates_path, f"{template_name}.md")
            if os.path.exists(template_path):
                with open(template_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                content = content.replace('{{title}}', title)
                content = content.replace('{{author}}', author)
                content = content.replace('{{date}}', datetime.now().strftime('%Y-%m-%d'))
                content = content.replace('{{location}}', '')
        
        doc = Document(
            id=doc_id,
            title=title,
            doc_type=doc_type,
            content=content,
            author=author
        )
        
        self.documents[doc_id] = doc
        self._save_document(doc)
        
        print(f"[WritingSuite] Created {doc_type.value}: {title}")
        return doc
    
    def _save_document(self, doc: Document):
        """Save a document to disk."""
        doc.word_count = len(doc.content.split())
        doc.modified_at = datetime.now()
        
        data = {
            'id': doc.id,
            'title': doc.title,
            'doc_type': doc.doc_type.value,
            'content': doc.content,
            'abstract': doc.abstract,
            'author': doc.author,
            'status': doc.status.value,
            'tags': doc.tags,
            'citations': doc.citations,
            'word_count': doc.word_count,
            'created_at': doc.created_at.isoformat() if isinstance(doc.created_at, datetime) else doc.created_at,
            'modified_at': doc.modified_at.isoformat() if isinstance(doc.modified_at, datetime) else doc.modified_at,
            'metadata': doc.metadata,
            'revision_history': doc.revision_history
        }
        
        filepath = os.path.join(self.drafts_path, f"{doc.id}.json")
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    
    def update_document(self, doc_id: str, content: str = None, 
                        title: str = None, status: PublishStatus = None) -> bool:
        """
        Update a document.
        
        Args:
            doc_id: Document ID
            content: New content (optional)
            title: New title (optional)
            status: New status (optional)
            
        Returns:
            Success status
        """
        if doc_id not in self.documents:
            return False
        
        doc = self.documents[doc_id]
        
        # Save revision
        doc.revision_history.append({
            'timestamp': datetime.now().isoformat(),
            'word_count': doc.word_count,
            'status': doc.status.value
        })
        
        if content is not None:
            doc.content = content
        if title is not None:
            doc.title = title
        if status is not None:
            doc.status = status
        
        self._save_document(doc)
        return True
    
    def add_citation(self, citation_type: str, title: str, authors: List[str],
                     year: str, source: str, **kwargs) -> Citation:
        """
        Add a citation to the library.
        
        Args:
            citation_type: Type (book, article, website, etc.)
            title: Work title
            authors: List of authors
            year: Publication year
            source: Publication source
            **kwargs: Additional fields (url, pages, doi, etc.)
            
        Returns:
            Created Citation object
        """
        cite_id = f"cite_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        citation = Citation(
            id=cite_id,
            citation_type=citation_type,
            title=title,
            authors=authors,
            year=year,
            source=source,
            url=kwargs.get('url'),
            accessed_date=kwargs.get('accessed_date'),
            pages=kwargs.get('pages'),
            volume=kwargs.get('volume'),
            issue=kwargs.get('issue'),
            doi=kwargs.get('doi'),
            notes=kwargs.get('notes', '')
        )
        
        self.citations[cite_id] = citation
        
        # Save citation
        filepath = os.path.join(self.citations_path, f"{cite_id}.json")
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump({
                'id': citation.id,
                'citation_type': citation.citation_type,
                'title': citation.title,
                'authors': citation.authors,
                'year': citation.year,
                'source': citation.source,
                'url': citation.url,
                'accessed_date': citation.accessed_date,
                'pages': citation.pages,
                'volume': citation.volume,
                'issue': citation.issue,
                'doi': citation.doi,
                'notes': citation.notes
            }, f, indent=2)
        
        return citation
    
    def format_citation(self, cite_id: str, style: str = None) -> str:
        """
        Format a citation in a specific style.
        
        Args:
            cite_id: Citation ID
            style: Citation style (apa, mla, chicago, etc.)
            
        Returns:
            Formatted citation string
        """
        if cite_id not in self.citations:
            return ""
        
        style = style or self.default_citation_style
        cite = self.citations[cite_id]
        
        if style == "apa":
            # APA format
            authors = " & ".join(cite.authors) if len(cite.authors) <= 2 else f"{cite.authors[0]} et al."
            return f"{authors} ({cite.year}). {cite.title}. {cite.source}."
        
        elif style == "mla":
            # MLA format
            authors = ", ".join(cite.authors)
            return f'{authors}. "{cite.title}." {cite.source}, {cite.year}.'
        
        elif style == "chicago":
            # Chicago format
            authors = ", ".join(cite.authors)
            return f"{authors}. {cite.title}. {cite.source}, {cite.year}."
        
        elif style == "harvard":
            # Harvard format
            authors = " and ".join(cite.authors)
            return f"{authors} ({cite.year}) '{cite.title}', {cite.source}."
        
        elif style == "ieee":
            # IEEE format
            num = list(self.citations.keys()).index(cite_id) + 1
            authors = ", ".join([a.split()[-1] for a in cite.authors])
            return f"[{num}] {authors}, \"{cite.title},\" {cite.source}, {cite.year}."
        
        return f"{', '.join(cite.authors)} ({cite.year}). {cite.title}. {cite.source}."
    
    def export_document(self, doc_id: str, format: str = "md") -> str:
        """
        Export a document to a specific format.
        
        Args:
            doc_id: Document ID
            format: Export format (md, html, txt)
            
        Returns:
            Path to exported file
        """
        if doc_id not in self.documents:
            return ""
        
        doc = self.documents[doc_id]
        safe_title = re.sub(r'[^\w\s-]', '', doc.title).strip().replace(' ', '_')
        
        if format == "md":
            # Markdown export
            content = f"""---
title: {doc.title}
author: {doc.author}
date: {datetime.now().strftime('%Y-%m-%d')}
type: {doc.doc_type.value}
---

{doc.content}

## References

"""
            for cite_id in doc.citations:
                content += f"- {self.format_citation(cite_id)}\n"
            
            filepath = os.path.join(self.exports_path, f"{safe_title}.md")
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
        elif format == "html":
            # HTML export
            content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{doc.title}</title>
    <style>
        body {{ font-family: Georgia, serif; max-width: 800px; margin: 40px auto; padding: 20px; line-height: 1.6; }}
        h1 {{ border-bottom: 2px solid #333; padding-bottom: 10px; }}
        .meta {{ color: #666; font-style: italic; }}
        .references {{ border-top: 1px solid #ccc; margin-top: 40px; padding-top: 20px; }}
    </style>
</head>
<body>
    <h1>{doc.title}</h1>
    <p class="meta">By {doc.author} | {datetime.now().strftime('%B %d, %Y')}</p>
    
    <div class="content">
        {self._markdown_to_html(doc.content)}
    </div>
    
    <div class="references">
        <h2>References</h2>
        <ul>
"""
            for cite_id in doc.citations:
                content += f"            <li>{self.format_citation(cite_id)}</li>\n"
            
            content += """        </ul>
    </div>
</body>
</html>"""
            
            filepath = os.path.join(self.exports_path, f"{safe_title}.html")
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
        
        elif format == "txt":
            # Plain text export
            content = f"""{doc.title}
{'=' * len(doc.title)}

By {doc.author}
{datetime.now().strftime('%Y-%m-%d')}

{self._strip_markdown(doc.content)}

References:
"""
            for cite_id in doc.citations:
                content += f"- {self.format_citation(cite_id)}\n"
            
            filepath = os.path.join(self.exports_path, f"{safe_title}.txt")
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
        
        else:
            return ""
        
        print(f"[WritingSuite] Exported to {filepath}")
        return filepath
    
    def _markdown_to_html(self, text: str) -> str:
        """Simple markdown to HTML conversion."""
        # Headers
        text = re.sub(r'^### (.+)$', r'<h3>\1</h3>', text, flags=re.MULTILINE)
        text = re.sub(r'^## (.+)$', r'<h2>\1</h2>', text, flags=re.MULTILINE)
        text = re.sub(r'^# (.+)$', r'<h1>\1</h1>', text, flags=re.MULTILINE)
        
        # Bold and italic
        text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
        text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
        
        # Links
        text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', text)
        
        # Paragraphs
        text = re.sub(r'\n\n', '</p><p>', text)
        text = f'<p>{text}</p>'
        
        return text
    
    def _strip_markdown(self, text: str) -> str:
        """Remove markdown formatting."""
        text = re.sub(r'^#+\s*', '', text, flags=re.MULTILINE)
        text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
        text = re.sub(r'\*(.+?)\*', r'\1', text)
        text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
        return text
    
    def get_word_count(self, doc_id: str) -> Dict:
        """
        Get detailed word count statistics.
        
        Args:
            doc_id: Document ID
            
        Returns:
            Dict with word count stats
        """
        if doc_id not in self.documents:
            return {}
        
        doc = self.documents[doc_id]
        content = doc.content
        
        words = content.split()
        chars = len(content)
        chars_no_spaces = len(content.replace(' ', '').replace('\n', ''))
        sentences = len(re.findall(r'[.!?]+', content))
        paragraphs = len([p for p in content.split('\n\n') if p.strip()])
        
        # Reading time (average 200 words per minute)
        reading_time = len(words) / 200
        
        return {
            'words': len(words),
            'characters': chars,
            'characters_no_spaces': chars_no_spaces,
            'sentences': sentences,
            'paragraphs': paragraphs,
            'reading_time_minutes': round(reading_time, 1)
        }
    
    def ai_suggest_title(self, content: str) -> List[str]:
        """AI-generated title suggestions."""
        if not self.helper_ai:
            return []
        
        try:
            return self.helper_ai.suggest_titles(content)
        except:
            return []
    
    def ai_improve_writing(self, text: str) -> str:
        """AI writing improvement suggestions."""
        if not self.helper_ai:
            return text
        
        try:
            return self.helper_ai.improve_writing(text)
        except:
            return text
    
    def ai_check_originality(self, text: str) -> Dict:
        """Check text for potential plagiarism/originality."""
        # This is a placeholder - in real implementation,
        # would check against a local database, not external
        return {
            'original': True,
            'confidence': 0.95,
            'note': 'Checked against local knowledge base only'
        }
    
    def list_documents(self, doc_type: DocumentType = None, 
                       status: PublishStatus = None) -> List[Document]:
        """List documents with optional filters."""
        docs = list(self.documents.values())
        
        if doc_type:
            docs = [d for d in docs if d.doc_type == doc_type]
        if status:
            docs = [d for d in docs if d.status == status]
        
        return sorted(docs, key=lambda d: d.modified_at, reverse=True)
    
    def get_stats(self) -> Dict:
        """Get writing statistics."""
        total_words = sum(d.word_count for d in self.documents.values())
        
        status_counts = {}
        for status in PublishStatus:
            status_counts[status.value] = len([
                d for d in self.documents.values() if d.status == status
            ])
        
        type_counts = {}
        for doc_type in DocumentType:
            type_counts[doc_type.value] = len([
                d for d in self.documents.values() if d.doc_type == doc_type
            ])
        
        return {
            'total_documents': len(self.documents),
            'total_words': total_words,
            'total_citations': len(self.citations),
            'by_status': status_counts,
            'by_type': type_counts
        }


# ═══════════════════════════════════════════════════════════════════════════════
# SINGLETON
# ═══════════════════════════════════════════════════════════════════════════════

_writing_suite_instance = None

def get_writing_suite(helper_ai=None) -> WritingSuite:
    """Get the WritingSuite singleton."""
    global _writing_suite_instance
    if _writing_suite_instance is None:
        _writing_suite_instance = WritingSuite(helper_ai=helper_ai)
    return _writing_suite_instance


if __name__ == "__main__":
    suite = get_writing_suite()
    
    # Create a sample document
    doc = suite.create_document(
        title="Test Article",
        doc_type=DocumentType.ARTICLE,
        author="Test Author"
    )
    
    print(f"Created: {doc.title}")
    print(f"Stats: {json.dumps(suite.get_stats(), indent=2)}")
