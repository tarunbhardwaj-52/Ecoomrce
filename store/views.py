from django.shortcuts import render, get_object_or_404 ,redirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponseNotFound, JsonResponse
from django.db import models
from django.contrib import messages
from django.template.loader import render_to_string
from django.conf import settings
from django.urls import reverse, reverse_lazy
from django.views.generic import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from django.db.models import Q, Count, Sum, F, FloatField
from django.core.mail import EmailMultiAlternatives, send_mail
from django.template.loader import render_to_string
from django.shortcuts import render, HttpResponse
from django.contrib.gis.geoip2 import GeoIP2
from django.core.paginator import Paginator


from store.forms import CheckoutForm, ReviewForm
from store.models import Product, Category, CartOrder, CartOrderItem, Brand, Gallery, Review, ProductFaq, ProductBidders, ProductOffers
from core.models import Address
from blog.models import Post
from vendor.forms import CouponApplyForm
from vendor.models import Vendor, OrderTracker, PayoutTracker, Notification, Coupon
from addons.models import BasicAddon, Company, TaxRate

from datetime import datetime as d
from datetime import datetime
import datetime
import pytz
import json
import stripe
import requests
from decimal import Decimal
from anymail.message import attach_inline_image_file
from paypal.standard.forms import PayPalPaymentsForm


utc=pytz.UTC

def index(request):
    addon = BasicAddon.objects.filter().first()
    brands = Brand.objects.filter(active=True)
    products = Product.objects.filter(status="published", featured=True).order_by("-id")[:10]
    top_selling_products = Product.objects.filter(status="published").order_by("-orders")[:10]
    hot_deal = Product.objects.filter(status="published", hot_deal=True).first()
    all_products = Product.objects.filter(status="published")[:16]
    posts = Post.objects.filter(status="published", featured=True)
    
    query = request.GET.get("q")
    if query:
        products = products.filter(Q(title__icontains=query)|Q(description__icontains=query)).distinct()
        
    
    
    context = {
        "all_products":all_products,
        "addon":addon,
        "posts":posts,
        "brands":brands,
        'hot_deal':hot_deal,
        "products":products,
        "top_selling_products":top_selling_products,
    }
    return render(request, "store/index.html", context)


def category_list(request):
    categories_ = Category.objects.filter(active=True)
    
    context = {
        "categories_":categories_,
    }
    return render(request, "store/categories.html", context)



def search_list(request):
    products = Product.objects.filter(status="published").order_by("-id")
    product_count = Product.objects.filter(status="published").order_by("-id")
    
    query = request.GET.get("q")
    if query:
        products = products.filter(Q(title__icontains=query)|Q(description__icontains=query)|Q(category__title__icontains=query)).distinct()
        product_count = product_count.filter(Q(title__icontains=query)|Q(description__icontains=query)|Q(category__title__icontains=query)).distinct()
        
    paginator = Paginator(products, 16)
    page_number = request.GET.get('page')
    products = paginator.get_page(page_number)
    
    
    context = {
        "product_count":product_count,
        "products":products,
        "query":query,
    }
    return render(request, "store/search_list.html", context)


def shop(request):
    brands = Brand.objects.filter(active=True)
    products = Product.objects.filter(status="published").order_by("-id")
    products_couunt = Product.objects.filter(status="published").order_by("-id")
    top_selling = Product.objects.filter(status="published").order_by("-orders")[:20]
    
    paginator = Paginator(products, 16)
    page_number = request.GET.get('page')
    products = paginator.get_page(page_number)
    
    context = {
        "products_couunt":products_couunt,
        "brands":brands,
        "products":products,
        "top_selling":top_selling,
    }
    return render(request, "store/shop.html", context)


def hot_deals(request):
    products = Product.objects.filter(status="published", hot_deal=True).order_by("-id")
    
    query = request.GET.get("q")
    if query:
        products = products.filter(Q(title__icontains=query)|Q(description__icontains=query)).distinct()
    
    paginator = Paginator(products, 16)
    page_number = request.GET.get('page')
    products = paginator.get_page(page_number)
    
    context = {
        "products":products,
    }
    return render(request, "store/hot-deals.html", context)



def category_detail(request, cid):
    category__ = Category.objects.get(cid=cid)
    top_selling = Product.objects.filter(status="published", category=category__).order_by("-id")[:10]
    products = Product.objects.filter(status="published", category=category__).order_by("orders")
    
    
    context = {
        "category__":category__,
        "products":products,
        "top_selling":top_selling,
    }
    return render(request, "store/category-detail.html", context)

def auction(request):
    products = Product.objects.filter(status="published", type="auction").order_by("-id")
    products_count = Product.objects.filter(status="published", type="auction")
    
    query = request.GET.get("q")
    if query:
        products = products.filter(Q(title__icontains=query)|Q(description__icontains=query)).distinct()
    
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    products = paginator.get_page(page_number)

    context = {
        "products":products,
        "products_count":products_count,
    }
    return render(request, "store/auction.html", context)

@login_required
def auction_detail(request, pid):
    product = Product.objects.get(status="published", type="auction", pid=pid)
    bidders = ProductBidders.objects.filter(product=product, active=True).order_by("-price")[:3]
    other_bidders = ProductBidders.objects.filter(product=product, active=True).order_by("-price")
    message = ""
    alert_tag = "success"
    completed = False
    winner = ProductBidders.objects.filter(product=product, active=True).order_by("-price").first()
    
    
    if timezone.now() < product.ending_date:
        message = "Bidding is still on going."
        completed = False
        product.auction_status = "on_going"
        product.bidding_ended = False
        product.save()
        try:
            winner.winner = False
            winner.win_status = "pending"
            winner.save()
        except:
            pass
        ProductBidders.objects.filter(product=product).update(winner=False)
        
    else:
        message = "Bidding have been completed"
        product.auction_status = "finished"
        product.bidding_ended = True
        product.save()
        completed = True
        try:
            winner.winner = True
            winner.win_status = "won"
            winner.save()
        except:
            pass
    
    if request.method == "POST":
        price = request.POST.get("price")
        if Decimal(price) < product.price:
            messages.warning(request, "You bidding price cannot be lower than the starting price")
            return redirect("store:auction_detail", product.pid)
        
        ProductBidders.objects.create(
            user=request.user,
            product=product,
            price=price,
            email=request.user.email,
            active=True
        )
        product.bidders.add(request.user)
        product.save()
        messages.success(request, "Bidding Placed Successfully.")
        return redirect("store:auction_detail", product.pid)
    
    context = {
        "winner":winner,
        "completed":completed,
        "alert_tag":alert_tag,
        "message":message,
        "product":product,
        "bidders":bidders,
        "other_bidders":other_bidders,
    }
    return render(request, "store/auction_detail.html", context)

@login_required
def auction_update(request, pid, bid):
    product = Product.objects.get(status="published", type="auction", pid=pid)
    bidders = ProductBidders.objects.filter(product=product, active=True).order_by("-price")[:3]
    other_bidders = ProductBidders.objects.filter(product=product, active=True).order_by("-price")
    bidding = ProductBidders.objects.get(bid=bid, product=product)
    
    if timezone.now() > product.ending_date:
        messages.error(request, "Bidding have been concluded, you cannot update your bidding amout again.")
        return redirect("store:auction_detail", product.pid)
    
    if request.method == "POST":
        price = request.POST.get("price")
        if Decimal(price) < product.price:
            messages.warning(request, "You bidding price cannot be lower than the starting price")
            return redirect("store:auction_update", product.pid, bidding.bid)
        
        if Decimal(price) < bidding.price:
            messages.warning(request, "You cannot go lower than your current bidding price")
            return redirect("store:auction_update", product.pid, bidding.bid)
        
        if Decimal(price) == bidding.price:
            messages.warning(request, "Your current bidding price cannot be the same as the new bidding price")
            return redirect("store:auction_update", product.pid, bidding.bid)
        
        
        bidding.price = Decimal(price)
        bidding.save()
        messages.success(request, "Bidding Placed Successfully.")
        return redirect("store:auction_detail", product.pid)
    
    context = {
        "product":product,
        "bidders":bidders,
        "other_bidders":other_bidders,
    }
    return render(request, "store/auction_update.html", context)


def offer(request):
    brands = Brand.objects.filter(active=True)
    products = Product.objects.filter(status="published", type="offer")

    context = {
        "brands":brands,
        "products":products,
    }
    return render(request, "store/offer.html", context)


