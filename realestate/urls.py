from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/financial/', views.financial_profile, name='financial_profile'),

    path('properties/', views.property_list, name='property_list'),
    path('properties/add/', views.add_property, name='add_property'),
    path('properties/<int:pk>/delete/', views.delete_property, name='delete_property'),

    path('analyze/<int:pk>/', views.analyze_property, name='analyze_property'),
    path('result/<int:pk>/', views.analysis_result, name='analysis_result'),
    path('history/', views.analysis_history, name='analysis_history'),
]
