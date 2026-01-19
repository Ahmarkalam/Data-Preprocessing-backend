# Data Preprocessing Backend - Complete Setup Guide

## 🚀 Quick Start (Recommended for First Time)

### 1. Clone/Download the Project
```bash
cd data-preprocessing-backend
```

### 2. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Mac/Linux
# OR
venv\Scripts\activate  # On Windows
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run Quick Setup
```bash
python scripts/quick_setup.py
```

This will:
- Create all necessary directories
- Initialize the database
- Create a demo client account
- Give you an API key

### 5. Start the API Server
```bash
python start.py
```

### 6. Test the API
Visit: `http://localhost:8000/docs`

---

## 📚 Manual Setup (For Advanced Users)

### Step 1: Initialize Database
```bash
python scripts/init_db.py
```

### Step 2: Create a Client
```bash
python scripts/manage_clients.py create my_client "John Doe" "john@example.com" --plan basic
```

Save the API key that's displayed!

### Step 3: Start Server
```bash
python start.py
```

---

## 🔧 Client Management

### Create a Client
```bash
python scripts/manage_clients.py create CLIENT_ID NAME EMAIL [--company COMPANY] [--plan PLAN]
```

Plans: `free` (1GB), `basic` (10GB), `premium` (100GB)

### List All Clients
```bash
python scripts/manage_clients.py list
```

### Get Client Details
```bash
python scripts/manage_clients.py get CLIENT_ID [--show-api-key]
```

### Update Client
```bash
python scripts/manage_clients.py update CLIENT_ID [--name NAME] [--plan PLAN]
```

### Delete Client
```bash
python scripts/manage_clients.py delete CLIENT_ID
```

### Reset Monthly Quota
```bash
python scripts/manage_clients.py reset-quota CLIENT_ID
```

---

## 🧪 Testing

### Complete Workflow Test
```bash
python tests/test_complete_workflow.py YOUR_API_KEY
```

This tests:
- File upload
- Job creation
- Job execution
- Quality metrics
- File download

---

## 📖 API Usage Examples

### Upload a File
```bash
curl -X POST "http://localhost:8000/upload/tabular" \
  -H "X-API-Key: YOUR_API_KEY" \
  -F "file=@/path/to/data.csv"
```

### Create and Execute Job
```bash
curl -X POST "http://localhost:8000/jobs/create?data_type=tabular&input_path=/path/to/uploaded/file&auto_execute=true" \
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

---

## 🗄️ Database Management

### Reset Database (⚠️ Deletes All Data)
```bash
python scripts/reset_db.py
```

---

## 📁 Project Structure