def product_detail(request, slug):
    product = Product.objects.get(status="published", slug=slug)
    
    if product.status == "disabled":
        return redirect("store:home")
    
    product_images = Gallery.objects.filter(product=product)
    vendor = Vendor.objects.get(user=product.user)
    vendor_product = Product.objects.filter(vendor=vendor).order_by("-id")
    reviews = Review.objects.filter(product=product, active=True).order_by("-id")
    review_form = ReviewForm()

    five_star = Review.objects.filter(product=product, active=True, rating=5).count()
    four_star = Review.objects.filter(product=product, active=True, rating=4).count()
    three_star = Review.objects.filter(product=product, active=True, rating=3).count()
    two_star = Review.objects.filter(product=product, active=True, rating=2).count()
    one_star = Review.objects.filter(product=product, active=True, rating=1).count()

    for c in product.category.all():
        relatedproduct = Product.objects.filter(category=c, status="published").order_by("-id")[:5]
    
    youmightlike = Product.objects.filter(status="published").order_by("orders")[:5]
    
    questions_answers = ProductFaq.objects.filter(product=product, active=True).order_by("-id")
    
    # Bdding
    bidders = ProductBidders.objects.filter(product=product).order_by("-price")[:3]
    all_bidders = ProductBidders.objects.filter(product=product).order_by("-price")
    basic_addon = BasicAddon.objects.all().first()
    
    # Handlers
    make_review = True 
    make_bid = True 
    make_offer = True 
    reviewer_status = False
    if request.user.is_authenticated:
        all_orders = CartOrder.objects.filter(buyer=request.user, payment_status="paid")
        
        if all_orders.exists():
            reviewer_status = True
        else:
            reviewer_status = False
        
   
    service_fee = basic_addon.service_fee_percentage / 100 
    service_fee_flat_rate = basic_addon.service_fee_flat_rate
    service_fee_rate = 0
    
    if basic_addon.service_fee_charge_type == "percentage":
        processing_fee = float(product.price) * float(service_fee)
        service_fee_rate = service_fee
        
    elif basic_addon.service_fee_charge_type == "flat_rate":
        processing_fee = float(product.price) * float(service_fee_flat_rate)
        service_fee_rate = service_fee_flat_rate
        
        
    else:
        processing_fee = float(product.price) * 0.5
        service_fee_rate = 0
        
        
    location_country = request.session['location_country']
    
    tax = TaxRate.objects.filter(country=location_country, active=True).first()
    if tax:
        new_rate = tax.rate / 100
    else:
        new_rate = 0.22
    product_plus_shipping = product.price + product.shipping_amount
    tax_rate_amount = Decimal(new_rate) * product_plus_shipping
    
    # print("tax_rate_amount  =====================", round(tax_rate_amount, 2))
    # print("tax_rate_amount  =====================", round(tax_rate_amount, 2))
    # print("tax_rate_amount  =====================", round(tax_rate_amount, 2))
    
    total_price = product.price + Decimal(tax_rate_amount) + Decimal(processing_fee) + Decimal(product.shipping_amount)
    
    
    try:
        my_bid_obj = ProductBidders.objects.filter(product=product, user=request.user).first()
        my_bid = ProductBidders.objects.filter(product=product, user=request.user)
    except:
        my_bid = None
        my_bid_obj = None
        
        
    try:
        my_offer_obj = ProductOffers.objects.filter(product=product, user=request.user).first()
        my_offer = ProductOffers.objects.filter(product=product, user=request.user)
        if my_offer.exists():
            make_offer = False
    except:
        my_offer = None
        my_offer_obj = None
    

    if request.user.is_authenticated:
        user_review_count = Review.objects.filter(user=request.user, product=product).count()

        if user_review_count > 0:
            make_review = False
    
    if request.user.is_authenticated:
        if product.type == "offer":
            try:
                my_offer_obj = ProductOffers.objects.filter(product=product, user=request.user).first()
                my_offer = ProductOffers.objects.filter(product=product, user=request.user)
                if my_offer.exists():
                    make_offer = False
            except:
                my_offer = None
                my_offer_obj = None
                
            if make_offer == True:
                if request.method == "POST":
                    amount = request.POST.get("offer_amount")
                    message = request.POST.get("custom_message")
                    
                    print("amount ==================", amount)
                    print("message ==================", message)
                    
                    offer = ProductOffers.objects.create(user=request.user,price=amount,message=message,product=product,email=request.user.email)
                    Notification.objects.create(vendor=product.vendor,product=product,offer=offer,amount=amount,type="new_offer")
                    basic_addon = BasicAddon.objects.all().first()
                    if basic_addon.send_email_notifications == True:
                    
                        company = Company.objects.all().first()
                        merge_data = {
                            'company': company, 
                            'o': product, 
                        }
                        subject = f"New Offer for {product.title}"
                        text_body = render_to_string("email/message_body.txt", merge_data)
                        html_body = render_to_string("email/message_offer.html", merge_data)
                        
                        msg = EmailMultiAlternatives(
                            subject=subject, from_email=settings.FROM_EMAIL,
                            to=[product.vendor.shop_email], body=text_body
                        )
                        msg.attach_alternative(html_body, "text/html")
                        msg.send()
                    messages.success(request, f"Offer submitted successfully.")
                    return redirect("store:product-detail", product.slug)

            if make_offer == False:
                if request.method == "POST":
                    price = request.POST.get("offer_amount_update")
                    my_offer_obj.price = price
                    my_offer_obj.save()
                    messages.success(request, "Offer Updated Successfully.")
                    
                    # Email ======================
                    basic_addon = BasicAddon.objects.all().first()
                    if basic_addon.send_email_notifications == True:
                        company = Company.objects.all().first()
                        merge_data = {
                            'company': company, 
                            'o': product, 
                            'bid': winner, 
                        }
                        subject = f"Updated Offer Price for {product.title}"
                        text_body = render_to_string("email/message_body.txt", merge_data)
                        html_body = render_to_string("email/message_offer.html", merge_data)
                        
                        msg = EmailMultiAlternatives(
                            subject=subject, from_email=settings.FROM_EMAIL,
                            to=[product.vendor.shop_email], body=text_body
                        )
                        msg.attach_alternative(html_body, "text/html")
                        msg.send()
                        # Email ==========================
                    
                    return redirect("store:product-detail", product.slug)
                
    if request.user.is_authenticated:
        if product.type == "auction":
            winner = ProductBidders.objects.filter(product=product, active=True).order_by("-price").first()
            try:
                my_bid_obj = ProductBidders.objects.filter(product=product, user=request.user).first()
                my_bid = ProductBidders.objects.filter(product=product, user=request.user)
                # print("my bid =======================", my_bid_obj.price)
                # print("my bid Exist =======================", my_bid.exists())
                if my_bid.exists():
                    make_bid = False
            except:
                my_bid = None
                my_bid_obj = None
            
            if timezone.now() < product.ending_date:
                message = "Bidding is still on going."
                completed = False
                product.auction_status = "on_going"
                product.bidding_ended = False
                product.save()
                try:
                    winner.winner = False
                    winner.win_status = "pending"
                    winner.save()
                except:
                    pass
                ProductBidders.objects.filter(product=product).update(winner=False)
                
            else:
                message = "Bidding have been completed"
                product.auction_status = "finished"
                product.bidding_ended = True
                product.save()
                completed = True
                try:
                    winner.winner = True
                    winner.win_status = "won"
                    winner.save()
                except:
                    pass
            if make_bid == True:
                if request.method == "POST":
                    price = request.POST.get("bidding_amount")
                    if Decimal(price) < product.price:
                        messages.warning(request, "You bidding price cannot be lower than the starting price")
                        return redirect("store:product-detail", product.slug)
                    
                    bid = ProductBidders.objects.create(
                        user=request.user,
                        product=product,
                        price=price,
                        email=request.user.email,
                        active=True
                    )
                    product.bidders.add(request.user)
                    product.save()
                    Notification.objects.create(
                        vendor=product.vendor,
                        product=product,
                        bid=bid,
                        amount=price,
                        type="new_bidding"
                )
                    messages.success(request, "Bidding Placed Successfully.")
                    
                    # Email ======================
                    basic_addon = BasicAddon.objects.all().first()
                    if basic_addon.send_email_notifications == True:
                    
                        company = Company.objects.all().first()
                        merge_data = {
                            'company': company, 
                            'o': product, 
                            'bid': winner, 
                        }
                        subject = f"New Bidding for {product.title}"
                        text_body = render_to_string("email/message_body.txt", merge_data)
                        html_body = render_to_string("email/message_bidding.html", merge_data)
                        
                        msg = EmailMultiAlternatives(
                            subject=subject, from_email=settings.FROM_EMAIL,
                            to=[product.vendor.shop_email], body=text_body
                        )
                        msg.attach_alternative(html_body, "text/html")
                        msg.send()
                    # Email ==========================
                    
                    return redirect("store:product-detail", product.slug)
                
            if make_bid == False:
                if request.method == "POST":
                    price = request.POST.get("bidding_amount_update")
                    if Decimal(price) < my_bid_obj.price:
                        messages.warning(request, "You New bidding price cannot be lower than your previous price")
                        return redirect("store:product-detail", product.slug)
                    
                    my_bid_obj.price = price
                    my_bid_obj.save()
                    messages.success(request, "Bidding Updated Successfully.")
                    
                    # Email ======================
                    basic_addon = BasicAddon.objects.all().first()
                    if basic_addon.send_email_notifications == True:
                        company = Company.objects.all().first()
                        merge_data = {
                            'company': company, 
                            'o': product, 
                            'bid': winner, 
                        }
                        subject = f"Updated Bidding Price for {product.title}"
                        text_body = render_to_string("email/message_body.txt", merge_data)
                        html_body = render_to_string("email/message_bidding_updated.html", merge_data)
                        
                        msg = EmailMultiAlternatives(
                            subject=subject, from_email=settings.FROM_EMAIL,
                            to=[product.vendor.shop_email], body=text_body
                        )
                        msg.attach_alternative(html_body, "text/html")
                        msg.send()
                        # Email ==========================
                    
                    return redirect("store:product-detail", product.slug)

    context = {
        "bidders":bidders,
        "product":product,
        "product_images":product_images,
        "vendor":vendor,
        "vendor_product":vendor_product,
        "reviews":reviews,
        "review_form":review_form,
        "tax_rate_amount":tax_rate_amount,
        "tax":tax,
        "processing_fee":processing_fee,
        # Handlers
        "make_review":make_review,
        "make_bid":make_bid,
        "my_bid":my_bid,
        "my_bid_obj":my_bid_obj,
        "all_bidders":all_bidders,
        # Offers
        "my_offer":my_offer,
        "my_offer_obj":my_offer_obj,
        "make_offer":make_offer,
        # Star ratings
        "five_star":five_star,
        "four_star":four_star,
        "three_star":three_star,
        "two_star":two_star,
        "one_star":one_star,
        "questions_answers":questions_answers,
        "relatedproduct":relatedproduct,
        "youmightlike":youmightlike,
        "questions_answers":questions_answers,
        "total_price":total_price,
        "new_rate":new_rate,
        "service_fee_rate":service_fee_rate,
        "reviewer_status":reviewer_status,
    }
    return render(request, "store/product_detail.html", context)


