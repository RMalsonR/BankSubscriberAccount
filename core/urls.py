from rest_framework.routers import DefaultRouter

from core.views import BankAccountViewSet


app_name = 'core'

router = DefaultRouter()
router.register('account', BankAccountViewSet, basename='account_viewset')

urlpatterns = [

] + router.urls
