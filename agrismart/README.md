# AgriSmart — Next-Gen AI Precision Agriculture & Marketplace Platform

AgriSmart is a full-stack Flask web platform for AI crop prediction, dynamic fertilizer advisory with SVG growth morphing simulation, seed/fertilizer marketplace with slide-out cart, live Open-Meteo meteorological telemetry, data analytics, and dark control-room administration.

---

## 🌟 Architecture & Completed Phases

### ✅ Phase 1: Foundation & Authentication
- Modular Flask application factory pattern (`app/__init__.py`)
- Full relational schema (`User`, `Admin`, `Prediction`, `Order`, `OrderItem`, `Product`, `Feedback`)
- Split-screen authentication with floating labels and inline validation
- Landing page with leaf particles, animated stat counters, and testimonials

### ✅ Phase 2: Farmer Intelligence Dashboard
- Desktop glassmorphic sidebar and mobile responsive bottom navigation
- Time-of-day greeting with live clock and notifications popover
- Live Open-Meteo weather station (real-time temperature, humidity, rainfall, and wind speed)
- Overview KPI summary tiles and recent prediction showcase

### ✅ Phase 3: AI Crop Prediction & Signature Fertilizer Visualizer
- Multi-parameter range sliders for Nitrogen (N), Phosphorus (P), Potassium (K), Temperature, Humidity, Soil pH, and Rainfall with live value badges
- Quick preset chips for 10 crops (Rice, Maize, Chickpea, Cotton, Coffee, Mango, Banana, Grapes, Watermelon, Coconut) with smooth slider animation
- Open-Meteo weather autofill integration directly into prediction sliders
- Sprouting seedling loader during inference
- Flip result card with model confidence and circular progress ring for yield efficiency
- **Signature Fertilizer Animation**:
  - Falling N-P-K fertilizer granule shower
  - 3-Stage morphing SVG potted plant (seedling -> vegetative -> vibrant foliage)
  - Staggered line-by-line typewriter reveal of tailored fertilizer adjustments
- Branded PDF Report generation via ReportLab with letterhead, metrics, and advisory

### ✅ Phase 4: Agro Marketplace & Order Stepper
- 3D tilting product cards with category filtering, search, and stock badges
- Micro-animated fly-to-cart particle trajectory
- Slide-out Cart Drawer with real-time total and quantity adjustments
- Mock checkout modal with card, UPI, and COD modes + confetti burst celebration
- Multi-step logistics timeline (Pending → Confirmed → Shipped → Delivered)

### ✅ Phase 5: Feedback, Profile, and Analytics
- Interactive 5-star animated feedback rating with community testimonials wall
- Inline editable farmer profile with prediction history and order receipts
- Interactive Chart.js analytics dashboard (Feature Importance, Model Accuracy benchmarks, Soil NPK distributions)

### ✅ Phase 6: Admin Control Room
- Dark, high-tech control-room design language (`/admin/login`)
- 7-Day operational telemetry line chart
- Live AJAX order status dropdowns (no page reload)
- Farmer directory with account enable/disable and deletion
- Full AI inference log with instant CSV export (`/admin/api/export-predictions`)
- Forced master password reset modal for initial setup

---

## 🔑 Default Credentials

| Portal | URL | Username | Password | Notes |
| :--- | :--- | :--- | :--- | :--- |
| **Farmer Dashboard** | `http://127.0.0.1:5000/auth/login` | `farmer_ravi` | `password123` | Pre-loaded with demo history |
| **Control Room** | `http://127.0.0.1:5000/admin/login` | `admin` | `admin123` | Master administrator |

---

## 🚀 Quick Start Guide

### 1. Environment Setup
```bash
# Navigate to project directory
cd agrismart

# Install dependencies using Python or uv
uv venv --python 3.11 .venv
.venv\Scripts\activate
uv pip install -r requirements.txt
```

### 2. Database Seeding
```bash
python seed.py
```

### 3. Run Application
```bash
python run.py
```
Open **`http://127.0.0.1:5000`** in your browser.

### 4. Run Automated Test Suite
```bash
python -m unittest tests/test_app.py
```

---

## 🎨 Design System & Color Tokens

| Token | Light Mode | Dark Mode | Usage |
| :--- | :--- | :--- | :--- |
| `--color-forest-green` | `#0f5132` | `#10b981` | Brand Primary / Badges |
| `--color-emerald` | `#10b981` | `#34d399` | Interactive Accents / Glow |
| `--color-amber` | `#f59e0b` | `#fbbf24` | CTAs, Warnings, Ratings |
| `--bg-primary` | `#faf8f3` (Warm Cream) | `#090d16` (Near-Black) | Base Background |
| `--card-bg` | `rgba(255,255,255,0.85)` | `rgba(30,41,59,0.75)` | Glassmorphic Cards |

---

## 📂 Project Structure

```
agrismart/
├── app/
│   ├── models.py                  # SQLAlchemy models (User, Admin, Prediction, Order, Product, Feedback)
│   ├── routes/
│   │   ├── main.py                # Landing page & navigation
│   │   ├── auth.py                # Split-screen login & registration
│   │   ├── dashboard.py           # Dashboard overview & weather API
│   │   ├── predict.py             # Prediction endpoint & PDF downloader
│   │   ├── marketplace.py         # Catalog, cart, and checkout API
│   │   ├── feedback.py            # Star rating & community reviews
│   │   ├── profile.py             # Profile settings & history tabs
│   │   ├── analytics.py           # Chart.js dataset analytics
│   │   └── admin.py               # Dark control-room administration & CSV export
│   ├── services/
│   │   ├── ml_service.py          # Bridge to RandomForest model.py & dataset
│   │   └── pdf_service.py         # ReportLab PDF report generation
│   ├── static/
│   │   ├── css/ (style.css, navbar.css, predict.css, marketplace.css, admin.css)
│   │   └── js/  (app.js, predict.js, marketplace.js, theme.js)
│   └── templates/                 # Jinja2 HTML templates for all views
├── tests/
│   └── test_app.py                # 6 automated unit & integration test suites
├── config.py                      # Development, Testing, Production configs
├── requirements.txt               # Dependencies list
├── seed.py                        # Database seeder
└── run.py                         # Application runner
```
