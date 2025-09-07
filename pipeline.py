from GoogleNews import GoogleNews
from supabase import create_client
import os
from urllib.parse import urlparse, urlunparse, parse_qs

def clean_link(link):
    if not link or not link.startswith("http"):
        return None
    # Remove Google tracking/query params
    parsed = urlparse(link)
    clean_url = urlunparse((parsed.scheme, parsed.netloc, parsed.path, '', '', ''))
    return clean_url

def fetch_zomato_news(limit=10):
    googlenews = GoogleNews(lang="en")
    googlenews.search("Zomato")
    results = googlenews.result()

    news_list = []
    for r in results[:limit]:
        news_list.append({
            "title": r.get("title"),
            "source": r.get("media"),
            "date": r.get("date"),
            "link": clean_link(r.get("link")),
            "image_url": r.get("img")
        })
    return news_list

def insert_into_supabase(news_list):
    url = os.environ["SUPABASE_URL"]
    key = os.environ["SUPABASE_KEY"]
    supabase = create_client(url, key)
    return supabase.table("news").upsert(news_list, on_conflict="link").execute()

if __name__ == "__main__":
    news = fetch_zomato_news()
    if news:
        insert_into_supabase(news)
        print(f"✅ Inserted {len(news)} articles into Supabase with clean links.")
    else:
        print("⚠️ No news found.")
