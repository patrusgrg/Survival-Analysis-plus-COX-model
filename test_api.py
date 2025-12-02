#!/usr/bin/env python
"""
Testing script for Survival Analysis API
Run this to test all endpoints
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
API_URL = "http://localhost:8000"

# ANSI colors for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_header(text):
    print(f"\n{BLUE}{'='*60}")
    print(f"{text}")
    print(f"{'='*60}{RESET}\n")

def print_success(text):
    print(f"{GREEN}✅ {text}{RESET}")

def print_error(text):
    print(f"{RED}❌ {text}{RESET}")

def print_warning(text):
    print(f"{YELLOW}⚠️  {text}{RESET}")

def test_health():
    """Test health check endpoint"""
    print_header("Testing Health Check Endpoint")
    
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"API is healthy: {data['status']}")
            print_success(f"Model loaded: {data['model_loaded']}")
            return True
        else:
            print_error(f"Health check failed: {response.status_code}")
            return False
    
    except Exception as e:
        print_error(f"Connection error: {str(e)}")
        return False

def test_single_prediction():
    """Test single patient prediction"""
    print_header("Testing Single Prediction Endpoint")
    
    patient_data = {
        "time": 55,
        "sex": 0,
        "chest_pain_type": 0,
        "resting_bp": 140,
        "cholesterol": 200,
        "fasting_bs": 0,
        "resting_ecg": 0,
        "max_hr": 140,
        "exercise_angina": 0,
        "oldpeak": 1.0,
        "st_slope": 1
    }
    
    print("Patient Data:")
    print(json.dumps(patient_data, indent=2))
    
    try:
        response = requests.post(
            f"{API_URL}/predict",
            json=patient_data,
            timeout=10
        )
        
        if response.status_code == 200:
            prediction = response.json()
            print_success("Prediction successful!")
            
            print(f"\n{BLUE}Results:{RESET}")
            print(f"  Hazard Ratio: {prediction['hazard_ratio']:.4f}")
            print(f"  Risk Score: {prediction['risk_score']}")
            print(f"  Median Survival Age: {prediction['median_survival_age']:.1f} years")
            
            print(f"\n{BLUE}Survival Probabilities:{RESET}")
            for age, prob in sorted(prediction['survival_probabilities'].items()):
                years_ahead = int(age) - int(patient_data['time'])
                print(f"  Age {age} (in {years_ahead} years): {prob:.1%}")
            
            return True
        else:
            print_error(f"Prediction failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False

def test_batch_prediction():
    """Test batch prediction endpoint"""
    print_header("Testing Batch Prediction Endpoint")
    
    patients_data = [
        {
            "time": 45,
            "sex": 0,
            "chest_pain_type": 0,
            "resting_bp": 120,
            "cholesterol": 150,
            "fasting_bs": 0,
            "resting_ecg": 0,
            "max_hr": 170,
            "exercise_angina": 0,
            "oldpeak": 0.0,
            "st_slope": 2
        },
        {
            "time": 65,
            "sex": 1,
            "chest_pain_type": 2,
            "resting_bp": 160,
            "cholesterol": 250,
            "fasting_bs": 1,
            "resting_ecg": 1,
            "max_hr": 100,
            "exercise_angina": 1,
            "oldpeak": 3.0,
            "st_slope": 0
        }
    ]
    
    print(f"Testing with {len(patients_data)} patients...")
    
    try:
        response = requests.post(
            f"{API_URL}/predict_batch",
            json=patients_data,
            timeout=15
        )
        
        if response.status_code == 200:
            predictions = response.json()
            print_success(f"Batch prediction successful!")
            
            for i, pred in enumerate(predictions):
                print(f"\n{BLUE}Patient {i+1}:{RESET}")
                print(f"  Age: {pred['patient_age']}")
                print(f"  Hazard Ratio: {pred['hazard_ratio']:.4f}")
                print(f"  Risk: {pred['risk_score']}")
            
            return True
        else:
            print_error(f"Batch prediction failed: {response.status_code}")
            return False
    
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False

def test_model_info():
    """Test model information endpoint"""
    print_header("Testing Model Information Endpoint")
    
    try:
        response = requests.get(f"{API_URL}/model-info", timeout=5)
        
        if response.status_code == 200:
            info = response.json()
            print_success("Model info retrieved!")
            
            print(f"{BLUE}Model Details:{RESET}")
            print(f"  Type: {info['model_type']}")
            print(f"  C-Index: {info['concordance_index']:.4f}")
            print(f"  Number of Features: {info['number_of_features']}")
            print(f"  Features: {', '.join(info['features'][:5])}...")
            
            return True
        else:
            print_error(f"Model info failed: {response.status_code}")
            return False
    
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False

def test_invalid_input():
    """Test API with invalid input"""
    print_header("Testing Invalid Input Handling")
    
    invalid_data = {
        "time": -10,  # Invalid age
        "sex": 999,    # Invalid sex
        "chest_pain_type": "invalid",
        "resting_bp": 140,
        "cholesterol": 200,
        "fasting_bs": 0,
        "resting_ecg": 0,
        "max_hr": 140,
        "exercise_angina": 0,
        "oldpeak": 1.0,
        "st_slope": 1
    }
    
    try:
        response = requests.post(
            f"{API_URL}/predict",
            json=invalid_data,
            timeout=5
        )
        
        if response.status_code != 200:
            print_success("Invalid input properly rejected!")
            print(f"Status Code: {response.status_code}")
            return True
        else:
            print_warning("Invalid input was accepted (unexpected)")
            return False
    
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False

def run_all_tests():
    """Run all tests"""
    print(f"\n{BLUE}{'='*60}")
    print("SURVIVAL ANALYSIS API - TEST SUITE")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print(f"API URL: {API_URL}")
    print(f"{'='*60}{RESET}\n")
    
    results = {
        "Health Check": test_health(),
        "Single Prediction": test_single_prediction(),
        "Batch Prediction": test_batch_prediction(),
        "Model Information": test_model_info(),
        "Invalid Input": test_invalid_input()
    }
    
    # Summary
    print_header("Test Summary")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, passed_test in results.items():
        status = f"{GREEN}PASSED{RESET}" if passed_test else f"{RED}FAILED{RESET}"
        print(f"{test_name}: {status}")
    
    print(f"\n{BLUE}Overall: {passed}/{total} tests passed{RESET}")
    
    if passed == total:
        print(f"{GREEN}✅ All tests passed!{RESET}\n")
        return 0
    else:
        print(f"{RED}❌ Some tests failed!{RESET}\n")
        return 1

if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)
