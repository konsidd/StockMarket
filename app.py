from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
import yfinance as yf
import google.generativeai as genai
import requests
import os
import asyncio
from datetime import datetime
from groq import Groq
import uvicorn
import json
from fastapi.middleware.cors import CORSMiddleware


# Remove proxy environment variables
proxy_vars = ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy', 'ALL_PROXY', 'all_proxy']
for var in proxy_vars:
    if var in os.environ:
        del os.environ[var]

# API Keys - In production, use environment variables
GROQ_API_KEY = "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"
NEWS_API_KEY = "b93b1f7dd17a46c8b88cd0e5aa2deab7"
GEMINI_API_KEY = "AIzaSyDHpQGHnSMjiMCh-9iOLpwgD46P7MfupNw"

# Configure APIs
genai.configure(api_key=GEMINI_API_KEY)
groq_client = Groq(api_key=GROQ_API_KEY)

# FastAPI app
app = FastAPI(
    title="Stock Market Pulse API",
    description="Get real-time stock analysis with momentum, news, and AI-powered pulse recommendations",
    version="1.0.0"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React's dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models for response structure
class MomentumData(BaseModel):
    returns: List[float]
    score: float


class NewsItem(BaseModel):
    title: str
    description: str
    url: str
    published: str


class MarketPulseResponse(BaseModel):
    ticker: str
    as_of: str
    momentum: MomentumData
    news: List[NewsItem]
    pulse: str
    llm_explanation: str


class HealthCheck(BaseModel):
    status: str
    timestamp: str
    services: dict


# Core business logic functions
async def get_price_momentum(ticker_symbol: str) -> tuple[Optional[dict], Optional[str]]:
    """Get last 5 trading days returns and momentum score"""
    try:
        ticker = yf.Ticker(ticker_symbol)
        hist = ticker.history(period="10d")

        if len(hist) < 5:
            return None, "Insufficient data for momentum calculation"

        # Get last 5 trading days
        last_5_days = hist.tail(5)

        # Calculate daily returns
        daily_returns = []
        prices = last_5_days['Close'].tolist()

        for i in range(1, len(prices)):
            daily_return = ((prices[i] - prices[i - 1]) / prices[i - 1]) * 100
            daily_returns.append(round(daily_return, 2))

        # Calculate momentum score (average of 5-day returns)
        momentum_score = sum(daily_returns) / len(daily_returns) if daily_returns else 0

        momentum_data = {
            'returns': daily_returns,
            'score': round(momentum_score, 2)
        }

        return momentum_data, None

    except Exception as e:
        return None, f"Error calculating momentum: {e}"


async def get_news_feed(ticker_symbol: str) -> tuple[List[dict], Optional[str]]:
    """Get latest 5 news headlines from NewsAPI"""
    try:
        # Get company name for better search
        ticker = yf.Ticker(ticker_symbol)
        company_name = ticker.info.get('longName', ticker_symbol)

        # NewsAPI endpoint
        url = "https://newsapi.org/v2/everything"

        params = {
            'q': f"{company_name} OR {ticker_symbol}",
            'sortBy': 'publishedAt',
            'pageSize': 5,
            'language': 'en',
            'apiKey': NEWS_API_KEY
        }

        response = requests.get(url, params=params)
        response.raise_for_status()

        news_data = response.json()

        if news_data['status'] == 'ok' and news_data['totalResults'] > 0:
            headlines = []
            for article in news_data['articles']:
                headlines.append({
                    'title': article['title'],
                    'description': article['description'] or 'No description available',
                    'url': article['url'],
                    'published': article['publishedAt'][:10]  # Just the date
                })
            return headlines, None
        else:
            return [], "No news found"

    except Exception as e:
        return [], f"Error fetching news: {e}"


async def get_ai_pulse_analysis(ticker_symbol: str, momentum_data: dict, news_headlines: List[dict]) -> tuple[str, str]:
    """Get AI-powered pulse analysis and recommendation"""
    try:
        # Get basic stock info
        ticker = yf.Ticker(ticker_symbol)
        stock_info = ticker.info
        company_name = stock_info.get("longName", ticker_symbol)
        stock_price = stock_info.get("currentPrice") or stock_info.get("regularMarketPrice", "N/A")

        # Create analysis prompt
        prompt_parts = [
            f"**STOCK PULSE ANALYSIS REQUEST**",
            f"Company: {company_name} ({ticker_symbol})",
            f"Current Price: ${stock_price}",
            f"",
            f"**MOMENTUM DATA:**",
            f"- 5-Day Returns: {momentum_data['returns']}%",
            f"- Momentum Score: {momentum_data['score']}%",
            f"",
            f"**NEWS HEADLINES:**"
        ]

        # Add news sentiment
        for i, headline in enumerate(news_headlines, 1):
            prompt_parts.append(f"{i}. {headline['title']}")

        prompt_parts.extend([
            f"",
            f"**ANALYSIS REQUEST:**",
            f"Based on the momentum and news data above, provide:",
            f"",
            f"1. **PULSE CLASSIFICATION**: Choose EXACTLY ONE word:",
            f"   - bullish (strong positive signals)",
            f"   - neutral (mixed signals)",
            f"   - bearish (negative signals)",
            f"",
            f"2. **EXPLANATION**: One concise sentence explaining the pulse decision based on:",
            f"   - Momentum score interpretation",
            f"   - News sentiment impact",
            f"",
            f"Format your response as:",
            f"PULSE: [bullish/neutral/bearish]",
            f"EXPLANATION: [your explanation]"
        ])

        prompt = "\n".join(prompt_parts)

        # Get Gemini analysis
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(prompt)

        response_text = response.text.strip()

        # Parse response
        pulse = "neutral"  # default
        explanation = "Unable to generate explanation"

        lines = response_text.split('\n')
        for line in lines:
            if line.startswith('PULSE:'):
                pulse_text = line.replace('PULSE:', '').strip().lower()
                if pulse_text in ['bullish', 'neutral', 'bearish']:
                    pulse = pulse_text
            elif line.startswith('EXPLANATION:'):
                explanation = line.replace('EXPLANATION:', '').strip()

        return pulse, explanation

    except Exception as e:
        return "neutral", f"Error in AI analysis: {e}"


# API Routes
@app.get("/", response_model=dict)
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Stock Market Pulse API",
        "version": "1.0.0",
        "endpoints": {
            "market_pulse": "/api/v1/market-pulse?ticker=TICKER",
            "health": "/health"
        }
    }


