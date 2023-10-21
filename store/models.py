from django.db import models
from shortuuid.django_fields import ShortUUIDField
from django.utils.html import mark_safe
from django.utils import timezone
from django_ckeditor_5.fields import CKEditor5Field
from django.template.defaultfilters import escape
from django.urls import reverse
from django.shortcuts import redirect
from django.utils.text import slugify

from userauths.models import User, user_directory_path, Profile
from core.models import Address, BillingAddress
import shortuuid

from taggit.managers import TaggableManager
from vendor.models import Vendor, Coupon





STATUS_CHOICE = (
    ("processing", "Processing"),
    ("shipped", "Shipped"),
    ("delivered", "Delivered"),
)


STATUS = (
    ("draft", "Draft"),
    ("disabled", "Disabled"),
    ("rejected", "Rejected"),
    ("in_review", "In Review"),
    ("published", "Published"),
)


PAYMENT_STATUS = (
    ("paid", "Paid"),
    ("pending", "Pending"),
    ("processing", "Processing"),
    ("cancelled", "Cancelled"),
    ("initiated", 'Initiated'),
    ("failed", 'failed'),
    ("refunding", 'refunding'),
    ("refunded", 'refunded'),
    ("unpaid", 'unpaid'),
    ("expired", 'expired'),
)


ORDER_STATUS = (
    ("pending", "pending"),
    ("fulfilled", "fulfilled"),
    ("partially_fulfilled", "Partially Fulfilled"),
    ("cancelled", "Cancelled"),
    
)

AUCTION_STATUS = (
    ("on_going", "On Going"),
    ("finished", "finished"),
    ("cancelled", "cancelled")
)

WIN_STATUS = (
    ("won", "Won"),
    ("lost", "Lost"),
    ("pending", "pending")
)

PRODUCT_TYPE = (
    ("regular", "Regular"),
    ("auction", "Auction"),
    ("offer", "Offer")
)

OFFER_STATUS = (
    ("accepted", "Accepted"),
    ("rejected", "Rejected"),
    ("pending", "Pending"),
)

PRODUCT_CONDITION = (
    ("new", "New"),
    ("old_2nd_hand", "“Used or 2nd Hand"),
    ("custom", "Custom"),
)

PRODUCT_CONDITION_RATING = (
    (1, "1/10"),
    (2, "2/10"),
    (3, "3/10"),
    (4, "4/10"),
    (5, "5/10"),
    (6, "6/10"),
    (7, "7/10"),
    (8, "8/10"),
    (9, "9/10"),
    (10,"10/10"),
)


DELIVERY_STATUS = (
    ("on_hold", "On Hold"),
    ("shipping_processing", "Shipping Processing"),
    ("shipped", "Shipped"),
    ("arrived", "Arrived"),
    ("delivered", "Delivered"),
    ("returning", 'Returning'),
    ("returned", 'Returned'),
)

PAYMENT_METHOD = (
    ("Paypal", "Paypal"),
    ("Credit/Debit Card", "Credit/Debit Card"),
    ("Wallet Points", "Wallet Points"),
    
)




class Category(models.Model):
    cid = ShortUUIDField(unique=True, length=10, max_length=20, alphabet="abcdefghijklmnopqrstuvxyz")
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to="category", default="category.jpg", null=True, blank=True)
    active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "Categories"

    def category_image(self):
        return mark_safe('<img src="%s" width="50" height="50" style="object-fit:cover; border-radius: 6px;" />' % (self.image.url))

    def __str__(self):
        return self.title
    
    def product_count(self):
        product_count = Product.objects.filter(category=self).count()
        return product_count

class Brand(models.Model):
    bid = ShortUUIDField(unique=True, length=10, max_length=20, alphabet="abcdefghijklmnopqrstuvxyz")
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to="brand", default="brand.jpg", null=True, blank=True)
    active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name_plural = "Brands"

    def brand_image(self):
        return mark_safe('<img src="%s" width="50" height="50" style="object-fit:cover; border-radius: 6px;" />' % (self.image.url))

    def __str__(self):
        return self.title




