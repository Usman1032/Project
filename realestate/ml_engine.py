"""
ML Prediction Engine
Trains a Random Forest model on synthetic Indian real estate data.
In production, replace with a real dataset (Kaggle housing data, etc.)
"""
import numpy as np
import os
import joblib

# Location multipliers (simulating Indian city price differences)
LOCATION_MULTIPLIERS = {
    'mumbai': 2.5, 'delhi': 2.2, 'bangalore': 2.0, 'hyderabad': 1.7,
    'pune': 1.6, 'chennai': 1.5, 'kolkata': 1.3, 'ahmedabad': 1.2,
    'mysuru': 1.1, 'mysore': 1.1, 'jaipur': 1.1, 'lucknow': 1.0,
    'default': 1.0
}

# Annual appreciation rates by location
APPRECIATION_RATES = {
    'mumbai': 0.08, 'delhi': 0.07, 'bangalore': 0.09, 'hyderabad': 0.10,
    'pune': 0.08, 'chennai': 0.07, 'mysuru': 0.08, 'mysore': 0.08,
    'default': 0.07
}

MODEL_PATH = os.path.join(os.path.dirname(__file__), 'ml_models', 'price_model.pkl')
RENTAL_MODEL_PATH = os.path.join(os.path.dirname(__file__), 'ml_models', 'rental_model.pkl')


def _get_location_multiplier(location: str) -> float:
    loc = location.lower().strip()
    for key in LOCATION_MULTIPLIERS:
        if key in loc:
            return LOCATION_MULTIPLIERS[key]
    return LOCATION_MULTIPLIERS['default']


def _generate_training_data(n=2000):
    """Generate realistic synthetic Indian real estate training data."""
    np.random.seed(42)
    areas = np.random.uniform(400, 5000, n)
    bhks = np.random.randint(1, 6, n)
    age = np.random.randint(0, 30, n)
    floor_ratio = np.random.uniform(0.1, 1.0, n)
    loc_mult = np.random.choice(list(LOCATION_MULTIPLIERS.values())[:-1], n)

    # Base price per sqft: 3000-8000 INR
    base_psf = 3000 + (loc_mult - 1.0) * 3000 + np.random.normal(0, 300, n)
    base_psf = np.clip(base_psf, 2000, 15000)

    # Price formula with noise
    prices = (areas * base_psf
              + bhks * 150000
              - age * 50000
              + floor_ratio * 200000
              + np.random.normal(0, 200000, n))
    prices = np.clip(prices, 500000, 50000000)

    # Rental: roughly 0.25-0.35% of property value per month
    rentals = prices * np.random.uniform(0.0025, 0.0035, n)
    rentals = np.clip(rentals, 5000, 150000)

    X = np.column_stack([areas, bhks, age, floor_ratio, loc_mult])
    return X, prices, rentals


def train_and_save_models():
    """Train and save ML models if not already saved."""
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    if os.path.exists(MODEL_PATH) and os.path.exists(RENTAL_MODEL_PATH):
        return

    from sklearn.ensemble import RandomForestRegressor
    from sklearn.preprocessing import StandardScaler
    from sklearn.pipeline import Pipeline

    X, y_price, y_rental = _generate_training_data()

    price_model = Pipeline([
        ('scaler', StandardScaler()),
        ('rf', RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1))
    ])
    price_model.fit(X, y_price)
    joblib.dump(price_model, MODEL_PATH)

    rental_model = Pipeline([
        ('scaler', StandardScaler()),
        ('rf', RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1))
    ])
    rental_model.fit(X, y_rental)
    joblib.dump(rental_model, RENTAL_MODEL_PATH)


def predict_property_value(location: str, area_sqft: float, bhk: int,
                            age_years: int = 0, floor_number: int = 1,
                            total_floors: int = 5) -> dict:
    """Predict property value and rental income."""
    train_and_save_models()

    price_model = joblib.load(MODEL_PATH)
    rental_model = joblib.load(RENTAL_MODEL_PATH)

    loc_mult = _get_location_multiplier(location)
    floor_ratio = floor_number / max(total_floors, 1)

    features = np.array([[area_sqft, bhk, age_years, floor_ratio, loc_mult]])

    predicted_price = float(price_model.predict(features)[0])
    predicted_rental = float(rental_model.predict(features)[0])

    # Appreciation rate
    loc_key = location.lower().strip()
    app_rate = next((v for k, v in APPRECIATION_RATES.items() if k in loc_key),
                    APPRECIATION_RATES['default'])

    projected_5yr = predicted_price * ((1 + app_rate) ** 5)

    return {
        'predicted_price': round(predicted_price, 2),
        'predicted_rental': round(predicted_rental, 2),
        'projected_5yr': round(projected_5yr, 2),
        'appreciation_rate': app_rate * 100,
        'location_multiplier': loc_mult,
    }
