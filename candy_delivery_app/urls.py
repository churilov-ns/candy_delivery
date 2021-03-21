from django.urls import path, re_path
from . import views


# =====================================================================================================================


urlpatterns = [
    path('couriers', views.post_couriers, name='post_couriers'),
    re_path('couriers/[0-9]+', views.get_patch_courier, name='get_patch_courier'),
    path('orders', views.post_orders, name='post_orders'),
]