class Product(models.Model):
    pid = ShortUUIDField(unique=True, length=10, max_length=20, alphabet="abcdefghijklmnopqrstuvxyz")
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,)
    vendor = models.ForeignKey(Vendor, on_delete=models.SET_NULL, null=True, related_name="vendor")
    
    category = models.ManyToManyField(Category, blank=True, related_name="category")
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True, related_name="product_brand")

    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to=user_directory_path, default="product.jpg")
    description = CKEditor5Field(config_name='extends', null=True, blank=True)

    price = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, null=True, blank=True)
    old_price = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, null=True, blank=True)
    
    shipping_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    show_old_price = models.BooleanField(default=True)
    tags = TaggableManager(blank=True)
    status = models.CharField(choices=STATUS, max_length=10, default="published", null=True, blank=True)
    product_condition = models.CharField(choices=PRODUCT_CONDITION, max_length=50, default="new", null=True, blank=True)
    product_condition_rating = models.IntegerField(choices=PRODUCT_CONDITION_RATING, default=1, null=True, blank=True)
    product_condition_description = models.CharField(max_length=1000,  null=True, blank=True)
    
    stock_qty = models.IntegerField(default=0)
    in_stock = models.BooleanField(default=True)
    
    featured = models.BooleanField(default=False)
    hero_section_featured = models.BooleanField(default=False)
    hot_deal = models.BooleanField(default=False)
    digital = models.BooleanField(default=False)
    sku = ShortUUIDField(unique=True, length=5, max_length=10, prefix="SKU", alphabet="1234567890")
    type = models.CharField(choices=PRODUCT_TYPE, max_length=10, default="regular")
    auction_status = models.CharField(choices=AUCTION_STATUS, max_length=10, default="on_going")
    ending_date = models.DateTimeField(auto_now_add=False, null=True, blank=True)
    bidding_ended = models.BooleanField(default=False)

    views = models.PositiveIntegerField(default=0)
    saved = models.PositiveIntegerField(default=0)
    orders = models.PositiveIntegerField(default=0)
    liked = models.ManyToManyField(User, related_name="likes", blank=True)
    bidders = models.ManyToManyField(User, related_name="bidders", blank=True)
    slug = models.SlugField(null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']
        verbose_name_plural = "Products"

    def product_image(self):
        return mark_safe('<img src="%s" width="50" height="50" style="object-fit:cover; border-radius: 6px;" />' % (self.image.url))

    def __str__(self):
        return self.title
    
    def category_count(self):
        return Product.objects.filter(category__in=self.category).count()

    def get_precentage(self):
        new_price = (self.price / self.old_price) * 100
        return new_price
    
    def product_rating(self):
        product_rating = Review.objects.filter(product=self).aggregate(avg_rating=models.Avg('rating'))
        return product_rating['avg_rating']
    
    def rating_count(self):
        rating_count = Review.objects.filter(product=self).count()
        return rating_count
    
    def order_count(self):
        order_count = CartOrderItem.objects.filter(product_obj=self, order__payment_status="paid").count()
        return order_count
    
    def save(self, *args, **kwargs):
        if self.slug == "" or self.slug == None:
            uuid_key = shortuuid.uuid()
            uniqueid = uuid_key[:4]
            self.slug = slugify(self.title) + "-" + str(uniqueid.lower())
        
        if self.stock_qty != None:
            if self.stock_qty == 0:
                self.in_stock = False
                
            if self.stock_qty > 0:
                self.in_stock = True
        else:
            self.stock_qty = 0
            self.in_stock = False
            
        super(Product, self).save(*args, **kwargs) 


class Gallery(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, related_name="product_gallery")
    image = models.ImageField(upload_to="product_gallery", default="gallery.jpg")
    active = models.BooleanField(default=True)
    date = models.DateTimeField(auto_now_add=True)
    gid = ShortUUIDField(length=10, max_length=25, alphabet="abcdefghijklmnopqrstuvxyz")

    class Meta:
        ordering = ["date"]
        verbose_name_plural = "Product Images"

    def __str__(self):
        return "Image"
        
class ProductBidders(models.Model):
    bid = ShortUUIDField(unique=True, length=10, max_length=20, alphabet="abcdefghijklmnopqrstuvxyz")
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, related_name="product_bidders")
    email = models.EmailField(blank=True, null=True)
    price = models.DecimalField(max_digits=12, decimal_places=2, default=1.00)
    active = models.BooleanField(default=True)
    winner = models.BooleanField(default=False)
    win_status = models.CharField(choices=WIN_STATUS, max_length=10, default="pending")
    date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Product Bidders"
        ordering = ["-date"]
        

    def __str__(self):
        return str(self.product)
    