def helpful_review(request):
    print("helpful")
    id = request.GET['id']
    review = Review.objects.get(id=id)
    if request.user in review.helpful.all():
        review.helpful.remove(request.user)
        review.save()

    else:
        review.helpful.add(request.user)
        review.save()

    data = {
        "bool": True,
        "message": "Thanks for rating this review"
    }
    return JsonResponse({"data":data})

def add_review(request, pid):
    product = Product.objects.get(pk=pid)
    user = request.user 

    review = Review.objects.create(
        user=user,
        product=product,
        review = request.POST['review'],
        rating = request.POST['rating'],
    )

    context = {
        'user': user.username,
        'review': request.POST['review'],
        'rating': request.POST['rating'],
    }

    average_reviews = Review.objects.filter(product=product).aggregate(rating=models.Avg("rating"))

    return JsonResponse(
       {
        'bool': True,
        'context': context,
        'average_reviews': average_reviews
       }
    )


def ask_question(request):
    id = request.GET['id']
    product = Product.objects.get(id=id)
    faq = ProductFaq.objects.create(product=product, email=request.user.email ,user=request.user, question=request.GET['question'])
    faq.save()
    return JsonResponse({'bool': True})
    
        

def add_to_cart(request):
    cart_product = {}
    

    cart_product[str(request.GET['id'])] = {
        'title': request.GET['title'],
        'qty': request.GET['qty'],
        'price': request.GET['price'],
        'product_slug': request.GET['product_slug'],
        'shipping_amount': request.GET['shipping_amount'],
        'vendor': request.GET['vendor'],
        'shop_name': request.GET['vendor_name'],
        'image': request.GET['image'],
        'pid': request.GET['pid'],
        'product_processing_fee': request.GET['product_processing_fee'],
        'product_tax_fee': request.GET['product_tax_fee'],
        "product_stock_qty":request.GET["product_stock_qty"],
        "product_in_stock":request.GET["product_in_stock"],        
        "product_vendor_slug":request.GET["product_vendor_slug"],

    }

    if 'cart_data_obj' in request.session:
        if str(request.GET['id']) in request.session['cart_data_obj']:

            cart_data = request.session['cart_data_obj']
            cart_data[str(request.GET['id'])]['qty'] = int(cart_product[str(request.GET['id'])]['qty'])
            cart_data.update(cart_data)
            request.session['cart_data_obj'] = cart_data
        else:
            cart_data = request.session['cart_data_obj']
            cart_data.update(cart_product)
            request.session['cart_data_obj'] = cart_data

    else:
        request.session['cart_data_obj'] = cart_product
    return JsonResponse({"data":request.session['cart_data_obj'], 'totalcartitems': len(request.session['cart_data_obj'])})