@app.get("/health", response_model=HealthCheck)
async def health_check():
    """Health check endpoint"""
    services = {}

    # Test yfinance
    try:
        test_ticker = yf.Ticker("AAPL")
        test_info = test_ticker.info
        services["yfinance"] = "connected"
    except Exception as e:
        services["yfinance"] = f"error: {str(e)}"

    # Test Groq
    try:
        test_response = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": "test"}],
            model="llama3-70b-8192",
            max_tokens=5
        )
        services["groq"] = "connected"
    except Exception as e:
        services["groq"] = f"error: {str(e)}"

    # Test Gemini
    try:
        test_model = genai.GenerativeModel("gemini-2.0-flash")
        test_response = test_model.generate_content("test")
        services["gemini"] = "connected"
    except Exception as e:
        services["gemini"] = f"error: {str(e)}"

    # Test News API
    try:
        test_url = "https://newsapi.org/v2/everything"
        test_params = {
            'q': 'AAPL',
            'pageSize': 1,
            'apiKey': NEWS_API_KEY
        }
        test_response = requests.get(test_url, params=test_params)
        test_response.raise_for_status()
        services["news_api"] = "connected"
    except Exception as e:
        services["news_api"] = f"error: {str(e)}"

    return HealthCheck(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        services=services
    )


@app.get("/api/v1/market-pulse", response_model=MarketPulseResponse)
async def get_market_pulse(ticker: str = Query(..., description="Stock ticker symbol (e.g., MSFT, AAPL, NVDA)")):
    """
    Get comprehensive market pulse analysis for a stock ticker

    Returns:
    - Momentum data (5-day returns and score)
    - Latest news headlines
    - AI-powered pulse classification (bullish/neutral/bearish)
    - LLM explanation of the analysis
    """
    try:
        ticker = ticker.upper()

        # Validate ticker exists
        try:
            test_ticker = yf.Ticker(ticker)
            test_info = test_ticker.info
            if 'symbol' not in test_info and 'shortName' not in test_info:
                raise HTTPException(status_code=404, detail=f"Ticker '{ticker}' not found")
        except Exception:
            raise HTTPException(status_code=404, detail=f"Ticker '{ticker}' not found")

        # Get momentum data
        momentum_data, momentum_error = await get_price_momentum(ticker)
        if momentum_error:
            raise HTTPException(status_code=500, detail=f"Momentum calculation error: {momentum_error}")

        # Get news data
        news_headlines, news_error = await get_news_feed(ticker)
        if news_error:
            # Don't fail completely if news fails, just log it
            news_headlines = []

        # Get AI pulse analysis
        pulse, explanation = await get_ai_pulse_analysis(ticker, momentum_data, news_headlines)

        # Format response
        response = MarketPulseResponse(
            ticker=ticker,
            as_of=datetime.now().strftime("%Y-%m-%d"),
            momentum=MomentumData(
                returns=momentum_data['returns'],
                score=momentum_data['score']
            ),
            news=[
                NewsItem(
                    title=item['title'],
                    description=item['description'],
                    url=item['url'],
                    published=item['published']
                ) for item in news_headlines
            ],
            pulse=pulse,
            llm_explanation=explanation
        )

        return response

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return {"error": "Not found", "detail": str(exc.detail)}


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return {"error": "Internal server error", "detail": str(exc.detail)}


# Run the application
if __name__ == "__main__":
    print("🚀 Starting Stock Market Pulse API...")
    print("📊 Available endpoints:")
    print("   - GET /api/v1/market-pulse?ticker=MSFT")
    print("   - GET /health")
    print("   - GET /")
    print("\n🌐 Access the API at: http://localhost:8000")
    print("📚 Interactive docs at: http://localhost:8000/docs")

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )