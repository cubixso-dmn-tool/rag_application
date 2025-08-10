#!/usr/bin/env python3

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_health_endpoint():
    """Test the health endpoint"""
    print("Testing /health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_root_endpoint():
    """Test the root endpoint"""
    print("\nTesting / endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_status_endpoint():
    """Test the status endpoint"""
    print("\nTesting /status endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/status")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_ingest_folder_endpoint():
    """Test the ingest folder endpoint"""
    print("\nTesting /ingest/folder endpoint...")
    try:
        response = requests.post(f"{BASE_URL}/ingest/folder")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_query_endpoint():
    """Test the query endpoint"""
    print("\nTesting /query endpoint...")
    try:
        query_data = {
            "question": "What are the key points in the document?",
            "k": 3
        }
        response = requests.post(
            f"{BASE_URL}/query",
            headers={"Content-Type": "application/json"},
            data=json.dumps(query_data)
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200 or response.status_code == 400  # 400 if no docs ingested
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_upload_endpoint():
    """Test the upload endpoint with a sample text file"""
    print("\nTesting /ingest/upload endpoint...")
    try:
        # Create a temporary test file
        test_content = "This is a test document for the RAG application. It contains sample text to verify the upload functionality."
        
        files = {
            'file': ('test_document.txt', test_content, 'text/plain')
        }
        
        response = requests.post(f"{BASE_URL}/ingest/upload", files=files)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    print("Starting API tests...")
    print("=" * 50)
    
    # Wait a moment for server to be ready
    time.sleep(2)
    
    tests = [
        ("Health Check", test_health_endpoint),
        ("Root Endpoint", test_root_endpoint),
        ("Status Check", test_status_endpoint),
        ("Ingest Folder", test_ingest_folder_endpoint),
        ("Upload File", test_upload_endpoint),
        ("Query Documents", test_query_endpoint),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        result = test_func()
        results.append((test_name, result))
        print(f"Result: {'PASS' if result else 'FAIL'}")
    
    print("\n" + "=" * 50)
    print("TEST SUMMARY:")
    print("=" * 50)
    
    passed = 0
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nTotal: {len(results)} tests")
    print(f"Passed: {passed}")
    print(f"Failed: {len(results) - passed}")
    
    if passed == len(results):
        print("\n🎉 All tests passed!")
    else:
        print(f"\n❌ {len(results) - passed} test(s) failed")

if __name__ == "__main__":
    main()