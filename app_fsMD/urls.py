from django.urls import path
from django.contrib.sitemaps.views import sitemap
from . import views
from .sitemaps import StaticViewSitemap, CategorySitemap, ProductSitemap

sitemaps = {
    "static": StaticViewSitemap,
    "categories": CategorySitemap,
    "products": ProductSitemap,
}

urlpatterns = [
    path('', views.home, name='home'),
    path('contact-us/', views.contact, name='contact'),
    path('about-us/', views.about, name='about'),
    path('terms-and-conditions/', views.terms_conditions, name='terms_conditions'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('refund-policy/', views.refund_policy, name='refund_policy'),
    path('telehealth-consent/', views.telehealth_consent, name='telehealth_consent'),
    path('hipaa-notice-of-privacy-practices/', views.hipaa_notice, name='hipaa_notice'),
    path('medical-disclaimer/', views.medical_disclaimer, name='medical_disclaimer'),
    path('accessibility-statement/', views.accessibility_statement, name='accessibility_statement'),
    path('faqs/', views.faqs, name='faqs'),

    path('blogs-and-updates/', views.blgs_updts, name='blgs_updts'),
    path('newsletter/subscribe/', views.newsletter_subscribe, name='newsletter_subscribe'),

    path("program-details/<slug:slug>/", views.prgrm_dtls, name="prgrm_dtls"),
    path("product-details/<slug:slug>/", views.prdct_dtls, name="prdct_dtls"),
    path("programs-and-services/", views.prgrms_srvcs, name="prgrms_srvcs"),
    
    path("cart/add/", views.cart_add, name="cart_add"),
    path("cart/summary/", views.cart_summary, name="cart_summary"),
    path("cart/", views.cart_page, name="cart_page"),   
    path("cart/update/", views.cart_update, name="cart_update"),
    path("cart/remove/", views.cart_remove, name="cart_remove"),

    path("robots.txt", views.robots_txt, name="robots_txt"),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="django.contrib.sitemaps.views.sitemap"),
    path("test-404/", views.test_404, name="test_404"),

]
