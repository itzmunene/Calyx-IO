#!/usr/bin/env python3
"""
Test script for Calyx.io API
Usage: python test_api.py [API_URL]
"""

import requests
import sys
import json
from pathlib import Path

def test_health(base_url):
    """Test health endpoint"""
    print("\n🏥 Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"   Response: {response.json()}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_root(base_url):
    """Test root endpoint"""
    print("\n🏠 Testing root endpoint...")
    try:
        response = requests.get(base_url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✅ Root endpoint passed")
            print(f"   API: {data.get('name')}")
            print(f"   Version: {data.get('version')}")
            print(f"   Flowers: {data.get('flowers_count')}")
            return True
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_search(base_url):
    """Test search endpoint"""
    print("\n🔍 Testing search endpoint...")
    queries = ["rose", "tulip", "sunflower"]
    
    for query in queries:
        try:
            response = requests.get(
                f"{base_url}/api/v1/search",
                params={"q": query, "limit": 5},
                timeout=10
            )
            if response.status_code == 200:
                results = response.json()
                print(f"✅ Search for '{query}': {len(results)} results")
                if results:
                    print(f"   First result: {results[0]['scientific_name']}")
            else:
                print(f"❌ Search failed for '{query}': {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Error searching '{query}': {e}")
            return False
    
    return True

def test_species_detail(base_url):
    """Test species detail endpoint"""
    print("\n📋 Testing species detail endpoint...")
    
    # First, get a species ID from search
    try:
        search_response = requests.get(
            f"{base_url}/api/v1/search",
            params={"q": "rose", "limit": 1},
            timeout=10
        )
        
        if search_response.status_code != 200 or not search_response.json():
            print("⚠️ Skipping: No species found")
            return True
        
        species_id = search_response.json()[0]['id']
        
        # Get species details
        detail_response = requests.get(
            f"{base_url}/api/v1/species/{species_id}",
            timeout=10
        )
        
        if detail_response.status_code == 200:
            data = detail_response.json()
            print("✅ Species detail endpoint passed")
            print(f"   Name: {data['scientific_name']}")
            print(f"   Common: {', '.join(data['common_names'])}")
            return True
        else:
            print(f"❌ Species detail failed: {detail_response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_identify(base_url, image_path=None):
    """Test identification endpoint"""
    print("\n🌸 Testing identification endpoint...")
    
    if image_path and Path(image_path).exists():
        try:
            with open(image_path, 'rb') as f:
                files = {'image': ('flower.jpg', f, 'image/jpeg')}
                response = requests.post(
                    f"{base_url}/api/v1/identify",
                    files=files,
                    timeout=30
                )
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Identification endpoint passed")
                print(f"   Species: {data['scientific_name']}")
                print(f"   Confidence: {data['confidence']:.2f}")
                print(f"   Method: {data['method']}")
                print(f"   Response time: {data['response_time_ms']}ms")
                return True
            else:
                print(f"❌ Identification failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    else:
        print("⚠️ Skipping: No image file provided")
        print("   Usage: python test_api.py [API_URL] [IMAGE_PATH]")
        return True

def test_stats(base_url):
    """Test stats endpoint"""
    print("\n📊 Testing stats endpoint...")
    try:
        response = requests.get(f"{base_url}/api/v1/stats", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✅ Stats endpoint passed")
            print(f"   Total IDs: {data['total_identifications']}")
            print(f"   Cache hits: {data['total_cache_hits']}")
            print(f"   Hit rate: {data['cache_hit_rate']:.1%}")
            return True
        else:
            print(f"❌ Stats failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Main test runner"""
    print("🌸 Calyx.io API Test Suite")
    print("=" * 50)
    
    # Get API URL from command line or use default
    if len(sys.argv) > 1:
        base_url = sys.argv[1].rstrip('/')
    else:
        base_url = "http://localhost:8000"
    
    # Get image path if provided
    image_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    print(f"🎯 Testing API: {base_url}")
    
    # Run tests
    tests = [
        ("Health Check", lambda: test_health(base_url)),
        ("Root Endpoint", lambda: test_root(base_url)),
        ("Search", lambda: test_search(base_url)),
        ("Species Detail", lambda: test_species_detail(base_url)),
        ("Identification", lambda: test_identify(base_url, image_path)),
        ("Stats", lambda: test_stats(base_url))
    ]
    
    results = []
    for name, test_func in tests:
        try:
            passed = test_func()
            results.append((name, passed))
        except Exception as e:
            print(f"\n❌ Unexpected error in {name}: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary:")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
    
    print("=" * 50)
    print(f"Results: {passed}/{total} tests passed ({passed/total*100:.0f}%)")
    
    if passed == total:
        print("\n🎉 All tests passed! API is working correctly.")
        sys.exit(0)
    else:
        print("\n⚠️ Some tests failed. Check the output above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
