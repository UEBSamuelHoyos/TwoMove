from django.http import JsonResponse

def index(request):
    return JsonResponse({"service": "Bikes", "status": "running"})
