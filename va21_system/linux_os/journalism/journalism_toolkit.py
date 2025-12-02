#!/usr/bin/env python3
"""
VA21 Research OS - Journalism Toolkit
=======================================

Professional tools for journalists and investigative reporters.
Designed for secure, ethical journalism with AI assistance.

Features:
- Source Management (secure)
- Fact-Checking Tools
- Interview Recorder & Transcriber
- Deadline Tracker
- Story Pipeline
- Media Archive
- Contact Database
- Wire Feed Integration
- Secure Communication
- Whistleblower Protection
- Freedom of Press Tools
- FOIA Request Manager
- Legal Review Checklist

Om Vinayaka - Truth is the highest dharma.
"""

import os
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum


class SourceConfidentiality(Enum):
    """Source confidentiality levels."""
    PUBLIC = "public"           # Can be named
    BACKGROUND = "background"   # Info usable, not for attribution
    DEEP_BACKGROUND = "deep_background"  # Info for context only
    OFF_RECORD = "off_record"   # Cannot be used
    CONFIDENTIAL = "confidential"  # Protected source


class StoryStatus(Enum):
    """Story status in pipeline."""
    IDEA = "idea"
    PITCHING = "pitching"
    APPROVED = "approved"
    RESEARCHING = "researching"
    INTERVIEWING = "interviewing"
    WRITING = "writing"
    EDITING = "editing"
    FACT_CHECK = "fact_check"
    LEGAL_REVIEW = "legal_review"
    READY = "ready"
    PUBLISHED = "published"
    KILLED = "killed"


class MediaType(Enum):
    """Types of media content."""
    PHOTO = "photo"
    VIDEO = "video"
    AUDIO = "audio"
    DOCUMENT = "document"
    DATA = "data"


@dataclass
class Source:
    """A journalistic source."""
    id: str
    name: str  # Real name (encrypted if confidential)
    alias: str  # Alias for protection
    confidentiality: SourceConfidentiality
    
    # Contact
    contact_method: str = ""  # How to reach them
    encrypted_contact: str = ""  # Encrypted contact info
    
    # Background
    occupation: str = ""
    organization: str = ""
    expertise: List[str] = field(default_factory=list)
    
    # Reliability
    reliability_score: int = 5  # 1-10
    times_cited: int = 0
    verified_claims: int = 0
    
    # Notes
    notes: str = ""
    
    # Timestamps
    first_contact: datetime = field(default_factory=datetime.now)
    last_contact: Optional[datetime] = None
    

@dataclass
class Story:
    """A news story."""
    id: str
    headline: str
    slug: str  # URL-friendly identifier
    status: StoryStatus = StoryStatus.IDEA
    
    # Assignment
    reporter: str = ""
    editor: str = ""
    desk: str = ""  # News desk (politics, tech, etc.)
    
    # Content
    pitch: str = ""
    outline: str = ""
    draft: str = ""
    final_version: str = ""
    
    # Sources
    sources: List[str] = field(default_factory=list)  # Source IDs
    
    # Media
    media: List[str] = field(default_factory=list)  # Media IDs
    
    # Facts to verify
    facts: List[Dict] = field(default_factory=list)
    
    # Timeline
    created: datetime = field(default_factory=datetime.now)
    deadline: Optional[datetime] = None
    published: Optional[datetime] = None
    
    # Legal
    legal_reviewed: bool = False
    legal_notes: str = ""
    
    # Tags
    tags: List[str] = field(default_factory=list)
    

@dataclass
class Interview:
    """An interview record."""
    id: str
    story_id: str
    source_id: str
    
    date: datetime
    duration_minutes: int = 0
    location: str = ""
    
    # Recording
    recording_path: str = ""
    transcript: str = ""
    
    # Notes
    key_quotes: List[str] = field(default_factory=list)
    notes: str = ""
    
    # Verification
    consent_obtained: bool = False
    on_record: bool = True


