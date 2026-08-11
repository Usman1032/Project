from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.http import JsonResponse, request
import json

from .models import FinancialProfile, Property, InvestmentAnalysis
from .forms import RegisterForm, FinancialProfileForm, PropertyForm, AnalysisForm
from .ml_engine import predict_property_value
from .finance_engine import full_analysis


# ─── Auth Views ───────────────────────────────────────────────────────────────

def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'realestate/home.html')


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    form = RegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, f"Welcome, {user.first_name}! Please set up your financial profile.")
        return redirect('financial_profile')
    return render(request, 'realestate/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        login(request, user)
        messages.success(request, f"Welcome back, {user.first_name}!")
        return redirect('dashboard')
    return render(request, 'realestate/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('home')


# ─── Dashboard ────────────────────────────────────────────────────────────────

@login_required
def dashboard(request):
    all_analyses = InvestmentAnalysis.objects.filter(user=request.user).select_related('property')
    analyses = all_analyses[:10]
    properties = Property.objects.filter(user=request.user)
    has_profile = hasattr(request.user, 'financial_profile')

    # Stats for dashboard cards
    buy_count = all_analyses.filter(recommendation='BUY').count()
    avg_score = 0
    if all_analyses.exists():
        scores = [float(a.investment_score or 0) for a in all_analyses]
        avg_score = sum(scores) / len(scores)

    context = {
        'analyses': analyses,
        'properties': properties,
        'has_profile': has_profile,
        'buy_count': buy_count,
        'avg_score': round(avg_score, 1),
        'total_properties': properties.count(),
    }
    return render(request, 'realestate/dashboard.html', context)


# ─── Financial Profile ────────────────────────────────────────────────────────

@login_required
def financial_profile(request):
    profile = getattr(request.user, 'financial_profile', None)
    form = FinancialProfileForm(request.POST or None, instance=profile)
    if request.method == 'POST' and form.is_valid():
        fp = form.save(commit=False)
        fp.user = request.user
        fp.save()
        messages.success(request, "Financial profile saved successfully!")
        return redirect('dashboard')
    return render(request, 'realestate/financial_profile.html', {'form': form, 'profile': profile})


# ─── Property Views ───────────────────────────────────────────────────────────

@login_required
def add_property(request):
    if not hasattr(request.user, 'financial_profile'):
        messages.warning(request, "Please set up your financial profile first.")
        return redirect('financial_profile')
    form = PropertyForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        prop = form.save(commit=False)
        prop.user = request.user
        prop.save()
        messages.success(request, f"Property '{prop.title}' added. Now run the analysis!")
        return redirect('analyze_property', pk=prop.pk)
    return render(request, 'realestate/add_property.html', {'form': form})


@login_required
def property_list(request):
    properties = Property.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'realestate/property_list.html', {'properties': properties})


@login_required
def delete_property(request, pk):
    prop = get_object_or_404(Property, pk=pk, user=request.user)
    if request.method == 'POST':
        prop.delete()
        messages.success(request, "Property deleted.")
    return redirect('property_list')


# ─── Analysis Views ───────────────────────────────────────────────────────────

@login_required
def analyze_property(request, pk):
    prop = get_object_or_404(Property, pk=pk, user=request.user)
    profile = getattr(request.user, 'financial_profile', None)
    if not profile:
        messages.warning(request, "Please set up your financial profile first.")
        return redirect('financial_profile')

    form = AnalysisForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        down_pct = form.cleaned_data['down_payment_pct']
        tenure = form.cleaned_data['loan_tenure_years']
        rate = float(form.cleaned_data['interest_rate'])
        property_price = float(prop.price)
        down_payment = property_price * (down_pct / 100)

        # ML Prediction
        ml_preds = predict_property_value(
            location=prop.location,
            area_sqft=float(prop.area_sqft),
            bhk=prop.bhk,
            age_years=prop.age_years,
            floor_number=prop.floor_number,
            total_floors=prop.total_floors,
        )

        # Financial Analysis
        property_data = {
            'price': property_price,
            'down_payment': down_payment,
            'loan_tenure_years': tenure,
            'interest_rate': rate,
        }
        financial_data = {
            'monthly_salary': float(profile.monthly_salary),
            'monthly_expenses': float(profile.monthly_expenses),
            'total_savings': float(profile.total_savings),
            'risk_tolerance': profile.risk_tolerance,
        }
        result = full_analysis(property_data, financial_data, ml_preds)

        # Save to DB
        analysis = InvestmentAnalysis.objects.create(
            user=request.user,
            property=prop,
            predicted_price=ml_preds['predicted_price'],
            predicted_rental=ml_preds['predicted_rental'],
            down_payment=down_payment,
            loan_amount=result['loan_amount'],
            loan_tenure_years=tenure,
            interest_rate=rate,
            emi=result['emi_data']['emi'],
            total_interest=result['emi_data']['total_interest'],
            affordability_score=result['affordability']['score'],
            roi_percentage=result['roi']['net_roi_5yr'],
            investment_score=result['investment']['investment_score'],
            recommendation=result['investment']['recommendation'],
            projected_value_5yr=ml_preds['projected_5yr'],
        )

        return redirect('analysis_result', pk=analysis.pk)

    return render(request, 'realestate/analyze_property.html', {'property': prop, 'form': form, 'profile': profile})


@login_required
def analysis_result(request, pk):
    analysis = get_object_or_404(InvestmentAnalysis, pk=pk, user=request.user)
    prop = analysis.property
    profile = request.user.financial_profile

    # Rebuild results for display
    ml_preds = {
        'predicted_price': float(analysis.predicted_price),
        'predicted_rental': float(analysis.predicted_rental),
        'projected_5yr': float(analysis.projected_value_5yr),
    }
    property_data = {
        'price': float(prop.price),
        'down_payment': float(analysis.down_payment),
        'loan_tenure_years': analysis.loan_tenure_years,
        'interest_rate': float(analysis.interest_rate),
    }
    financial_data = {
        'monthly_salary': float(profile.monthly_salary),
        'monthly_expenses': float(profile.monthly_expenses),
        'total_savings': float(profile.total_savings),
        'risk_tolerance': profile.risk_tolerance,
    }
    result = full_analysis(property_data, financial_data, ml_preds)

    # EMI breakdown for chart (principal vs interest per year)
    emi = result['emi_data']['emi']
    annual_emi = emi * 12
    total_months = result['emi_data']['total_months']

    # Wealth projection data for chart
    appreciation = 0.08
    wealth_labels = []
    wealth_values = []
    rent_values = []
    for yr in range(0, 6):
        wealth_labels.append(f"Year {yr}")
        wealth_values.append(round(float(prop.price) * ((1 + appreciation) ** yr)))
        rent_values.append(round(float(analysis.predicted_rental) * 12 * yr))

    context = {
        'analysis': analysis,
        'property': prop,
        'result': result,
        'ml_preds': ml_preds,
        'wealth_labels': json.dumps(wealth_labels),
        'wealth_values': json.dumps(wealth_values),
        'rent_values': json.dumps(rent_values),
        'emi_principal': round(float(analysis.loan_amount)),
        'emi_interest': round(float(analysis.total_interest)),
    }
    return render(request, 'realestate/analysis_result.html', context)


@login_required
def analysis_history(request):
    analyses = InvestmentAnalysis.objects.filter(user=request.user).select_related('property')
    return render(request, 'realestate/analysis_history.html', {'analyses': analyses})
