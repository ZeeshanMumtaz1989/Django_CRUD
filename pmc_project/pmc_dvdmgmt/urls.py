from django.contrib import admin
from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static



urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', views.index, name='index'),
    path('inventory/', views.inventory, name='inventory'), 
    path('dvdAddition/', views.dvdAddition, name='dvdAddition'), 
    path('dvdDeletionPage/<int:dvd_id>/', views.dvdDeletionPage, name='dvdDeletionPage'),  # Corrected URL pattern
    path('dvdDeletion/<int:dvd_id>/', views.dvdDeletion, name='dvdDeletion'),  # Corrected URL pattern
    path('issuereceiverecord/', views.issuereceiverecord, name='issuereceiverecord'), 
    path('dvdIssuance/', views.dvdIssuance, name='dvdIssuance'), 
    path('inventoryView/<int:dvd_id>/', views.inventoryView, name='inventoryView'),  
    path('issuereceiverecordlist/<int:dvd_id>/', views.issuereceiverecordlist, name='issuereceiverecordlist'), 
    path('issuereceiverecordquery/', views.issuereceiverecordquery, name='issuereceiverecordquery'),  
    path('editinventoryitem/<int:dvd_id>/', views.editinventoryitem, name='editinventoryitem'), 
    path('editdvdissuance/<int:dvd_id>/', views.editdvdissuance, name='editdvdissuance'), 
    path('bulkdvdaddition/', views.bulkdvdaddition, name='bulkdvdaddition'),    
    path('issuereceiverecordadvsearch/', views.issuereceiverecordadvsearch, name='issuereceiverecordadvsearch'),
    path('outofordershredding/', views.outofordershredding, name='outofordershredding'),
    path('shredd_dvds/', views.shredd_dvds, name='shredd_dvds'),
    path('login/', views.loginPage, name='login'),
    path('logout/', views.logoutUser, name='logout'),
    path('inventoryAvailable/', views.inventoryAvailable, name='inventoryAvailable'), 
    path('inventoryReserved/', views.inventoryReserved, name='inventoryReserved'), 
    path('inventoryOutofOrder/', views.inventoryOutofOrder, name='inventoryOutofOrder'),
   
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