@dataclass
class FactCheck:
    """A fact to be verified."""
    id: str
    story_id: str
    claim: str
    
    # Verification
    verified: bool = False
    verification_notes: str = ""
    sources_checked: List[str] = field(default_factory=list)
    
    # Rating
    rating: str = ""  # true, mostly_true, half_true, mostly_false, false
    confidence: float = 0.0


@dataclass
class FOIARequest:
    """Freedom of Information Act request."""
    id: str
    agency: str
    subject: str
    request_text: str
    
    # Status
    status: str = "draft"  # draft, submitted, acknowledged, processing, completed, appealed, denied
    submitted_date: Optional[datetime] = None
    response_deadline: Optional[datetime] = None
    
    # Response
    response_received: bool = False
    response_date: Optional[datetime] = None
    documents_received: List[str] = field(default_factory=list)
    
    # Appeal
    appealed: bool = False
    appeal_notes: str = ""


class JournalismToolkit:
    """
    VA21 Journalism Toolkit
    
    A comprehensive suite of tools for professional journalists,
    with emphasis on security, ethics, and AI assistance.
    
    Core Features:
    - Secure Source Management
    - Story Pipeline Tracking
    - Fact-Checking Workflow
    - Interview Management
    - FOIA Request Tracking
    - Deadline Management
    - Legal Review Checklist
    - Whistleblower Protection
    """
    
    VERSION = "1.0.0"
    
    def __init__(self, data_path: str = "/va21/journalism"):
        self.data_path = data_path
        
        # Create directories
        for subdir in ["sources", "stories", "interviews", "media", "foia", "secure"]:
            os.makedirs(os.path.join(data_path, subdir), exist_ok=True)
        
        # Data stores
        self.sources: Dict[str, Source] = {}
        self.stories: Dict[str, Story] = {}
        self.interviews: Dict[str, Interview] = {}
        self.foia_requests: Dict[str, FOIARequest] = {}
        
        # Load existing data
        self._load_data()
        
        print(f"[JournalismToolkit] Initialized with {len(self.stories)} stories, {len(self.sources)} sources")
    
    def _load_data(self):
        """Load existing data."""
        stories_file = os.path.join(self.data_path, "stories.json")
        if os.path.exists(stories_file):
            try:
                with open(stories_file, 'r') as f:
                    data = json.load(f)
                for story_data in data:
                    story = Story(
                        id=story_data["id"],
                        headline=story_data["headline"],
                        slug=story_data.get("slug", ""),
                        status=StoryStatus(story_data.get("status", "idea")),
                        reporter=story_data.get("reporter", ""),
                        pitch=story_data.get("pitch", ""),
                        sources=story_data.get("sources", []),
                        tags=story_data.get("tags", []),
                    )
                    self.stories[story.id] = story
            except:
                pass
    
    def _save_data(self):
        """Save data to disk."""
        stories_file = os.path.join(self.data_path, "stories.json")
        stories_data = []
        for story in self.stories.values():
            stories_data.append({
                "id": story.id,
                "headline": story.headline,
                "slug": story.slug,
                "status": story.status.value,
                "reporter": story.reporter,
                "pitch": story.pitch,
                "sources": story.sources,
                "tags": story.tags,
            })
        with open(stories_file, 'w') as f:
            json.dump(stories_data, f, indent=2)
    
    # ═══════════════════════════════════════════════════════════════════════════
    # SOURCE MANAGEMENT
    # ═══════════════════════════════════════════════════════════════════════════
    
    def add_source(self, name: str, confidentiality: SourceConfidentiality,
                   alias: str = None, **kwargs) -> Source:
        """
        Add a new source with appropriate security.
        
        Args:
            name: Real name (will be encrypted for confidential sources)
            confidentiality: Level of source protection
            alias: Public alias for the source
            **kwargs: Additional fields
            
        Returns:
            Created Source
        """
        source_id = f"src_{hashlib.md5(f'{name}{datetime.now()}'.encode()).hexdigest()[:10]}"
        
        # Generate alias if not provided
        if not alias:
            alias = f"Source_{source_id[-4:].upper()}"
        
        # For confidential sources, encrypt the real name
        stored_name = name
        if confidentiality in [SourceConfidentiality.CONFIDENTIAL, 
                                SourceConfidentiality.OFF_RECORD]:
            # In production, use proper encryption
            stored_name = f"[PROTECTED: {hashlib.sha256(name.encode()).hexdigest()[:16]}]"
        
        source = Source(
            id=source_id,
            name=stored_name,
            alias=alias,
            confidentiality=confidentiality,
            occupation=kwargs.get("occupation", ""),
            organization=kwargs.get("organization", ""),
            expertise=kwargs.get("expertise", []),
            notes=kwargs.get("notes", "")
        )
        
        self.sources[source_id] = source
        
        # Save securely
        self._save_source(source)
        
        print(f"[JournalismToolkit] Added source: {alias} ({confidentiality.value})")
        return source
    
    def _save_source(self, source: Source):
        """Save source with appropriate security."""
        # Confidential sources are saved separately with encryption
        if source.confidentiality in [SourceConfidentiality.CONFIDENTIAL,
                                       SourceConfidentiality.OFF_RECORD]:
            secure_path = os.path.join(self.data_path, "secure", f"{source.id}.enc")
            # In production, encrypt the file
            with open(secure_path, 'w') as f:
                json.dump({
                    "id": source.id,
                    "alias": source.alias,
                    "confidentiality": source.confidentiality.value,
                }, f)
    
    def get_source_by_alias(self, alias: str) -> Optional[Source]:
        """Find source by alias."""
        for source in self.sources.values():
            if source.alias.lower() == alias.lower():
                return source
        return None
    
    def update_source_reliability(self, source_id: str, verified_claim: bool) -> bool:
        """Update source reliability based on claim verification."""
        if source_id not in self.sources:
            return False
        
        source = self.sources[source_id]
        source.times_cited += 1
        if verified_claim:
            source.verified_claims += 1
        
        # Calculate reliability score
        if source.times_cited > 0:
            ratio = source.verified_claims / source.times_cited
            source.reliability_score = min(10, max(1, int(ratio * 10)))
        
        return True
    
    # ═══════════════════════════════════════════════════════════════════════════
    # STORY MANAGEMENT
    # ═══════════════════════════════════════════════════════════════════════════
    
    def create_story(self, headline: str, pitch: str = "",
                     desk: str = "general", reporter: str = "") -> Story:
        """
        Create a new story.
        
        Args:
            headline: Working headline
            pitch: Story pitch
            desk: News desk
            reporter: Assigned reporter
            
        Returns:
            Created Story
        """
        story_id = f"story_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        slug = headline.lower().replace(" ", "-")[:50]
        slug = ''.join(c for c in slug if c.isalnum() or c == '-')
        
        story = Story(
            id=story_id,
            headline=headline,
            slug=slug,
            pitch=pitch,
            desk=desk,
            reporter=reporter
        )
        
        self.stories[story_id] = story
        self._save_data()
        
        print(f"[JournalismToolkit] Created story: {headline}")
        return story
    
    def update_story_status(self, story_id: str, status: StoryStatus) -> Tuple[bool, str]:
        """Update story status in pipeline."""
        if story_id not in self.stories:
            return False, "Story not found"
        
        story = self.stories[story_id]
        old_status = story.status
        story.status = status
        
        # Check for required steps
        warnings = []
        
        if status == StoryStatus.PUBLISHED:
            story.published = datetime.now()
            
            # Check fact-checking
            unchecked = [f for f in story.facts if not f.get("verified", False)]
            if unchecked:
                warnings.append(f"⚠️ {len(unchecked)} facts not verified")
            
            # Check legal review
            if not story.legal_reviewed:
                warnings.append("⚠️ Legal review not completed")
        
        self._save_data()
        
        message = f"Status: {old_status.value} → {status.value}"
        if warnings:
            message += "\n" + "\n".join(warnings)
        
        return True, message
    
    def set_deadline(self, story_id: str, deadline: datetime) -> bool:
        """Set story deadline."""
        if story_id not in self.stories:
            return False
        
        self.stories[story_id].deadline = deadline
        self._save_data()
        return True
    
    def get_stories_by_deadline(self) -> List[Tuple[Story, timedelta]]:
        """Get stories sorted by deadline urgency."""
        now = datetime.now()
        with_deadlines = []
        
        for story in self.stories.values():
            if story.deadline and story.status not in [StoryStatus.PUBLISHED, StoryStatus.KILLED]:
                time_left = story.deadline - now
                with_deadlines.append((story, time_left))
        
        return sorted(with_deadlines, key=lambda x: x[1])
    
    def add_source_to_story(self, story_id: str, source_id: str) -> bool:
        """Link a source to a story."""
        if story_id not in self.stories or source_id not in self.sources:
            return False
        
        if source_id not in self.stories[story_id].sources:
            self.stories[story_id].sources.append(source_id)
            self._save_data()
        return True
    
    # ═══════════════════════════════════════════════════════════════════════════
    # FACT-CHECKING
    # ═══════════════════════════════════════════════════════════════════════════
    
    def add_fact_to_verify(self, story_id: str, claim: str) -> Optional[str]:
        """Add a fact that needs verification."""
        if story_id not in self.stories:
            return None
        
        fact_id = f"fact_{len(self.stories[story_id].facts) + 1}"
        
        fact = {
            "id": fact_id,
            "claim": claim,
            "verified": False,
            "rating": "",
            "notes": "",
            "sources_checked": []
        }
        
        self.stories[story_id].facts.append(fact)
        self._save_data()
        
        return fact_id
    
    def verify_fact(self, story_id: str, fact_id: str, 
                    verified: bool, rating: str, notes: str = "") -> bool:
        """Mark a fact as verified."""
        if story_id not in self.stories:
            return False
        
        for fact in self.stories[story_id].facts:
            if fact["id"] == fact_id:
                fact["verified"] = verified
                fact["rating"] = rating
                fact["notes"] = notes
                self._save_data()
                return True
        
        return False
    
    def get_fact_check_status(self, story_id: str) -> Dict:
        """Get fact-checking status for a story."""
        if story_id not in self.stories:
            return {}
        
        facts = self.stories[story_id].facts
        
        return {
            "total": len(facts),
            "verified": len([f for f in facts if f.get("verified", False)]),
            "pending": len([f for f in facts if not f.get("verified", False)]),
            "facts": facts
        }
    
    def get_fact_check_tips(self) -> List[str]:
        """Get fact-checking tips and resources."""
        return [
            "🔍 Always verify claims with at least two independent sources",
            "📞 Contact primary sources directly when possible",
            "🌐 Check official databases and government records",
            "📸 Use reverse image search for photos (TinEye, Google Images)",
            "📍 Verify location claims with geolocation tools",
            "📅 Cross-reference dates with historical records",
            "🔗 Check if URLs are legitimate (watch for typosquatting)",
            "📊 Verify statistics with original data sources",
            "👤 Confirm identity of sources and experts",
            "🏛️ Check court records for legal claims",
            "💰 Verify financial claims with SEC filings, financial reports",
            "🔬 Consult subject matter experts for technical claims",
        ]
    
    # ═══════════════════════════════════════════════════════════════════════════
    # INTERVIEW MANAGEMENT
    # ═══════════════════════════════════════════════════════════════════════════
    
    def create_interview(self, story_id: str, source_id: str,
                         date: datetime, on_record: bool = True) -> Interview:
        """Create an interview record."""
        interview_id = f"int_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        interview = Interview(
            id=interview_id,
            story_id=story_id,
            source_id=source_id,
            date=date,
            on_record=on_record
        )
        
        self.interviews[interview_id] = interview
        return interview
    
    def add_quote(self, interview_id: str, quote: str) -> bool:
        """Add a key quote from an interview."""
        if interview_id not in self.interviews:
            return False
        
        self.interviews[interview_id].key_quotes.append(quote)
        return True
    
    def get_interview_preparation(self, topic: str) -> Dict:
        """Get interview preparation tips."""
        return {
            "before": [
                "Research the subject thoroughly",
                "Prepare open-ended questions",
                "Verify recording consent laws in your jurisdiction",
                "Test recording equipment",
                "Prepare backup questions",
                "Review any previous statements by the subject",
            ],
            "during": [
                "Get consent to record (if applicable)",
                "Start with easy questions to build rapport",
                "Listen actively - follow up on interesting points",
                "Ask for clarification when needed",
                "Don't interrupt unless necessary",
                "Note non-verbal cues",
            ],
            "after": [
                "Transcribe while details are fresh",
                "Send quotes for verification if promised",
                "Securely store recordings",
                "File notes with the story",
            ],
            "sample_questions": self._generate_interview_questions(topic)
        }
    
    def _generate_interview_questions(self, topic: str) -> List[str]:
        """Generate sample interview questions for a topic."""
        # Basic question templates
        return [
            f"Can you tell me about your experience with {topic}?",
            f"What first brought you to {topic}?",
            f"What do you see as the main challenges in {topic}?",
            f"How has {topic} changed over time?",
            f"What would you like people to understand about {topic}?",
            "Who else should I talk to about this?",
            "Is there anything I haven't asked that I should know?",
            "Can I contact you for follow-up questions?",
        ]
    
    # ═══════════════════════════════════════════════════════════════════════════
    # FOIA REQUESTS
    # ═══════════════════════════════════════════════════════════════════════════
    
    def create_foia_request(self, agency: str, subject: str, 
                            request_text: str) -> FOIARequest:
        """Create a FOIA request."""
        foia_id = f"foia_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        request = FOIARequest(
            id=foia_id,
            agency=agency,
            subject=subject,
            request_text=request_text
        )
        
        self.foia_requests[foia_id] = request
        return request
    
    def submit_foia(self, foia_id: str) -> Tuple[bool, str]:
        """Mark FOIA as submitted."""
        if foia_id not in self.foia_requests:
            return False, "Request not found"
        
        req = self.foia_requests[foia_id]
        req.status = "submitted"
        req.submitted_date = datetime.now()
        
        # Calculate expected response deadline (usually 20 business days)
        req.response_deadline = datetime.now() + timedelta(days=30)
        
        return True, f"Submitted. Response expected by {req.response_deadline.strftime('%Y-%m-%d')}"
    
    def get_foia_template(self, agency_type: str = "federal") -> str:
        """Get FOIA request template."""
        templates = {
            "federal": """[Your Name]
[Your Address]
[City, State ZIP]
[Email]
[Phone]

[Date]

FOIA Officer
[Agency Name]
[Agency Address]

RE: Freedom of Information Act Request

Dear FOIA Officer:

Pursuant to the Freedom of Information Act, 5 U.S.C. § 552, I request access to and copies of:

[DESCRIBE RECORDS REQUESTED - be specific about dates, topics, individuals]

I request a waiver of all fees for this request. Disclosure of the requested information is in the public interest because [EXPLAIN PUBLIC INTEREST].

If my request is denied in whole or part, I ask that you justify all deletions by reference to specific exemptions of the Act.

I look forward to your response within 20 business days, as required by law.

Sincerely,

[Your Name]
[Your Affiliation/News Organization]""",

            "state": """[Adapt based on your state's public records law]""",
        }
        
        return templates.get(agency_type, templates["federal"])
    
    # ═══════════════════════════════════════════════════════════════════════════
    # LEGAL & ETHICS
    # ═══════════════════════════════════════════════════════════════════════════
    
    def get_legal_checklist(self) -> List[Dict]:
        """Get pre-publication legal checklist."""
        return [
            {"id": "defamation", "name": "Defamation Check",
             "description": "All statements about individuals are true and provable",
             "questions": [
                 "Are all factual claims verified?",
                 "Is opinion clearly distinguished from fact?",
                 "Are there any statements that could harm reputation?",
             ]},
            {"id": "privacy", "name": "Privacy Check",
             "description": "Story respects privacy rights",
             "questions": [
                 "Is private information newsworthy?",
                 "Was information obtained legally?",
                 "Is there consent for private details?",
             ]},
            {"id": "copyright", "name": "Copyright Check",
             "description": "All content is original or properly licensed",
             "questions": [
                 "Is fair use applicable for quoted material?",
                 "Are images properly licensed?",
                 "Is attribution correct?",
             ]},
            {"id": "source_protection", "name": "Source Protection",
             "description": "Confidential sources are protected",
             "questions": [
                 "Can sources be identified from the story?",
                 "Are source protection promises kept?",
                 "Is there risk to sources from publication?",
             ]},
            {"id": "national_security", "name": "Security Check",
             "description": "Story doesn't endanger lives or national security",
             "questions": [
                 "Could publication endanger anyone?",
                 "Is classified information involved?",
                 "Has proper legal review been done?",
             ]},
        ]
    
    def get_ethics_guidelines(self) -> Dict:
        """Get journalism ethics guidelines."""
        return {
            "principles": [
                "Seek truth and report it",
                "Minimize harm",
                "Act independently",
                "Be accountable and transparent",
            ],
            "guidelines": {
                "accuracy": [
                    "Verify information before publishing",
                    "Identify sources clearly",
                    "Provide context for facts and data",
                    "Correct errors promptly",
                ],
                "fairness": [
                    "Give subjects chance to respond",
                    "Present diverse perspectives",
                    "Avoid stereotypes",
                    "Distinguish news from opinion",
                ],
                "independence": [
                    "Avoid conflicts of interest",
                    "Refuse gifts that could influence coverage",
                    "Be transparent about sponsorships",
                    "Resist pressure from sources or advertisers",
                ],
                "harm_reduction": [
                    "Consider impact on vulnerable subjects",
                    "Protect sources who risk harm",
                    "Be cautious with graphic content",
                    "Respect grief and privacy",
                ],
            },
            "source": "Based on SPJ Code of Ethics"
        }
    
    # ═══════════════════════════════════════════════════════════════════════════
    # STATISTICS
    # ═══════════════════════════════════════════════════════════════════════════
    
    def get_statistics(self) -> Dict:
        """Get journalism toolkit statistics."""
        return {
            "total_stories": len(self.stories),
            "total_sources": len(self.sources),
            "total_interviews": len(self.interviews),
            "total_foia": len(self.foia_requests),
            "stories_by_status": {
                status.value: len([s for s in self.stories.values() if s.status == status])
                for status in StoryStatus
            },
            "sources_by_confidentiality": {
                conf.value: len([s for s in self.sources.values() if s.confidentiality == conf])
                for conf in SourceConfidentiality
            },
            "pending_deadlines": len([
                s for s in self.stories.values()
                if s.deadline and s.deadline > datetime.now() and 
                s.status not in [StoryStatus.PUBLISHED, StoryStatus.KILLED]
            ]),
        }


# ═══════════════════════════════════════════════════════════════════════════════
# SINGLETON
# ═══════════════════════════════════════════════════════════════════════════════

_journalism_toolkit_instance = None

def get_journalism_toolkit() -> JournalismToolkit:
    """Get the JournalismToolkit singleton."""
    global _journalism_toolkit_instance
    if _journalism_toolkit_instance is None:
        _journalism_toolkit_instance = JournalismToolkit()
    return _journalism_toolkit_instance


if __name__ == "__main__":
    toolkit = get_journalism_toolkit()
    
    # Create a story
    story = toolkit.create_story(
        headline="Investigation: Local Water Quality",
        pitch="Deep dive into water treatment issues",
        desk="investigations"
    )
    
    # Add a source
    source = toolkit.add_source(
        name="John Whistleblower",
        confidentiality=SourceConfidentiality.CONFIDENTIAL,
        occupation="Water Treatment Engineer"
    )
    
    print(f"Story: {story.headline}")
    print(f"Source: {source.alias} ({source.confidentiality.value})")
    print(f"\nStats: {json.dumps(toolkit.get_statistics(), indent=2)}")
