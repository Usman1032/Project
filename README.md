# 🏠 RealEstateAI — Setup & Run Guide

## Prerequisites
- Python 3.10+ installed
- pip installed

---

## ⚡ Quick Setup (5 Steps)

### Step 1 — Create a virtual environment
```bash
cd realestate_project
python -m venv venv

# Activate it:
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate
```

### Step 2 — Install dependencies
```bash
pip install Django scikit-learn pandas numpy joblib
```
> Note: `mysqlclient` is only needed if you switch to MySQL.
> By default the project uses **SQLite** (zero config needed).

### Step 3 — Run database migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 4 — Create an admin user (optional)
```bash
python manage.py createsuperuser
```

### Step 5 — Start the server
```bash
python manage.py runserver
```

Open your browser at: **http://127.0.0.1:8000**

---

## 🗄️ Optional: Switch to MySQL

1. Install MySQL and create a database:
```sql
CREATE DATABASE realestate_db CHARACTER SET utf8mb4;
```

2. Install the MySQL client:
```bash
pip install mysqlclient
```

3. In `realestate_project/settings.py`, comment out the SQLite block
   and uncomment the MySQL block, filling in your credentials.

4. Re-run migrations:
```bash
python manage.py migrate
```

---

## 📁 Project Structure

```
realestate_project/
├── manage.py
├── requirements.txt
├── realestate_project/
│   ├── settings.py        ← Django config
│   └── urls.py            ← Root URL routing
└── realestate/
    ├── models.py          ← DB models (FinancialProfile, Property, Analysis)
    ├── views.py           ← All page logic
    ├── forms.py           ← Input forms
    ├── urls.py            ← App URL routing
    ├── ml_engine.py       ← ML prediction (price + rental)
    ├── finance_engine.py  ← EMI, ROI, affordability, investment score
    ├── ml_models/         ← Saved ML model files (auto-created on first run)
    └── templates/realestate/
        ├── base.html
        ├── home.html
        ├── dashboard.html
        ├── financial_profile.html
        ├── add_property.html
        ├── property_list.html
        ├── analyze_property.html
        ├── analysis_result.html
        └── analysis_history.html
```

---

## 🧭 User Flow

1. **Register** → `/register/`
2. **Set Financial Profile** → enter salary, expenses, savings, risk level
3. **Add a Property** → enter location, price, area, BHK
4. **Run Analysis** → configure loan % and tenure, click Analyze
5. **View Report** → ML prediction + EMI + ROI + BUY/HOLD/AVOID verdict + charts

---

## 🔬 How the ML Works

The ML engine (`ml_engine.py`) trains a **Random Forest** model on synthetic Indian
real estate data (2000 samples) when the app runs for the first time.
The model is then saved to `ml_models/` and reused on subsequent runs.

**Features used:**
- Area (sqft)
- BHK count
- Property age
- Floor ratio
- Location multiplier (city-based)

To use a real dataset (recommended for production), replace the
`_generate_training_data()` function in `ml_engine.py` with code that
loads a CSV from Kaggle (e.g. the Bangalore Housing dataset).

---

## 🔐 Admin Panel

Visit **http://127.0.0.1:8000/admin/** and log in with your superuser credentials
to manage users, properties, and analyses directly.
