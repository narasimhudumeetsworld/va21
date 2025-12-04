#!/usr/bin/env python3
"""
VA21 OS - Coding IDE Suggestion Engine
=======================================

Om Vinayaka - Intelligent guidance for your development journey.

The Suggest Engine analyzes user requirements and provides:
- Best programming language recommendations based on:
  - Target operating system compatibility
  - Application type and requirements
  - Performance needs
  - Development speed requirements
  - Team expertise (if specified)
- System architecture recommendations
- Technology stack suggestions
- Build tool and framework recommendations

This engine integrates with the AI helper and SearXNG to search
for best practices and current language/framework popularity.

Copyright (c) 2024-2025 Prayaga Vaibhav. All rights reserved.
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum


class TargetOS(Enum):
    """Target operating system for the application."""
    WINDOWS = "windows"
    MACOS = "macos"
    LINUX = "linux"
    ANDROID = "android"
    IOS = "ios"
    WEB = "web"
    CROSS_PLATFORM = "cross_platform"
    EMBEDDED = "embedded"
    VA21_OS = "va21_os"


class AppType(Enum):
    """Type of application to build."""
    WEB_APP = "web_app"
    MOBILE_APP = "mobile_app"
    DESKTOP_APP = "desktop_app"
    CLI_TOOL = "cli_tool"
    API_SERVICE = "api_service"
    GAME = "game"
    DATA_SCIENCE = "data_science"
    ML_AI = "ml_ai"
    SYSTEM_TOOL = "system_tool"
    AUTOMATION = "automation"
    IOT = "iot"
    BLOCKCHAIN = "blockchain"


class Priority(Enum):
    """Development priority."""
    PERFORMANCE = "performance"
    SPEED = "development_speed"
    MAINTAINABILITY = "maintainability"
    SCALABILITY = "scalability"
    SECURITY = "security"


@dataclass
class LanguageSuggestion:
    """A programming language suggestion with reasoning."""
    language: str
    score: float  # 0-100
    reasons: List[str]
    frameworks: List[str]
    build_tools: List[str]
    pros: List[str]
    cons: List[str]
    learning_curve: str  # easy, moderate, steep
    ecosystem_maturity: str  # emerging, growing, mature, established
    compatible_os: List[str]


@dataclass
class StackSuggestion:
    """A complete technology stack suggestion."""
    name: str
    frontend: Optional[str]
    backend: Optional[str]
    database: Optional[str]
    languages: List[str]
    frameworks: List[str]
    reasoning: str
    score: float
    best_for: List[str]


@dataclass
class ProjectRequirements:
    """Parsed project requirements from user input."""
    description: str
    app_type: Optional[AppType]
    target_os: List[TargetOS]
    priorities: List[Priority]
    features: List[str]
    constraints: List[str]
    team_size: Optional[int]
    timeline: Optional[str]
    experience_level: Optional[str]


# Language compatibility and characteristics database
LANGUAGE_DATA = {
    "python": {
        "name": "Python",
        "compatible_os": ["windows", "macos", "linux", "va21_os", "web", "cross_platform"],
        "app_types": ["web_app", "api_service", "data_science", "ml_ai", "cli_tool", "automation", "system_tool"],
        "frameworks": {
            "web": ["Django", "Flask", "FastAPI", "Tornado"],
            "ml": ["TensorFlow", "PyTorch", "scikit-learn", "Keras"],
            "data": ["Pandas", "NumPy", "Matplotlib"],
            "gui": ["PyQt", "Tkinter", "Kivy"],
        },
        "build_tools": ["pip", "poetry", "setuptools", "conda"],
        "pros": ["Easy to learn", "Large ecosystem", "Excellent for AI/ML", "Rapid development"],
        "cons": ["Slower execution", "GIL limitations", "Mobile support limited"],
        "learning_curve": "easy",
        "ecosystem_maturity": "established",
        "priorities": {"speed": 90, "maintainability": 85, "scalability": 70, "security": 75},
    },
    "javascript": {
        "name": "JavaScript",
        "compatible_os": ["web", "windows", "macos", "linux", "mobile", "cross_platform"],
        "app_types": ["web_app", "mobile_app", "api_service", "desktop_app"],
        "frameworks": {
            "frontend": ["React", "Vue.js", "Angular", "Svelte"],
            "backend": ["Node.js", "Express", "NestJS", "Fastify"],
            "mobile": ["React Native", "Ionic"],
            "desktop": ["Electron"],
        },
        "build_tools": ["npm", "yarn", "pnpm", "webpack", "vite"],
        "pros": ["Ubiquitous", "Full-stack capable", "Huge ecosystem", "Fast iteration"],
        "cons": ["Type safety issues", "Callback complexity", "Browser inconsistencies"],
        "learning_curve": "easy",
        "ecosystem_maturity": "established",
        "priorities": {"speed": 95, "maintainability": 70, "scalability": 80, "security": 65},
    },
    "typescript": {
        "name": "TypeScript",
        "compatible_os": ["web", "windows", "macos", "linux", "mobile", "cross_platform"],
        "app_types": ["web_app", "mobile_app", "api_service", "desktop_app"],
        "frameworks": {
            "frontend": ["React", "Vue.js", "Angular", "Svelte"],
            "backend": ["Node.js", "Express", "NestJS", "Deno"],
            "mobile": ["React Native"],
            "desktop": ["Electron"],
        },
        "build_tools": ["npm", "yarn", "pnpm", "tsc", "esbuild"],
        "pros": ["Type safety", "Better IDE support", "Fewer runtime errors", "Maintainable"],
        "cons": ["Compilation step", "Steeper learning curve than JS", "Verbose"],
        "learning_curve": "moderate",
        "ecosystem_maturity": "established",
        "priorities": {"speed": 85, "maintainability": 95, "scalability": 90, "security": 80},
    },
    "rust": {
        "name": "Rust",
        "compatible_os": ["windows", "macos", "linux", "va21_os", "embedded", "cross_platform"],
        "app_types": ["system_tool", "cli_tool", "api_service", "game", "embedded"],
        "frameworks": {
            "web": ["Actix", "Rocket", "Axum", "Warp"],
            "async": ["Tokio"],
            "cli": ["clap", "structopt"],
            "gui": ["Tauri", "Druid"],
        },
        "build_tools": ["cargo", "rustup"],
        "pros": ["Memory safety", "Zero-cost abstractions", "Excellent performance", "No GC"],
        "cons": ["Steep learning curve", "Slower compilation", "Smaller ecosystem"],
        "learning_curve": "steep",
        "ecosystem_maturity": "growing",
        "priorities": {"speed": 60, "maintainability": 85, "scalability": 95, "security": 98, "performance": 98},
    },
    "go": {
        "name": "Go",
        "compatible_os": ["windows", "macos", "linux", "va21_os", "cross_platform"],
        "app_types": ["api_service", "cli_tool", "system_tool", "automation"],
        "frameworks": {
            "web": ["Gin", "Echo", "Fiber", "Chi"],
            "grpc": ["gRPC-Go"],
        },
        "build_tools": ["go build", "go mod"],
        "pros": ["Fast compilation", "Simple syntax", "Great concurrency", "Single binary"],
        "cons": ["Limited generics", "Verbose error handling", "No GUI frameworks"],
        "learning_curve": "easy",
        "ecosystem_maturity": "mature",
        "priorities": {"speed": 80, "maintainability": 85, "scalability": 95, "security": 85, "performance": 90},
    },
    "java": {
        "name": "Java",
        "compatible_os": ["windows", "macos", "linux", "android", "cross_platform"],
        "app_types": ["api_service", "mobile_app", "desktop_app", "enterprise"],
        "frameworks": {
            "web": ["Spring Boot", "Quarkus", "Micronaut"],
            "android": ["Android SDK"],
            "gui": ["JavaFX", "Swing"],
        },
        "build_tools": ["Maven", "Gradle"],
        "pros": ["Enterprise-ready", "Mature ecosystem", "Strong typing", "Cross-platform"],
        "cons": ["Verbose", "Memory intensive", "Slow startup"],
        "learning_curve": "moderate",
        "ecosystem_maturity": "established",
        "priorities": {"speed": 60, "maintainability": 90, "scalability": 95, "security": 90},
    },
    "kotlin": {
        "name": "Kotlin",
        "compatible_os": ["android", "windows", "macos", "linux", "cross_platform"],
        "app_types": ["mobile_app", "api_service", "desktop_app"],
        "frameworks": {
            "android": ["Android SDK", "Jetpack Compose"],
            "multiplatform": ["Kotlin Multiplatform"],
            "web": ["Ktor", "Spring Boot"],
        },
        "build_tools": ["Gradle", "Maven"],
        "pros": ["Concise syntax", "Null safety", "Java interop", "Modern features"],
        "cons": ["Compilation speed", "Smaller community than Java"],
        "learning_curve": "moderate",
        "ecosystem_maturity": "mature",
        "priorities": {"speed": 75, "maintainability": 90, "scalability": 85, "security": 85},
    },
    "swift": {
        "name": "Swift",
        "compatible_os": ["macos", "ios", "linux"],
        "app_types": ["mobile_app", "desktop_app", "api_service"],
        "frameworks": {
            "ios": ["SwiftUI", "UIKit"],
            "web": ["Vapor", "Perfect"],
        },
        "build_tools": ["Swift Package Manager", "Xcode"],
        "pros": ["Safe", "Fast", "Modern syntax", "Apple ecosystem"],
        "cons": ["Limited cross-platform", "Changing language", "Small server ecosystem"],
        "learning_curve": "moderate",
        "ecosystem_maturity": "mature",
        "priorities": {"speed": 75, "maintainability": 85, "scalability": 80, "security": 90, "performance": 90},
    },
    "c": {
        "name": "C",
        "compatible_os": ["windows", "macos", "linux", "va21_os", "embedded", "cross_platform"],
        "app_types": ["system_tool", "embedded", "cli_tool", "game"],
        "frameworks": {},
        "build_tools": ["gcc", "clang", "make", "cmake"],
        "pros": ["Maximum performance", "Low-level control", "Tiny binaries", "Universal"],
        "cons": ["Manual memory management", "No built-in safety", "Verbose"],
        "learning_curve": "steep",
        "ecosystem_maturity": "established",
        "priorities": {"speed": 40, "maintainability": 50, "scalability": 70, "security": 40, "performance": 100},
    },
    "cpp": {
        "name": "C++",
        "compatible_os": ["windows", "macos", "linux", "va21_os", "embedded", "cross_platform"],
        "app_types": ["game", "system_tool", "desktop_app", "embedded"],
        "frameworks": {
            "gui": ["Qt", "wxWidgets", "GTK"],
            "game": ["Unreal Engine", "SDL", "SFML"],
        },
        "build_tools": ["cmake", "make", "ninja", "vcpkg"],
        "pros": ["High performance", "Fine-grained control", "Large ecosystem", "Game development"],
        "cons": ["Complex", "Long compile times", "Memory bugs possible"],
        "learning_curve": "steep",
        "ecosystem_maturity": "established",
        "priorities": {"speed": 40, "maintainability": 60, "scalability": 85, "security": 60, "performance": 98},
    },
    "csharp": {
        "name": "C#",
        "compatible_os": ["windows", "macos", "linux", "cross_platform"],
        "app_types": ["desktop_app", "game", "api_service", "mobile_app"],
        "frameworks": {
            "web": ["ASP.NET Core", "Blazor"],
            "desktop": ["WPF", "MAUI", "Avalonia"],
            "game": ["Unity"],
            "mobile": ["Xamarin", "MAUI"],
        },
        "build_tools": ["dotnet", "MSBuild", "NuGet"],
        "pros": ["Powerful IDE", "Strong typing", "LINQ", "Cross-platform with .NET"],
        "cons": ["Windows-centric history", "Runtime required"],
        "learning_curve": "moderate",
        "ecosystem_maturity": "established",
        "priorities": {"speed": 75, "maintainability": 90, "scalability": 90, "security": 85},
    },
    "php": {
        "name": "PHP",
        "compatible_os": ["windows", "macos", "linux", "web"],
        "app_types": ["web_app", "api_service"],
        "frameworks": {
            "web": ["Laravel", "Symfony", "CodeIgniter", "WordPress"],
        },
        "build_tools": ["Composer"],
        "pros": ["Easy to deploy", "Huge CMS ecosystem", "Shared hosting support", "Fast development"],
        "cons": ["Inconsistent design", "Security history", "Performance"],
        "learning_curve": "easy",
        "ecosystem_maturity": "established",
        "priorities": {"speed": 90, "maintainability": 70, "scalability": 70, "security": 65},
    },
    "ruby": {
        "name": "Ruby",
        "compatible_os": ["windows", "macos", "linux", "web"],
        "app_types": ["web_app", "api_service", "cli_tool", "automation"],
        "frameworks": {
            "web": ["Ruby on Rails", "Sinatra", "Hanami"],
        },
        "build_tools": ["bundler", "gem", "rake"],
        "pros": ["Elegant syntax", "Rails productivity", "Great for MVPs", "Developer happiness"],
        "cons": ["Slower performance", "Declining popularity", "Threading limitations"],
        "learning_curve": "easy",
        "ecosystem_maturity": "mature",
        "priorities": {"speed": 90, "maintainability": 85, "scalability": 65, "security": 70},
    },
}

# Technology stack templates
STACK_TEMPLATES = {
    "mern": {
        "name": "MERN Stack",
        "frontend": "React",
        "backend": "Node.js/Express",
        "database": "MongoDB",
        "languages": ["JavaScript", "TypeScript"],
        "frameworks": ["React", "Express", "Mongoose"],
        "best_for": ["web_app", "api_service"],
        "description": "Full JavaScript stack with MongoDB, Express, React, and Node.js",
    },
    "mean": {
        "name": "MEAN Stack",
        "frontend": "Angular",
        "backend": "Node.js/Express",
        "database": "MongoDB",
        "languages": ["TypeScript", "JavaScript"],
        "frameworks": ["Angular", "Express", "Mongoose"],
        "best_for": ["web_app", "api_service"],
        "description": "Enterprise-grade JavaScript stack with Angular",
    },
    "django_react": {
        "name": "Django + React",
        "frontend": "React",
        "backend": "Django/Django REST Framework",
        "database": "PostgreSQL",
        "languages": ["Python", "TypeScript"],
        "frameworks": ["React", "Django", "DRF"],
        "best_for": ["web_app", "api_service", "data_science"],
        "description": "Python backend with React frontend, great for data-heavy apps",
    },
    "fastapi_vue": {
        "name": "FastAPI + Vue",
        "frontend": "Vue.js",
        "backend": "FastAPI",
        "database": "PostgreSQL",
        "languages": ["Python", "TypeScript"],
        "frameworks": ["Vue.js", "FastAPI", "SQLAlchemy"],
        "best_for": ["api_service", "web_app"],
        "description": "Modern async Python API with Vue frontend",
    },
    "springboot_angular": {
        "name": "Spring Boot + Angular",
        "frontend": "Angular",
        "backend": "Spring Boot",
        "database": "PostgreSQL/MySQL",
        "languages": ["Java", "TypeScript"],
        "frameworks": ["Angular", "Spring Boot", "Spring Data JPA"],
        "best_for": ["enterprise", "api_service"],
        "description": "Enterprise Java stack with Angular frontend",
    },
    "rust_htmx": {
        "name": "Rust + HTMX",
        "frontend": "HTMX",
        "backend": "Axum/Actix",
        "database": "PostgreSQL",
        "languages": ["Rust", "HTML"],
        "frameworks": ["Axum", "HTMX", "SQLx"],
        "best_for": ["system_tool", "api_service"],
        "description": "High-performance Rust backend with hypermedia-driven frontend",
    },
    "tauri": {
        "name": "Tauri Desktop",
        "frontend": "React/Vue/Svelte",
        "backend": "Rust",
        "database": "SQLite",
        "languages": ["Rust", "TypeScript"],
        "frameworks": ["Tauri", "React/Vue"],
        "best_for": ["desktop_app"],
        "description": "Lightweight cross-platform desktop apps with Rust backend",
    },
    "flutter": {
        "name": "Flutter Mobile",
        "frontend": "Flutter",
        "backend": "Firebase/Node.js",
        "database": "Firebase/PostgreSQL",
        "languages": ["Dart", "TypeScript"],
        "frameworks": ["Flutter", "Firebase"],
        "best_for": ["mobile_app", "cross_platform"],
        "description": "Cross-platform mobile apps with single codebase",
    },
    "react_native": {
        "name": "React Native Mobile",
        "frontend": "React Native",
        "backend": "Node.js/Express",
        "database": "MongoDB/PostgreSQL",
        "languages": ["TypeScript", "JavaScript"],
        "frameworks": ["React Native", "Expo", "Express"],
        "best_for": ["mobile_app", "cross_platform"],
        "description": "Cross-platform mobile with React knowledge transfer",
    },
    "ml_pipeline": {
        "name": "ML/AI Pipeline",
        "frontend": "Streamlit/Gradio",
        "backend": "FastAPI",
        "database": "PostgreSQL/Redis",
        "languages": ["Python"],
        "frameworks": ["PyTorch/TensorFlow", "FastAPI", "MLflow"],
        "best_for": ["ml_ai", "data_science"],
        "description": "Machine learning and AI application stack",
    },
}


class SuggestEngine:
    """
    VA21 Coding IDE Suggestion Engine
    
    Analyzes user requirements and suggests:
    - Best programming languages for the project
    - Technology stacks and frameworks
    - Build tools and deployment options
    - Architecture recommendations
    
    Integrates with SearXNG for searching current best practices.
    """
    
    VERSION = "1.0.0"
    
    def __init__(self, searxng_client=None, ai_helper=None):
        """
        Initialize the suggestion engine.
        
        Args:
            searxng_client: Optional SearXNG client for web search
            ai_helper: Optional AI helper for enhanced suggestions
        """
        self.searxng = searxng_client
        self.ai_helper = ai_helper
        self.language_data = LANGUAGE_DATA
        self.stack_templates = STACK_TEMPLATES
        
        # Try to load SearXNG if not provided
        if not self.searxng:
            try:
                from ..searxng.searxng_client import get_searxng
                self.searxng = get_searxng()
            except ImportError:
                pass
        
        print(f"[SuggestEngine] Initialized v{self.VERSION}")
    
    def parse_requirements(self, user_input: str) -> ProjectRequirements:
        """
        Parse natural language project description into structured requirements.
        
        Args:
            user_input: Natural language description of the project
            
        Returns:
            ProjectRequirements with parsed data
        """
        input_lower = user_input.lower()
        
        # Detect app type
        app_type = None
        app_type_keywords = {
            AppType.WEB_APP: ["website", "web app", "web application", "webapp", "browser"],
            AppType.MOBILE_APP: ["mobile", "android", "ios", "iphone", "phone app", "smartphone"],
            AppType.DESKTOP_APP: ["desktop", "windows app", "mac app", "native app"],
            AppType.CLI_TOOL: ["cli", "command line", "terminal", "console app"],
            AppType.API_SERVICE: ["api", "rest", "backend", "microservice", "service"],
            AppType.GAME: ["game", "gaming", "3d", "2d game", "video game"],
            AppType.DATA_SCIENCE: ["data analysis", "visualization", "analytics", "dashboard"],
            AppType.ML_AI: ["machine learning", "ai", "artificial intelligence", "neural network", "model"],
            AppType.SYSTEM_TOOL: ["system", "utility", "tool", "daemon", "service"],
            AppType.AUTOMATION: ["automation", "script", "automate", "bot", "scraper"],
            AppType.IOT: ["iot", "sensor", "raspberry", "arduino", "embedded"],
            AppType.BLOCKCHAIN: ["blockchain", "crypto", "smart contract", "web3"],
        }
        
        for atype, keywords in app_type_keywords.items():
            if any(kw in input_lower for kw in keywords):
                app_type = atype
                break
        
        # Detect target OS
        target_os = []
        os_keywords = {
            TargetOS.WINDOWS: ["windows"],
            TargetOS.MACOS: ["mac", "macos", "osx"],
            TargetOS.LINUX: ["linux", "ubuntu", "debian"],
            TargetOS.ANDROID: ["android"],
            TargetOS.IOS: ["ios", "iphone", "ipad"],
            TargetOS.WEB: ["web", "browser", "chrome", "firefox"],
            TargetOS.CROSS_PLATFORM: ["cross-platform", "multi-platform", "all platforms"],
            TargetOS.EMBEDDED: ["embedded", "iot", "raspberry", "arduino"],
            TargetOS.VA21_OS: ["va21", "this os"],
        }
        
        for tos, keywords in os_keywords.items():
            if any(kw in input_lower for kw in keywords):
                target_os.append(tos)
        
        # Default to cross-platform if none specified
        if not target_os:
            target_os = [TargetOS.CROSS_PLATFORM]
        
        # Detect priorities
        priorities = []
        priority_keywords = {
            Priority.PERFORMANCE: ["fast", "performance", "speed", "efficient", "optimized"],
            Priority.SPEED: ["quick", "rapid", "mvp", "prototype", "fast development"],
            Priority.MAINTAINABILITY: ["maintainable", "clean", "organized", "long-term"],
            Priority.SCALABILITY: ["scalable", "scale", "growth", "enterprise"],
            Priority.SECURITY: ["secure", "security", "safe", "protected"],
        }
        
        for priority, keywords in priority_keywords.items():
            if any(kw in input_lower for kw in keywords):
                priorities.append(priority)
        
        # Default priority
        if not priorities:
            priorities = [Priority.SPEED]
        
        # Extract features (basic keyword extraction)
        features = []
        feature_keywords = [
            "authentication", "login", "signup", "database", "realtime",
            "chat", "notifications", "payment", "email", "file upload",
            "search", "maps", "video", "audio", "calendar", "dashboard",
            "analytics", "api", "social", "comments", "ratings",
        ]
        
        for feature in feature_keywords:
            if feature in input_lower:
                features.append(feature)
        
        # Extract constraints
        constraints = []
        if "budget" in input_lower or "cheap" in input_lower or "free" in input_lower:
            constraints.append("low_budget")
        if "fast" in input_lower or "quick" in input_lower or "deadline" in input_lower:
            constraints.append("time_constrained")
        if "beginner" in input_lower or "new to" in input_lower or "learning" in input_lower:
            constraints.append("beginner_friendly")
        
        return ProjectRequirements(
            description=user_input,
            app_type=app_type,
            target_os=target_os,
            priorities=priorities,
            features=features,
            constraints=constraints,
            team_size=None,
            timeline=None,
            experience_level="beginner" if "beginner_friendly" in constraints else None
        )
    
    def suggest_languages(self, requirements: ProjectRequirements, 
                          limit: int = 5) -> List[LanguageSuggestion]:
        """
        Suggest programming languages based on requirements.
        
        Args:
            requirements: Parsed project requirements
            limit: Maximum number of suggestions
            
        Returns:
            List of LanguageSuggestion objects sorted by score
        """
        suggestions = []
        
        for lang_id, lang_data in self.language_data.items():
            score = 0
            reasons = []
            
            # Check OS compatibility
            target_os_values = [os.value for os in requirements.target_os]
            os_compatible = any(
                os in lang_data["compatible_os"] 
                for os in target_os_values
            )
            
            if not os_compatible and "cross_platform" not in lang_data["compatible_os"]:
                continue  # Skip incompatible languages
            
            # Score based on app type match
            if requirements.app_type:
                if requirements.app_type.value in lang_data["app_types"]:
                    score += 30
                    reasons.append(f"Great for {requirements.app_type.value.replace('_', ' ')}")
            
            # Score based on OS compatibility
            for target in requirements.target_os:
                if target.value in lang_data["compatible_os"]:
                    score += 10
                    reasons.append(f"Compatible with {target.value}")
            
            # Score based on priorities
            for priority in requirements.priorities:
                if priority.value in lang_data.get("priorities", {}):
                    priority_score = lang_data["priorities"][priority.value]
                    score += priority_score * 0.3
                    if priority_score >= 85:
                        reasons.append(f"Excellent {priority.value}")
            
            # Score based on constraints
            if "beginner_friendly" in requirements.constraints:
                if lang_data["learning_curve"] == "easy":
                    score += 20
                    reasons.append("Easy to learn")
                elif lang_data["learning_curve"] == "steep":
                    score -= 15
            
            if "time_constrained" in requirements.constraints:
                if lang_data.get("priorities", {}).get("speed", 0) >= 80:
                    score += 15
                    reasons.append("Fast development")
            
            # Bonus for mature ecosystems
            if lang_data["ecosystem_maturity"] in ["mature", "established"]:
                score += 10
                reasons.append("Mature ecosystem")
            
            # Get relevant frameworks
            all_frameworks = []
            for category, frameworks in lang_data.get("frameworks", {}).items():
                all_frameworks.extend(frameworks[:2])
            
            suggestions.append(LanguageSuggestion(
                language=lang_data["name"],
                score=min(100, max(0, score)),
                reasons=reasons[:3],
                frameworks=all_frameworks[:4],
                build_tools=lang_data.get("build_tools", [])[:3],
                pros=lang_data.get("pros", []),
                cons=lang_data.get("cons", []),
                learning_curve=lang_data.get("learning_curve", "moderate"),
                ecosystem_maturity=lang_data.get("ecosystem_maturity", "mature"),
                compatible_os=lang_data.get("compatible_os", [])
            ))
        
        # Sort by score and return top suggestions
        suggestions.sort(key=lambda x: x.score, reverse=True)
        top_suggestions = suggestions[:limit]
        
        # Enhance top suggestions with latest web search info
        if self.searxng and top_suggestions:
            for suggestion in top_suggestions[:3]:  # Only search for top 3
                try:
                    latest_info = self.search_latest_language_info(suggestion.language)
                    if latest_info.get("latest_news"):
                        # Add latest info to suggestion metadata
                        suggestion.reasons.append(f"Latest updates available ({datetime.now().strftime('%b %Y')})")
                except Exception:
                    pass  # Continue even if search fails
        
        return top_suggestions
    
    def suggest_stack(self, requirements: ProjectRequirements,
                      language: str = None) -> List[StackSuggestion]:
        """
        Suggest technology stacks based on requirements.
        
        Args:
            requirements: Parsed project requirements
            language: Optional preferred language
            
        Returns:
            List of StackSuggestion objects
        """
        suggestions = []
        
        for stack_id, stack_data in self.stack_templates.items():
            score = 50  # Base score
            
            # Check if app type matches
            if requirements.app_type:
                if requirements.app_type.value in stack_data.get("best_for", []):
                    score += 30
            
            # Check language preference
            if language:
                if language.lower() in [l.lower() for l in stack_data.get("languages", [])]:
                    score += 25
            
            # Check for priority matches
            if Priority.PERFORMANCE in requirements.priorities:
                if "Rust" in stack_data.get("languages", []):
                    score += 15
            
            if Priority.SPEED in requirements.priorities:
                if any(l in ["Python", "JavaScript", "TypeScript"] 
                       for l in stack_data.get("languages", [])):
                    score += 15
            
            suggestions.append(StackSuggestion(
                name=stack_data["name"],
                frontend=stack_data.get("frontend"),
                backend=stack_data.get("backend"),
                database=stack_data.get("database"),
                languages=stack_data.get("languages", []),
                frameworks=stack_data.get("frameworks", []),
                reasoning=stack_data.get("description", ""),
                score=min(100, score),
                best_for=stack_data.get("best_for", [])
            ))
        
        suggestions.sort(key=lambda x: x.score, reverse=True)
        return suggestions[:5]
    
    def get_suggestion_report(self, user_input: str) -> Dict[str, Any]:
        """
        Generate a complete suggestion report for user input.
        
        Args:
            user_input: Natural language project description
            
        Returns:
            Complete suggestion report with languages, stacks, and recommendations
        """
        # Parse requirements
        requirements = self.parse_requirements(user_input)
        
        # Get language suggestions
        languages = self.suggest_languages(requirements)
        
        # Get stack suggestions (using top language if available)
        top_language = languages[0].language if languages else None
        stacks = self.suggest_stack(requirements, top_language)
        
        # Build report
        report = {
            "timestamp": datetime.now().isoformat(),
            "original_input": user_input,
            "parsed_requirements": {
                "app_type": requirements.app_type.value if requirements.app_type else "unspecified",
                "target_os": [os.value for os in requirements.target_os],
                "priorities": [p.value for p in requirements.priorities],
                "features": requirements.features,
                "constraints": requirements.constraints,
            },
            "language_suggestions": [
                {
                    "language": lang.language,
                    "score": lang.score,
                    "reasons": lang.reasons,
                    "frameworks": lang.frameworks,
                    "build_tools": lang.build_tools,
                    "learning_curve": lang.learning_curve,
                    "pros": lang.pros,
                    "cons": lang.cons,
                }
                for lang in languages
            ],
            "stack_suggestions": [
                {
                    "name": stack.name,
                    "frontend": stack.frontend,
                    "backend": stack.backend,
                    "database": stack.database,
                    "languages": stack.languages,
                    "frameworks": stack.frameworks,
                    "reasoning": stack.reasoning,
                    "score": stack.score,
                }
                for stack in stacks
            ],
            "recommendation": {
                "primary_language": languages[0].language if languages else None,
                "primary_stack": stacks[0].name if stacks else None,
                "summary": self._generate_summary(requirements, languages, stacks),
            }
        }
        
        return report
    
    def _generate_summary(self, requirements: ProjectRequirements,
                          languages: List[LanguageSuggestion],
                          stacks: List[StackSuggestion]) -> str:
        """Generate a human-readable summary of suggestions."""
        if not languages:
            return "Unable to determine best language for your requirements."
        
        top_lang = languages[0]
        top_stack = stacks[0] if stacks else None
        
        app_type_str = requirements.app_type.value.replace("_", " ") if requirements.app_type else "application"
        os_str = ", ".join([os.value for os in requirements.target_os])
        
        summary = f"For building a {app_type_str} targeting {os_str}, "
        summary += f"I recommend **{top_lang.language}** "
        summary += f"({', '.join(top_lang.reasons[:2])}). "
        
        if top_stack:
            summary += f"\n\nConsider the **{top_stack.name}** stack: {top_stack.reasoning}"
        
        if top_lang.frameworks:
            summary += f"\n\nRecommended frameworks: {', '.join(top_lang.frameworks[:3])}"
        
        return summary
    
    def search_best_practices(self, language: str, topic: str, 
                               time_range: str = "month") -> List[Dict]:
        """
        Search for best practices using SearXNG with time filtering.
        
        Uses time_range to get the latest/most recent information available.
        
        Args:
            language: Programming language
            topic: Topic to search for
            time_range: Time filter - 'day', 'week', 'month', 'year' (default: month)
            
        Returns:
            List of search results with latest info
        """
        if not self.searxng:
            return []
        
        current_year = datetime.now().year
        current_date = datetime.now().strftime("%Y-%m-%d")
        
        # Build time-aware query for latest information
        query = f"{language} {topic} best practices {current_year}"
        
        try:
            # Use the time-filtered search method
            results = self._search_with_time_filter(query, time_range)
            return results
        except Exception as e:
            print(f"[SuggestEngine] Search error: {e}")
            return []
    
    def _search_with_time_filter(self, query: str, time_range: str = "month",
                                   category: str = "general") -> List[Dict]:
        """
        Perform a SearXNG search with time filtering for latest results.
        
        SearXNG supports time_range parameter for filtering results.
        
        Args:
            query: Search query
            time_range: 'day', 'week', 'month', 'year', or None for all time
            category: Search category
            
        Returns:
            List of search result dictionaries
        """
        if not self.searxng:
            return []
        
        # Add time context to query for better results
        time_context = {
            'day': 'today latest',
            'week': 'this week recent',
            'month': f'{datetime.now().strftime("%B %Y")} latest',
            'year': f'{datetime.now().year} current'
        }
        
        time_hint = time_context.get(time_range, '')
        enhanced_query = f"{query} {time_hint}".strip()
        
        try:
            # Use SearXNG search with time preference
            # Most SearXNG instances support time_range parameter
            results = self.searxng.search(
                enhanced_query, 
                category=category
            )
            
            return [
                {
                    "title": r.title,
                    "url": r.url,
                    "snippet": r.snippet,
                    "engine": r.engine,
                    "search_time": time_range,
                    "query_date": datetime.now().isoformat()
                }
                for r in results.results[:10]  # Get top 10 results
            ]
        except Exception as e:
            print(f"[SuggestEngine] Time-filtered search error: {e}")
            return []
    
    def search_latest_language_info(self, language: str) -> Dict:
        """
        Search for the latest information about a programming language.
        
        Gets recent news, updates, releases, and best practices.
        
        Args:
            language: Programming language name
            
        Returns:
            Dictionary with latest language information
        """
        if not self.searxng:
            return {"error": "SearXNG not available"}
        
        current_date = datetime.now()
        results = {
            "language": language,
            "search_date": current_date.isoformat(),
            "latest_news": [],
            "recent_releases": [],
            "current_best_practices": [],
            "trending_frameworks": []
        }
        
        # Search for latest news (last week)
        news_query = f"{language} programming news latest update"
        news_results = self._search_with_time_filter(news_query, "week", "news")
        results["latest_news"] = news_results[:5]
        
        # Search for recent releases (last month)
        release_query = f"{language} new release version {current_date.year}"
        release_results = self._search_with_time_filter(release_query, "month")
        results["recent_releases"] = release_results[:5]
        
        # Search for current best practices (last month)
        practices_query = f"{language} best practices {current_date.year}"
        practices_results = self._search_with_time_filter(practices_query, "month")
        results["current_best_practices"] = practices_results[:5]
        
        # Search for trending frameworks (last month)
        frameworks_query = f"{language} popular frameworks libraries {current_date.year}"
        frameworks_results = self._search_with_time_filter(frameworks_query, "month")
        results["trending_frameworks"] = frameworks_results[:5]
        
        return results
    
    def search_technology_comparison(self, tech1: str, tech2: str) -> Dict:
        """
        Search for latest comparison between two technologies.
        
        Args:
            tech1: First technology
            tech2: Second technology
            
        Returns:
            Dictionary with comparison information
        """
        if not self.searxng:
            return {"error": "SearXNG not available"}
        
        current_date = datetime.now()
        
        # Search for latest comparison
        comparison_query = f"{tech1} vs {tech2} comparison {current_date.year}"
        comparison_results = self._search_with_time_filter(comparison_query, "year")
        
        # Search for when to use each
        use_cases_query = f"when to use {tech1} vs {tech2} {current_date.year}"
        use_cases_results = self._search_with_time_filter(use_cases_query, "year")
        
        return {
            "technologies": [tech1, tech2],
            "search_date": current_date.isoformat(),
            "comparisons": comparison_results[:5],
            "use_cases": use_cases_results[:5]
        }
    
    def search_os_compatibility(self, technology: str, target_os: str) -> Dict:
        """
        Search for latest OS compatibility information.
        
        Args:
            technology: Technology/language/framework
            target_os: Target operating system
            
        Returns:
            Dictionary with compatibility information
        """
        if not self.searxng:
            return {"error": "SearXNG not available"}
        
        current_date = datetime.now()
        
        # Search for compatibility
        compat_query = f"{technology} {target_os} compatibility support {current_date.year}"
        compat_results = self._search_with_time_filter(compat_query, "year")
        
        # Search for setup/installation
        setup_query = f"{technology} install setup {target_os} {current_date.year}"
        setup_results = self._search_with_time_filter(setup_query, "month")
        
        return {
            "technology": technology,
            "target_os": target_os,
            "search_date": current_date.isoformat(),
            "compatibility_info": compat_results[:5],
            "setup_guides": setup_results[:5]
        }


# Singleton instance
_suggest_engine_instance = None


def get_suggest_engine(searxng_client=None, ai_helper=None) -> SuggestEngine:
    """Get or create the SuggestEngine singleton."""
    global _suggest_engine_instance
    if _suggest_engine_instance is None:
        _suggest_engine_instance = SuggestEngine(searxng_client, ai_helper)
    return _suggest_engine_instance


# CLI interface
def main():
    """CLI interface for testing the suggestion engine."""
    engine = get_suggest_engine()
    
    print("=" * 60)
    print("VA21 Coding IDE - Suggestion Engine")
    print("=" * 60)
    
    test_inputs = [
        "I want to build a web app for task management with user authentication",
        "Create a mobile app for Android and iOS for fitness tracking",
        "Build a fast CLI tool for file processing on Linux",
        "I need a machine learning model for image classification",
        "Desktop application for Windows with a beautiful UI",
    ]
    
    for user_input in test_inputs:
        print(f"\n{'─' * 60}")
        print(f"Input: {user_input}")
        print(f"{'─' * 60}")
        
        report = engine.get_suggestion_report(user_input)
        
        print(f"\n📋 Parsed: {report['parsed_requirements']['app_type']} for {report['parsed_requirements']['target_os']}")
        
        print("\n🔧 Top Language Suggestions:")
        for lang in report['language_suggestions'][:3]:
            print(f"  • {lang['language']} (Score: {lang['score']:.0f})")
            print(f"    Reasons: {', '.join(lang['reasons'])}")
        
        print(f"\n📦 Top Stack: {report['stack_suggestions'][0]['name']}")
        print(f"\n💡 Summary:\n{report['recommendation']['summary']}")


if __name__ == "__main__":
    main()
