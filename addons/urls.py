from django.urls import path
from addons import views

app_name = "addons"

urlpatterns = [
    path("contact_us/", views.contact_us, name="contact_us"),
    path("about_us/", views.about_us, name="about_us"),
    path("send_faq_qs/", views.send_faq_qs, name="send_faq_qs"),
    path("subscribe_to_newsletter/", views.subscribe_to_newsletter, name="subscribe_to_newsletter"),
    path("privacy_terms_condition/", views.privacy_terms_condition, name="privacy_terms_condition"),
]
