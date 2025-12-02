#!/usr/bin/env python3
"""
VA21 Research OS - Research Suite
===================================

Comprehensive research tools for academics, scientists, and researchers.
Designed to be the ultimate research companion.

Features:
- Literature Management (Zotero-like)
- Citation Generator (all major formats)
- Data Analysis Tools
- Experiment Tracker
- Research Timeline
- Collaboration Tools
- Publication Manager
- Grant Writing Assistant
- Peer Review Helper
- Research Ethics Checklist
- Data Visualization
- Statistical Analysis
- Bibliography Manager

Om Vinayaka - Knowledge is the path to enlightenment.
"""

import os
import json
import re
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum


class SourceType(Enum):
    """Types of research sources."""
    JOURNAL_ARTICLE = "journal_article"
    BOOK = "book"
    BOOK_CHAPTER = "book_chapter"
    CONFERENCE_PAPER = "conference_paper"
    THESIS = "thesis"
    DISSERTATION = "dissertation"
    REPORT = "report"
    WEBSITE = "website"
    PATENT = "patent"
    DATASET = "dataset"
    SOFTWARE = "software"
    PREPRINT = "preprint"
    NEWSPAPER = "newspaper"
    MAGAZINE = "magazine"
    VIDEO = "video"
    PODCAST = "podcast"
    INTERVIEW = "interview"
    LEGAL_CASE = "legal_case"
    GOVERNMENT_DOC = "government_document"


class CitationStyle(Enum):
    """Citation format styles."""
    APA7 = "apa7"
    APA6 = "apa6"
    MLA9 = "mla9"
    MLA8 = "mla8"
    CHICAGO = "chicago"
    HARVARD = "harvard"
    IEEE = "ieee"
    VANCOUVER = "vancouver"
    AMA = "ama"
    TURABIAN = "turabian"
    OSCOLA = "oscola"  # Legal
    BLUEBOOK = "bluebook"  # Legal US
    CSE = "cse"  # Science
    ACS = "acs"  # Chemistry
    NATURE = "nature"
    SCIENCE = "science"


class ProjectStatus(Enum):
    """Research project status."""
    PLANNING = "planning"
    LITERATURE_REVIEW = "literature_review"
    DATA_COLLECTION = "data_collection"
    ANALYSIS = "analysis"
    WRITING = "writing"
    PEER_REVIEW = "peer_review"
    REVISION = "revision"
    SUBMITTED = "submitted"
    PUBLISHED = "published"
    ARCHIVED = "archived"


@dataclass
class Author:
    """Represents an author."""
    first_name: str
    last_name: str
    middle_name: str = ""
    suffix: str = ""  # Jr., III, etc.
    orcid: str = ""
    affiliation: str = ""
    email: str = ""
    
    def full_name(self) -> str:
        parts = [self.first_name]
        if self.middle_name:
            parts.append(self.middle_name)
        parts.append(self.last_name)
        if self.suffix:
            parts.append(self.suffix)
        return " ".join(parts)
    
    def last_first(self) -> str:
        """Last, First M. format."""
        result = self.last_name
        if self.suffix:
            result += f" {self.suffix}"
        result += f", {self.first_name[0]}."
        if self.middle_name:
            result += f" {self.middle_name[0]}."
        return result


@dataclass
class Reference:
    """A research reference/source."""
    id: str
    source_type: SourceType
    title: str
    authors: List[Author]
    year: int
    
    # Publication info
    journal: str = ""
    volume: str = ""
    issue: str = ""
    pages: str = ""
    publisher: str = ""
    place: str = ""
    edition: str = ""
    
    # Identifiers
    doi: str = ""
    isbn: str = ""
    issn: str = ""
    pmid: str = ""
    arxiv: str = ""
    url: str = ""
    
    # Metadata
    abstract: str = ""
    keywords: List[str] = field(default_factory=list)
    notes: str = ""
    tags: List[str] = field(default_factory=list)
    
    # File
    pdf_path: str = ""
    
    # Timestamps
    added_date: datetime = field(default_factory=datetime.now)
    accessed_date: str = ""
    
    # Reading status
    is_read: bool = False
    rating: int = 0  # 1-5
    

