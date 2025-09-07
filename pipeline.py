from GoogleNews import GoogleNews
from supabase import create_client
from newspaper import Article
import os

# -----------------------------
# Utility Functions
# -----------------------------
def clean_link(link):
    """
    Clean GoogleNews/redirect link to get actual article URL.
    Removes Google tracking params and trailing slashes.
    """
    if not link or not link.startswith("http"):
        return None
    # Keep only the part before the first '&'
    clean_url = link.split('&')[0].rstrip('/')
    return clean_url

def fetch_article_image(url):
    """
    Fetches the top image from the article page using newspaper3k.
    Returns None if no image found.
    """
    try:
        article = Article(url)
        article.download()
        article.parse()
        return article.top_image or None
    except:
        return None

# -----------------------------
# Main Functions
# -----------------------------
def fetch_zomato_news(limit=10):
    """
    Fetches latest Zomato news from GoogleNews and returns a list of dicts.
    Each dict contains title, source, date, link, image_url.
    """
    googlenews = GoogleNews(lang="en")
    googlenews.search("Zomato")
    results = googlenews.result()

    news_list = []
    for r in results[:limit]:
        cleaned_link = clean_link(r.get("link"))
        if not cleaned_link:
            continue

        # Fetch real image from article page
        image_url = fetch_article_image(cleaned_link)

        news_list.append({
            "title": r.get("title"),
            "source": r.get("media"),
            "date": r.get("date"),
            "link": cleaned_link,
            "image_url": image_url
        })

    return news_list

def insert_into_supabase(news_list):
    """
    Upserts the list of news articles into Supabase 'news' table.
    Avoids duplicates using 'link' as unique constraint.
    """
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    supabase = create_client(url, key)
    return supabase.table("news").upsert(news_list, on_conflict="link").execute()

# -----------------------------
# Script Execution
# -----------------------------
if __name__ == "__main__":
    print("Fetching latest Zomato news...")
    news = fetch_zomato_news(limit=10)

    if news:
        insert_into_supabase(news)
        print(f"✅ Inserted {len(news)} articles into Supabase with real images.")
    else:
        print("⚠️ No news found.")
