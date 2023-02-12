from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.redirect_analysis),
    path('analysis', views.redirect_analysis),
    path('upload/', views.upload_doc, name = 'upload'),
    path('display/<slug:slug>', views.display_output, name = 'display'),
    path('analysis/<str:scale>', views.analysis, name = 'analysis'),
    path('enter_finances/', views.enter_finances, name = 'enter_finances'),
    path('view_finances/', views.view_finances, name = 'view_finances'),

    path('show_invoices/', views.show_items, name = 'show_invoices'),
    path('delete/<int:pk>', views.delete_invoice, name = 'delete_invoice'),
    path('buttons/', views.buttons, name = 'button')
]
