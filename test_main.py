import requests
import json

def test_fixed_endpoint():
    """Test the fixed A2A endpoint"""
    
    base_url = "http://localhost:8000"
    
    print("🧪 Testing Fixed A2A Endpoint...")
    
    test_data = {
        "jsonrpc": "2.0",
        "id": "validation-test-001",
        "method": "message/send",
        "params": {
            "message": {
                "role": "user",
                "parts": [{
                    "kind": "text",
                    "text": "I'm feeling great about this fix!"
                }]
            }
        }
    }
    
    try:
        response = requests.post(
            f"{base_url}/a2a/moodmirror",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"Response Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print("🎉 SUCCESS! Endpoint is working!")
            print(f"JSON-RPC ID: {result.get('id')}")
            print(f"Has result: {'result' in result}")
            
            if 'result' in result:
                print(f"Task State: {result['result'].get('status', {}).get('state')}")
                
        else:
            print(f" Still failing: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f" Request failed: {e}")

def test_options():
    """Test OPTIONS preflight"""
    base_url = "http://localhost:8000"
    
    try:
        response = requests.options(
            f"{base_url}/a2a/moodmirror",
            headers={"Origin": "https://validator.example.com"}
        )
        print(f"OPTIONS Status: {response.status_code}")
        print(f"OPTIONS Headers: {dict(response.headers)}")
    except Exception as e:
        print(f"OPTIONS failed: {e}")

if __name__ == "__main__":
    test_options()
    print("\n" + "="*50)
    test_fixed_endpoint()