@csrf_exempt
def cart_view(request):
    
    cart_total_amount = 0
    total_shipping_amount = 0
    total_tax = 0
    total_amount = 0
    
    cart_total_amount_ = 0
    shipping_amount_ = 0
    total_amount_ = 0
    tax_amount = 0
    
    cart_total_amount_items = 0
    products_amount = 0
    service_fee_amount = 0
    service_fee_calc = 0
    tax_amount_ = 0
    shipping_amount__ = 0
    total_amount__ = 0
    processing_fee = 0
    processing_fee_ = 0
    order = []
    
    product_plus_shipping = 0
    
    main_cart_total = 0
    main_cart_total_item = 0
    # tax_rate = 0
    
    try:
        location_country = request.session['location_country']
        tax_country = TaxRate.objects.filter(country=location_country).first()
        tax_rate = tax_country.rate / 100
        # print("tax_rate =====================", tax_rate)
        # print("location_country =====================", location_country)
        
    except:
        location_country = "United States"
        tax_country = TaxRate.objects.filter(country=location_country).first()
        tax_rate = tax_country.rate / 100
        # print("location_country =====================", location_country)
        
    try:
        basic_addon = BasicAddon.objects.all().first()
        tax = basic_addon.general_tax_percentage / 100
        service_fee = basic_addon.service_fee_percentage / 100 
        service_fee_flat_rate = basic_addon.service_fee_flat_rate  
        vendor_fee = basic_addon.vendor_fee_percentage / 100 
    except:
        basic_addon = None
        tax = 0.5
        service_fee = 0.5
        vendor_fee = 0.5
        service_fee_flat_rate = 1
    
    if 'coupon_name' in request.session:
        vendor_coupon = Coupon.objects.filter(code=request.session['coupon_name'])
        print("vendor_coupon ===============", vendor_coupon)
    else:
        coupon_name = None
        

    if 'cart_data_obj' in request.session:
        
        for p_id, item in request.session['cart_data_obj'].items():
            cart_total_amount += int(item['qty']) * float(item['price'])
            total_shipping_amount += int(item['qty']) * float(item['shipping_amount'])
            total_tax += int(item['qty']) * float(tax_rate)
            products_amount += int(item['qty']) * float(item['price'])
            shipping_amount__ += int(item['qty']) * float(item['shipping_amount'])
            product_plus_shipping = products_amount + shipping_amount__
            
            # print("product_plus_shipping ==================", product_plus_shipping)
            # print("product_plus_shipping ==================", product_plus_shipping)
            # print("tax_amount_ ==================", tax_amount_)
            # print("tax_rate ==================", tax_rate)
            
            
            service_fee_calc = products_amount
            if basic_addon.service_fee_charge_type == "percentage":
                service_fee_amount = service_fee_calc * service_fee
                
            elif basic_addon.service_fee_charge_type == "flat_rate":
                service_fee_amount = service_fee_calc * float(service_fee_flat_rate)
                
            else:
                service_fee_amount = service_fee_calc * 0.5
                
                
            vendor = item['vendor']

            # total_amount = cart_total_amount + total_shipping_amount + total_tax + service_fee_amount
            main_cart_total = cart_total_amount + shipping_amount__
            tax_amount_ = main_cart_total * tax_rate
            
            total_amount = cart_total_amount + total_shipping_amount + service_fee_amount + tax_amount_
            
            product = Product.objects.get(id=p_id)
            
        # form = CheckoutForm()
        # if request.method == 'POST':
        #     form = CheckoutForm(request.POST)
        #     if form.is_valid():
        #         new_form = form.save(commit=False)
                
        #         full_name = new_form.full_name
        #         email = new_form.email
        #         mobile = new_form.mobile
        #         country = new_form.country
        #         state = new_form.state
        #         town_city = new_form.town_city
        #         address = new_form.address
                
                
        #         # tax_rate_fee = TaxRate.objects.filter(country=country)
        #         # if tax_rate_fee.exists():
        #         #     main_tax_fee = main_cart_total * tax_rate_fee.first().rate / 100
        #         #     print("tax_rate_fee ========================", main_tax_fee)
        #         # else:
        #         #     print("Failed ========================", tax_rate_fee)
        #         #     main_tax_fee = main_cart_total * 0.01
            
            
        #     main_tax_fee = main_cart_total * tax_rate
        #     total_amount__ = cart_total_amount + shipping_amount__ + main_tax_fee + service_fee_amount
        #     # print("main_tax_fee ==================", main_tax_fee)
            

        #     if request.user.is_authenticated:
        #         order = CartOrder.objects.create(
        #             full_name=full_name,
        #             email=email,
        #             mobile=mobile,
        #             country=country,
        #             state=state,
        #             town_city=town_city,
        #             address=address,
                    
        #             price=cart_total_amount, 
        #             buyer=request.user, 
        #             total=total_amount__, 
        #             shipping=shipping_amount__, 
        #             vat=main_tax_fee, 
        #             service_fee=service_fee_amount 
        #         )
        #         order.save()
        #     else:
        #         order = CartOrder.objects.create(
        #             full_name=full_name,
        #             email=email,
        #             mobile=mobile,
        #             country=country,
        #             state=state,
        #             town_city=town_city,
        #             address=address,
                    
        #             price=cart_total_amount, 
        #             buyer=None, 
        #             total=total_amount__, 
        #             shipping=shipping_amount__, 
        #             vat=main_tax_fee, 
        #             service_fee=service_fee_amount 
        #         )
        #         order.save()
        
        #     for p_id, item in request.session['cart_data_obj'].items():
        #         product = Product.objects.get(id=p_id)
        #         cart_total_amount_ += int(item['qty']) * float(item['price'])
        #         shipping_amount_ += int(item['qty']) * product.shipping_amount
        #         tax_amount += int(item['qty']) * float(tax)
        #         cart_total_amount_items = int(item['qty']) * float(item['price'])
        #         # Remove vendor fee from vendors products amounts
        #         total_payable = cart_total_amount_items -  vendor_fee
        #         item_shipping = int(item['qty']) * product.shipping_amount
                
        #         item_cart_total = int(item['qty']) * float(item['price'])
        #         main_cart_total_item = item_cart_total + float(item_shipping)
                
                
        #         service_fee_calc = products_amount
        #         # print("service_fee_calc ==================", service_fee_calc)
        #         if basic_addon.service_fee_charge_type == "percentage":
        #             service_fee_amount = service_fee_calc * service_fee
                    
        #         elif basic_addon.service_fee_charge_type == "flat_rate":
        #             service_fee_amount = service_fee_calc * float(service_fee_flat_rate)
                    
        #         else:
        #             service_fee_amount = service_fee_calc * 0.5

                
        #         tax_rate_fee = TaxRate.objects.filter(country=country)
        #         if tax_rate_fee.exists():
        #             main_tax_fee_item = main_cart_total_item * tax_rate_fee.first().rate / 100
        #             # print("tax_rate_fee ========================", main_tax_fee)
        #         else:
        #             # print("Failed ========================", tax_rate_fee)
        #             main_tax_fee_item = main_cart_total_item * 0.01
                
        #         grand_total = float(item['qty']) * float(item['price']) + float(item_shipping) + float(main_tax_fee_item) + float(service_fee_amount)
                
        #         cart_order_products = CartOrderItem.objects.create(
        #             order=order,
        #             vendor=product.vendor,
        #             invoice_no="#" + str(order.oid), 
        #             product=item['title'],
        #             image=item['image'],
        #             qty=item['qty'],
        #             product_obj=product,
        #             price=item['price'],
        #             shipping=item_shipping,
        #             paid_vendor=False,
        #             grand_total=grand_total,
        #             vat=main_tax_fee_item, 
        #             service_fee=service_fee_amount ,
        #             total_payable=total_payable,
        #             total=float(item['qty']) * float(item['price'])
        #         )
        #         cart_order_products.save()
        #         order.vendor.add(item['vendor'])

        #     return redirect('store:checkout', order.oid)
        now = timezone.now()
        if request.method == "POST":
            try:
                code = request.POST.get('code')
                coupon = Coupon.objects.get(code__iexact=code,valid_from__lte=now,valid_to__gte=now,active=True)
                print("coupon ===================", coupon.code)
                request.session['coupon_id'] = coupon.id
                request.session['coupon_name'] = coupon.code
                messages.success(request, f"Coupon Found and activated")
                return redirect("store:cart-view")
            except:
                messages.error(request, f"Coupon Not Found")
                return redirect("store:cart-view")
        else:
            form = CouponApplyForm()
        
        # del request.session['coupon_id']
        if 'coupon_name' in request.session:
            coupon_name = request.session['coupon_name']
        else:
            coupon_name = None
            
        context = {
            "cart_data":request.session['cart_data_obj'], 
            'totalcartitems': len(request.session['cart_data_obj']), 
            'cart_total_amount':cart_total_amount, 
            'tax_amount_':tax_amount_, 
            'total_shipping_amount':total_shipping_amount , 
            'total_tax':total_tax, 
            'total_amount':total_amount,
            'service_fee_amount':service_fee_amount,
            'form':form,
            'coupon_name':coupon_name,
        }

        return render(request, "store/cart.html", context)
    else:
        messages.warning(request, "Your cart is empty, add something to the cart to continue")
        return redirect("store:home")