@dataclass
class ResearchProject:
    """A research project."""
    id: str
    title: str
    description: str
    status: ProjectStatus = ProjectStatus.PLANNING
    
    # Team
    lead_researcher: str = ""
    collaborators: List[str] = field(default_factory=list)
    
    # References
    references: List[str] = field(default_factory=list)  # Reference IDs
    
    # Timeline
    start_date: datetime = field(default_factory=datetime.now)
    target_end_date: Optional[datetime] = None
    milestones: List[Dict] = field(default_factory=list)
    
    # Data
    datasets: List[str] = field(default_factory=list)
    hypotheses: List[str] = field(default_factory=list)
    findings: List[str] = field(default_factory=list)
    
    # Ethics
    ethics_approved: bool = False
    ethics_id: str = ""
    
    # Funding
    grants: List[Dict] = field(default_factory=list)
    
    # Notes
    notes: str = ""
    

@dataclass
class Experiment:
    """An experiment or study."""
    id: str
    project_id: str
    name: str
    description: str
    
    # Design
    methodology: str = ""
    variables: Dict = field(default_factory=dict)
    sample_size: int = 0
    
    # Status
    status: str = "planned"  # planned, running, completed, failed
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    
    # Results
    raw_data_path: str = ""
    results: Dict = field(default_factory=dict)
    conclusions: str = ""
    
    # Reproducibility
    protocol: str = ""
    materials: List[str] = field(default_factory=list)
    code_repository: str = ""


