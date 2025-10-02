from django.http import JsonResponse

def index(request):
    return JsonResponse({"service": "Stations", "status": "running"})
