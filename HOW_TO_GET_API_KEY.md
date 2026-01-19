# 🔑 How to Get an API Key

There are **3 ways** to get an API key for the Data Preprocessing API:

---

## **Method 1: Quick Setup (Recommended for First Time)**

This is the easiest way if you're setting up for the first time:

```bash
python scripts/quick_setup.py
```

This will:
- Create all necessary directories
- Initialize the database
- Prompt you to create a demo client
- **Display your API key immediately**

**Example output:**
```
============================================================
CLIENT CREDENTIALS
============================================================
Client ID:  demo_client
API Key:    AbC123XyZ456DeF789GhI012JkL345MnO678PqR901StU234
Plan:       free
Quota:      1000 MB/month
============================================================
```

---

## **Method 2: Create a New Client**

Use the client management script to create a new client:

```bash
python scripts/manage_clients.py create CLIENT_ID "Your Name" "your@email.com" --plan free
```

**Options:**
- `CLIENT_ID` - A unique identifier (e.g., `my_client`, `test_user`)
- `"Your Name"` - Your full name
- `"your@email.com"` - Your email address
- `--plan` - Choose: `free` (1GB), `basic` (10GB), or `premium` (100GB)
- `--company` - Optional company name

**Example:**
```bash
python scripts/manage_clients.py create john_doe "John Doe" "john@example.com" --plan basic --company "Acme Corp"
```

**Output:**
```
✅ Client created successfully!

============================================================
Client ID:      john_doe
Name:           John Doe
Email:          john@example.com
Company:        Acme Corp
Plan:           basic
Monthly Quota:  10000 MB
API Key:        XyZ789AbC123DeF456GhI789JkL012MnO345PqR678
============================================================

⚠️  IMPORTANT: Save the API key securely!
   It will be needed for authentication.
```

---

## **Method 3: Get Existing Client's API Key**

If you already have a client but forgot the API key:

```bash
python scripts/manage_clients.py get CLIENT_ID --show-api-key
```

**Example:**
```bash
python scripts/manage_clients.py get demo_client --show-api-key
```

**Output:**
```
============================================================
CLIENT DETAILS
============================================================
Client ID:        demo_client
Name:             Demo User
Email:            demo@example.com
...
API Key:          AbC123XyZ456DeF789GhI012JkL345MnO678PqR901StU234
```

**Note:** Without `--show-api-key`, the API key will be hidden for security.

---

## **Method 4: List All Clients**

To see all clients (without API keys):

```bash
python scripts/manage_clients.py list
```

This shows:
- Client ID
- Name
- Email
- Plan
- Active status

Then use Method 3 to get a specific client's API key.

---

## **Method 5: Via API Endpoint**

You can also create a client via the API (if you have admin access):

```bash
curl -X POST "http://localhost:8000/clients/" \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": "api_client",
    "name": "API User",
    "email": "api@example.com",
    "plan_type": "free"
  }'
```

The response includes the `api_key` field.

---

## **Using Your API Key**

Once you have your API key, use it in API requests:

### **cURL Example:**
```bash
curl -H "X-API-Key: YOUR_API_KEY_HERE" \
  http://localhost:8000/jobs/
```

### **Python Example:**
```python
import requests

headers = {"X-API-Key": "YOUR_API_KEY_HERE"}
response = requests.get("http://localhost:8000/jobs/", headers=headers)
print(response.json())
```

### **In Browser (Swagger UI):**
1. Go to `http://localhost:8000/docs`
2. Click "Authorize" button (top right)
3. Enter your API key in the `X-API-Key` field
4. Click "Authorize"

---

## **Security Tips**

1. **Save your API key securely** - You won't be able to retrieve it later (only regenerate)
2. **Don't commit API keys to git** - Add them to `.gitignore`
3. **Use environment variables** in production:
   ```bash
   export API_KEY="your_api_key_here"
   ```
4. **Rotate keys regularly** - Create new clients and delete old ones if needed

---

## **Troubleshooting**

### "Client not found"
- Make sure you're using the correct Client ID
- List all clients: `python scripts/manage_clients.py list`

### "Invalid API key"
- Check for typos (API keys are case-sensitive)
- Make sure you're including the `X-API-Key` header
- Verify the client is active: `python scripts/manage_clients.py get CLIENT_ID`

### "Database not initialized"
```bash
python scripts/init_db.py
```

---

## **Quick Reference**

| Command | Purpose |
|---------|---------|
| `python scripts/quick_setup.py` | First-time setup + get API key |
| `python scripts/manage_clients.py create ...` | Create new client + get API key |
| `python scripts/manage_clients.py get CLIENT_ID --show-api-key` | Get existing API key |
| `python scripts/manage_clients.py list` | List all clients |

---

**Need help?** Check the logs in the `logs/` directory or visit `http://localhost:8000/docs` for API documentation.
