from django.http import JsonResponse

def index(request):
    return JsonResponse({"service": "Rentals", "status": "running"})
