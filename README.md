# Data Preprocessing Backend API

A professional, production-ready data preprocessing service API built with FastAPI. Perfect for AI/ML companies that need to clean, validate, and preprocess data before model training.

## 🚀 Features

- **Multi-format Support**: Process tabular (CSV, Excel, JSON, Parquet), image, and text data
- **Quality Metrics**: Automatic data quality scoring and issue detection
- **Multi-tenant**: API key-based authentication with quota management
- **Job Management**: Create, execute, cancel, and track preprocessing jobs
- **Rate Limiting**: Built-in rate limiting per API key
- **Background Processing**: Asynchronous job execution
- **Comprehensive Logging**: Detailed logs for debugging and monitoring

## 📋 Requirements

- Python 3.8+
- SQLite (default) or PostgreSQL
- 2GB+ RAM recommended

## 🛠️ Quick Start

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd data-preprocessing-backend
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Quick Setup

```bash
python scripts/quick_setup.py
```

This will:
- Create necessary directories
- Initialize the database
- Create a demo client account
- **Display your API key** (save it!)

### 5. Start the Server

```bash
python start.py
```

The API will be available at `http://localhost:8000`

### 6. Access Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📚 Documentation

- **[Setup Guide](SETUP.md)** - Detailed setup instructions
- **[How to Get API Key](HOW_TO_GET_API_KEY.md)** - API key management
- **[Next Steps](NEXT_STEPS.md)** - Post-setup recommendations

## 🔑 Getting an API Key

### Quick Method

```bash
python scripts/quick_setup.py
```

### Create New Client

```bash
python scripts/manage_clients.py create CLIENT_ID "Your Name" "your@email.com" --plan free
```

### Get Existing API Key

```bash
python scripts/manage_clients.py get CLIENT_ID --show-api-key
```

See [HOW_TO_GET_API_KEY.md](HOW_TO_GET_API_KEY.md) for more details.

## 💻 Usage Examples

### Upload a File

```bash
curl -X POST "http://localhost:8000/upload/tabular" \
  -H "X-API-Key: YOUR_API_KEY" \
  -F "file=@data.csv"
```

### Create and Execute Job

```bash
curl -X POST "http://localhost:8000/jobs/create?data_type=tabular&input_path=/path/to/file.csv&auto_execute=true" \
  -H "X-API-Key: YOUR_API_KEY"
```

### Check Job Status

```bash
curl "http://localhost:8000/jobs/JOB_ID/status" \
  -H "X-API-Key: YOUR_API_KEY"
```

### Download Processed File

```bash
curl "http://localhost:8000/jobs/JOB_ID/download" \
  -H "X-API-Key: YOUR_API_KEY" \
  -o processed_data.csv
```

## 🏗️ Project Structure

```
data-preprocessing-backend/
├── src/
│   ├── api/              # FastAPI routes and middleware
│   ├── core/             # Data processors (tabular, image, text)
│   ├── database/         # Database models and CRUD operations
│   ├── pipelines/        # Job management
│   └── utils/            # Utilities (logging, etc.)
├── scripts/              # Management scripts
├── tests/                # Test files
├── config/               # Configuration
├── data/                 # Data storage (gitignored)
└── logs/                 # Log files (gitignored)
```

## 🔧 Configuration

Create a `.env` file for environment-specific settings:

```bash
# Database
DATABASE_URL=sqlite:///./preprocessing.db

# CORS (comma-separated for production)
CORS_ORIGINS=http://localhost:3000

# Environment
ENVIRONMENT=development

# Logging
LOG_LEVEL=INFO
```

## 🧪 Testing

Run the complete workflow test:

```bash
python tests/test_complete_workflow.py YOUR_API_KEY
```

## 📊 Supported Data Types

- **Tabular**: CSV, Excel (.xlsx, .xls), JSON, Parquet
- **Image**: JPG, PNG, BMP, TIFF
- **Text**: TXT, DOC, DOCX, PDF

## 🔐 Security Features

- API key authentication
- Rate limiting (configurable per plan)
- CORS protection
- Input validation
- SQL injection protection (SQLAlchemy ORM)

## 📝 License

[Add your license here]

## 🤝 Contributing

[Add contributing guidelines here]

## 📞 Support

For issues and questions, please open an issue on GitHub.

---

**Made with ❤️ for AI/ML teams**