@csrf_exempt
def shipping_address(request):
    
    cart_total_amount = 0
    total_shipping_amount = 0
    total_tax = 0
    total_amount = 0
    
    cart_total_amount_ = 0
    shipping_amount_ = 0
    total_amount_ = 0
    tax_amount = 0
    
    cart_total_amount_items = 0
    products_amount = 0
    service_fee_amount = 0
    service_fee_amount_ = 0
    service_fee_calc = 0
    service_fee_calc_ = 0
    tax_amount_ = 0
    shipping_amount__ = 0
    total_amount__ = 0
    processing_fee = 0
    processing_fee_ = 0
    order = []
    products_amount__ = 0
    product_plus_shipping = 0
    
    main_cart_total = 0
    main_cart_total_item = 0
    # tax_rate = 0
    
    try:
        location_country = request.session['location_country']
        tax_country = TaxRate.objects.filter(country=location_country).first()
        tax_rate = tax_country.rate / 100
        # print("tax_rate =====================", tax_rate)
        # print("location_country =====================", location_country)
        
    except:
        location_country = "United States"
        tax_country = TaxRate.objects.filter(country=location_country).first()
        tax_rate = tax_country.rate / 100
        # print("location_country =====================", location_country)
        
    try:
        basic_addon = BasicAddon.objects.all().first()
        tax = basic_addon.general_tax_percentage / 100
        service_fee = basic_addon.service_fee_percentage / 100 
        service_fee_flat_rate = basic_addon.service_fee_flat_rate  
        vendor_fee = basic_addon.vendor_fee_percentage / 100 
    except:
        basic_addon = None
        tax = 0.5
        service_fee = 0.5
        vendor_fee = 0.5
        service_fee_flat_rate = 1

    if 'cart_data_obj' in request.session:
        
        for p_id, item in request.session['cart_data_obj'].items():
            cart_total_amount += int(item['qty']) * float(item['price'])
            total_shipping_amount += int(item['qty']) * float(item['shipping_amount'])
            total_tax += int(item['qty']) * float(tax_rate)
            products_amount += int(item['qty']) * float(item['price'])
            shipping_amount__ += int(item['qty']) * float(item['shipping_amount'])
            product_plus_shipping = products_amount + shipping_amount__
            
            # print("product_plus_shipping ==================", product_plus_shipping)
            # print("product_plus_shipping ==================", product_plus_shipping)
            # print("tax_amount_ ==================", tax_amount_)
            # print("tax_rate ==================", tax_rate)
            
            
            service_fee_calc = products_amount
            if basic_addon.service_fee_charge_type == "percentage":
                service_fee_amount = service_fee_calc * service_fee
                
            elif basic_addon.service_fee_charge_type == "flat_rate":
                service_fee_amount = service_fee_calc * float(service_fee_flat_rate)
                
            else:
                service_fee_amount = service_fee_calc * 0.5
                
                
            vendor = item['vendor']

            # total_amount = cart_total_amount + total_shipping_amount + total_tax + service_fee_amount
            main_cart_total = cart_total_amount + shipping_amount__
            tax_amount_ = main_cart_total * tax_rate
            
            total_amount = cart_total_amount + total_shipping_amount + service_fee_amount + tax_amount_
            
            product = Product.objects.get(id=p_id)
            
        form = CheckoutForm()
        if request.method == 'POST':
            form = CheckoutForm(request.POST)
            if form.is_valid():
                new_form = form.save(commit=False)
                
                full_name = new_form.full_name
                email = new_form.email
                mobile = new_form.mobile
                country = new_form.country
                state = new_form.state
                town_city = new_form.town_city
                address = new_form.address

                billing_country = new_form.billing_country
                billing_state = new_form.billing_state
                billing_town_city = new_form.billing_town_city
                billing_address = new_form.billing_address
                
                
                # tax_rate_fee = TaxRate.objects.filter(country=country)
                # if tax_rate_fee.exists():
                #     main_tax_fee = main_cart_total * tax_rate_fee.first().rate / 100
                #     print("tax_rate_fee ========================", main_tax_fee)
                # else:
                #     print("Failed ========================", tax_rate_fee)
                #     main_tax_fee = main_cart_total * 0.01
            
            
            main_tax_fee = main_cart_total * tax_rate
            total_amount__ = cart_total_amount + shipping_amount__ + main_tax_fee + service_fee_amount
            # print("main_tax_fee ==================", main_tax_fee)
            

            if request.user.is_authenticated:
                order = CartOrder.objects.create(
                    full_name=full_name,
                    email=email,
                    mobile=mobile,
                    country=country,
                    state=state,
                    town_city=town_city,
                    address=address,

                    billing_country=billing_country,
                    billing_state=billing_state,
                    billing_town_city=billing_town_city,
                    billing_address=billing_address,
                    
                    price=cart_total_amount, 
                    buyer=request.user, 
                    total=total_amount__, 
                    original_total=total_amount__,
                    shipping=shipping_amount__, 
                    vat=main_tax_fee, 
                    service_fee=service_fee_amount 
                )
                order.save()
            else:
                order = CartOrder.objects.create(
                    full_name=full_name,
                    email=email,
                    mobile=mobile,
                    
                    country=country,
                    state=state,
                    town_city=town_city,
                    address=address,

                    billing_country=billing_country,
                    billing_state=billing_state,
                    billing_town_city=billing_town_city,
                    billing_address=billing_address,
                    
                    price=cart_total_amount, 
                    buyer=None, 
                    original_total=total_amount__,
                    total=total_amount__, 
                    shipping=shipping_amount__, 
                    vat=main_tax_fee, 
                    service_fee=service_fee_amount 
                )
                order.save()
        
            for p_id, item in request.session['cart_data_obj'].items():
                product = Product.objects.get(id=p_id)
                
                cart_total_amount_ += int(item['qty']) * float(item['price'])
                shipping_amount_ += int(item['qty']) * product.shipping_amount
                tax_amount += float(item['qty']) * tax_rate
                cart_total_amount_items = int(item['qty']) * float(item['price'])
                # Remove vendor fee from vendors products amounts
                total_payable = cart_total_amount_items -  vendor_fee
                item_shipping = int(item['qty']) * product.shipping_amount
                
                item_cart_total = int(item['qty']) * float(item['price'])
                main_cart_total_item = item_cart_total + float(item_shipping)
                
                products_amount__ = int(item['qty']) * float(item['price'])
                
                service_fee_calc_ = products_amount__
                # print("service_fee_calc ==================", service_fee_calc)
                if basic_addon.service_fee_charge_type == "percentage":
                    service_fee_amount_ = service_fee_calc_ * service_fee
                    
                elif basic_addon.service_fee_charge_type == "flat_rate":
                    service_fee_amount_ = service_fee_calc_ * float(service_fee_flat_rate)
                    
                else:
                    service_fee_amount_ = service_fee_calc_ * 0.5

                
               
                main_tax_fee_item = main_cart_total_item * tax_rate
                print("main_tax_fee_item ========================", main_tax_fee_item)
                print("service_fee_amount ========================", service_fee_amount_)
                
                
                grand_total = float(item['qty']) * float(item['price']) + float(item_shipping) + float(main_tax_fee_item) + float(service_fee_amount_)
                original_grand_total = float(item['qty']) * float(item['price']) + float(item_shipping) + float(main_tax_fee_item) + float(service_fee_amount_)
                cart_order_products = CartOrderItem.objects.create(
                    order=order,
                    vendor=product.vendor,
                    invoice_no="#" + str(order.oid), 
                    product=item['title'],
                    image=item['image'],
                    qty=item['qty'],
                    product_obj=product,
                    price=item['price'],
                    shipping=item_shipping,
                    paid_vendor=False,
                    original_grand_total=original_grand_total,
                    grand_total=grand_total,
                    vat=main_tax_fee_item, 
                    service_fee=service_fee_amount_ ,
                    total_payable=total_payable,
                    total=float(item['qty']) * float(item['price'])
                )
                cart_order_products.save()
                order.vendor.add(item['vendor'])

            return redirect('store:checkout', order.oid)

        context = {
            "cart_data":request.session['cart_data_obj'], 
            'totalcartitems': len(request.session['cart_data_obj']), 
            'cart_total_amount':cart_total_amount, 
            'tax_amount_':tax_amount_, 
            'total_shipping_amount':total_shipping_amount , 
            'total_tax':total_tax, 
            'total_amount':total_amount,
            'service_fee_amount':service_fee_amount,
            'form':form
        }

        return render(request, "store/shipping_address.html", context)
    else:
        messages.warning(request, "Your cart is empty, add something to the cart to continue")
        return redirect("store:home")


def delete_item_from_cart(request):
    product_id = str(request.GET['id'])
    if 'cart_data_obj' in request.session:
        if product_id in request.session['cart_data_obj']:
            cart_data = request.session['cart_data_obj']
            del request.session['cart_data_obj'][product_id]
            request.session['cart_data_obj'] = cart_data

    basic_addon = BasicAddon.objects.all().first()
    tax = basic_addon.general_tax_percentage / 100
    cs = basic_addon.currency_sign
    
    try:
        location_country = request.session['location_country']
        tax_country = TaxRate.objects.filter(country=location_country).first()
        tax_rate = tax_country.rate / 100
    except:
        tax_rate = None
        tax_country = "united States"

    cart_total_amount = 0
    shipping_amount_ = 0
    total_amount = 0
    tax_amount = 0
    product_processing_fee_ = 0
    total_plus_shipping = 0
    if 'cart_data_obj' in request.session:
        for p_id, item in request.session['cart_data_obj'].items():
            cart_total_amount += int(item['qty']) * float(item['price'])
            shipping_amount_ += int(item['qty']) * float(item['shipping_amount'])
            
            total_plus_shipping = cart_total_amount + shipping_amount_
            
            product_processing_fee_ = int(cart_total_amount) * float(item['product_processing_fee'])
            tax_amount = total_plus_shipping * tax_rate

            total_amount = cart_total_amount + shipping_amount_ + tax_amount + product_processing_fee_

    context = render_to_string("store/async/cart-list.html", {"cart_data":request.session['cart_data_obj'], 'totalcartitems': len(request.session['cart_data_obj']), 'cart_total_amount':cart_total_amount, 'total_shipping_amount':shipping_amount_ , 'total_tax':tax_amount, "cs":cs, 'total_amount':total_amount, 'product_processing_fee_':product_processing_fee_, "tax_country":tax_country})
    return JsonResponse({"data": context, 'totalcartitems': len(request.session['cart_data_obj'])})

