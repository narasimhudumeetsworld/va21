import feedparser
import time

# A list of security-related RSS feeds.
# In a real application, this would come from a config file or a database.
SECURITY_RSS_FEEDS = [
    "https://krebsonsecurity.com/feed/",
    "https://www.schneier.com/feed/",
    "https://feeds.feedburner.com/TheHackersNews",
    "https://threatpost.com/feed/"
]

def fetch_stories_from_rss(feed_urls):
    """
    Fetches the latest stories from a list of RSS feeds.

    :param feed_urls: A list of URLs for the RSS feeds.
    :return: A list of strings, where each string is a combination of
             the story's title and summary.
    """
    all_stories = []
    for url in feed_urls:
        try:
            print(f"Fetching feed: {url}")
            feed = feedparser.parse(url)

            for entry in feed.entries:
                # Combine title and summary for better context in the RAG.
                title = entry.get("title", "")
                summary = entry.get("summary", "")
                story_text = f"Title: {title}\nSummary: {summary}"
                all_stories.append(story_text)

            # Be a good internet citizen and don't spam requests.
            time.sleep(1)

        except Exception as e:
            print(f"Error fetching or parsing feed {url}: {e}")
            continue

    return all_stories

# Example Usage (for testing purposes)
if __name__ == '__main__':
    print("Fetching latest stories from security RSS feeds...")
    latest_stories = fetch_stories_from_rss(SECURITY_RSS_FEEDS)

    if latest_stories:
        print(f"\nSuccessfully fetched {len(latest_stories)} total stories.")
        print("Here are the first 5:")
        for i, story_text in enumerate(latest_stories[:5], 1):
            print(f"--- Story {i} ---\n{story_text}\n")
    else:
        print("Failed to fetch any stories.")
