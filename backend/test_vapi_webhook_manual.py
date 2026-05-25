"""
Manual webhook testing for VAPI integration debugging
Run with: python test_vapi_webhook_manual.py
"""
import requests
import json
from datetime import date, timedelta

BASE_URL = "http://localhost:8001/vapi-webhook"

def test_call_started():
    """Test call.started event"""
    print("\n📞 Testing: call.started")
    print("=" * 60)
    
    payload = {
        "message": {
            "type": "call.started",
            "call": {
                "id": "test-call-001",
                "customer": {"number": "+1-555-0001"},
                "assistant": {"name": "Alex"}
            }
        }
    }
    
    response = requests.post(BASE_URL, json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200


def test_get_available_slots():
    """Test get_available_slots tool call"""
    print("\n🗓️ Testing: get_available_slots")
    print("=" * 60)
    
    # Test with a weekday (Monday)
    next_monday = date.today() + timedelta(days=(7 - date.today().weekday()))
    
    payload = {
        "message": {
            "type": "tool-calls",
            "toolCallList": [
                {
                    "id": "tool-call-001",
                    "function": {
                        "name": "get_available_slots",
                        "arguments": {
                            "date": next_monday.isoformat()
                        }
                    }
                }
            ]
        }
    }
    
    response = requests.post(BASE_URL, json=payload)
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Response: {json.dumps(result, indent=2)}")
    return response.status_code == 200


def test_book_appointment():
    """Test book_appointment tool call"""
    print("\n📅 Testing: book_appointment")
    print("=" * 60)
    
    next_monday = date.today() + timedelta(days=(7 - date.today().weekday()))
    
    payload = {
        "message": {
            "type": "tool-calls",
            "toolCallList": [
                {
                    "id": "tool-call-002",
                    "function": {
                        "name": "book_appointment",
                        "arguments": {
                            "name": "Test Customer",
                            "phone": "+1-555-9999",
                            "date": next_monday.isoformat(),
                            "time": "09:00",
                            "notes": "Test booking"
                        }
                    }
                }
            ]
        }
    }
    
    response = requests.post(BASE_URL, json=payload)
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Response: {json.dumps(result, indent=2)}")
    return response.status_code == 200


def test_call_ended():
    """Test call.ended / end-of-call-report"""
    print("\n📞 Testing: call.ended")
    print("=" * 60)
    
    payload = {
        "message": {
            "type": "end-of-call-report",
            "call": {
                "id": "test-call-001",
                "customer": {"number": "+1-555-0001"},
                "endedReason": "customer_hangup",
                "analysis": {
                    "successEvaluation": "success",
                    "score": 85
                },
                "artifact": {
                    "transcript": "Test call transcript"
                }
            }
        }
    }
    
    response = requests.post(BASE_URL, json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200


def test_invalid_tool():
    """Test invalid tool name (should not crash)"""
    print("\n❌ Testing: Invalid Tool")
    print("=" * 60)
    
    payload = {
        "message": {
            "type": "tool-calls",
            "toolCallList": [
                {
                    "id": "tool-call-invalid",
                    "function": {
                        "name": "nonexistent_tool",
                        "arguments": {}
                    }
                }
            ]
        }
    }
    
    response = requests.post(BASE_URL, json=payload)
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Response: {json.dumps(result, indent=2)}")
    return response.status_code == 200


if __name__ == "__main__":
    print("🧪 VAPI Webhook Test Suite")
    print("=" * 60)
    
    tests = [
        ("call.started", test_call_started),
        ("get_available_slots", test_get_available_slots),
        ("book_appointment", test_book_appointment),
        ("call.ended", test_call_ended),
        ("invalid_tool", test_invalid_tool),
    ]
    
    results = {}
    for name, test_func in tests:
        try:
            results[name] = test_func()
        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            results[name] = False
    
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    for name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} | {name}")
    
    all_passed = all(results.values())
    print("=" * 60)
    print(f"Overall: {'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")
