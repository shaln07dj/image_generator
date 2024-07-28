from celery import shared_task
import requests
import os
import json

STABILITY_API_KEY = os.getenv('STABILITY_API_KEY')
API_URL = "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"

@shared_task(bind=True)
def generate_image(self, prompt):
    headers = {
        'Authorization': f'Bearer {STABILITY_API_KEY}',
        'Content-Type': 'application/json'
    }
    data = {
        "prompt": prompt,
        "steps": 50
    }

    try:
        response = requests.post(API_URL, json=data, headers=headers)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx and 5xx)

        response_data = response.json()
        print(f"API Response: {json.dumps(response_data, indent=2)}")
        
        if 'output' in response_data and len(response_data['output']) > 0:
            return response_data['output'][0]['url']
        else:
            self.retry(exc=Exception("Invalid API response structure"), countdown=10, max_retries=3)
    except requests.RequestException as e:
        self.retry(exc=e, countdown=10, max_retries=3)
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        raise self.retry(exc=e, countdown=10, max_retries=3)
