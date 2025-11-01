# Sales & Website Analytics Chat Assistant

Natural language chat interface for querying sales and website traffic data. Ask questions in plain English and receive insights with charts and natural language summaries.

## 🚀 Quick Start (Docker - Recommended)

**Want to run the app in 2 minutes with no setup?**

See **[QUICKSTART.md](QUICKSTART.md)** or **[README-DOCKER.md](README-DOCKER.md)**

No API keys required! Uses local LLM (Ollama) and includes sample data.

```bash
# Windows
start-docker.bat

# Linux/Mac
./start-docker.sh
```

Then open: http://localhost:5173

## Overview

This system enables business users to access sales and website analytics data through conversational queries, without needing SQL knowledge. Built with constitutional principles ensuring security, safety, and consistency.

## Features

### ✅ User Story 1 - Sales Metrics (MVP) - IMPLEMENTED

- Query sales data with natural language
- Get text summaries with charts
- Date range queries ("What were sales last week?")
- Top products analysis ("Show me top selling products")
- Revenue aggregations ("Total revenue this month")

### 🚧 User Story 2 - Website Traffic (Pending)

- Visitor count and trends
- Peak traffic time analysis
- Traffic source breakdown
- Period-over-period comparisons

### 🚧 User Story 3 - Conversion Insights (Pending)

- Conversion rate calculations
- Revenue per visitor metrics
- Multi-metric business summaries

## Architecture

### Constitutional Principles

1. **Single Database Source of Truth** - One authoritative database
2. **English Chat UX** - Natural language only, no SQL exposure
3. **Template-Only SQL** - Pre-approved, version-controlled templates
4. **No Automatic JOINs** - Explicit JOIN logic in templates
5. **LLM Parameter Filling** - LLM selects templates and fills parameters only
6. **Strict Safety Controls** - Whitelists, LIMITs, read-only, timeouts, rate limiting
7. **Consistent Output Formats** - Standardized text and chart responses

### Technology Stack

**Backend:**
- Python 3.11+
- FastAPI (web framework)
- PostgreSQL (database)
- OpenAI/Anthropic (LLM)

**Frontend:**
- React + TypeScript
- Recharts (visualizations)
- Axios (API client)

### Pipeline Flow

```
User Query
    ↓
[Rate Limiting]
    ↓
[Intent Classification] → sales/traffic/conversion
    ↓
[Template Selection] → Match to SQL template
    ↓
[Parameter Extraction] → Extract dates, filters
    ↓
[Parameter Validation] → Type & range checking
    ↓
[SQL Execution] → Read-only query with LIMIT
    ↓
[Response Formatting] → Text + Chart
    ↓
[Citation Generation] → Data source attribution
    ↓
Response (JSON)
```

## Installation

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 14+

### Backend Setup

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment variables (create `.env`):
```bash
# Database (read-only credentials)
DATABASE_URL=postgresql://readonly_user:password@localhost:5432/analytics_db

# LLM API Keys
OPENAI_API_KEY=your_openai_key
# or
ANTHROPIC_API_KEY=your_anthropic_key

# Safety Settings
QUERY_TIMEOUT_SECONDS=30
DEFAULT_ROW_LIMIT=100
MAX_ROW_LIMIT=1000
RATE_LIMIT_PER_MINUTE=10
```

3. Start the API server:
```bash
python src/main.py
# or
uvicorn src.main:app --reload
```

API runs on `http://localhost:8000`

### Frontend Setup

1. Install Node dependencies:
```bash
cd frontend
npm install
```

2. Start development server:
```bash
npm run dev
```

Frontend runs on `http://localhost:5173`

## Usage

### Example Queries

**Sales:**
- "What were total sales this month?"
- "Show me top 5 selling products"
- "Sales from October 1 to October 15"
- "Average transaction value this year"

**Traffic (not yet implemented):**
- "How many visitors yesterday?"
- "What's the trend in website visits this month?"
- "Where are our visitors from?"

**Conversion (not yet implemented):**
- "What's our conversion rate this week?"
- "Revenue per visitor this month"
- "How is the business doing?"

### API Endpoints

#### POST `/api/query/sales`

Query sales data with natural language.

**Request:**
```json
{
  "query": "What were sales last week?",
  "user_id": "user123"
}
```