class ProductOffers(models.Model):
    oid = ShortUUIDField(unique=True, length=10, max_length=20, alphabet="abcdefghijklmnopqrstuvxyz")
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, related_name="product_offer")
    email = models.EmailField(blank=True, null=True)
    message = models.CharField(blank=True, null=True, max_length=1000)
    price = models.DecimalField(max_digits=12, decimal_places=2, default=1.99)
    active = models.BooleanField(default=True)
    status = models.CharField(choices=OFFER_STATUS, max_length=10, default="pending")
    date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Product Offers"
        ordering = ["-date"]
        
    def __str__(self):
        return str(self.product)
        

class ProductFaq(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    pid = ShortUUIDField(unique=True, length=10, max_length=20, alphabet="abcdefghijklmnopqrstuvxyz")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, related_name="product_faq")
    email = models.EmailField()
    question = models.CharField(max_length=1000)
    answer = models.CharField(max_length=10000, null=True, blank=True)
    active = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Product Faqs"
        ordering = ["-date"]
        

    def __str__(self):
        return self.question


class CartOrder(models.Model):
    vendor = models.ManyToManyField(Vendor, blank=True)
    coupons = models.ManyToManyField(Coupon, blank=True)
    buyer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="buyer", blank=True)
    
    payment_status = models.CharField(max_length=100, choices=PAYMENT_STATUS, default="initiated")
    payment_method = models.CharField(max_length=100, choices=PAYMENT_METHOD, null=True, blank=True)
    order_status = models.CharField(max_length=100, choices=ORDER_STATUS, default="initiated")
    delivery_status = models.CharField(max_length=100, choices=DELIVERY_STATUS, default="on_hold")
    price = models.DecimalField(default=0.00, max_digits=12, decimal_places=2)
    shipping = models.DecimalField(default=0.00, max_digits=12, decimal_places=2)
    vat = models.DecimalField(default=0.00, max_digits=12, decimal_places=2)
    service_fee = models.DecimalField(default=0.00, max_digits=12, decimal_places=2)
    total = models.DecimalField(default=0.00, max_digits=12, decimal_places=2)
    original_total = models.DecimalField(default=0.00, max_digits=12, decimal_places=2)
    saved = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, null=True, blank=True, help_text="Amount saved by customer")
    full_name = models.CharField(max_length=1000)
    email = models.CharField(max_length=1000)
    mobile = models.CharField(max_length=1000)
    
    # Shipping Address
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, blank=True)
    country = models.ForeignKey("addons.TaxRate", on_delete=models.SET_NULL, null=True, related_name="country_tax", blank=True)
    state = models.CharField(max_length=1000, null=True, blank=True)
    town_city = models.CharField(max_length=1000, null=True, blank=True)
    address = models.CharField(max_length=1000, null=True, blank=True)
    postal_code = models.CharField(max_length=1000, null=True, blank=True)
    # End of billing

    # Billing
    billing_address_obj = models.ForeignKey(BillingAddress, on_delete=models.SET_NULL, null=True, blank=True)
    billing_country = models.ForeignKey("addons.TaxRate", on_delete=models.SET_NULL, null=True, related_name="billing_country_field", blank=True)
    billing_state = models.CharField(max_length=1000, null=True, blank=True)
    billing_town_city = models.CharField(max_length=1000, null=True, blank=True)
    billing_address = models.CharField(max_length=1000, null=True, blank=True)
    billing_postal_code = models.CharField(max_length=1000, null=True, blank=True)
    # End of billing

    custom_order = models.BooleanField(default=False)
    
    stripe_payment_intent = models.CharField(max_length=200,null=True, blank=True)
    oid = ShortUUIDField(length=10, max_length=25, alphabet="abcdefghijklmnopqrstuvxyz")
    date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ["-date"]
        verbose_name_plural = "Cart Order"

    def __str__(self):
        return self.oid
    


