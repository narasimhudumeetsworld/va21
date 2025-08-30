import feedparser
import time
from urllib.parse import urlparse

# A stricter, official list of security RSS feeds.
SECURITY_RSS_FEEDS = [
    "https://security.googleblog.com/feeds/posts/default",
    "https://msrc.microsoft.com/blog/feed/",
    "https://googleprojectzero.blogspot.com/feeds/posts/default",
]

def fetch_stories_from_rss(feed_urls, whois_lookup_func, sandbox_func):
    """
    Fetches stories from RSS feeds, performs a WHOIS check on the source,
    and processes the text in a sandbox.

    :param feed_urls: A list of URLs for the RSS feeds.
    :param whois_lookup_func: A function that performs a WHOIS lookup on a domain.
    :param sandbox_func: A function that processes text in a sandbox.
    :return: A list of processed story strings.
    """
    all_stories = []
    for url in feed_urls:
        try:
            print(f"[ThreatIntel] Fetching feed: {url}")
            feed = feedparser.parse(url)

            for entry in feed.entries:
                link = entry.get("link")
                if not link:
                    continue

                # 1. Perform WHOIS check on the domain
                domain = urlparse(link).netloc
                print(f"[ThreatIntel] Verifying domain: {domain}")
                whois_info = whois_lookup_func(domain)

                # A simple legitimacy check (can be expanded)
                if "google" in whois_info.lower() or "microsoft" in whois_info.lower() or "blogspot.com" in whois_info.lower():
                    print(f"[ThreatIntel] Domain {domain} verified as legitimate.")

                    # 2. Process text in sandbox
                    title = sandbox_func(entry.get("title", ""))
                    summary = sandbox_func(entry.get("summary", ""))

                    story_text = f"Title: {title}\nSummary: {summary}"
                    all_stories.append(story_text)
                else:
                    print(f"[ThreatIntel] Domain {domain} could not be verified. Skipping. Info: {whois_info}")

            time.sleep(1)

        except Exception as e:
            print(f"[ThreatIntel] Error processing feed {url}: {e}")
            continue

    return all_stories

# Example Usage (for testing purposes)
if __name__ == '__main__':
    # Mock functions for testing
    def mock_whois(domain):
        if "google" in domain or "microsoft" in domain:
            return f"Domain: {domain}\nRegistrar: MarkMonitor Inc."
        return "Domain not found."

    def mock_sandbox(text):
        print(f"[MockSandbox] Processing: {text[:30]}...")
        return text

    print("--- Testing RSS Fetching with Zero-Trust Logic ---")
    latest_stories = fetch_stories_from_rss(SECURITY_RSS_FEEDS, mock_whois, mock_sandbox)

    if latest_stories:
        print(f"\nSuccessfully fetched and processed {len(latest_stories)} total stories.")
        print("Here is the first one:")
        print(latest_stories[0])
    else:
        print("Failed to fetch any stories.")
