"""
Financial Analysis Engine
Handles EMI, ROI, affordability, and investment scoring.
"""


def calculate_emi(principal: float, annual_rate: float, tenure_years: int) -> dict:
    """Calculate EMI using standard formula."""
    if principal <= 0 or tenure_years <= 0:
        return {'emi': 0, 'total_payment': 0, 'total_interest': 0}

    monthly_rate = annual_rate / (12 * 100)
    n = tenure_years * 12

    if monthly_rate == 0:
        emi = principal / n
    else:
        emi = principal * monthly_rate * ((1 + monthly_rate) ** n) / (((1 + monthly_rate) ** n) - 1)

    total_payment = emi * n
    total_interest = total_payment - principal

    return {
        'emi': round(emi, 2),
        'total_payment': round(total_payment, 2),
        'total_interest': round(total_interest, 2),
        'monthly_rate': round(monthly_rate * 100, 4),
        'total_months': n,
    }


def calculate_affordability(emi: float, monthly_salary: float,
                              monthly_expenses: float, total_savings: float,
                              down_payment: float) -> dict:
    """
    Affordability Score (0-100):
    - EMI should be < 40% of salary
    - Down payment should be coverable from savings
    - Disposable income after EMI should be positive
    """
    score = 100.0
    issues = []

    # EMI to income ratio (ideal < 30%, acceptable < 40%)
    emi_ratio = (emi / monthly_salary * 100) if monthly_salary > 0 else 100
    if emi_ratio > 50:
        score -= 40
        issues.append(f"EMI ({emi_ratio:.1f}% of salary) is very high — above 50%")
    elif emi_ratio > 40:
        score -= 25
        issues.append(f"EMI ({emi_ratio:.1f}% of salary) exceeds recommended 40%")
    elif emi_ratio > 30:
        score -= 10
        issues.append(f"EMI ({emi_ratio:.1f}% of salary) is moderate — ideal is under 30%")

    # Savings vs down payment
    if total_savings < down_payment:
        score -= 30
        issues.append("Savings are insufficient to cover the down payment")
    elif total_savings < down_payment * 1.2:
        score -= 10
        issues.append("Savings barely cover the down payment — emergency fund at risk")

    # Monthly surplus after EMI and expenses
    monthly_surplus = monthly_salary - monthly_expenses - emi
    if monthly_surplus < 0:
        score -= 20
        issues.append("Monthly cash flow is negative after EMI and expenses")
    elif monthly_surplus < monthly_salary * 0.1:
        score -= 10
        issues.append("Very little monthly surplus remaining after all payments")

    score = max(0, min(100, score))

    if score >= 75:
        level = "Excellent"
        color = "success"
    elif score >= 55:
        level = "Good"
        color = "info"
    elif score >= 35:
        level = "Moderate"
        color = "warning"
    else:
        level = "Poor"
        color = "danger"

    return {
        'score': round(score, 1),
        'level': level,
        'color': color,
        'emi_ratio': round(emi_ratio, 1),
        'monthly_surplus': round(monthly_surplus, 2),
        'issues': issues,
    }


def calculate_roi(property_price: float, predicted_rental: float,
                   projected_5yr_value: float, down_payment: float,
                   total_interest: float) -> dict:
    """
    ROI Calculation:
    - Rental Yield = (Annual Rent / Property Price) * 100
    - Capital Gain = (Projected Value - Purchase Price) / Purchase Price * 100
    - Total ROI over 5 years
    """
    annual_rent = predicted_rental * 12
    rental_yield = (annual_rent / property_price * 100) if property_price > 0 else 0

    capital_gain_5yr = projected_5yr_value - property_price
    capital_gain_pct = (capital_gain_5yr / property_price * 100) if property_price > 0 else 0

    total_cost = property_price + total_interest
    total_returns = (annual_rent * 5) + capital_gain_5yr
    net_roi_5yr = ((total_returns - total_cost + property_price) / total_cost * 100) if total_cost > 0 else 0

    return {
        'rental_yield': round(rental_yield, 2),
        'annual_rent': round(annual_rent, 2),
        'capital_gain_5yr': round(capital_gain_5yr, 2),
        'capital_gain_pct': round(capital_gain_pct, 2),
        'net_roi_5yr': round(net_roi_5yr, 2),
        'total_rental_5yr': round(annual_rent * 5, 2),
    }


