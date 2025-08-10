# RAG Application API

This is a REST API version of the RAG (Retrieval-Augmented Generation) application that can ingest documents and answer questions based on the ingested content.

## Features

- **Document Ingestion**: Upload PDF and TXT files or ingest from a folder
- **Question Answering**: Query the ingested documents using natural language
- **Azure OpenAI Integration**: Uses Azure OpenAI for embeddings and chat completion
- **FastAPI Framework**: Modern, fast web framework with automatic API documentation
- **Docker Support**: Containerized for easy deployment
- **Azure Deployment Ready**: Includes deployment scripts and configurations

## API Endpoints

### Health & Status
- `GET /` - Root endpoint with basic info
- `GET /health` - Health check endpoint
- `GET /status` - Get current ingestor status

### Document Ingestion
- `POST /ingest/folder` - Ingest all documents from the knowledge_base folder
- `POST /ingest/upload` - Upload and ingest a single file (PDF or TXT)

### Querying
- `POST /query` - Query the ingested documents
- `DELETE /reset` - Reset the ingestor (clear all documents)

## Quick Start

### Local Development

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your Azure OpenAI credentials
   ```

3. **Run the API:**
   ```bash
   python src/app.py
   # Or using uvicorn directly:
   uvicorn src.app:app --host 0.0.0.0 --port 8000 --reload
   ```

4. **Access the API:**
   - API: http://localhost:8000
   - Interactive docs: http://localhost:8000/docs
   - Alternative docs: http://localhost:8000/redoc

### Using Docker

1. **Build and run with Docker:**
   ```bash
   docker build -t rag-api .
   docker run -p 8000:8000 --env-file .env rag-api
   ```

2. **Or use Docker Compose:**
   ```bash
   docker-compose up -d
   ```

### Deploy to Azure

1. **Using the deployment script:**
   ```bash
   ./deploy-to-azure.sh
   ```

2. **Or manually with Azure CLI:**
   ```bash
   # Create resources and deploy
   az group create --name rag-app-rg --location eastus
   az acr create --resource-group rag-app-rg --name ragappregistry --sku Basic
   az acr build --registry ragappregistry --image rag-api:latest .
   # ... (see deploy-to-azure.sh for complete commands)
   ```

## Usage Examples

### 1. Ingest Documents from Folder
```bash
curl -X POST "http://localhost:8000/ingest/folder"
```

### 2. Upload and Ingest a File
```bash
curl -X POST "http://localhost:8000/ingest/upload" \
  -F "file=@your_document.pdf"
```

### 3. Query Documents
```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are the main topics discussed?",
    "k": 5
  }'
```

### 4. Check Status
```bash
curl -X GET "http://localhost:8000/status"
```

## Testing

Run the test script to verify all endpoints:

```bash
python test_api.py
```

Make sure the API is running before executing tests.

## Environment Variables

Create a `.env` file with the following variables:

```env
AZURE_OPENAI_API_KEY=your_api_key_here
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_VERSION=2024-12-01-preview
```

## File Structure

```
├── src/
│   ├── app.py          # FastAPI application
│   ├── ingest.py       # Document ingestion logic
│   ├── rag.py          # RAG query processing
│   └── utils.py        # Utility functions
├── knowledge_base/     # Default folder for documents
├── uploads/           # Temporary storage for uploaded files
├── Dockerfile         # Docker configuration
├── docker-compose.yml # Docker Compose configuration
├── requirements.txt   # Python dependencies
├── test_api.py       # API testing script
└── deploy-to-azure.sh # Azure deployment script
```

## API Response Examples

### Query Response
```json
{
  "answer": "Based on the documents, the main topics include...",
  "message": "Query processed successfully"
}
```

### Status Response
```json
{
  "ingestor_initialized": true,
  "documents_count": 15,
  "index_built": true
}
```

## Troubleshooting

1. **API not starting**: Check if all dependencies are installed and environment variables are set
2. **Query failing**: Make sure documents are ingested first using `/ingest/folder` or `/ingest/upload`
3. **Upload failing**: Ensure file is PDF or TXT format and size is reasonable
4. **Azure deployment issues**: Verify Azure CLI is logged in and subscription is set correctly

## Production Considerations

- Set up proper authentication/authorization
- Configure HTTPS/SSL certificates
- Set up monitoring and logging
- Use a production WSGI server (already configured with uvicorn)
- Configure resource limits and auto-scaling
- Set up backup for persistent data if needed