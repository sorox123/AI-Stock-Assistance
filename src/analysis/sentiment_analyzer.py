"""
Sentiment Analysis Module
Analyzes news sentiment using VADER and NewsAPI
"""

import os
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import time


class SentimentAnalyzer:
    """Analyze news sentiment for stocks"""
    
    def __init__(self):
        """Initialize sentiment analyzer with NewsAPI"""
        self.news_api_key = os.getenv('NEWS_API_KEY')
        self.vader = SentimentIntensityAnalyzer()
        
        if not self.news_api_key or self.news_api_key.startswith('your_'):
            print("[WARN] NewsAPI key not configured - sentiment analysis disabled")
            self.enabled = False
        else:
            self.enabled = True
            print("[OK] Sentiment analyzer initialized")
    
    def fetch_news(self, symbol: str, days_back: int = 1) -> List[Dict]:
        """
        Fetch recent news articles for a symbol
        
        Args:
            symbol: Stock ticker
            days_back: Days of news to fetch
        
        Returns:
            List of news articles with title, description, source
        """
        if not self.enabled:
            return []
        
        try:
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_back)
            
            # NewsAPI endpoint
            url = "https://newsapi.org/v2/everything"
            
            params = {
                'apiKey': self.news_api_key,
                'q': symbol,
                'from': start_date.strftime('%Y-%m-%d'),
                'to': end_date.strftime('%Y-%m-%d'),
                'language': 'en',
                'sortBy': 'relevancy',
                'pageSize': 10
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('status') != 'ok':
                print(f"[WARN] NewsAPI returned status: {data.get('status')}")
                return []
            
            articles = []
            for article in data.get('articles', []):
                articles.append({
                    'title': article.get('title', ''),
                    'description': article.get('description', ''),
                    'source': article.get('source', {}).get('name', 'Unknown'),
                    'published_at': article.get('publishedAt', ''),
                    'url': article.get('url', '')
                })
            
            return articles
            
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Failed to fetch news for {symbol}: {e}")
            return []
        except Exception as e:
            print(f"[ERROR] Unexpected error fetching news: {e}")
            return []
    
    def analyze_text(self, text: str) -> Dict:
        """
        Analyze sentiment of text using VADER
        
        Args:
            text: Text to analyze
        
        Returns:
            Dictionary with sentiment scores
        """
        scores = self.vader.polarity_scores(text)
        
        # Determine sentiment label
        if scores['compound'] >= 0.05:
            label = 'positive'
        elif scores['compound'] <= -0.05:
            label = 'negative'
        else:
            label = 'neutral'
        
        return {
            'compound': scores['compound'],  # -1 to +1
            'positive': scores['pos'],
            'negative': scores['neg'],
            'neutral': scores['neu'],
            'label': label
        }
    
    def analyze_symbol(self, symbol: str, days_back: int = 1) -> Dict:
        """
        Analyze overall sentiment for a symbol based on recent news
        
        Args:
            symbol: Stock ticker
            days_back: Days of news to analyze
        
        Returns:
            Dictionary with sentiment analysis results
        """
        if not self.enabled:
            return {
                'enabled': False,
                'symbol': symbol,
                'sentiment_score': 0,
                'sentiment_label': 'neutral',
                'article_count': 0
            }
        
        # Fetch news articles
        articles = self.fetch_news(symbol, days_back)
        
        if not articles:
            return {
                'enabled': True,
                'symbol': symbol,
                'sentiment_score': 0,
                'sentiment_label': 'neutral',
                'article_count': 0,
                'message': 'No news articles found'
            }
        
        # Analyze sentiment for each article
        sentiments = []
        for article in articles:
            # Combine title and description for analysis
            text = f"{article['title']} {article['description']}"
            sentiment = self.analyze_text(text)
            sentiments.append(sentiment['compound'])
        
        # Calculate average sentiment
        avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0
        
        # Determine label
        if avg_sentiment >= 0.05:
            label = 'positive'
        elif avg_sentiment <= -0.05:
            label = 'negative'
        else:
            label = 'neutral'
        
        # Calculate sentiment distribution
        positive_count = sum(1 for s in sentiments if s >= 0.05)
        negative_count = sum(1 for s in sentiments if s <= -0.05)
        neutral_count = len(sentiments) - positive_count - negative_count
        
        return {
            'enabled': True,
            'symbol': symbol,
            'sentiment_score': round(avg_sentiment, 3),
            'sentiment_label': label,
            'article_count': len(articles),
            'positive_articles': positive_count,
            'negative_articles': negative_count,
            'neutral_articles': neutral_count,
            'recent_headlines': [a['title'] for a in articles[:3]]
        }
    
    def get_sentiment_signal(self, sentiment_score: float) -> str:
        """
        Convert sentiment score to trading signal
        
        Args:
            sentiment_score: Compound sentiment score (-1 to +1)
        
        Returns:
            Signal: 'bullish', 'bearish', or 'neutral'
        """
        if sentiment_score >= 0.2:
            return 'bullish'
        elif sentiment_score <= -0.2:
            return 'bearish'
        else:
            return 'neutral'


def test_sentiment_analysis():
    """Test sentiment analysis functionality"""
    print("\n" + "="*60)
    print("TESTING SENTIMENT ANALYSIS")
    print("="*60)
    
    analyzer = SentimentAnalyzer()
    
    if not analyzer.enabled:
        print("\n[SKIPPED] NewsAPI key not configured")
        print("To enable sentiment analysis:")
        print("1. Get free API key from https://newsapi.org")
        print("2. Add NEWS_API_KEY to your .env file")
        return
    
    # Test with popular stocks
    test_symbols = ['AAPL', 'TSLA']
    
    for symbol in test_symbols:
        print(f"\n[ANALYZING NEWS FOR {symbol}]")
        result = analyzer.analyze_symbol(symbol, days_back=1)
        
        print(f"  Articles Found: {result['article_count']}")
        print(f"  Sentiment Score: {result['sentiment_score']:+.3f}")
        print(f"  Sentiment Label: {result['sentiment_label'].upper()}")
        print(f"  Signal: {analyzer.get_sentiment_signal(result['sentiment_score']).upper()}")
        
        if result['article_count'] > 0:
            print(f"  Distribution: {result['positive_articles']} positive, "
                  f"{result['negative_articles']} negative, "
                  f"{result['neutral_articles']} neutral")
            
            print("\n  Recent Headlines:")
            for headline in result['recent_headlines']:
                print(f"    - {headline}")
        
        time.sleep(1)  # Rate limiting
    
    print("\n" + "="*60)
    print("SENTIMENT ANALYSIS TEST COMPLETE")
    print("="*60 + "\n")


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    test_sentiment_analysis()
