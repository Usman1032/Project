from django.contrib import admin
from .models import FinancialProfile, Property, InvestmentAnalysis

@admin.register(FinancialProfile)
class FinancialProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'monthly_salary', 'total_savings', 'risk_tolerance']

@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'location', 'price', 'bhk', 'area_sqft']
    list_filter = ['location', 'bhk', 'property_type']

@admin.register(InvestmentAnalysis)
class InvestmentAnalysisAdmin(admin.ModelAdmin):
    list_display = ['property', 'user', 'investment_score', 'recommendation', 'created_at']
    list_filter = ['recommendation']
