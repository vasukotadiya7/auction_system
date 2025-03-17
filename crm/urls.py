from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    
    path('',views.homepage,name=''),
    path('about_us',views.about_us,name='about_us'),
    path('contact_us',views.contact_us,name='contact_us'),
    
    path('registration',views.registration,name='registration'),
    path('verify',views.verify,name='verify'),    
    path('my_login',views.my_login,name='my_login'),
    path('user_logout',views.user_logout, name='user_logout'),

    path('dashboard',views.dashboard,name='dashboard'),
    path('profile',views.profile,name='profile'),

    path('add_product',views.add_product,name='add_product'),
    path('my_products',views.my_products,name='my_products'),
    path('my_bids',views.my_bids,name='my_bids'),
    # path('coming_soon_product_detail/<pid>/',views.coming_soon_product_detail,name='coming_soon_product_detail'),
    # path('closed_product_detail/<pid>/',views.closed_product_detail,name='closed_product_detail'),
    
    path('auction',views.auction,name='auction'),
    path('category_view/<cid>/',views.category_view,name='category_view'),
    path('product_detail/<pid>/',views.product_detail,name='product_detail'),  
    path('place_bid/<pid>/', views.place_bid, name='place_bid'),
    path('shipping_details/<pid>/', views.shipping_details, name='shipping_details'),
    path('payment/<pid>/', views.payment, name='payment'),
    path('success/', views.success, name='success'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
