
## 📈 Stock Market Pulse Analyzer

A full-stack web app that provides real-time stock market analysis using price momentum, latest news, and AI-powered pulse insights.

---

### 🛠️ Built With

* ⚙️ **Backend:** [FastAPI](https://fastapi.tiangolo.com/) – a high-performance Python framework for building APIs
* 💻 **Frontend:** [React.js](https://react.dev/) – a JavaScript library for building modern UIs
* 📦 **Data:** News scraping, price data, and momentum logic (custom Python)
* 🤖 **AI-Powered:** LLM-generated explanations for market sentiment

---

## 📸 Demo Preview

> 🔍 Enter a stock ticker (e.g. `AAPL`, `GOOG`, `TSLA`)
> 📊 See real-time momentum, pulse (bullish/bearish/neutral), and recent news
> 🧠 AI explains why the market pulse looks the way it does

---

## 🔧 Features

* 🔍 Ticker search with live fetch from backend
* 📈 Price momentum scoring (e.g. 5-day returns)
* 📰 Latest news aggregation for the stock
* 🤖 LLM-based explanation for sentiment
* 🎨 Clean, responsive UI built with React

---

## 📁 Project Structure

```
StockMarketAnalyzer/
│
├── backend/
│   ├── app.py                # FastAPI main app
│   └── services/             # Logic for momentum, news, LLM etc.
│
├── frontend/
│   ├── public/
│   └── src/
│       ├── App.js            # React main component
│       └── App.css           # Styling
│
├── .venv/                    # Python virtual environment
├── README.md
└── requirements.txt
```

---

## 🚀 Getting Started

Follow the steps below to set up both the backend and frontend.

---

## 🔙 Backend (FastAPI)

### 🧱 Requirements

* Python 3.9+
* `pip` or `pipenv`

### 🛠️ Setup

```bash
# 1. Clone the repo
git clone https://github.com/yourusername/StockMarketAnalyzer.git
cd StockMarketAnalyzer/backend

# 2. Create a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the FastAPI server
uvicorn app:app --reload
```

### ✅ API Endpoint

```http
GET /api/v1/market-pulse?ticker=AAPL
```

Returns:

```json
{
  "ticker": "AAPL",
  "pulse": "bullish",
  "as_of": "2025-07-15",
  "momentum": {
    "score": 12.4,
    "returns": [1.2, 2.1, 3.0, 2.9, 3.2]
  },
  "news": [
    {
      "title": "Apple releases new iPhone...",
      "url": "https://news.com/article",
      "published": "2025-07-15",
      "description": "Apple's stock rose after new release..."
    }
  ],
  "llm_explanation": "The momentum is strong and recent news indicates bullish sentiment."
}
```

---

## 🖥️ Frontend (React)

### 📦 Requirements

* Node.js (v18+)
* npm or yarn

### ⚙️ Setup

```bash
# 1. Go to frontend directory
cd ../frontend

# 2. Install dependencies
npm install

# 3. Start the development server
npm start
```

### 🌐 Open in browser

```
http://localhost:3000
```

You’ll see a simple UI to enter a stock ticker and view market pulse.

---

## 🔗 Connecting React + FastAPI

Make sure the API base URL in `App.js` matches your FastAPI backend:

```js
const API_BASE_URL = 'http://localhost:8000';
```

This allows React to fetch from the local backend.

If deploying, update it to your backend host, e.g. `https://api.yourdomain.com`.

---

## 🧪 Example Use

* Enter `AAPL` → Shows bullish pulse, 5-day momentum, news.
* Enter `TSLA` → Shows neutral or bearish pulse based on data.

---

## 🧹 Troubleshooting

| Problem                          | Solution                                                    |
| -------------------------------- | ----------------------------------------------------------- |
| `CORS error`                     | Enable CORS in FastAPI using `from fastapi.middleware.cors` |
| `Network error` in frontend      | Ensure FastAPI server is running on `localhost:8000`        |
| `ModuleNotFoundError` in backend | Check `.venv` is activated and `pip install` was successful |

---

## 🛡️ Tech Stack Summary

| Layer      | Stack                           |
| ---------- | ------------------------------- |
| Frontend   | React.js, JavaScript            |
| Backend    | FastAPI, Python                 |
| Data       | yfinance, requests, bs4         |
| LLM        | Gemini                          |
| Deployment | (Optional: Vercel + Railway)    |

---

## 🤝 Contribution

PRs welcome! If you’d like to contribute, feel free to fork and submit a pull request. Suggestions and issues are also appreciated.