def update_cart(request):
    product_id = str(request.GET['id'])
    product_qty = request.GET['qty']
    shipping_amount = request.GET['shipping_amount']
    product_tax_fee = request.GET['product_tax_fee']
    product_processing_fee = request.GET['product_processing_fee']
    

    basic_addon = BasicAddon.objects.all().first()
    tax = basic_addon.general_tax_percentage / 100
    cs = basic_addon.currency_sign
    
    try:
        location_country = request.session['location_country']
        tax_country = TaxRate.objects.filter(country=location_country).first()
        tax_rate = tax_country.rate / 100
    except:
        tax_rate = None

    # print("product_tax_fee =====================", product_tax_fee)


    if 'cart_data_obj' in request.session:
        if product_id in request.session['cart_data_obj']:
            cart_data = request.session['cart_data_obj']
            cart_data[str(request.GET['id'])]['qty'] = product_qty
            cart_data[str(request.GET['id'])]['shipping_amount'] = shipping_amount
            cart_data[str(request.GET['id'])]['product_tax_fee'] = product_tax_fee
            cart_data[str(request.GET['id'])]['product_processing_fee'] = product_processing_fee
            request.session['cart_data_obj'] = cart_data
    
    cart_total_amount = 0
    shipping_amount_ = 0
    total_amount = 0
    tax_amount = 0
    product_processing_fee_ = 0
    total_plus_shipping = 0
    
    if 'cart_data_obj' in request.session:
        for p_id, item in request.session['cart_data_obj'].items():
            cart_total_amount += int(item['qty']) * float(item['price'])
            shipping_amount_ += int(item['qty']) * float(item['shipping_amount'])
            
            total_plus_shipping = cart_total_amount + shipping_amount_
            
            product_processing_fee_ = int(cart_total_amount) * float(item['product_processing_fee'])
            tax_amount = total_plus_shipping * tax_rate

            total_amount = cart_total_amount + shipping_amount_ + tax_amount + product_processing_fee_
            
            # print("int(total_plus_shipping) =====================", int(total_plus_shipping))
            # print("float(item['product_tax_fee'] =====================", float(item['product_tax_fee']))
            
            

    context = render_to_string("store/async/cart-list.html", {"cart_data":request.session['cart_data_obj'], 'totalcartitems': len(request.session['cart_data_obj']), 'cart_total_amount':cart_total_amount ,  'total_shipping_amount':shipping_amount_ , 'total_tax':tax_amount, "cs":cs, 'total_amount':total_amount, 'product_processing_fee_':product_processing_fee_})
    return JsonResponse({"data": context, 'totalcartitems': len(request.session['cart_data_obj'])})

# def checkout_view(request, oid, *args, **kwargs):
#     try:
#         order = CartOrder.objects.get(oid=oid)
#         if order.payment_status == "paid":
#             messages.warning(request, "This Order have been paid for.")
#             return redirect("core:buyer-dashboard")
        
#         address = CartOrder.objects.get(oid=oid)
#         order_items = CartOrderItem.objects.filter(order=order)
#         # print("order_email =============", order.email)
#         order.payment_status = "processing"
#         order.save()
                
#         now = timezone.now()
#         if request.method == "POST":
#             try:
#                 if request.user.is_authenticated:
#                     code = request.POST.get('code')
#                     coupon = Coupon.objects.get(code__iexact=code,valid_from__lte=now,valid_to__gte=now,active=True)
                    
#                     order_items_ = CartOrderItem.objects.filter(vendor=coupon.vendor, order=order)
                    
#                     for o in order_items_:
#                         # if o.applied_coupon == False:
#                         if not coupon in o.coupon.all():

#                             calc = o.grand_total * coupon.discount / 100
#                             o.coupon_discount_grand_total = o.grand_total - calc
#                             coupon.redemption += 1
                            
#                             # Order
#                             order.coupons.add(coupon)
#                             order.total -= calc
#                             order.price -= calc
#                             order.saved += calc
                            
#                             # Order Items
#                             o.coupon.add(coupon)
#                             o.total_payable -= calc 
#                             o.grand_total -= calc
#                             o.saved += calc
#                             o.applied_coupon = True
#                             order.save()
#                             o.save()
#                             coupon.save()
#                             print("o.calc ==========", calc)
#                             print("o.coupon_discount_grand_total ==========", o.coupon_discount_grand_total)
#                         else:
#                             messages.warning(request, f"Coupon Already Activated")
#                             return redirect("store:checkout", order.oid)
#                     messages.success(request, f"Coupon Found and activated")
#                     return redirect("store:checkout", order.oid)
#                 else:
#                     code = request.POST.get('code')
#                     coupon = Coupon.objects.get(code__iexact=code,valid_from__lte=now,valid_to__gte=now,active=True)
                    
#                     order_items_ = CartOrderItem.objects.filter(vendor=coupon.vendor, order=order)
#                     for o in order_items_:
#                         if not coupon in o.coupon.all():
                            
#                             calc = o.grand_total * coupon.discount / 100
#                             o.coupon_discount_grand_total = o.grand_total - calc
#                             coupon.redemption += 1
                            
#                             # Order
#                             order.coupons.add(coupon)
#                             order.total -= calc
#                             order.price -= calc
#                             order.saved += calc
                            
#                             # Order Items
#                             # o.coupon = coupon
#                             o.coupon.add(coupon)
#                             o.total_payable -= calc 
#                             o.grand_total -= calc
#                             o.saved += calc
#                             o.applied_coupon = True
#                             order.save()
#                             o.save()
#                             coupon.save()
#                             print("o.calc ==========", calc)
#                             print("o.coupon_discount_grand_total ==========", o.coupon_discount_grand_total)
#                         else:
#                             messages.warning(request, f"Coupon Already Activated")
#                             return redirect("store:checkout", order.oid)
#                     messages.success(request, f"Coupon Found and activated")
#                     return redirect("store:checkout", order.oid)
#             except Coupon.DoesNotExist:
#                 messages.error(request, f"Coupon Not Found")
#                 return redirect("store:checkout", order.oid)    
#         else:
#             form = CouponApplyForm()
        
#         if 'coupon_id' in request.session:
#             del request.session['coupon_id']
#             del request.session['coupon_name']
        
        
#         host = request.get_host()
#         paypal_dict = {
#             'business': settings.PAYPAL_RECEIVER_EMAIL,
#             'amount': order.total,
#             'item_name': "Order-Item-No-" + str(order.id),
#             'invoice': "INVOICE_NO-" + str(timezone.now()),
#             'currency_code': "USD",
#             'notify_url': 'http://{}{}'.format(host, reverse("store:paypal-ipn")),
#             'return_url': 'http://{}{}'.format(host, reverse("store:payment-completed", kwargs={'oid': order.oid})),
#             'cancel_url': 'http://{}{}'.format(host, reverse("store:payment-failed")),
#         }
        
#         paypal_payment_button = PayPalPaymentsForm(initial=paypal_dict)
#     except CartOrder.DoesNotExist:
#         messages.warning(request, "The order you are trying is access does not exist.")
#         return redirect("store:home")
#     context = {
#         "order":order, 
#         "address":address, 
#         "order_items":order_items, 
#         "paypal_payment_button":paypal_payment_button, 
#         "stripe_publishable_key":settings.STRIPE_PUBLISHABLE_KEY, 
#         }

#     return render(request, "store/checkout.html", context)





