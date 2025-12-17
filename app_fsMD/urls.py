from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('contact-us/', views.contact, name='contact'),
    path('about-us/', views.about, name='about'),
    path('terms-and-conditions/', views.terms_conditions, name='terms_conditions'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('refund-policy/', views.refund_policy, name='refund_policy'),
    path('telehealth-consent/', views.telehealth_consent, name='telehealth_consent'),
    path('hipaa-notice-of-privacy-practices/', views.hipaa_notice, name='hipaa_notice'),
    path('medical-disclaimer/', views.medical_disclaimer, name='medical_disclaimer'),
    path('accessibility-statement/', views.accessibility_statement, name='accessibility_statement'),
    path('faq/', views.faq, name='faq'),
    path('blog/', views.blog, name='blog'),

    path("programs/<slug:slug>/", views.program_detail, name="program_detail"),
    path("products/<slug:slug>/", views.product_detail, name="product_detail"),
    
    path("cart/add/", views.cart_add, name="cart_add"),
    path("cart/summary/", views.cart_summary, name="cart_summary"),
    path("cart/", views.cart_page, name="cart_page"),   
    path("cart/update/", views.cart_update, name="cart_update"),
    path("cart/remove/", views.cart_remove, name="cart_remove"),

]
