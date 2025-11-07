# Modular RAG API

A FastAPI backend implementing the Modular RAG framework with JWT authentication.

## Features

- JWT-based authentication system
- Modular RAG implementation with 6 core modules:
  - Indexing Module
  - Pre-retrieval Module  
  - Retrieval Module
  - Post-retrieval Module
  - Generation Module
- Integration with Pinecone vector database
- Google Gemini for embeddings and text generation
- Clean architecture with separation of concerns

## Project Structure

```
api/
├── main.py                 # FastAPI application entry point
├── controller/            # Business logic layer
├── lib/                  # Configuration and utilities
├── routes/               # API endpoints
├── schema/               # Pydantic models
├── service/              # External service integrations
├── .env                  # Environment variables
└── requirements.txt      # Python dependencies
```

## Setup

1. Install dependencies:
```bash
uv sync
```

2. Configure environment variables in `.env`:
```bash
JWT_SECRET_KEY=your-secret-key
PINECONE_API_KEY=your-pinecone-key
GOOGLE_API_KEY=your-google-key
```

3. Run the application:
```bash
uv run python main.py
```

The API will be available at `http://localhost:8000`

## API Endpoints

### Authentication
- `POST /auth/signup` - Register a new user
- `POST /auth/login` - Login and get access token
- `GET /auth/me` - Get current user info (protected)

### RAG Operations
- `POST /rag/index-document` - Index a document (protected)
- `POST /rag/query` - Query documents using RAG (protected)
- `GET /rag/health` - RAG service health check

## Development

The system uses a simple in-memory user database for development. In production, replace this with a proper database solution.