#!/usr/bin/env python
"""
Test the API endpoints
"""
import requests
import json
import time
import sys

BASE_URL = "http://localhost:8000"

def test_health():
    """Test /health endpoint"""
    print("\n🏥 Testing /health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check: {data}")
            return True
        else:
            print(f"❌ Unexpected status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_predict():
    """Test /predict endpoint"""
    print("\n🔮 Testing /predict endpoint...")
    
    patient_data = {
        "time": 55.0,
        "sex": 1,
        "chest_pain_type": 0,
        "resting_bp": 130.0,
        "cholesterol": 230.0,
        "fasting_bs": 0,
        "resting_ecg": 1,
        "max_hr": 140.0,
        "exercise_angina": 0,
        "oldpeak": 0.5,
        "st_slope": 2
    }
    
    try:
        response = requests.post(f"{BASE_URL}/predict", json=patient_data, timeout=5)
        if response.status_code == 200:
            prediction = response.json()
            print(f"✅ Prediction successful!")
            print(f"   Risk Score: {prediction.get('risk_score', 'N/A'):.4f}")
            print(f"   Hazard Ratio: {prediction.get('hazard_ratio', 'N/A'):.4f}")
            print(f"   Risk Category: {prediction.get('risk_category', 'N/A')}")
            return True
        else:
            print(f"❌ Status code: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_model_info():
    """Test /model-info endpoint"""
    print("\n📊 Testing /model-info endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/model-info", timeout=5)
        if response.status_code == 200:
            info = response.json()
            print(f"✅ Model info retrieved!")
            print(f"   Model Type: {info.get('model_type', 'N/A')}")
            print(f"   C-Index: {info.get('c_index', 'N/A')}")
            print(f"   Features: {len(info.get('features', []))}")
            return True
        else:
            print(f"❌ Status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("="*80)
    print("🚀 SURVIVAL ANALYSIS API - TEST SUITE")
    print("="*80)
    
    print(f"\n🔗 Target: {BASE_URL}")
    print("⏳ Waiting for API to be ready...")
    
    # Wait for API to be ready
    max_retries = 10
    for i in range(max_retries):
        try:
            requests.get(f"{BASE_URL}/health", timeout=2)
            print("✅ API is ready!\n")
            break
        except:
            if i < max_retries - 1:
                print(f"   Attempt {i+1}/{max_retries}... retrying in 1s")
                time.sleep(1)
            else:
                print("❌ API did not start in time. Make sure it's running!")
                return
    
    # Run tests
    results = {
        'health': test_health(),
        'predict': test_predict(),
        'model_info': test_model_info()
    }
    
    # Summary
    print("\n" + "="*80)
    print("📋 TEST SUMMARY")
    print("="*80)
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    print(f"✅ Passed: {passed}/{total}")
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}: {test_name}")
    
    print("\n🎉 API is working correctly!" if passed == total else "\n⚠️  Some tests failed")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()
