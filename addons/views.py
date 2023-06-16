from django.shortcuts import render, redirect
from addons.models import BasicAddon, Company, EarningPoints, NewsLetter, Policy, TaxRate, SuperUserSignUpPin, ContactUs, FAQs, Announcements, PlatformNotifications, TutorialVideo
from addons.forms import ContactUSForm
from django.contrib import messages
from django.http import JsonResponse



def contact_us(request):
    
    if request.method == "POST":
        form = ContactUSForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'You message have been sent, an agent would would contact you soon.')
            return redirect("addons:contact_us")
    
    else:
        form = ContactUSForm()
    
    context = {
        "form":form,
    }
        
    return render(request, "addons/contact_us.html", context)
            
    
    
def send_faq_qs(request):
    question = request.POST.get("question")
    email = request.POST.get("email")
    FAQs.objects.create(question=question,email=email,)
    data = {
        "message":"Question sent successfully, would be answered soon."
    }
    return JsonResponse({"data":data})


def subscribe_to_newsletter(request):
    email = request.GET['email']
    NewsLetter.objects.create(email=email)
    data = {
        "message":"Thanks for subscribing to our newsletter."
    }
    return JsonResponse({"data":data})


def privacy_terms_condition(request):
    try:
        policy = Policy.objects.all().first()
    except:
        policy = None
    context = {
        "policy":policy,
    }
        
    return render(request, "addons/privacy_terms_condition.html", context)


def about_us(request):
    company = Company.objects.all().first()
    
    context = {
        "company":company,
    }
        
    return render(request, "addons/about_us.html", context)