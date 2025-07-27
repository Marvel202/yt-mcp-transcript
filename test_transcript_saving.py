#!/usr/bin/env python3
"""
Test script to verify transcript saving functionality
"""
import requests
import json
from pathlib import Path

# Configuration
API_BASE_URL = "http://localhost:8080"
TRANSCRIPT_DIR = Path(__file__).parent / "transcript"

def test_server_health():
    """Test if the FastAPI server is running."""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        print(f"✅ Server health check: {response.status_code == 200}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Server health check failed: {e}")
        return False

def test_transcript_save():
    """Test saving a transcript."""
    if not test_server_health():
        print("❌ Server is not running. Please start it first.")
        return
    
    # Test data
    video_id = "pebgrFQ-C7M"
    request_data = {
        "video_id": video_id,
        "with_timestamps": True,
        "language": "en"
    }
    
    try:
        # Make API request to save transcript
        response = requests.post(
            f"{API_BASE_URL}/transcript/save",
            json=request_data,
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        
        print(f"API Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"API Response: {json.dumps(data, indent=2)}")
            
            # Check if file exists
            expected_filename = f"{video_id}_en_with_timestamps.txt"
            expected_path = TRANSCRIPT_DIR / expected_filename
            
            print(f"Expected file path: {expected_path}")
            print(f"File exists: {expected_path.exists()}")
            
            if expected_path.exists():
                file_size = expected_path.stat().st_size
                print(f"File size: {file_size:,} bytes")
                
                # Read first few lines
                with open(expected_path, 'r', encoding='utf-8') as f:
                    first_lines = f.read(500)
                print(f"First 500 characters:\n{first_lines}")
            
        else:
            print(f"❌ API request failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Error during test: {e}")

def list_existing_files():
    """List all existing transcript files."""
    print(f"Transcript directory: {TRANSCRIPT_DIR}")
    print(f"Directory exists: {TRANSCRIPT_DIR.exists()}")
    
    if TRANSCRIPT_DIR.exists():
        files = list(TRANSCRIPT_DIR.glob("*.txt"))
        print(f"Found {len(files)} files:")
        for file in files:
            size = file.stat().st_size
            print(f"  📄 {file.name} ({size:,} bytes)")
    else:
        print("❌ Transcript directory does not exist")

if __name__ == "__main__":
    print("🧪 Testing YouTube Transcript Saving Functionality")
    print("=" * 50)
    
    print("\n1. Listing existing files:")
    list_existing_files()
    
    print("\n2. Testing transcript save:")
    test_transcript_save()
    
    print("\n3. Final file list:")
    list_existing_files()
