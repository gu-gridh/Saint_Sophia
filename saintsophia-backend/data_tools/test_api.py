#!/usr/bin/env python3
"""
Simple script to test the Saint Sophia API.
"""

import requests
import json

def test_api():
    """Test the annotation API with a sample surface."""
    print("Testing Saint Sophia API...")
    
    url = "https://saintsophia.dh.gu.se/api/inscriptions/annotation/"
    surface_id = "208-02"  # Sample surface ID
    
    print(f"Testing with surface: {surface_id}")
    print(f"URL: {url}?surface={surface_id}")
    
    try:
        response = requests.get(url, params={'surface': surface_id}, timeout=10)
        
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Success! Got {len(data) if isinstance(data, list) else 1} annotation(s)")
            
            # Save sample for inspection
            with open('sample_annotation.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print("Sample saved as 'sample_annotation.json'")
            
            # Show first few lines
            print("\nSample data:")
            print(json.dumps(data, indent=2, ensure_ascii=False)[:500] + "...")
            
        elif response.status_code == 404:
            print("No annotation found for this surface (this is normal for some surfaces)")
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    test_api()
