"""
Test client for the Data Preprocessing API
"""
import requests
import json
from pathlib import Path

# API base URL
BASE_URL = "http://localhost:8000"

def test_health_check():
    """Test health check endpoint"""
    print("\n=== Testing Health Check ===")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_upload_csv(file_path: str, client_id: str = "test_client"):
    """Test CSV file upload"""
    print("\n=== Testing CSV Upload ===")
    
    with open(file_path, 'rb') as f:
        files = {'file': f}
        data = {'client_id': client_id}
        response = requests.post(
            f"{BASE_URL}/upload/tabular",
            files=files,
            data=data
        )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.json()

def test_create_and_execute_job(input_path: str, client_id: str = "test_client"):
    """Test job creation and execution"""
    print("\n=== Testing Job Creation and Execution ===")
    
    params = {
        'client_id': client_id,
        'data_type': 'tabular',
        'input_path': input_path,
        'remove_duplicates': True,
        'handle_missing_values': True,
        'missing_value_strategy': 'mean',
        'auto_execute': False  # We'll execute manually
    }
    
    # Create job
    response = requests.post(f"{BASE_URL}/jobs/create", params=params)
    print(f"Create Job Status: {response.status_code}")
    job_data = response.json()
    print(f"Job Created: {json.dumps(job_data, indent=2)}")
    
    job_id = job_data['job_id']
    
    # Execute job
    print(f"\nExecuting job {job_id}...")
    response = requests.post(f"{BASE_URL}/jobs/{job_id}/execute")
    print(f"Execute Status: {response.status_code}")
    print(f"Result: {json.dumps(response.json(), indent=2)}")
    
    return job_id

def test_get_job_status(job_id: str):
    """Test getting job status"""
    print(f"\n=== Testing Get Job Status ===")
    response = requests.get(f"{BASE_URL}/jobs/{job_id}/status")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_list_jobs(client_id: str = "test_client"):
    """Test listing jobs"""
    print("\n=== Testing List Jobs ===")
    response = requests.get(f"{BASE_URL}/jobs/", params={'client_id': client_id})
    print(f"Status: {response.status_code}")
    jobs = response.json()
    print(f"Found {len(jobs)} jobs")
    for job in jobs:
        print(f"  - {job['job_id']}: {job['status']}")

if __name__ == "__main__":
    # Test health check
    test_health_check()
    
    # Note: Update these paths to actual test files
    # test_csv_path = "path/to/your/test.csv"
    # upload_result = test_upload_csv(test_csv_path)
    # job_id = test_create_and_execute_job(upload_result['file_path'])
    # test_get_job_status(job_id)
    # test_list_jobs()
    
    print("\n=== Tests Complete ===")