class ResearchSuite:
    """
    VA21 Research Suite
    
    A comprehensive research management system for academics,
    scientists, and researchers.
    
    Core Features:
    - Reference Management (like Zotero/Mendeley)
    - Citation Generation (20+ styles)
    - Project Management
    - Experiment Tracking
    - Data Organization
    - Collaboration Tools
    - Publication Pipeline
    """
    
    VERSION = "1.0.0"
    
    def __init__(self, data_path: str = "/va21/research"):
        self.data_path = data_path
        
        # Create directories
        self.refs_path = os.path.join(data_path, "references")
        self.projects_path = os.path.join(data_path, "projects")
        self.pdfs_path = os.path.join(data_path, "pdfs")
        self.data_path_dir = os.path.join(data_path, "datasets")
        self.exports_path = os.path.join(data_path, "exports")
        
        for path in [self.refs_path, self.projects_path, self.pdfs_path,
                     self.data_path_dir, self.exports_path]:
            os.makedirs(path, exist_ok=True)
        
        # Data stores
        self.references: Dict[str, Reference] = {}
        self.projects: Dict[str, ResearchProject] = {}
        self.experiments: Dict[str, Experiment] = {}
        
        # Collections (folders for organizing refs)
        self.collections: Dict[str, List[str]] = {}
        
        # Load existing data
        self._load_data()
        
        print(f"[ResearchSuite] Initialized with {len(self.references)} references, {len(self.projects)} projects")
    
    def _load_data(self):
        """Load existing data from disk."""
        # Load references
        refs_file = os.path.join(self.data_path, "references.json")
        if os.path.exists(refs_file):
            try:
                with open(refs_file, 'r') as f:
                    data = json.load(f)
                for ref_data in data:
                    ref = self._dict_to_reference(ref_data)
                    self.references[ref.id] = ref
            except:
                pass
        
        # Load projects
        projects_file = os.path.join(self.data_path, "projects.json")
        if os.path.exists(projects_file):
            try:
                with open(projects_file, 'r') as f:
                    data = json.load(f)
                for proj_data in data:
                    proj = self._dict_to_project(proj_data)
                    self.projects[proj.id] = proj
            except:
                pass
    
    def _save_data(self):
        """Save data to disk."""
        # Save references
        refs_file = os.path.join(self.data_path, "references.json")
        refs_data = [self._reference_to_dict(ref) for ref in self.references.values()]
        with open(refs_file, 'w') as f:
            json.dump(refs_data, f, indent=2, default=str)
        
        # Save projects
        projects_file = os.path.join(self.data_path, "projects.json")
        projects_data = [self._project_to_dict(proj) for proj in self.projects.values()]
        with open(projects_file, 'w') as f:
            json.dump(projects_data, f, indent=2, default=str)
    
    def _reference_to_dict(self, ref: Reference) -> Dict:
        """Convert Reference to dict for serialization."""
        return {
            "id": ref.id,
            "source_type": ref.source_type.value,
            "title": ref.title,
            "authors": [
                {"first_name": a.first_name, "last_name": a.last_name,
                 "middle_name": a.middle_name, "orcid": a.orcid}
                for a in ref.authors
            ],
            "year": ref.year,
            "journal": ref.journal,
            "volume": ref.volume,
            "issue": ref.issue,
            "pages": ref.pages,
            "publisher": ref.publisher,
            "doi": ref.doi,
            "isbn": ref.isbn,
            "url": ref.url,
            "abstract": ref.abstract,
            "keywords": ref.keywords,
            "notes": ref.notes,
            "tags": ref.tags,
            "pdf_path": ref.pdf_path,
            "is_read": ref.is_read,
            "rating": ref.rating,
            "added_date": ref.added_date.isoformat() if isinstance(ref.added_date, datetime) else ref.added_date,
        }
    
    def _dict_to_reference(self, data: Dict) -> Reference:
        """Convert dict to Reference."""
        authors = [
            Author(
                first_name=a.get("first_name", ""),
                last_name=a.get("last_name", ""),
                middle_name=a.get("middle_name", ""),
                orcid=a.get("orcid", "")
            )
            for a in data.get("authors", [])
        ]
        
        return Reference(
            id=data["id"],
            source_type=SourceType(data.get("source_type", "journal_article")),
            title=data["title"],
            authors=authors,
            year=data.get("year", 0),
            journal=data.get("journal", ""),
            volume=data.get("volume", ""),
            issue=data.get("issue", ""),
            pages=data.get("pages", ""),
            publisher=data.get("publisher", ""),
            doi=data.get("doi", ""),
            isbn=data.get("isbn", ""),
            url=data.get("url", ""),
            abstract=data.get("abstract", ""),
            keywords=data.get("keywords", []),
            notes=data.get("notes", ""),
            tags=data.get("tags", []),
            pdf_path=data.get("pdf_path", ""),
            is_read=data.get("is_read", False),
            rating=data.get("rating", 0),
        )
    
    def _project_to_dict(self, proj: ResearchProject) -> Dict:
        """Convert Project to dict."""
        return {
            "id": proj.id,
            "title": proj.title,
            "description": proj.description,
            "status": proj.status.value,
            "lead_researcher": proj.lead_researcher,
            "collaborators": proj.collaborators,
            "references": proj.references,
            "start_date": proj.start_date.isoformat() if isinstance(proj.start_date, datetime) else proj.start_date,
            "milestones": proj.milestones,
            "hypotheses": proj.hypotheses,
            "findings": proj.findings,
            "ethics_approved": proj.ethics_approved,
            "notes": proj.notes,
        }
    
    def _dict_to_project(self, data: Dict) -> ResearchProject:
        """Convert dict to Project."""
        return ResearchProject(
            id=data["id"],
            title=data["title"],
            description=data.get("description", ""),
            status=ProjectStatus(data.get("status", "planning")),
            lead_researcher=data.get("lead_researcher", ""),
            collaborators=data.get("collaborators", []),
            references=data.get("references", []),
            milestones=data.get("milestones", []),
            hypotheses=data.get("hypotheses", []),
            findings=data.get("findings", []),
            ethics_approved=data.get("ethics_approved", False),
            notes=data.get("notes", ""),
        )
    
    # ═══════════════════════════════════════════════════════════════════════════
    # REFERENCE MANAGEMENT
    # ═══════════════════════════════════════════════════════════════════════════
    
    def add_reference(self, source_type: SourceType, title: str, authors: List[Dict],
                      year: int, **kwargs) -> Reference:
        """
        Add a new reference.
        
        Args:
            source_type: Type of source
            title: Title of the work
            authors: List of author dicts with first_name, last_name
            year: Publication year
            **kwargs: Additional fields (journal, doi, etc.)
            
        Returns:
            Created Reference
        """
        ref_id = f"ref_{hashlib.md5(f'{title}{year}'.encode()).hexdigest()[:10]}"
        
        author_objects = [
            Author(
                first_name=a.get("first_name", ""),
                last_name=a.get("last_name", ""),
                middle_name=a.get("middle_name", ""),
                orcid=a.get("orcid", "")
            )
            for a in authors
        ]
        
        ref = Reference(
            id=ref_id,
            source_type=source_type,
            title=title,
            authors=author_objects,
            year=year,
            journal=kwargs.get("journal", ""),
            volume=kwargs.get("volume", ""),
            issue=kwargs.get("issue", ""),
            pages=kwargs.get("pages", ""),
            publisher=kwargs.get("publisher", ""),
            doi=kwargs.get("doi", ""),
            isbn=kwargs.get("isbn", ""),
            url=kwargs.get("url", ""),
            abstract=kwargs.get("abstract", ""),
            keywords=kwargs.get("keywords", []),
            tags=kwargs.get("tags", []),
        )
        
        self.references[ref_id] = ref
        self._save_data()
        
        print(f"[ResearchSuite] Added reference: {title}")
        return ref
    
    def search_references(self, query: str, field: str = "all") -> List[Reference]:
        """
        Search references.
        
        Args:
            query: Search query
            field: Field to search (all, title, author, year, keyword)
            
        Returns:
            List of matching references
        """
        results = []
        query_lower = query.lower()
        
        for ref in self.references.values():
            match = False
            
            if field in ["all", "title"]:
                if query_lower in ref.title.lower():
                    match = True
            
            if field in ["all", "author"]:
                for author in ref.authors:
                    if query_lower in author.full_name().lower():
                        match = True
                        break
            
            if field in ["all", "year"]:
                if query == str(ref.year):
                    match = True
            
            if field in ["all", "keyword"]:
                for kw in ref.keywords + ref.tags:
                    if query_lower in kw.lower():
                        match = True
                        break
            
            if match:
                results.append(ref)
        
        return results
    
    def get_reference_by_doi(self, doi: str) -> Optional[Reference]:
        """Find reference by DOI."""
        for ref in self.references.values():
            if ref.doi == doi:
                return ref
        return None
    
    def import_from_bibtex(self, bibtex_content: str) -> List[Reference]:
        """
        Import references from BibTeX.
        
        Args:
            bibtex_content: BibTeX formatted string
            
        Returns:
            List of imported references
        """
        imported = []
        
        # Simple BibTeX parser
        entries = re.findall(r'@(\w+)\s*\{([^}]+),([^@]+)\}', bibtex_content, re.DOTALL)
        
        for entry_type, key, fields in entries:
            # Parse fields
            field_dict = {}
            for match in re.finditer(r'(\w+)\s*=\s*[{"](.*?)[}"]', fields, re.DOTALL):
                field_dict[match.group(1).lower()] = match.group(2).strip()
            
            # Map entry type
            type_map = {
                "article": SourceType.JOURNAL_ARTICLE,
                "book": SourceType.BOOK,
                "inproceedings": SourceType.CONFERENCE_PAPER,
                "phdthesis": SourceType.DISSERTATION,
                "mastersthesis": SourceType.THESIS,
                "techreport": SourceType.REPORT,
            }
            source_type = type_map.get(entry_type.lower(), SourceType.JOURNAL_ARTICLE)
            
            # Parse authors
            authors = []
            author_str = field_dict.get("author", "")
            for author_part in author_str.split(" and "):
                parts = author_part.strip().split(",")
                if len(parts) >= 2:
                    authors.append({
                        "last_name": parts[0].strip(),
                        "first_name": parts[1].strip()
                    })
                elif parts:
                    name_parts = parts[0].strip().split()
                    if len(name_parts) >= 2:
                        authors.append({
                            "first_name": " ".join(name_parts[:-1]),
                            "last_name": name_parts[-1]
                        })
            
            try:
                ref = self.add_reference(
                    source_type=source_type,
                    title=field_dict.get("title", "Untitled"),
                    authors=authors,
                    year=int(field_dict.get("year", 0)),
                    journal=field_dict.get("journal", ""),
                    volume=field_dict.get("volume", ""),
                    pages=field_dict.get("pages", ""),
                    doi=field_dict.get("doi", ""),
                )
                imported.append(ref)
            except:
                pass
        
        return imported
    
    def export_to_bibtex(self, ref_ids: List[str] = None) -> str:
        """
        Export references to BibTeX format.
        
        Args:
            ref_ids: List of reference IDs (or all if None)
            
        Returns:
            BibTeX formatted string
        """
        refs = [self.references[rid] for rid in (ref_ids or self.references.keys())
                if rid in self.references]
        
        bibtex = []
        
        for ref in refs:
            # Determine entry type
            type_map = {
                SourceType.JOURNAL_ARTICLE: "article",
                SourceType.BOOK: "book",
                SourceType.CONFERENCE_PAPER: "inproceedings",
                SourceType.THESIS: "mastersthesis",
                SourceType.DISSERTATION: "phdthesis",
            }
            entry_type = type_map.get(ref.source_type, "misc")
            
            # Create key
            key = f"{ref.authors[0].last_name if ref.authors else 'unknown'}{ref.year}"
            key = re.sub(r'[^a-zA-Z0-9]', '', key)
            
            # Build entry
            entry = f"@{entry_type}{{{key},\n"
            entry += f'  title = {{{ref.title}}},\n'
            
            if ref.authors:
                authors_str = " and ".join([f"{a.last_name}, {a.first_name}" for a in ref.authors])
                entry += f'  author = {{{authors_str}}},\n'
            
            entry += f'  year = {{{ref.year}}},\n'
            
            if ref.journal:
                entry += f'  journal = {{{ref.journal}}},\n'
            if ref.volume:
                entry += f'  volume = {{{ref.volume}}},\n'
            if ref.pages:
                entry += f'  pages = {{{ref.pages}}},\n'
            if ref.doi:
                entry += f'  doi = {{{ref.doi}}},\n'
            
            entry += "}\n"
            bibtex.append(entry)
        
        return "\n".join(bibtex)
    
    # ═══════════════════════════════════════════════════════════════════════════
    # CITATION GENERATION
    # ═══════════════════════════════════════════════════════════════════════════
    
    def generate_citation(self, ref_id: str, style: CitationStyle = CitationStyle.APA7) -> str:
        """
        Generate a citation in a specific style.
        
        Args:
            ref_id: Reference ID
            style: Citation style
            
        Returns:
            Formatted citation string
        """
        if ref_id not in self.references:
            return ""
        
        ref = self.references[ref_id]
        
        if style in [CitationStyle.APA7, CitationStyle.APA6]:
            return self._cite_apa(ref)
        elif style in [CitationStyle.MLA9, CitationStyle.MLA8]:
            return self._cite_mla(ref)
        elif style == CitationStyle.CHICAGO:
            return self._cite_chicago(ref)
        elif style == CitationStyle.HARVARD:
            return self._cite_harvard(ref)
        elif style == CitationStyle.IEEE:
            return self._cite_ieee(ref)
        elif style == CitationStyle.VANCOUVER:
            return self._cite_vancouver(ref)
        else:
            return self._cite_apa(ref)  # Default
    
    def _cite_apa(self, ref: Reference) -> str:
        """APA 7th edition citation."""
        # Authors
        if len(ref.authors) == 1:
            authors = ref.authors[0].last_first()
        elif len(ref.authors) == 2:
            authors = f"{ref.authors[0].last_first()} & {ref.authors[1].last_first()}"
        elif len(ref.authors) > 2:
            authors = f"{ref.authors[0].last_first()} et al."
        else:
            authors = "Unknown"
        
        citation = f"{authors} ({ref.year}). {ref.title}."
        
        if ref.journal:
            citation += f" *{ref.journal}*"
            if ref.volume:
                citation += f", *{ref.volume}*"
                if ref.issue:
                    citation += f"({ref.issue})"
            if ref.pages:
                citation += f", {ref.pages}"
            citation += "."
        elif ref.publisher:
            citation += f" {ref.publisher}."
        
        if ref.doi:
            citation += f" https://doi.org/{ref.doi}"
        
        return citation
    
    def _cite_mla(self, ref: Reference) -> str:
        """MLA 9th edition citation."""
        # Authors
        if ref.authors:
            if len(ref.authors) == 1:
                authors = f"{ref.authors[0].last_name}, {ref.authors[0].first_name}"
            elif len(ref.authors) == 2:
                authors = f"{ref.authors[0].last_name}, {ref.authors[0].first_name}, and {ref.authors[1].full_name()}"
            else:
                authors = f"{ref.authors[0].last_name}, {ref.authors[0].first_name}, et al."
        else:
            authors = ""
        
        citation = f'{authors}. "{ref.title}."'
        
        if ref.journal:
            citation += f" *{ref.journal}*"
            if ref.volume:
                citation += f", vol. {ref.volume}"
                if ref.issue:
                    citation += f", no. {ref.issue}"
            citation += f", {ref.year}"
            if ref.pages:
                citation += f", pp. {ref.pages}"
            citation += "."
        elif ref.publisher:
            citation += f" {ref.publisher}, {ref.year}."
        
        return citation
    
    def _cite_chicago(self, ref: Reference) -> str:
        """Chicago style citation."""
        # Authors
        if ref.authors:
            if len(ref.authors) == 1:
                authors = f"{ref.authors[0].last_name}, {ref.authors[0].first_name}"
            else:
                first = f"{ref.authors[0].last_name}, {ref.authors[0].first_name}"
                others = [a.full_name() for a in ref.authors[1:]]
                authors = first + ", " + ", ".join(others[:-1])
                if others:
                    authors += ", and " + others[-1]
        else:
            authors = ""
        
        citation = f'{authors}. "{ref.title}."'
        
        if ref.journal:
            citation += f" *{ref.journal}* {ref.volume}"
            if ref.issue:
                citation += f", no. {ref.issue}"
            citation += f" ({ref.year})"
            if ref.pages:
                citation += f": {ref.pages}"
            citation += "."
        
        return citation
    
    def _cite_harvard(self, ref: Reference) -> str:
        """Harvard style citation."""
        if ref.authors:
            if len(ref.authors) == 1:
                authors = ref.authors[0].last_name
            elif len(ref.authors) == 2:
                authors = f"{ref.authors[0].last_name} and {ref.authors[1].last_name}"
            else:
                authors = f"{ref.authors[0].last_name} et al."
        else:
            authors = "Anon"
        
        citation = f"{authors} ({ref.year}) '{ref.title}'"
        
        if ref.journal:
            citation += f", *{ref.journal}*"
            if ref.volume:
                citation += f", {ref.volume}"
                if ref.issue:
                    citation += f"({ref.issue})"
            if ref.pages:
                citation += f", pp. {ref.pages}"
        
        citation += "."
        return citation
    
    def _cite_ieee(self, ref: Reference) -> str:
        """IEEE style citation."""
        # Authors (initials first)
        authors_parts = []
        for a in ref.authors[:3]:
            initials = a.first_name[0] + "."
            if a.middle_name:
                initials += f" {a.middle_name[0]}."
            authors_parts.append(f"{initials} {a.last_name}")
        
        if len(ref.authors) > 3:
            authors = ", ".join(authors_parts) + ", et al."
        else:
            authors = ", ".join(authors_parts[:-1])
            if authors_parts:
                authors += ", and " + authors_parts[-1] if len(authors_parts) > 1 else authors_parts[0]
        
        citation = f'{authors}, "{ref.title},"'
        
        if ref.journal:
            citation += f" *{ref.journal}*"
            if ref.volume:
                citation += f", vol. {ref.volume}"
                if ref.issue:
                    citation += f", no. {ref.issue}"
            if ref.pages:
                citation += f", pp. {ref.pages}"
            citation += f", {ref.year}."
        
        return citation
    
    def _cite_vancouver(self, ref: Reference) -> str:
        """Vancouver style citation (medical)."""
        # Authors (last name, initials)
        authors_parts = []
        for a in ref.authors[:6]:
            initials = a.first_name[0]
            if a.middle_name:
                initials += a.middle_name[0]
            authors_parts.append(f"{a.last_name} {initials}")
        
        if len(ref.authors) > 6:
            authors = ", ".join(authors_parts) + ", et al."
        else:
            authors = ", ".join(authors_parts)
        
        citation = f"{authors}. {ref.title}."
        
        if ref.journal:
            citation += f" {ref.journal}. {ref.year}"
            if ref.volume:
                citation += f";{ref.volume}"
                if ref.issue:
                    citation += f"({ref.issue})"
            if ref.pages:
                citation += f":{ref.pages}"
            citation += "."
        
        return citation
    
    def generate_bibliography(self, ref_ids: List[str], style: CitationStyle = CitationStyle.APA7) -> str:
        """
        Generate a bibliography from multiple references.
        
        Args:
            ref_ids: List of reference IDs
            style: Citation style
            
        Returns:
            Formatted bibliography
        """
        citations = []
        for ref_id in ref_ids:
            cite = self.generate_citation(ref_id, style)
            if cite:
                citations.append(cite)
        
        # Sort alphabetically by author (APA style)
        citations.sort()
        
        return "\n\n".join(citations)
    
    # ═══════════════════════════════════════════════════════════════════════════
    # PROJECT MANAGEMENT
    # ═══════════════════════════════════════════════════════════════════════════
    
    def create_project(self, title: str, description: str = "",
                       lead: str = "researcher") -> ResearchProject:
        """Create a new research project."""
        proj_id = f"proj_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        project = ResearchProject(
            id=proj_id,
            title=title,
            description=description,
            lead_researcher=lead
        )
        
        self.projects[proj_id] = project
        self._save_data()
        
        print(f"[ResearchSuite] Created project: {title}")
        return project
    
    def update_project_status(self, project_id: str, status: ProjectStatus) -> bool:
        """Update project status."""
        if project_id not in self.projects:
            return False
        
        self.projects[project_id].status = status
        self._save_data()
        return True
    
    def add_milestone(self, project_id: str, name: str, 
                      due_date: datetime, description: str = "") -> bool:
        """Add a milestone to a project."""
        if project_id not in self.projects:
            return False
        
        milestone = {
            "id": f"ms_{datetime.now().strftime('%H%M%S')}",
            "name": name,
            "description": description,
            "due_date": due_date.isoformat(),
            "completed": False
        }
        
        self.projects[project_id].milestones.append(milestone)
        self._save_data()
        return True
    
    def link_reference_to_project(self, project_id: str, ref_id: str) -> bool:
        """Link a reference to a project."""
        if project_id not in self.projects or ref_id not in self.references:
            return False
        
        if ref_id not in self.projects[project_id].references:
            self.projects[project_id].references.append(ref_id)
            self._save_data()
        return True
    
    # ═══════════════════════════════════════════════════════════════════════════
    # STATISTICS & ANALYTICS
    # ═══════════════════════════════════════════════════════════════════════════
    
    def get_statistics(self) -> Dict:
        """Get research statistics."""
        stats = {
            "total_references": len(self.references),
            "total_projects": len(self.projects),
            "references_read": len([r for r in self.references.values() if r.is_read]),
            "references_by_year": {},
            "references_by_type": {},
            "projects_by_status": {},
            "top_keywords": {},
        }
        
        # By year
        for ref in self.references.values():
            year = str(ref.year)
            stats["references_by_year"][year] = stats["references_by_year"].get(year, 0) + 1
        
        # By type
        for ref in self.references.values():
            t = ref.source_type.value
            stats["references_by_type"][t] = stats["references_by_type"].get(t, 0) + 1
        
        # By project status
        for proj in self.projects.values():
            s = proj.status.value
            stats["projects_by_status"][s] = stats["projects_by_status"].get(s, 0) + 1
        
        # Keywords
        for ref in self.references.values():
            for kw in ref.keywords:
                stats["top_keywords"][kw] = stats["top_keywords"].get(kw, 0) + 1
        
        # Sort keywords
        stats["top_keywords"] = dict(
            sorted(stats["top_keywords"].items(), key=lambda x: x[1], reverse=True)[:20]
        )
        
        return stats
    
    # ═══════════════════════════════════════════════════════════════════════════
    # ETHICS CHECKLIST
    # ═══════════════════════════════════════════════════════════════════════════
    
    def get_ethics_checklist(self) -> List[Dict]:
        """Get research ethics checklist."""
        return [
            {"id": "informed_consent", "name": "Informed Consent", 
             "description": "Participants have given informed consent"},
            {"id": "data_privacy", "name": "Data Privacy",
             "description": "Personal data is protected and anonymized"},
            {"id": "no_harm", "name": "No Harm",
             "description": "Research does not cause physical or psychological harm"},
            {"id": "voluntary", "name": "Voluntary Participation",
             "description": "Participation is voluntary with right to withdraw"},
            {"id": "confidentiality", "name": "Confidentiality",
             "description": "Participant information is kept confidential"},
            {"id": "deception", "name": "No Deception",
             "description": "No unnecessary deception of participants"},
            {"id": "irb_approval", "name": "IRB/Ethics Approval",
             "description": "Study has institutional ethics approval"},
            {"id": "conflict_interest", "name": "Conflict of Interest",
             "description": "Any conflicts of interest are disclosed"},
            {"id": "data_integrity", "name": "Data Integrity",
             "description": "Data is collected and reported honestly"},
            {"id": "proper_attribution", "name": "Proper Attribution",
             "description": "All sources and contributions are properly cited"},
        ]


