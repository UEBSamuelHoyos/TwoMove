from rest_framework.routers import DefaultRouter
from .views import BikeViewSet

router = DefaultRouter()
router.register(r'bikes', BikeViewSet, basename='bike')

urlpatterns = router.urls
