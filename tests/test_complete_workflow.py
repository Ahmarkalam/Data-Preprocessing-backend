#!/usr/bin/env python
"""
Complete workflow test - tests the entire system end-to-end
"""
import sys
from pathlib import Path
import csv
import requests
import time

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

BASE_URL = "http://localhost:8000"

def create_test_csv():
    """Create a test CSV file with messy data"""
    test_file = Path("tests/test_data.csv")
    test_file.parent.mkdir(exist_ok=True)
    
    data = [
        ["Name", "Age", "Salary", "Department"],
        ["John Doe", "30", "50000", "Engineering"],
        ["Jane Smith", "25", "60000", "Marketing"],
        ["John Doe", "30", "50000", "Engineering"],  # Duplicate
        ["Bob Johnson", "", "55000", "Sales"],  # Missing age
        ["Alice Williams", "35", "", "Engineering"],  # Missing salary
        ["Charlie Brown", "28", "52000", "Marketing"],
        ["", "32", "58000", "Sales"],  # Missing name
    ]
    
    with open(test_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(data)
    
    print(f"✅ Created test CSV: {test_file}")
    return str(test_file)

def test_workflow(api_key: str):
    """Test complete workflow"""
    print("\n" + "="*60)
    print("  COMPLETE WORKFLOW TEST")
    print("="*60 + "\n")
    
    headers = {"X-API-Key": api_key}
    
    # Step 1: Create test data
    print("📝 Step 1: Creating test data...")
    test_file = create_test_csv()
    print()
    
    # Step 2: Upload file
    print("📤 Step 2: Uploading file...")
    with open(test_file, 'rb') as f:
        files = {'file': f}
        response = requests.post(
            f"{BASE_URL}/upload/tabular",
            files=files,
            headers=headers
        )
    
    if response.status_code != 200:
        print(f"❌ Upload failed: {response.text}")
        return False
    
    upload_data = response.json()
    uploaded_path = upload_data['file_path']
    print(f"✅ File uploaded: {uploaded_path}")
    print(f"   Size: {upload_data['file_size']} bytes\n")
    
    # Step 3: Create and execute job
    print("⚙️  Step 3: Creating processing job...")
    params = {
        'data_type': 'tabular',
        'input_path': uploaded_path,
        'remove_duplicates': True,
        'handle_missing_values': True,
        'missing_value_strategy': 'mean',
        'auto_execute': False
    }
    
    response = requests.post(
        f"{BASE_URL}/jobs/create",
        params=params,
        headers=headers
    )
    
    if response.status_code != 200:
        print(f"❌ Job creation failed: {response.text}")
        return False
    
    job_data = response.json()
    job_id = job_data['job_id']
    print(f"✅ Job created: {job_id}\n")
    
    # Step 4: Test job cancellation (before executing)
    print("🛑 Step 4: Testing job cancellation...")
    cancel_response = requests.post(
        f"{BASE_URL}/jobs/{job_id}/cancel",
        headers=headers
    )
    
    if cancel_response.status_code == 200:
        print(f"✅ Job cancelled successfully")
        cancel_data = cancel_response.json()
        print(f"   Status: {cancel_data['status']}")
        print(f"   Error message: {cancel_data.get('error_message', 'None')}\n")
        
        # Create a new job for execution since we cancelled the first one
        print("⚙️  Creating new job for execution...")
        response = requests.post(
            f"{BASE_URL}/jobs/create",
            params=params,
            headers=headers
        )
        if response.status_code != 200:
            print(f"❌ Job creation failed: {response.text}")
            return False
        job_data = response.json()
        job_id = job_data['job_id']
        print(f"✅ New job created: {job_id}\n")
    else:
        print(f"⚠️  Could not cancel job (may already be processing): {cancel_response.text}\n")
    
    # Step 5: Execute job
    print("🚀 Step 5: Executing job...")
    response = requests.post(
        f"{BASE_URL}/jobs/{job_id}/execute",
        headers=headers
    )
    
    if response.status_code != 200:
        print(f"❌ Job execution failed: {response.text}")
        return False
    
    result = response.json()
    print(f"✅ Job completed: {result['status']}\n")
    
    # Step 6: Check quality metrics
    print("📊 Step 6: Quality Metrics:")
    if result.get('quality_metrics'):
        metrics = result['quality_metrics']
        print(f"   Total Records:        {metrics['total_records']}")
        print(f"   Valid Records:        {metrics['valid_records']}")
        print(f"   Invalid Records:      {metrics['invalid_records']}")
        print(f"   Missing Values:       {metrics['missing_values_percent']}%")
        print(f"   Duplicates:           {metrics['duplicate_percent']}%")
        print(f"   Quality Score:        {metrics['quality_score']}")
        if metrics.get('issues'):
            print(f"   Issues:               {', '.join(metrics['issues'])}")
    print()
    
    # Step 7: List jobs
    print("📋 Step 7: Listing jobs...")
    response = requests.get(f"{BASE_URL}/jobs/", headers=headers)
    
    if response.status_code != 200:
        print(f"❌ Failed to list jobs: {response.text}")
        return False
    
    jobs = response.json()
    print(f"✅ Found {len(jobs)} job(s)")
    for job in jobs[:3]:  # Show first 3
        print(f"   - {job['job_id']}: {job['status']}")
    print()
    
    # Step 8: Download result
    print("💾 Step 8: Downloading processed file...")
    response = requests.get(
        f"{BASE_URL}/jobs/{job_id}/download",
        headers=headers
    )
    
    if response.status_code != 200:
        print(f"❌ Download failed: {response.text}")
        return False
    
    output_file = Path("tests/processed_output.csv")
    with open(output_file, 'wb') as f:
        f.write(response.content)
    
    print(f"✅ File downloaded: {output_file}")
    print(f"   Size: {len(response.content)} bytes\n")
    
    print("="*60)
    print("  ✅ ALL TESTS PASSED!")
    print("="*60 + "\n")
    
    return True

def main():
    """Main test entry point"""
    if len(sys.argv) < 2:
        print("Usage: python tests/test_complete_workflow.py <API_KEY>")
        print("\nGet your API key from:")
        print("  python scripts/manage_clients.py get <client_id> --show-api-key")
        sys.exit(1)
    
    api_key = sys.argv[1]
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code != 200:
            print("❌ API server is not responding correctly")
            sys.exit(1)
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API server")
        print("   Make sure the server is running: python start.py")
        sys.exit(1)
    
    # Run tests
    success = test_workflow(api_key)
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()