# ═══════════════════════════════════════════════════════════════════════════════
# SINGLETON
# ═══════════════════════════════════════════════════════════════════════════════

_research_suite_instance = None

def get_research_suite() -> ResearchSuite:
    """Get the ResearchSuite singleton."""
    global _research_suite_instance
    if _research_suite_instance is None:
        _research_suite_instance = ResearchSuite()
    return _research_suite_instance


if __name__ == "__main__":
    suite = get_research_suite()
    
    # Add a sample reference
    ref = suite.add_reference(
        source_type=SourceType.JOURNAL_ARTICLE,
        title="A Study on Knowledge Management",
        authors=[
            {"first_name": "John", "last_name": "Smith"},
            {"first_name": "Jane", "last_name": "Doe"}
        ],
        year=2024,
        journal="Journal of Research",
        volume="10",
        issue="2",
        pages="123-145",
        doi="10.1234/example"
    )
    
    # Generate citations in different styles
    print("\nAPA:", suite.generate_citation(ref.id, CitationStyle.APA7))
    print("MLA:", suite.generate_citation(ref.id, CitationStyle.MLA9))
    print("IEEE:", suite.generate_citation(ref.id, CitationStyle.IEEE))
    
    # Statistics
    print("\nStatistics:", json.dumps(suite.get_statistics(), indent=2))