**Response:**
```json
{
  "success": true,
  "text_response": "Total sales: $12,450.00 across 7 day(s). Average daily revenue: $1,778.57.",
  "chart_data": {
    "type": "bar",
    "labels": ["2024-10-24", "2024-10-25", ...],
    "datasets": [...]
  },
  "citation": "Source: sales_transactions | Date range: 2024-10-24 to 2024-10-31 | 7 record(s) | Retrieved: 2024-10-31 12:34:56",
  "template_id": "sales_by_date_range"
}
```

## SQL Templates

Templates are stored in `templates/sql/` as JSON files.

### Creating New Templates

1. Define template in `templates/sql/your_template.json`:
```json
{
  "template_id": "your_template",
  "description": "What this template does",
  "category": "sales",
  "sql_structure": "SELECT ... WHERE ... {parameter}",
  "parameters": [...],
  "whitelisted_tables": ["sales_transactions"],
  "chart_type": "bar"
}
```

2. Add few-shot examples in `templates/few_shot_examples.json`

3. Validate template with `tools/validate_templates.py` (not yet implemented)

## Security & Safety

### Database Safety
- **Read-only credentials** - No data modification possible
- **Connection isolation** - Read-only transactions
- **Query timeouts** - 30 second limit (configurable)

### SQL Safety
- **Template-only** - No dynamic SQL generation
- **Blocked keywords** - DROP, DELETE, UPDATE, INSERT, etc.
- **LIMIT enforcement** - All queries capped at 1000 rows max
- **No subqueries** - Prevents nested query attacks
- **No wildcards** - SELECT * is blocked

### Access Control
- **Table whitelist** - Only sales_transactions and website_visits
- **Column whitelist** - Specified per template
- **Rate limiting** - 10 queries per minute per user
- **Parameter validation** - Type and range checking

### Audit & Monitoring
- **Complete logging** - All queries, parameters, results
- **Template tracking** - Which template was selected
- **Performance metrics** - Execution time, row counts
- **Error tracking** - Validation failures, timeouts

## Development Status

### Implemented (33/71 tasks - 46%)

- ✅ Phase 1: Setup (5/5)
- ✅ Phase 2: Foundational (15/15)
- ✅ Phase 3: User Story 1 - Sales Queries MVP (13/13)

### Pending (38/71 tasks)

- ⏳ Phase 4: User Story 2 - Traffic Analysis (14 tasks)
- ⏳ Phase 5: User Story 3 - Conversion Insights (14 tasks)
- ⏳ Phase 6: Polish & Cross-Cutting (10 tasks)

## Testing

### Independent Test - User Story 1

Ask the question: **"What were total sales this month?"**

Expected response:
- Text summary with total sales amount
- Bar chart showing daily breakdown
- Data source citation

### Running Tests

```bash
# Backend tests (not yet implemented)
pytest tests/

# Frontend tests (not yet implemented)
cd frontend
npm test
```

## Configuration

See `config/settings.py` for all configuration options:

- Database connection
- LLM settings (model, temperature)
- Safety controls (limits, timeouts, rate limits)
- Whitelisted tables
- Blocked SQL keywords
- CORS settings

## Project Structure

```
TalkingLakeHouseHC/
├── src/                      # Backend source
│   ├── api/                  # API endpoints
│   ├── database/             # DB connection & query execution
│   ├── security/             # Whitelist & SQL validation
│   ├── validation/           # Parameter validation
│   ├── pipeline/             # LLM pipeline components
│   ├── templates/            # Template loader
│   ├── visualization/        # Chart selection
│   ├── formatting/           # Text & citation formatting
│   ├── context/              # Conversation context
│   ├── errors/               # Error messages
│   ├── logging/              # Audit logging
│   └── main.py               # FastAPI app
├── frontend/                 # React frontend
│   └── src/
│       ├── components/       # React components
│       ├── charts/           # Chart components
│       └── handlers/         # Response handlers
├── templates/                # SQL templates
│   ├── sql/                  # Template JSON files
│   └── few_shot_examples.json
├── config/                   # Configuration
│   └── settings.py
├── tests/                    # Tests
├── specs/                    # Feature specifications
└── requirements.txt          # Python dependencies
```

## Contributing

1. All SQL templates must be reviewed and approved
2. Follow constitutional principles
3. Add few-shot examples for new query patterns
4. Include error handling and user-friendly messages
5. Update audit logging for new features

## License

[Your License Here]

## Support

For issues or questions, please open an issue on GitHub or contact the development team.
