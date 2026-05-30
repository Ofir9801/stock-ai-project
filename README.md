# 📈 AI Stock Research Dashboard

> A full-stack web application that combines real-time financial data with AI-powered sentiment analysis, built with Python, FastAPI, and Streamlit.

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green?style=flat-square&logo=fastapi)
![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-red?style=flat-square&logo=streamlit)
![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)

---

## 🚀 Live Demo

👉 **[View Live App](https://your-app.onrender.com)** ← *(יעודכן אחרי deploy)*

---

## 📸 Screenshots

> *(תוסיף צילום מסך של האפליקציה כאן — לוחצים Print Screen בזמן שהאפליקציה פתוחה)*

---

## ✨ Features

- **Real-time stock data** — Fetches live prices and 30-day price history via `yfinance`
- **AI-powered sentiment analysis** — Analyzes company news and fundamentals using Claude AI
- **Interactive charts** — Visualizes price trends with Plotly
- **Business summary** — Auto-fetches company description and key metrics
- **Clean REST API** — Modular FastAPI backend with clear service separation

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Frontend | Streamlit + Plotly | Interactive UI & charts |
| Backend | FastAPI + Uvicorn | REST API server |
| Data | yFinance + Pandas | Financial data fetching & processing |
| AI | OpenAI API (GPT-4o) | Sentiment analysis & research |
| Config | python-dotenv | Secure environment variable management |
| Deploy | Render / Streamlit Cloud | Cloud hosting |

---

## 📁 Project Structure

```
stock-ai-dashboard/
├── app/
│   ├── main.py               # FastAPI server & routes
│   └── services/
│       ├── finance_service.py  # yFinance data fetching
│       └── ai_service.py       # Claude AI integration
├── dashboard.py              # Streamlit frontend
├── requirements.txt
├── .env.example              # Environment variable template
├── .gitignore
└── README.md
```

---

## ⚡ Quick Start

### Prerequisites
- Python 3.10+
- An Openai API key 

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/ofir9801/stock-ai-dashboard.git
cd stock-ai-dashboard

# 2. Create and activate virtual environment
python -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate      # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cp .env.example .env
# Add your API key to .env:
# ANTHROPIC_API_KEY=your_key_here
```

### Running the App

```bash
# Terminal 1 — Start the backend
uvicorn app.main:app --reload

# Terminal 2 — Start the frontend
streamlit run dashboard.py
```

Open your browser at `http://localhost:8501` 🎉

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/stock/{ticker}` | Get stock data + AI analysis for a ticker symbol |
| `GET` | `/health` | Health check |

**Example:**
```bash
curl http://localhost:8000/stock/AAPL
```

**Response:**
```json
{
  "symbol": "AAPL",
  "current_price": 189.5,
  "sentiment": "Bullish",
  "ai_analysis": "Apple shows strong fundamentals with...",
  "history": { ... }
}
```

---

## 🔐 Environment Variables

Create a `.env` file based on `.env.example`:

```env
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

> ⚠️ Never commit your `.env` file to Git. It's already in `.gitignore`.

---

## 🗺️ Roadmap

- [x] Real-time stock price fetching
- [x] 30-day historical chart
- [x] AI sentiment analysis
- [x] Business summary display
- [ ] News feed integration (NewsAPI)
- [ ] Multi-stock comparison
- [ ] Portfolio tracker
- [ ] Price alerts via email

---

## 🤝 Contributing

Pull requests are welcome. For major changes, please open an issue first.

---

## 📄 License

MIT © [Your Name](https://github.com/ofir9801)

---

*Built as a portfolio project to explore the intersection of financial data and AI-powered analysis.*
