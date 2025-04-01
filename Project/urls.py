"""
URL configuration for Project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from app import views
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.landing, name="login-page"),
    path('register/', views.register, name="user-registration"),
    path('home/', views.home, name='dashboard'),
    path('home/inventory/', views.view_inventory, name='inventory'),
    path('inventory/<int:product_id>/edit/', views.edit_product, name='edit-product'),
    path('inventory/<int:product_id>/delete/', views.delete_product, name='delete-product'),
    path('products/history/', views.product_history, name='product-history'),
    path('home/category/', views.category , name='category'),
    path('categories/<int:category_id>/edit/', views.edit_category, name='edit-category'),
    path('categories/<int:category_id>/delete/', views.delete_category, name='delete-category'),
    path('home/suppliers/', views.suppliers, name='suppliers'),
    path('suppliers/edit/<int:supplier_id>/', views.edit_supplier, name='edit-supplier'),
    path('suppliers/delete/<int:supplier_id>/', views.delete_supplier, name='delete-supplier'),
    path('logout/', views.logout_view, name='logout'),
    path('home/settings/', views.settings_view, name="settings")

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)