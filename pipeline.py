from GoogleNews import GoogleNews
from supabase import create_client
import os


def fetch_zomato_news(limit=10):
    googlenews = GoogleNews(lang="en")
    googlenews.search("Zomato")
    results = googlenews.result()

    return [
        {
            "title": r.get("title"),
            "source": r.get("media"),
            "date": r.get("date"),
            "link": r.get("link"),
            "image_url": r.get("img")
        }
        for r in results[:limit]
    ]


def insert_into_supabase(news_list):
    url = os.environ["SUPABASE_URL"]
    key = os.environ["SUPABASE_KEY"]
    supabase = create_client(url, key)
    return supabase.table("news").insert(news_list).execute()


if __name__ == "__main__":
    news = fetch_zomato_news()
    if news:
        insert_into_supabase(news)
        print(f"✅ Inserted {len(news)} articles into Supabase.")
    else:
        print("⚠️ No news found.")
