# Conversational AI Business Intelligence Dashboard

A full-stack application that converts natural language queries into interactive business dashboards using Google Gemini AI.

## Features

- Natural language query interface
- Automatic SQL generation using Gemini AI
- Smart chart type selection
- Interactive visualizations
- Real-time dashboard generation
- Query history tracking

## Tech Stack

- **Frontend**: React.js + Recharts
- **Backend**: Python FastAPI
- **LLM**: Google Gemini API
- **Database**: SQLite with sample business data

## Project Structure

```
├── backend/
│   ├── main.py              # FastAPI server
│   ├── database.py          # Database setup and queries
│   ├── llm_service.py       # Gemini AI integration
│   ├── chart_selector.py    # Smart chart selection logic
│   └── requirements.txt     # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── App.js           # Main React component
│   │   ├── components/
│   │   │   ├── QueryInput.js
│   │   │   ├── Dashboard.js
│   │   │   └── ChartRenderer.js
│   │   └── services/
│   │       └── api.js
│   ├── package.json
│   └── public/
├── database/
│   └── sample_data.sql      # Sample business data
└── .env.example             # Environment variables template
```

## Setup Instructions

### Prerequisites

- Node.js 16+ and npm
- Python 3.8+
- Google Gemini API key

### 1. Get Gemini API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Copy the key for later use

### 2. Backend Setup

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
echo GEMINI_API_KEY=your_api_key_here > .env

# Initialize database
python database.py

# Start backend server
python main.py
```

Backend will run on `http://localhost:8000`

### 3. Frontend Setup

```bash
cd frontend
npm install
npm start
```

Frontend will run on `http://localhost:3000`

## Usage

1. Open `http://localhost:3000` in your browser
2. Type a natural language query like:
   - "Show me total sales by region"
   - "Display monthly revenue trend for 2024"
   - "Compare product category performance by region"
3. The system will generate an interactive dashboard automatically

## Example Queries

1. **Simple aggregation**: "Show total sales by region"
2. **Time series**: "Display monthly revenue trend for the last year"
3. **Complex comparison**: "Compare product category performance by region"
4. **Top performers**: "Show top 5 products by revenue"
5. **Filtered analysis**: "What were the sales in Q3 2024?"

## API Endpoints

- `POST /api/query` - Process natural language query
- `GET /api/history` - Get query history
- `GET /api/health` - Health check

## Architecture

```
User Query → Gemini AI → SQL Generation → SQLite Query → 
Data Processing → Chart Selection → Dashboard Rendering
```

## Advanced Features

- Query history with timestamps
- Multiple chart types (bar, line, pie, table)
- Interactive tooltips and legends
- Responsive design
- Error handling and validation

## Troubleshooting

- **API Key Error**: Ensure your Gemini API key is correctly set in `.env`
- **CORS Issues**: Backend includes CORS middleware for localhost
- **Database Error**: Run `python database.py` to reinitialize the database

## License

MIT
