#!/usr/bin/env python3
"""
Gurmukhi RAG System for Latest Punjabi Stories and Articles
Fetches and processes Punjabi content with bilingual support
"""

import requests
import feedparser
from bs4 import BeautifulSoup
import sqlite3
from datetime import datetime
from typing import List, Dict, Optional
import json
import re

class GurmukhiRAG:
    def __init__(self, db_path="gurmukhi_content.db"):
        self.db_path = db_path
        self.init_database()
        
        # Punjabi news sources and RSS feeds
        self.punjabi_sources = [
            {
                "name": "Ajit Daily",
                "rss": "https://www.ajitweekly.com/rss.xml",
                "language": "punjabi"
            },
            {
                "name": "Punjab Kesari",
                "rss": "https://www.punjabkesari.in/rss/punjab-news",
                "language": "punjabi"
            },
            {
                "name": "Jagbani",
                "rss": "https://www.jagbani.com/rss/punjab",
                "language": "punjabi"
            }
        ]
    
    def init_database(self):
        """Initialize database for storing Punjabi content"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS punjabi_articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title_punjabi TEXT,
                title_english TEXT,
                content_punjabi TEXT,
                content_english TEXT,
                source TEXT,
                url TEXT,
                difficulty_level INTEGER,
                gurmukhi_letters TEXT,
                created_date TEXT,
                category TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS vocabulary (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                word_punjabi TEXT,
                word_english TEXT,
                pronunciation TEXT,
                difficulty INTEGER,
                category TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def fetch_punjabi_content(self) -> List[Dict]:
        """Fetch latest Punjabi articles from RSS feeds"""
        articles = []
        
        for source in self.punjabi_sources:
            try:
                feed = feedparser.parse(source["rss"])
                
                for entry in feed.entries[:5]:  # Get latest 5 articles
                    article = {
                        "title": entry.title,
                        "link": entry.link,
                        "summary": getattr(entry, 'summary', ''),
                        "published": getattr(entry, 'published', ''),
                        "source": source["name"]
                    }
                    
                    # Fetch full content
                    content = self.extract_article_content(entry.link)
                    if content:
                        article["content"] = content
                        articles.append(article)
                        
            except Exception as e:
                print(f"Error fetching from {source['name']}: {e}")
                continue
        
        return articles
    
    def extract_article_content(self, url: str) -> Optional[str]:
        """Extract article content from URL"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove unwanted elements
            for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
                element.decompose()
            
            # Try to find main content
            content_selectors = [
                'article', '.article-content', '.post-content', 
                '.entry-content', '.content', 'main'
            ]
            
            content = ""
            for selector in content_selectors:
                elements = soup.select(selector)
                if elements:
                    content = elements[0].get_text(strip=True)
                    break
            
            if not content:
                # Fallback to body text
                content = soup.get_text(strip=True)
            
            return content[:2000]  # Limit content length
            
        except Exception as e:
            print(f"Error extracting content from {url}: {e}")
            return None
    
    def analyze_gurmukhi_content(self, text: str) -> Dict:
        """Analyze Gurmukhi text for learning purposes"""
        # Define Gurmukhi Unicode range
        gurmukhi_pattern = r'[\u0A00-\u0A7F]+'
        
        # Extract Gurmukhi text
        gurmukhi_matches = re.findall(gurmukhi_pattern, text)
        gurmukhi_text = ' '.join(gurmukhi_matches)
        
        # Count unique letters
        unique_letters = set()
        for char in gurmukhi_text:
            if '\u0A01' <= char <= '\u0A75':  # Gurmukhi letters range
                unique_letters.add(char)
        
        # Determine difficulty based on text complexity
        word_count = len(gurmukhi_text.split())
        letter_count = len(unique_letters)
        
        if word_count < 20 and letter_count < 15:
            difficulty = 1  # Beginner
        elif word_count < 50 and letter_count < 25:
            difficulty = 2  # Intermediate
        else:
            difficulty = 3  # Advanced
        
        return {
            "gurmukhi_text": gurmukhi_text,
            "unique_letters": list(unique_letters),
            "word_count": word_count,
            "letter_count": letter_count,
            "difficulty": difficulty
        }
    
    def translate_to_english(self, punjabi_text: str) -> str:
        """Translate Punjabi text to English (placeholder for actual translation service)"""
        # In a real implementation, this would use Google Translate API or similar
        # For now, return a placeholder
        return f"[English translation of: {punjabi_text[:50]}...]"
    
    def store_article(self, article_data: Dict):
        """Store processed article in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Analyze content
        analysis = self.analyze_gurmukhi_content(article_data.get('content', ''))
        
        # Translate title and content
        title_english = self.translate_to_english(article_data.get('title', ''))
        content_english = self.translate_to_english(analysis['gurmukhi_text'])
        
        cursor.execute('''
            INSERT INTO punjabi_articles 
            (title_punjabi, title_english, content_punjabi, content_english, 
             source, url, difficulty_level, gurmukhi_letters, created_date, category)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            article_data.get('title', ''),
            title_english,
            analysis['gurmukhi_text'],
            content_english,
            article_data.get('source', ''),
            article_data.get('link', ''),
            analysis['difficulty'],
            json.dumps(analysis['unique_letters']),
            str(datetime.now()),
            'news'
        ))
        
        conn.commit()
        conn.close()
    
    def get_articles_by_difficulty(self, difficulty: int) -> List[Dict]:
        """Retrieve articles by difficulty level"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT title_punjabi, title_english, content_punjabi, content_english,
                   source, difficulty_level, gurmukhi_letters
            FROM punjabi_articles 
            WHERE difficulty_level = ?
            ORDER BY created_date DESC
            LIMIT 10
        ''', (difficulty,))
        
        articles = []
        for row in cursor.fetchall():
            articles.append({
                'title_punjabi': row[0],
                'title_english': row[1],
                'content_punjabi': row[2],
                'content_english': row[3],
                'source': row[4],
                'difficulty': row[5],
                'letters': json.loads(row[6]) if row[6] else []
            })
        
        conn.close()
        return articles
    
    def create_learning_stories(self) -> List[Dict]:
        """Create kid-friendly learning stories from news content"""
        articles = self.get_articles_by_difficulty(1)  # Get beginner level content
        
        learning_stories = []
        for article in articles[:3]:  # Process top 3 articles
            # Simplify content for kids
            simplified_story = self.simplify_for_kids(article)
            learning_stories.append(simplified_story)
        
        return learning_stories
    
    def simplify_for_kids(self, article: Dict) -> Dict:
        """Simplify article content for children"""
        # This would use LLM to simplify content in real implementation
        return {
            'title_punjabi': article['title_punjabi'],
            'title_english': f"Story: {article['title_english']}",
            'content_punjabi': article['content_punjabi'][:200] + "...",
            'content_english': article['content_english'][:200] + "...",
            'difficulty': 1,
            'category': 'story'
        }
    
    def update_content_database(self):
        """Fetch and update content database"""
        print("Fetching latest Punjabi content...")
        articles = self.fetch_punjabi_content()
        
        for article in articles:
            self.store_article(article)
        
        print(f"Updated database with {len(articles)} new articles")
        return len(articles)

# Sample usage and testing
if __name__ == "__main__":
    rag = GurmukhiRAG()
    
    # Add some sample stories for testing
    sample_stories = [
        {
            "title": "ਚੰਗਾ ਬੱਚਾ",
            "content": "ਇੱਕ ਵਾਰ ਇੱਕ ਚੰਗਾ ਬੱਚਾ ਸੀ। ਉਹ ਰੋਜ਼ ਸਕੂਲ ਜਾਂਦਾ ਸੀ। ਉਸਦੇ ਮਾਤਾ-ਪਿਤਾ ਬਹੁਤ ਖੁਸ਼ ਸਨ।",
            "source": "Sample Story",
            "link": "sample"
        },
        {
            "title": "ਸੁੰਦਰ ਬਾਗ਼",
            "content": "ਬਾਗ਼ ਵਿੱਚ ਬਹੁਤ ਸਾਰੇ ਫੁੱਲ ਸਨ। ਤਿਤਲੀਆਂ ਉੱਡ ਰਹੀਆਂ ਸਨ। ਬੱਚੇ ਖੇਡ ਰਹੇ ਸਨ।",
            "source": "Sample Story",
            "link": "sample"
        }
    ]
    
    for story in sample_stories:
        rag.store_article(story)
    
    print("Sample stories added to database!")
