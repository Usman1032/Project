from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import FinancialProfile, Property, InvestmentAnalysis


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


class FinancialProfileForm(forms.ModelForm):
    class Meta:
        model = FinancialProfile
        exclude = ['user']
        widgets = {
            'monthly_salary': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 80000'}),
            'monthly_expenses': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 30000'}),
            'total_savings': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 500000'}),
            'risk_tolerance': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'monthly_salary': 'Monthly Salary (₹)',
            'monthly_expenses': 'Monthly Expenses (₹)',
            'total_savings': 'Total Savings (₹)',
            'risk_tolerance': 'Risk Tolerance',
        }


class PropertyForm(forms.ModelForm):
    class Meta:
        model = Property
        exclude = ['user']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 2BHK Apartment in Koramangala'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Bangalore'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 7500000'}),
            'area_sqft': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 1200'}),
            'bhk': forms.Select(attrs={'class': 'form-select'}),
            'property_type': forms.Select(attrs={'class': 'form-select'}),
            'age_years': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 3'}),
            'floor_number': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 4'}),
            'total_floors': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 10'}),
        }
        labels = {
            'price': 'Property Price (₹)',
            'area_sqft': 'Area (sq ft)',
            'bhk': 'Number of BHK',
            'age_years': 'Property Age (years)',
        }


class AnalysisForm(forms.Form):
    down_payment_pct = forms.IntegerField(
        label='Down Payment (%)',
        min_value=10, max_value=80, initial=20,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '20'})
    )
    loan_tenure_years = forms.IntegerField(
        label='Loan Tenure (Years)',
        min_value=5, max_value=30, initial=20,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '20'})
    )
    interest_rate = forms.DecimalField(
        label='Interest Rate (% p.a.)',
        min_value=5.0, max_value=20.0, initial=8.5,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '8.5', 'step': '0.1'})
    )
