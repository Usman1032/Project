from django.db import models
from django.contrib.auth.models import User


class FinancialProfile(models.Model):
    RISK_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='financial_profile')
    monthly_salary = models.DecimalField(max_digits=12, decimal_places=2)
    monthly_expenses = models.DecimalField(max_digits=12, decimal_places=2)
    total_savings = models.DecimalField(max_digits=15, decimal_places=2)
    risk_tolerance = models.CharField(max_length=10, choices=RISK_CHOICES, default='medium')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Financial Profile"

    @property
    def monthly_disposable(self):
        return float(self.monthly_salary) - float(self.monthly_expenses)

    @property
    def safe_emi_limit(self):
        # Max 40% of salary towards EMI
        return float(self.monthly_salary) * 0.40


class Property(models.Model):
    PROPERTY_TYPE_CHOICES = [
        ('apartment', 'Apartment'),
        ('villa', 'Villa'),
        ('plot', 'Plot'),
        ('commercial', 'Commercial'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='properties')
    title = models.CharField(max_length=200)
    location = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=15, decimal_places=2)
    area_sqft = models.DecimalField(max_digits=10, decimal_places=2)
    bhk = models.IntegerField(choices=[(1,'1 BHK'),(2,'2 BHK'),(3,'3 BHK'),(4,'4 BHK'),(5,'5+ BHK')])
    property_type = models.CharField(max_length=20, choices=PROPERTY_TYPE_CHOICES, default='apartment')
    age_years = models.IntegerField(default=0, help_text="Age of property in years")
    floor_number = models.IntegerField(default=1)
    total_floors = models.IntegerField(default=5)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.location}"

    @property
    def price_per_sqft(self):
        if self.area_sqft > 0:
            return float(self.price) / float(self.area_sqft)
        return 0


class InvestmentAnalysis(models.Model):
    RECOMMENDATION_CHOICES = [
        ('BUY', 'Buy'),
        ('HOLD', 'Hold'),
        ('AVOID', 'Avoid'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='analyses')
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='analyses')

    # ML Predictions
    predicted_price = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    predicted_rental = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    # Financial Calculations
    down_payment = models.DecimalField(max_digits=15, decimal_places=2)
    loan_amount = models.DecimalField(max_digits=15, decimal_places=2)
    loan_tenure_years = models.IntegerField(default=20)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, default=8.5)
    emi = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    total_interest = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)

    # Scores
    affordability_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    roi_percentage = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    investment_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    recommendation = models.CharField(max_length=10, choices=RECOMMENDATION_CHOICES, null=True, blank=True)

    # Wealth projection (5 years)
    projected_value_5yr = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Analysis: {self.property.title} by {self.user.username}"

    class Meta:
        ordering = ['-created_at']
