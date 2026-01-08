"""
Comprehensive API testing script for Nimbly
Tests all endpoints as per task 18
"""
import requests
import json
from pathlib import Path

BASE_URL = "http://localhost:8000"

def print_test(name, passed, details=""):
    status = "✓ PASS" if passed else "✗ FAIL"
    print(f"{status} - {name}")
    if details:
        print(f"  {details}")
    print()

def test_root():
    """Test root endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/")
        passed = response.status_code == 200 and "Nimbly API" in response.text
        print_test("Root endpoint", passed, f"Status: {response.status_code}, Response: {response.json()}")
        return passed
    except Exception as e:
        print_test("Root endpoint", False, f"Error: {e}")
        return False

def test_health():
    """Test health endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        data = response.json()
        passed = response.status_code == 200 and data.get("status") == "healthy"
        print_test("Health endpoint", passed, f"Status: {response.status_code}, Response: {data}")
        return passed
    except Exception as e:
        print_test("Health endpoint", False, f"Error: {e}")
        return False

def test_docs():
    """Test OpenAPI docs endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/docs")
        passed = response.status_code == 200 and "swagger" in response.text.lower()
        print_test("OpenAPI docs", passed, f"Status: {response.status_code}")
        return passed
    except Exception as e:
        print_test("OpenAPI docs", False, f"Error: {e}")
        return False

def test_magic_link_request():
    """Test magic link request"""
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/request-magic-link",
            json={"email": "test@example.com"}
        )
        data = response.json()
        passed = response.status_code == 200 and "message" in data
        print_test("Magic link request", passed, f"Status: {response.status_code}, Response: {data}")
        return passed
    except Exception as e:
        print_test("Magic link request", False, f"Error: {e}")
        return False

def test_magic_link_invalid_email():
    """Test magic link with invalid email"""
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/request-magic-link",
            json={"email": "invalid-email"}
        )
        # Accept either 400 or 422 as both indicate validation error
        passed = response.status_code in [400, 422]
        print_test("Magic link invalid email", passed, f"Status: {response.status_code}")
        return passed
    except Exception as e:
        print_test("Magic link invalid email", False, f"Error: {e}")
        return False

def test_receipt_upload_no_auth():
    """Test receipt upload without authentication"""
    try:
        # Create a dummy file to send
        files = {'file': ('test.txt', 'test content', 'text/plain')}
        response = requests.post(f"{BASE_URL}/api/receipts/upload", files=files)
        data = response.json() if response.headers.get('content-type') == 'application/json' else response.text
        passed = response.status_code == 401  # Unauthorized
        print_test("Receipt upload (no auth)", passed, f"Status: {response.status_code}, Response: {data}")
        return passed
    except Exception as e:
        print_test("Receipt upload (no auth)", False, f"Error: {e}")
        return False

def test_receipts_list_no_auth():
    """Test receipts list without authentication"""
    try:
        response = requests.get(f"{BASE_URL}/api/receipts")
        data = response.json() if response.headers.get('content-type') == 'application/json' else response.text
        passed = response.status_code == 401  # Unauthorized
        print_test("Receipts list (no auth)", passed, f"Status: {response.status_code}, Response: {data}")
        return passed
    except Exception as e:
        print_test("Receipts list (no auth)", False, f"Error: {e}")
        return False

def test_insights_no_auth():
    """Test insights without authentication"""
    try:
        response = requests.get(f"{BASE_URL}/api/insights")
        data = response.json() if response.headers.get('content-type') == 'application/json' else response.text
        passed = response.status_code == 401  # Unauthorized
        print_test("Insights (no auth)", passed, f"Status: {response.status_code}, Response: {data}")
        return passed
    except Exception as e:
        print_test("Insights (no auth)", False, f"Error: {e}")
        return False

def test_invalid_endpoint():
    """Test invalid endpoint returns 404"""
    try:
        response = requests.get(f"{BASE_URL}/invalid-endpoint")
        passed = response.status_code == 404
        print_test("Invalid endpoint", passed, f"Status: {response.status_code}")
        return passed
    except Exception as e:
        print_test("Invalid endpoint", False, f"Error: {e}")
        return False

def main():
    print("=" * 60)
    print("NIMBLY API COMPREHENSIVE TEST SUITE")
    print("=" * 60)
    print()
    
    results = []
    
    # Public endpoints
    print("--- PUBLIC ENDPOINTS ---")
    results.append(test_root())
    results.append(test_health())
    results.append(test_docs())
    
    # Auth endpoints
    print("--- AUTH ENDPOINTS ---")
    results.append(test_magic_link_request())
    results.append(test_magic_link_invalid_email())
    
    # Protected endpoints (should fail without auth)
    print("--- PROTECTED ENDPOINTS (No Auth) ---")
    results.append(test_receipt_upload_no_auth())
    results.append(test_receipts_list_no_auth())
    results.append(test_insights_no_auth())
    
    # Error handling
    print("--- ERROR HANDLING ---")
    results.append(test_invalid_endpoint())
    
    # Summary
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Tests passed: {passed}/{total}")
    print(f"Success rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1

if __name__ == "__main__":
    exit(main())
