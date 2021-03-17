from django.urls import path
from . import views


# =====================================================================================================================


urlpatterns = [
    path('couriers', views.post_couriers, name='post_couriers'),
]