class CartOrderItem(models.Model):
    order = models.ForeignKey(CartOrder, on_delete=models.CASCADE)
    vendor = models.ForeignKey(Vendor, on_delete=models.SET_NULL, null=True)
    # coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True)
    coupon = models.ManyToManyField(Coupon, blank=True)
    qty = models.IntegerField(default=0)
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, help_text="Total of Product price * Product Qty")
    vat = models.DecimalField(default=0.00, max_digits=12, decimal_places=2, help_text="Estimated Vat based on delivery country = tax_rate * (total + shipping)")
    service_fee = models.DecimalField(default=0.00, max_digits=12, decimal_places=2, help_text="Estimated Service Fee = service_fee * total (paid by buyer to platform)")
    shipping = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, help_text="Estimated Shipping Fee = shipping_fee * total")
    total_payable = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, help_text="Vendor Payable Earning Excluding Vendor Sales Fee")
    grand_total = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, help_text="Grand Total of all amount listed above")
    original_grand_total = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, help_text="Grand Total of all amount listed above")
    coupon_discount_grand_total = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, null=True, blank=True, help_text="Grand Total after applying coupon")
    saved = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, null=True, blank=True, help_text="Amount saved by customer")
    delivery_status = models.CharField(max_length=100, choices=DELIVERY_STATUS, default="on_hold")
    delivery_couriers = models.ForeignKey("vendor.DeliveryCouriers", on_delete=models.SET_NULL, null=True, blank=True)
    tracking_id = models.CharField(max_length=100000, null=True, blank=True)
    
    invoice_no = models.CharField(max_length=200)
    product = models.CharField(max_length=200)
    product_obj = models.ForeignKey(Product, on_delete=models.CASCADE)
    image = models.CharField(max_length=200)
    paid = models.BooleanField(default=False)
    paid_vendor = models.BooleanField(default=False)
    cancelled = models.BooleanField(default=False)
    applied_coupon = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    oid = ShortUUIDField(length=10, max_length=25, alphabet="abcdefghijklmnopqrstuvxyz")

    class Meta:
        verbose_name_plural = "Cart Order Item"
        ordering = ["-date"]
        
    def order_img(self):
        return mark_safe('<img src="%s" width="50" height="50" style="object-fit:cover; border-radius: 6px;" />' % (self.product_obj.image.url))
   
    def total_payout(self):
        return self.shipping + self.total_payable
    
    def __str__(self):
        return self.oid
    
    

RATING = (
    ( 1,  "★☆☆☆☆"),
    ( 2,  "★★☆☆☆"),
    ( 3,  "★★★☆☆"),
    ( 4,  "★★★★☆"),
    ( 5,  "★★★★★"),
)


class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, blank=True, null=True, related_name="reviews")
    review = models.TextField()
    reply = models.CharField(null=True, blank=True, max_length=1000)
    rating = models.IntegerField(choices=RATING, default=None)
    active = models.BooleanField(default=False)
    helpful = models.ManyToManyField(User, blank=True, related_name="helpful")
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Reviews & Rating"
        ordering = ["-date"]
        
    def __str__(self):
        if self.product:
            return self.product.title
        else:
            return "Review"
        
    def get_rating(self):
        return self.rating
    