def calculate_investment_score(affordability_score: float, roi_data: dict,
                                 predicted_price: float, actual_price: float,
                                 risk_tolerance: str) -> dict:
    """
    Investment Score (0-100) combining:
    - Affordability (30%)
    - Rental Yield (25%)
    - Capital Appreciation (25%)
    - Price vs Predicted Value (20%)
    """
    score = 0.0

    # 1. Affordability (30%)
    score += (affordability_score / 100) * 30

    # 2. Rental Yield (25%) — ideal > 3%, great > 4%
    rental_yield = roi_data['rental_yield']
    if rental_yield >= 4:
        score += 25
    elif rental_yield >= 3:
        score += 18
    elif rental_yield >= 2:
        score += 10
    else:
        score += 5

    # 3. Capital Appreciation (25%) — based on 5yr gain %
    cap_gain = roi_data['capital_gain_pct']
    if cap_gain >= 40:
        score += 25
    elif cap_gain >= 25:
        score += 18
    elif cap_gain >= 15:
        score += 12
    else:
        score += 5

    # 4. Price vs Predicted (20%) — is property fairly priced?
    if predicted_price > 0:
        price_ratio = actual_price / predicted_price
        if price_ratio <= 0.95:
            score += 20  # Underpriced — great deal
        elif price_ratio <= 1.05:
            score += 15  # Fairly priced
        elif price_ratio <= 1.15:
            score += 8   # Slightly overpriced
        else:
            score += 2   # Overpriced

    # Risk tolerance adjustment
    if risk_tolerance == 'low' and score < 60:
        score *= 0.9
    elif risk_tolerance == 'high' and score >= 50:
        score = min(100, score * 1.05)

    score = round(min(100, max(0, score)), 1)

    if score >= 70:
        recommendation = 'BUY'
        rec_color = 'success'
        rec_icon = '✅'
        rec_text = 'This property shows strong investment potential.'
    elif score >= 45:
        recommendation = 'HOLD'
        rec_color = 'warning'
        rec_icon = '⏸️'
        rec_text = 'Consider waiting for a better price or stronger rental yield.'
    else:
        recommendation = 'AVOID'
        rec_color = 'danger'
        rec_icon = '❌'
        rec_text = 'This investment does not align with your financial profile.'

    return {
        'investment_score': score,
        'recommendation': recommendation,
        'rec_color': rec_color,
        'rec_icon': rec_icon,
        'rec_text': rec_text,
    }


def full_analysis(property_data: dict, financial_data: dict, ml_predictions: dict) -> dict:
    """Run the complete financial analysis pipeline."""
    property_price = float(property_data['price'])
    down_payment = float(property_data.get('down_payment', property_price * 0.20))
    loan_amount = property_price - down_payment
    tenure = int(property_data.get('loan_tenure_years', 20))
    interest_rate = float(property_data.get('interest_rate', 8.5))

    monthly_salary = float(financial_data['monthly_salary'])
    monthly_expenses = float(financial_data['monthly_expenses'])
    total_savings = float(financial_data['total_savings'])
    risk_tolerance = financial_data.get('risk_tolerance', 'medium')

    predicted_price = ml_predictions['predicted_price']
    predicted_rental = ml_predictions['predicted_rental']
    projected_5yr = ml_predictions['projected_5yr']

    emi_data = calculate_emi(loan_amount, interest_rate, tenure)
    affordability = calculate_affordability(
        emi_data['emi'], monthly_salary, monthly_expenses, total_savings, down_payment
    )
    roi = calculate_roi(property_price, predicted_rental, projected_5yr,
                        down_payment, emi_data['total_interest'])
    investment = calculate_investment_score(
        affordability['score'], roi, predicted_price, property_price, risk_tolerance
    )

    return {
        'emi_data': emi_data,
        'affordability': affordability,
        'roi': roi,
        'investment': investment,
        'down_payment': down_payment,
        'loan_amount': loan_amount,
        'price_vs_predicted': round((property_price / predicted_price * 100) - 100, 1) if predicted_price > 0 else 0,
    }
