#!/usr/bin/env python3
"""
VA21 Research OS - SearXNG Integration
========================================

Integrates SearXNG, an open-source metasearch engine, for secure
internet research within the VA21 Research OS environment.

SearXNG provides:
- Privacy-respecting search (no tracking)
- Multiple search engine aggregation
- No ads or tracking
- Self-hostable

Om Vinayaka - Knowledge through secure discovery.
"""

import os
import json
import time
import urllib.parse
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, field

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


@dataclass
class SearchResult:
    """A single search result."""
    title: str
    url: str
    snippet: str
    engine: str
    position: int
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass  
class SearchQuery:
    """A search query and its results."""
    query: str
    category: str
    results: List[SearchResult] = field(default_factory=list)
    total_results: int = 0
    search_time: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)


class SearXNGClient:
    """
    SearXNG Client for VA21 Research OS
    
    This client interfaces with SearXNG instances (public or self-hosted)
    to provide privacy-respecting search capabilities.
    
    Features:
    - Multiple category search (general, images, news, science, files)
    - Result caching
    - Search history
    - Configurable SearXNG instances
    """
    
    VERSION = "1.0.0"
    
    # Public SearXNG instances (fallbacks)
    PUBLIC_INSTANCES = [
        "https://searx.be",
        "https://search.bus-hit.me", 
        "https://searx.tiekoetter.com",
        "https://search.sapti.me",
        "https://searx.prvcy.eu",
    ]
    
    def __init__(self, instance_url: str = None):
        """
        Initialize SearXNG client.
        
        Args:
            instance_url: URL of SearXNG instance (uses public instance if None)
        """
        self.instance_url = instance_url or self.PUBLIC_INSTANCES[0]
        self.timeout = 10
        self.max_results = 20
        
        # Search history
        self.search_history: List[SearchQuery] = []
        
        # Cache
        self.cache: Dict[str, SearchQuery] = {}
        self.cache_ttl = 300  # 5 minutes
        
        # Statistics
        self.stats = {
            "total_searches": 0,
            "cached_hits": 0,
            "failed_searches": 0
        }
        
        # Verify requests is available
        if not REQUESTS_AVAILABLE:
            print("[SearXNG] Warning: requests library not available")
        
        print(f"[SearXNG] Initialized v{self.VERSION}")
        print(f"[SearXNG] Instance: {self.instance_url}")
    
    def search(self, query: str, category: str = "general", 
               page: int = 1, language: str = "en") -> SearchQuery:
        """
        Perform a search query.
        
        Args:
            query: Search query string
            category: Search category (general, images, news, science, files, it)
            page: Page number for pagination
            language: Search language
            
        Returns:
            SearchQuery object with results
        """
        if not REQUESTS_AVAILABLE:
            return self._simulate_search(query, category)
        
        # Check cache
        cache_key = f"{query}:{category}:{page}"
        if cache_key in self.cache:
            cached = self.cache[cache_key]
            age = (datetime.now() - cached.timestamp).total_seconds()
            if age < self.cache_ttl:
                self.stats["cached_hits"] += 1
                return cached
        
        self.stats["total_searches"] += 1
        start_time = time.time()
        
        # Build request
        params = {
            "q": query,
            "categories": category,
            "pageno": page,
            "language": language,
            "format": "json"
        }
        
        search_url = f"{self.instance_url}/search"
        
        try:
            response = requests.get(
                search_url,
                params=params,
                timeout=self.timeout,
                headers={"User-Agent": "VA21-ResearchOS/1.0"}
            )
            
            response.raise_for_status()
            data = response.json()
            
            # Parse results
            results = []
            for i, item in enumerate(data.get("results", [])[:self.max_results]):
                results.append(SearchResult(
                    title=item.get("title", "No title"),
                    url=item.get("url", ""),
                    snippet=item.get("content", ""),
                    engine=item.get("engine", "unknown"),
                    position=i + 1
                ))
            
            search_query = SearchQuery(
                query=query,
                category=category,
                results=results,
                total_results=len(results),
                search_time=time.time() - start_time
            )
            
            # Cache result
            self.cache[cache_key] = search_query
            self.search_history.append(search_query)
            
            return search_query
            
        except requests.exceptions.Timeout:
            self.stats["failed_searches"] += 1
            # Try next instance
            return self._try_fallback_instance(query, category, page, language)
            
        except requests.exceptions.RequestException as e:
            self.stats["failed_searches"] += 1
            return SearchQuery(
                query=query,
                category=category,
                results=[],
                total_results=0,
                search_time=time.time() - start_time
            )
    
    def _try_fallback_instance(self, query: str, category: str, 
                                page: int, language: str) -> SearchQuery:
        """Try fallback instances if primary fails."""
        for instance in self.PUBLIC_INSTANCES:
            if instance == self.instance_url:
                continue
            
            try:
                old_instance = self.instance_url
                self.instance_url = instance
                result = self.search(query, category, page, language)
                
                if result.total_results > 0:
                    print(f"[SearXNG] Switched to fallback: {instance}")
                    return result
                    
                self.instance_url = old_instance
                
            except Exception:
                continue
        
        return SearchQuery(query=query, category=category, results=[], total_results=0)
    
    def _simulate_search(self, query: str, category: str) -> SearchQuery:
        """Simulate search when requests is not available."""
        # Return dummy results for testing
        results = [
            SearchResult(
                title=f"[Simulated] Result for: {query}",
                url=f"https://example.com/search?q={urllib.parse.quote(query)}",
                snippet=f"This is a simulated search result for '{query}'. Install 'requests' for real search.",
                engine="simulation",
                position=1
            ),
            SearchResult(
                title=f"[Simulated] Wikipedia - {query}",
                url=f"https://en.wikipedia.org/wiki/{urllib.parse.quote(query)}",
                snippet=f"Wikipedia article about {query}. (Simulated result)",
                engine="simulation",
                position=2
            )
        ]
        
        return SearchQuery(
            query=query,
            category=category,
            results=results,
            total_results=len(results),
            search_time=0.1
        )
    
    def search_images(self, query: str, page: int = 1) -> SearchQuery:
        """Search for images."""
        return self.search(query, category="images", page=page)
    
    def search_news(self, query: str, page: int = 1) -> SearchQuery:
        """Search for news."""
        return self.search(query, category="news", page=page)
    
    def search_science(self, query: str, page: int = 1) -> SearchQuery:
        """Search for scientific content."""
        return self.search(query, category="science", page=page)
    
    def search_it(self, query: str, page: int = 1) -> SearchQuery:
        """Search for IT/programming content."""
        return self.search(query, category="it", page=page)
    
    def search_files(self, query: str, page: int = 1) -> SearchQuery:
        """Search for files/downloads."""
        return self.search(query, category="files", page=page)
    
    def get_history(self, limit: int = 20) -> List[Dict]:
        """Get search history."""
        history = self.search_history[-limit:]
        history.reverse()
        
        return [{
            "query": q.query,
            "category": q.category,
            "results_count": q.total_results,
            "time": q.timestamp.isoformat()
        } for q in history]
    
    def clear_history(self):
        """Clear search history."""
        self.search_history.clear()
    
    def clear_cache(self):
        """Clear search cache."""
        self.cache.clear()
    
    def get_stats(self) -> Dict:
        """Get search statistics."""
        return {
            **self.stats,
            "history_size": len(self.search_history),
            "cache_size": len(self.cache),
            "instance": self.instance_url
        }
    
    def set_instance(self, url: str):
        """Set the SearXNG instance URL."""
        self.instance_url = url
        self.cache.clear()  # Clear cache when switching instances
        print(f"[SearXNG] Switched to: {url}")
    
    def get_available_instances(self) -> List[str]:
        """Get list of known public instances."""
        return self.PUBLIC_INSTANCES.copy()
    
    def test_instance(self, url: str = None) -> bool:
        """Test if an instance is working."""
        test_url = url or self.instance_url
        
        try:
            response = requests.get(
                f"{test_url}/search",
                params={"q": "test", "format": "json"},
                timeout=5
            )
            return response.status_code == 200
        except Exception:
            return False
    
    def format_results(self, search_query: SearchQuery) -> str:
        """Format search results for display."""
        lines = []
        lines.append(f"\n═══ Search Results: '{search_query.query}' ═══")
        lines.append(f"Category: {search_query.category} | Results: {search_query.total_results}")
        lines.append(f"Search time: {search_query.search_time:.2f}s")
        lines.append("─" * 50)
        
        if not search_query.results:
            lines.append("No results found.")
        else:
            for result in search_query.results:
                lines.append(f"\n[{result.position}] {result.title}")
                lines.append(f"    URL: {result.url}")
                if result.snippet:
                    # Truncate long snippets
                    snippet = result.snippet[:200] + "..." if len(result.snippet) > 200 else result.snippet
                    lines.append(f"    {snippet}")
                lines.append(f"    (via {result.engine})")
        
        lines.append("\n" + "─" * 50)
        return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════════════════
