from django.contrib import admin
from store.models import CartOrderItem, Product ,Category, CartOrder, Gallery, Brand, ProductFaq, Review, ProductBidders, ProductOffers
from import_export.admin import ImportExportModelAdmin
from django.contrib.auth.admin import UserAdmin
from django.db import models
from django.forms import ModelChoiceField
from userauths.models import User, Profile



@admin.action(description="Mark selected products as published")
def make_published(modeladmin, request, queryset):
    queryset.update(status="published")
    
@admin.action(description="Mark selected products as In Review")
def make_in_review(modeladmin, request, queryset):
    queryset.update(status="in_review")
    
@admin.action(description="Mark selected products as Featured")
def make_featured(modeladmin, request, queryset):
    queryset.update(featured=True)

class ProductImagesAdmin(admin.TabularInline):
    model = Gallery

class CartOrderItemsInlineAdmin(admin.TabularInline):
    model = CartOrderItem


class StaffUserChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.username

class ProductAdmin(ImportExportModelAdmin):
    inlines = [ProductImagesAdmin]
    search_fields = ['title', 'price']
    list_filter = ['featured', 'status', 'in_stock', 'type', 'vendor']
    list_editable = [ 'price', 'featured', 'status', 'shipping_amount', 'hot_deal', 'hero_section_featured']
    list_display = ['product_image' ,'title',  'price', 'featured', 'shipping_amount', 'in_stock' ,'stock_qty', 'order_count', 'vendor' ,'status', 'featured', 'hero_section_featured' ,'hot_deal']
    actions = [make_published, make_in_review, make_featured]
    # list_per_page = 500
    list_per_page = 1300
    prepopulated_fields = {"slug": ("title", )}

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'user':
            kwargs['queryset'] = User.objects.filter(is_staff=True)
            kwargs['form_class'] = StaffUserChoiceField
        return super().formfield_for_foreignkey(db_field, request, **kwargs)






# class ProductAdmin(admin.ModelAdmin):
#     def formfield_for_foreignkey(self, db_field, request, **kwargs):
#         if db_field.name == 'user':
#             kwargs['queryset'] = User.objects.filter(is_staff=True)
#             kwargs['form_class'] = StaffUserChoiceField
#         return super().formfield_for_foreignkey(db_field, request, **kwargs)


    
class CategoryAdmin(ImportExportModelAdmin):
    list_display = ['title', 'category_image']


class CartOrderAdmin(ImportExportModelAdmin):
    inlines = [CartOrderItemsInlineAdmin]
    search_fields = ['oid', 'tracking_id', 'product__title']
    list_editable = ['order_status', 'payment_status' ,'delivery_status']
    list_filter = ['payment_status', 'order_status', 'delivery_status']
    list_display = ['oid', 'payment_status', 'order_status', 'delivery_status' ,'price', 'shipping', 'vat', 'service_fee' ,'total', 'saved' ,'email','date']


class CartOrderItemsAdmin(ImportExportModelAdmin):
    search_fields = ['oid', 'tracking_id', 'product', 'coupon__code', 'order__oid', 'vendor__shop_name']
    list_filter = ['paid', 'paid_vendor', 'cancelled', 'delivery_couriers', 'applied_coupon']
    list_display = ['order',  'vendor' , 'order_img','product_obj' ,'qty', 'price', 'total', 'shipping' , 'service_fee', 'vat','total_payable', 'grand_total' , 'delivery_couriers' , 'paid', 'paid_vendor', 'applied_coupon' ,'cancelled']

class BrandAdmin(ImportExportModelAdmin):
    list_editable = [ 'active']
    list_display = ['title', 'brand_image', 'active']

class ProductFaqAdmin(ImportExportModelAdmin):
    list_editable = [ 'active', 'answer']
    list_display = ['user', 'question', 'answer' ,'active']
    
class ProductBiddersAdmin(ImportExportModelAdmin):
    list_display = ['user', 'product', 'price','winner', 'win_status' ,'email']

class ProductReviewAdmin(admin.ModelAdmin):
    list_editable = ['active']
    list_display = ['user', 'product', 'review', 'reply' ,'rating', 'active']


class ProductOfferAdmin(ImportExportModelAdmin):
    list_display = ['user', 'product', 'price','status', 'email']




admin.site.register(ProductBidders, ProductBiddersAdmin)
admin.site.register(Review, ProductReviewAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(CartOrder, CartOrderAdmin)
admin.site.register(CartOrderItem, CartOrderItemsAdmin)
admin.site.register(Brand, BrandAdmin)
admin.site.register(ProductFaq, ProductFaqAdmin)
admin.site.register(ProductOffers, ProductOfferAdmin)