def checkout_view(request, oid, *args, **kwargs):
    try:
        order = CartOrder.objects.get(oid=oid)
        if order.payment_status == "paid":
            messages.warning(request, "This Order have been paid for.")
            return redirect("core:buyer-dashboard")
        
        address = CartOrder.objects.get(oid=oid)
        order_items = CartOrderItem.objects.filter(order=order)
        # print("order_email =============", order.email)
        order.payment_status = "processing"
        order.save()
                
        now = timezone.now()
        if request.method == "POST":
            try:
                if request.user.is_authenticated:
                    code = request.POST.get('code')
                    coupon = Coupon.objects.get(code__iexact=code,valid_from__lte=now,valid_to__gte=now,active=True)
                    type = coupon.type
                    print("type =============", type)

                    order_items_ = CartOrderItem.objects.filter(vendor=coupon.vendor, order=order)
                    
                    for o in order_items_:
                        # if o.applied_coupon == False:
                        if not coupon in o.coupon.all():

                            
                            if type == "Percentage":

                                calc = o.total * coupon.discount / 100
                                o.coupon_discount_grand_total = o.grand_total - calc
                                coupon.redemption += 1
                                
                                # Order
                                order.coupons.add(coupon)
                                order.total -= calc
                                order.price -= calc
                                order.saved += calc
                                
                                # Order Items
                                o.coupon.add(coupon)
                                o.total_payable -= calc 
                                o.grand_total -= calc
                                o.saved += calc
                                o.applied_coupon = True
                                order.save()
                                o.save()
                                coupon.save()


                            elif type == "Flat Rate":

                                calc = coupon.discount

                                o.coupon_discount_grand_total = o.grand_total - calc
                                coupon.redemption += 1
                                
                                # Order
                                order.coupons.add(coupon)
                                order.total -= calc
                                order.price -= calc
                                order.saved += calc
                                
                                # Order Items
                                o.coupon.add(coupon)
                                o.total_payable -= calc 
                                o.grand_total -= calc
                                o.saved += calc
                                o.applied_coupon = True
                                order.save()
                                o.save()
                                coupon.save()
                                print("o.calc ==========", calc)
                                print("o.coupon_discount_grand_total ==========", o.coupon_discount_grand_total)
                            
                            else:
                                messages.error(request, f"Coupon Have No Discount Type")
                                return redirect("store:checkout", order.oid)
                        else:
                            messages.warning(request, f"Coupon Already Activated")
                            return redirect("store:checkout", order.oid)
                    messages.success(request, f"Coupon Found and activated")
                    return redirect("store:checkout", order.oid)
                else:
                    code = request.POST.get('code')
                    coupon = Coupon.objects.get(code__iexact=code,valid_from__lte=now,valid_to__gte=now,active=True)
                    
                    order_items_ = CartOrderItem.objects.filter(vendor=coupon.vendor, order=order)
                    for o in order_items_:
                        if not coupon in o.coupon.all():
                            
                            calc = o.grand_total * coupon.discount / 100
                            o.coupon_discount_grand_total = o.grand_total - calc
                            coupon.redemption += 1
                            
                            # Order
                            order.coupons.add(coupon)
                            order.total -= calc
                            order.price -= calc
                            order.saved += calc
                            
                            # Order Items
                            # o.coupon = coupon
                            o.coupon.add(coupon)
                            o.total_payable -= calc 
                            o.grand_total -= calc
                            o.saved += calc
                            o.applied_coupon = True
                            order.save()
                            o.save()
                            coupon.save()
                            print("o.calc ==========", calc)
                            print("o.coupon_discount_grand_total ==========", o.coupon_discount_grand_total)
                        else:
                            messages.warning(request, f"Coupon Already Activated")
                            return redirect("store:checkout", order.oid)
                    messages.success(request, f"Coupon Found and activated")
                    return redirect("store:checkout", order.oid)
            except Coupon.DoesNotExist:
                messages.error(request, f"Coupon Not Found")
                return redirect("store:checkout", order.oid)    
        else:
            form = CouponApplyForm()
        
        if 'coupon_id' in request.session:
            del request.session['coupon_id']
            del request.session['coupon_name']
        
        
        host = request.get_host()
        paypal_dict = {
            'business': settings.PAYPAL_RECEIVER_EMAIL,
            'amount': order.total,
            'item_name': "Order-Item-No-" + str(order.id),
            'invoice': "INVOICE_NO-" + str(timezone.now()),
            'currency_code': "USD",
            'notify_url': 'http://{}{}'.format(host, reverse("store:paypal-ipn")),
            'return_url': 'http://{}{}'.format(host, reverse("store:payment-completed", kwargs={'oid': order.oid})),
            'cancel_url': 'http://{}{}'.format(host, reverse("store:payment-failed")),
        }
        
        paypal_payment_button = PayPalPaymentsForm(initial=paypal_dict)
    except CartOrder.DoesNotExist:
        messages.warning(request, "The order you are trying is access does not exist.")
        return redirect("store:home")
    context = {
        "order":order, 
        "address":address, 
        "order_items":order_items, 
        "paypal_payment_button":paypal_payment_button, 
        "stripe_publishable_key":settings.STRIPE_PUBLISHABLE_KEY, 
        }

    return render(request, "store/checkout.html", context)



def custom_checkout_view(request, oid):
    order = CartOrder.objects.get(oid=oid)
    address = CartOrder.objects.get(oid=oid)
    order_items = CartOrderItem.objects.filter(order=order)
    print("order_email =============", order.email)

    host = request.get_host()
    paypal_dict = {
        'business': settings.PAYPAL_RECEIVER_EMAIL,
        'amount': order.total,
        'item_name': "Order-Item-No-" + str(order.id),
        'invoice': "INVOICE_NO-" + str(timezone.now()),
        'currency_code': "USD",
        'notify_url': 'http://{}{}'.format(host, reverse("store:paypal-ipn")),
        'return_url': 'http://{}{}'.format(host, reverse("store:payment-completed", kwargs={'oid': order.oid})),
        'cancel_url': 'http://{}{}'.format(host, reverse("store:payment-failed")),
    }
    
    paypal_payment_button = PayPalPaymentsForm(initial=paypal_dict)
    
    context = {
        "paypal_payment_button":paypal_payment_button, 
        "order":order, 
        "address":address, 
        "order_items":order_items, 
        "stripe_publishable_key":settings.STRIPE_PUBLISHABLE_KEY, 
    }

    return render(request, "store/checkout2.html", context)

class PaymentConfirmation(DetailView):
    model = CartOrder
    template_name = "payment/payment_detail.html"
    pk_url_kwarg = 'id'

    def get_context_data(self, **kwargs):
        context = super(PaymentConfirmation, self).get_context_data(**kwargs)
        context['stripe_publishable_key'] = settings.STRIPE_PUBLISHABLE_KEY
        return context  
    
from django.core.mail import send_mail

def PaymentSuccessView(request):
    session_id = request.GET.get('session_id')
    if session_id is None:
        return HttpResponseNotFound()
    stripe.api_key = settings.STRIPE_SECRET_KEY
    session = stripe.checkout.Session.retrieve(session_id)
    order = get_object_or_404(CartOrder, stripe_payment_intent=session.id)
    
    if order.payment_status == "processing":
        order.payment_status = "paid"
        order.payment_method = "Credit/Debit Card"
        order.delivery_status = "shipping_processing"
        order.save()
        
        
        
        CartOrderItem.objects.filter(order=order, order__payment_status="paid").update(paid=True, delivery_status="shipping_processing")
        order_items = CartOrderItem.objects.filter(order=order, order__payment_status="paid")
        
        company = Company.objects.all().first()
        basic_addon = BasicAddon.objects.all().first()

        if basic_addon.send_email_notifications == True:
            merge_data = {
                'company': company, 
                'order': order, 
                'order_items': order_items, 
            }
            subject = f"Order Placed Successfully. ID {order.oid}"
            text_body = render_to_string("email/message_body.txt", merge_data)
            html_body = render_to_string("email/message_customer.html", merge_data)
            
            msg = EmailMultiAlternatives(
                subject=subject, from_email=settings.FROM_EMAIL,
                to=[order.email], body=text_body
            )
            msg.attach_alternative(html_body, "text/html")
            msg.send()

        
        for o in order_items:
            o.product_obj.stock_qty -= o.qty
            o.product_obj.save()
            
            amount = o.total_payable +  o.shipping
            
            PayoutTracker.objects.create(vendor=o.vendor, currency=o.vendor.currency, amount=amount, item=order)
            Notification.objects.create(vendor=o.vendor, user=o.vendor.user, type="new_order", product=o.product_obj, amount=amount, order=o.order)
            
            company = Company.objects.all().first()
            basic_addon = BasicAddon.objects.all().first()
            
            
            if basic_addon.send_email_notifications == True:
                # Vendor Email
                merge_data = {
                    'company': company, 
                    'o': o, 
                }
                subject = f"New Order for {o.product_obj.title}"
                text_body = render_to_string("email/message_body.txt", merge_data)
                html_body = render_to_string("email/message_body.html", merge_data)
                
                msg = EmailMultiAlternatives(
                    subject=subject, from_email=settings.FROM_EMAIL,
                    to=[o.vendor.shop_email], body=text_body
                )
                msg.attach_alternative(html_body, "text/html")
                msg.send()
                
                
                
            
        for o in order.vendor.all():
        
            # cart_order_items = CartOrderItem.objects.filter(order=order, order__payment_status="paid", vendor=o).aggregate(amount=models.Sum('total_payable'))
            
            cart_order_items = CartOrderItem.objects.filter(order=order, order__payment_status="paid", vendor=o).aggregate(amount=models.Sum(F('total_payable') + F('shipping')))
            print("cart_order_items =========", round(cart_order_items['amount'], 2))
            basic_addon = BasicAddon.objects.all().first()
            
            if basic_addon.payout_vendor_fee_immediately == True:
                if o.payout_method == 'payout_to_stripe':
                    stripe.Transfer.create(
                        amount=int(cart_order_items['amount']) * 100,
                        currency="usd",
                        destination=o.stripe_user_id,
                        transfer_group="ORDER_95",
                    )
                    
                
                if o.payout_method == 'payout_to_paypal':
                    timestamp = d.now()
                    # timestamp = timezone.now()
                    username = settings.PAYPAL_CLIENT_ID
                    password = settings.PAYPAL_SECRET_ID
                    headers = {'Content-Type': 'application/json',}
                    data = '{"sender_batch_header": {"sender_batch_id": "Payouts_' + str(timestamp) + '","email_subject": "You have a payout!","email_message": "You have received a payout for an order!"},"items": [{"recipient_type": "EMAIL","amount": {"value": "'+ str(round(cart_order_items['amount'], 2)) +'","currency": "'+ str(o.currency) +'"},"note": "Thanks for your patronage!","sender_item_id": "201403140001","receiver": "'+ str(o.paypal_email_address) +'","notification_language": "en-US"}]}'
                    response = requests.post('https://api-m.sandbox.paypal.com/v1/payments/payouts', headers=headers, data=data, auth=(username, password))
                    
                    print("Response ============", response)
                    print("date ============", data)
                    
                    
                    
                if o.payout_method == 'payout_to_wallet':
                    o.wallet += cart_order_items['amount']
                    o.save()
            else:
                o.wallet += cart_order_items['amount']
                o.save()
                
            
            o.save()
            
    elif order.payment_status == "paid":
        messages.success(request, f'Your Order have been recieved.')
        return redirect("core:buyer-dashboard")
    else:
        messages.success(request, 'Opps... Internal Server Error; please try again later')
        return redirect("core:buyer-dashboard")
        
    products = CartOrderItem.objects.filter(order=order)
    return render(request, "payment/payment_success.html", {"order": order, 'products':products}) 

