#!/usr/bin/env python3
"""
Test script for the Interview API Gateway and Lambda function.
This script tests the API endpoint with a sample role description.
"""

import requests
import json
import sys

def test_interview_api(api_url, job_description):
    """
    Test the interview API with a sample job description for interviewer preparation.
    """
    print(f"Testing API at: {api_url}")
    print(f"Job description: {job_description}")
    print("-" * 50)
    
    # Prepare the request payload
    payload = {
        "role_description": job_description
    }
    
    try:
        # Make the POST request
        response = requests.post(
            api_url,
            json=payload,
            headers={
                'Content-Type': 'application/json'
            },
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print("\n Success! API Response:")
            print(json.dumps(result, indent=2))
            
            # Validate response structure
            if 'questions' in result:
                questions = result['questions']
                print(f"\nGenerated {len(questions)} interview questions for interviewer preparation")
                for i, q in enumerate(questions, 1):
                    print(f"\n{i}. [{q.get('category', 'N/A')}] {q.get('question', 'N/A')}")
                    print(f"   Suggested Answer: {q.get('suggestedAnswer', 'N/A')}")
            else:
                print("Warning: No questions found in response")
                
        else:
            print(f"Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

def main():
    """
    Main function to run the test.
    """
    # Sample job descriptions for testing interviewer preparation
    test_jobs = [
        "Senior Software Engineer with 5+ years of experience in Python, Django, and React. Responsibilities include leading development teams, architecting scalable web applications, and mentoring junior developers.",
        "DevOps Engineer specializing in AWS, Docker, Kubernetes, and CI/CD pipelines. Must have experience with infrastructure as code using Terraform and monitoring with Prometheus and Grafana.",
        "Data Scientist with expertise in machine learning, Python, and SQL. Experience with TensorFlow, PyTorch, and data visualization tools. Must be able to work with large datasets and communicate insights to stakeholders."
    ]
    
    # Get API URL from command line or use default
    if len(sys.argv) > 1:
        api_url = sys.argv[1]
    else:
        print("Usage: python test_api.py <API_GATEWAY_URL>")
        print("Example: python test_api.py https://abc123.execute-api.eu-west-3.amazonaws.com/prod/interview")
        sys.exit(1)
    
    # Test with each job description
    for i, job in enumerate(test_jobs, 1):
        print(f"\n{'='*60}")
        print(f"TEST {i}: {job[:50]}...")
        print('='*60)
        test_interview_api(api_url, job)
        
        if i < len(test_jobs):
            input("\nPress Enter to continue to next test...")

if __name__ == "__main__":
    main()
