from django.http import JsonResponse

def index(request):
    return JsonResponse({"service": "Users", "status": "running"})