def PaymentFailedView(request):
    session_id = request.GET.get('session_id')
    if session_id is None:
        return HttpResponseNotFound()
    
    stripe.api_key = settings.STRIPE_SECRET_KEY
    session = stripe.checkout.Session.retrieve(session_id)
    print("session ===========", session)
    order = get_object_or_404(CartOrder, stripe_payment_intent=session.id)
    order.payment_status = "failed"
    order.save()
    print("order ====", order)
    
    return render(request, "payment/payment_failed.html", {"order": order}) 

@csrf_exempt
def create_checkout_session(request, id):

    request_data = json.loads(request.body)
    order = get_object_or_404(CartOrder, oid=id)

    stripe.api_key = settings.STRIPE_SECRET_KEY
    checkout_session = stripe.checkout.Session.create(
        customer_email = order.email,
        payment_method_types=['card'],
        line_items=[
            {
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                    'name': order.full_name,
                    },
                    
                    'unit_amount': int(order.total * 100),
                },
                'quantity': 1,
            }
        ],
        mode='payment',
        success_url=request.build_absolute_uri(
            reverse('store:success')
        ) + "?session_id={CHECKOUT_SESSION_ID}",
        cancel_url=request.build_absolute_uri(reverse('store:failed'))+ "?session_id={CHECKOUT_SESSION_ID}",
    )

    order.payment_status = "processing"
    order.stripe_payment_intent = checkout_session['id']
    order.save()

    print("checkout_session ==============", checkout_session)
    return JsonResponse({'sessionId': checkout_session.id})



def payment_completed_view(request, oid, *args, **kwargs):
    order = CartOrder.objects.get(oid=oid)
    
    if order.payment_status == "processing":
        order.payment_status = "paid"
        order.payment_method = "Paypal"
        order.delivery_status = "shipping_processing"
        order.save()
        
        
        CartOrderItem.objects.filter(order=order, order__payment_status="paid").update(paid=True, delivery_status="shipping_processing")
        order_items = CartOrderItem.objects.filter(order=order, order__payment_status="paid")
        
        
        company = Company.objects.all().first()
        basic_addon = BasicAddon.objects.all().first()
        if basic_addon.send_email_notifications == True:
            merge_data = {
                'company': company, 
                'order': order, 
                'order_items': order_items, 
            }
            subject = f"Order Placed Successfully. ID {order.oid}"
            text_body = render_to_string("email/message_body.txt", merge_data)
            html_body = render_to_string("email/message_customer.html", merge_data)
            
            msg = EmailMultiAlternatives(
                subject=subject, from_email=settings.FROM_EMAIL,
                to=[order.email], body=text_body
            )
            msg.attach_alternative(html_body, "text/html")
            msg.send()

        
        for o in order_items:
            o.product_obj.stock_qty -= o.qty
            o.product_obj.save()
            
            amount = o.total_payable +  o.shipping
            
            PayoutTracker.objects.create(vendor=o.vendor, currency=o.vendor.currency, amount=amount, item=order)
            Notification.objects.create(vendor=o.vendor, user=o.vendor.user, type="new_order", product=o.product_obj, amount=amount, order=o.order)
            
            company = Company.objects.all().first()
            basic_addon = BasicAddon.objects.all().first()
            if basic_addon.send_email_notifications == True:
                merge_data = {
                    'company': company, 
                    'o': o, 
                }
                subject = render_to_string("email/message_subject.txt", merge_data).strip()
                text_body = render_to_string("email/message_body.txt", merge_data)
                html_body = render_to_string("email/message_body.html", merge_data)
                
                msg = EmailMultiAlternatives(
                    subject=subject, from_email=settings.FROM_EMAIL,
                    to=[o.vendor.shop_email], body=text_body
                )
                msg.attach_alternative(html_body, "text/html")
                msg.send()
                
            
        for o in order.vendor.all():
        
            # cart_order_items = CartOrderItem.objects.filter(order=order, order__payment_status="paid", vendor=o).aggregate(amount=models.Sum('total_payable'))
            
            cart_order_items = CartOrderItem.objects.filter(order=order, order__payment_status="paid", vendor=o).aggregate(amount=models.Sum(F('total_payable') + F('shipping')))
            print("cart_order_items =========", round(cart_order_items['amount'], 2))
            basic_addon = BasicAddon.objects.all().first()
            
            if basic_addon.payout_vendor_fee_immediately == True:
                if o.payout_method == 'payout_to_stripe':
                    stripe.Transfer.create(
                        amount=int(cart_order_items['amount']) * 100,
                        currency="usd",
                        destination=o.stripe_user_id,
                        transfer_group="ORDER_95",
                    )
                    
                if o.payout_method == 'payout_to_paypal':
                    timestamp = d.now()
                    # timestamp = timezone.now()
                    username = settings.PAYPAL_CLIENT_ID
                    password = settings.PAYPAL_SECRET_ID
                    headers = {'Content-Type': 'application/json',}
                    data = '{"sender_batch_header": {"sender_batch_id": "Payouts_' + str(timestamp) + '","email_subject": "You have a payout!","email_message": "You have received a payout for an order!"},"items": [{"recipient_type": "EMAIL","amount": {"value": "'+ str(round(cart_order_items['amount'], 2)) +'","currency": "'+ str(o.currency) +'"},"note": "Thanks for your patronage!","sender_item_id": "201403140001","receiver": "'+ str(o.paypal_email_address) +'","notification_language": "en-US"}]}'
                    response = requests.post('https://api-m.sandbox.paypal.com/v1/payments/payouts', headers=headers, data=data, auth=(username, password))
                    
                    print("Response ============", response)
                    print("date ============", data)
                    
                if o.payout_method == 'payout_to_wallet':
                    o.wallet += cart_order_items['amount']
                    o.save()
            else:
                o.wallet += cart_order_items['amount']
                o.save()
            
            o.save()
            
    elif order.payment_status == "paid":
        messages.success(request, f'Your Order have been recieved.')
        return redirect("core:buyer-dashboard")
    else:
        messages.success(request, 'Opps... Internal Server Error; please try again later')
        return redirect("core:buyer-dashboard")
        
    products = CartOrderItem.objects.filter(order=order)
    
    context = {
        "order":order,
        'products':products,
    }
    return render(request, "payment/paypal_payment_success.html", context) 



def payment_failed_view(request):
    return render(request, "payment/paypal_payment_failed.html") 


def country_get(request):
    # x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    # if x_forwarded_for:
    #     ip = x_forwarded_for.split(',')[0]
    # else:
    #     ip = request.META.get('REMOTE_ADDR')
    
    # device_type = ""
    # browser_type = ""
    # browser_version = ""
    # os_type = ""
    # os_version = ""
    # if request.user_agent.is_mobile:
    #     device_type = "Mobile"
    # if request.user_agent.is_tablet:
    #     device_type = "Tablet"
    # if request.user_agent.is_pc:
    #     device_type = "PC"
    
    # browser_type = request.user_agent.browser.family
    # browser_version = request.user_agent.browser.version_string
    # os_type = request.user_agent.os.family
    # os_version = request.user_agent.os.version_string
    
    # g = GeoIP2()
    # location = g.city(ip)
    # location_country = location["country_name"]
    # location_city = location["city"]
    
    # tax = TaxRate.objects.filter(country=location_country, active=True).first()
    # print("NOTE: =================== ", tax)
    
    
        
    
    # context = {
    #     "ip": ip,
    #     "device_type": device_type,
    #     "browser_type": browser_type,
    #     "browser_version": browser_version,
    #     "os_type":os_type,
    #     "os_version":os_version,
    #     "location_country": location_country,
    #     "location_city": location_city
    # }
    return render(request, "store/country_get.html")


