from GoogleNews import GoogleNews
from supabase import create_client
import os

def clean_link(link):
    if not link or not link.startswith("http"):
        return None
    clean_url = link.split('&')[0]  # Remove Google tracking params
    return clean_url.rstrip('/')
    
def clean_image_url(img_url):
    """
    Returns the image URL if valid, else None.
    Filters out base64 placeholders or empty strings.
    """
    if not img_url:
        return None
    # Filter out base64 1x1 gifs
    if img_url.startswith("data:image/gif;base64,"):
        return None
    return img_url

def fetch_zomato_news(limit=10):
    googlenews = GoogleNews(lang="en")
    googlenews.search("Zomato")
    results = googlenews.result()

    news_list = []
    for r in results[:limit]:
        cleaned = clean_link(r.get("link"))
        cleaned_img = clean_image_url(r.get("img"))
        if cleaned:
            news_list.append({
                "title": r.get("title"),
                "source": r.get("media"),
                "date": r.get("date"),
                "link": cleaned,
                "image_url": cleaned_img
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
