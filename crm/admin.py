from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
from .models import Contact
from .models import Profile,Category,Seller,Product,BidHistory,Bid,ShippingDetails,Payment

# Register your models here.

class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff', 'birthday']  # Add 'birthday' to list_display
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Information', {'fields': ('birthday','address')}),
    )

class ProfileAdmin(admin.ModelAdmin):

    list_display=Profile.DisplayFields
    search_fields=Profile.SearchableFields
    list_filter=Profile.FilterFields

class ProductAdmin(admin.ModelAdmin):

    list_display =  ['user','product_name','product_image','min_price']

class CategoryAdmin(admin.ModelAdmin):

    list_display =  ['title','category_image']

class SellerAdmin(admin.ModelAdmin):

    list_display =  ['title','contact']



admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Contact)
admin.site.register(Profile,ProfileAdmin)
admin.site.register(Product,ProductAdmin)
admin.site.register(Category,CategoryAdmin)
admin.site.register(Seller,SellerAdmin)
admin.site.register(Bid)
admin.site.register(BidHistory)
admin.site.register(ShippingDetails)
admin.site.register(Payment)
