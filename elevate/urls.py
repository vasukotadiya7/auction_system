
from django.contrib import admin
from django.urls import path , include


# admin.site.site_header = "Auction House Admin"

urlpatterns = [
    path("admin/", admin.site.urls),
    path('',include('crm.urls'))
]