# SINGLETON
# ═══════════════════════════════════════════════════════════════════════════════

_searxng_instance = None

def get_searxng() -> SearXNGClient:
    """Get the SearXNG client singleton."""
    global _searxng_instance
    if _searxng_instance is None:
        _searxng_instance = SearXNGClient()
    return _searxng_instance


# ═══════════════════════════════════════════════════════════════════════════════
# CLI INTERFACE
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    """CLI interface for SearXNG."""
    import argparse
    
    parser = argparse.ArgumentParser(description="VA21 SearXNG Search")
    parser.add_argument("query", nargs="?", help="Search query")
    parser.add_argument("-c", "--category", default="general",
                       choices=["general", "images", "news", "science", "it", "files"],
                       help="Search category")
    parser.add_argument("-i", "--instance", help="SearXNG instance URL")
    parser.add_argument("--history", action="store_true", help="Show search history")
    parser.add_argument("--stats", action="store_true", help="Show statistics")
    parser.add_argument("--instances", action="store_true", help="List public instances")
    
    args = parser.parse_args()
    
    client = get_searxng()
    
    if args.instance:
        client.set_instance(args.instance)
    
    if args.history:
        history = client.get_history()
        print("\nSearch History:")
        for item in history:
            print(f"  [{item['time']}] {item['query']} ({item['category']}) - {item['results_count']} results")
        return
    
    if args.stats:
        stats = client.get_stats()
        print("\nSearch Statistics:")
        print(json.dumps(stats, indent=2))
        return
    
    if args.instances:
        print("\nPublic SearXNG Instances:")
        for inst in client.get_available_instances():
            working = "✅" if client.test_instance(inst) else "❌"
            print(f"  {working} {inst}")
        return
    
    if not args.query:
        parser.print_help()
        return
    
    # Perform search
    result = client.search(args.query, category=args.category)
    print(client.format_results(result))


if __name__ == "__main__":
    main()
