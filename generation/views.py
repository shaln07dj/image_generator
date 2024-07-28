from django.shortcuts import render
from django.http import JsonResponse
from .tasks import generate_image
from .models import GeneratedImage

def generate_images(request):
    prompts = ["A red flying dog", "A piano ninja", "A footballer kid"]
    task_ids = [generate_image.delay(prompt) for prompt in prompts]
    
    return JsonResponse({"task_ids": [task_id.id for task_id in task_ids]})

def check_status(request, task_id):
    from celery.result import AsyncResult
    result = AsyncResult(task_id)
    if result.ready():
        url = result.get()
        if url:
            prompt = result.args[0]
            GeneratedImage.objects.create(prompt=prompt, image_url=url)
        return JsonResponse({"status": "completed", "url": url})
    else:
        return JsonResponse({"status": "pending"})
