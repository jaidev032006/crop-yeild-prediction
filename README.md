# 🌾 AgriSmart — Unified Precision Agriculture & Advisory Platform

An AI-driven precision agriculture system integrating **730+ Indian agricultural districts & soil telemetry**, machine learning crop recommendation (Random Forest 98.6% accuracy), real-time satellite weather tracking, and an agro-marketplace.

---

## ⚡ Quick Start: One-Command Startup

You can run the entire unified project with a single command from this root folder:

```bash
python app.py
```

> **What happens automatically when you run this command:**
> 1. ✅ **Environment Detection:** Verifies all Python dependencies and loads `.env`.
> 2. 🗄️ **Database Initialization:** Checks database tables and seeds demo farmer/admin accounts if empty without overwriting existing data.
> 3. 🌐 **Server Launch:** Starts the unified web server on `http://localhost:5000`.
> 4. 🚀 **Automatic Browser Open:** Automatically opens the crop advisory dashboard in your default browser once the server is ready.

---

## 🛑 How to Stop the Application

To shut down the server gracefully, go to your terminal where `python app.py` is running and press:

```
Ctrl + C
```

The process will release ports and perform a clean exit.

---

## 🔑 Demo Login Credentials

If prompted to log in:

| Role | Username | Password | Access / Capabilities |
|---|---|---|---|
| **Farmer (User)** | `farmer_ravi` | `password123` | Crop advisory, location intelligence, marketplace, PDF downloads |
| **Admin** | `admin` | `admin123` | User management, product catalog, platform analytics |

*(You can also click **Register** on the login page to create a new farmer profile).*

---

## 🧭 Key Platform Features

- **📍 730+ Indian Locations & District Selector (`/predict`):** Select any state and district across India to immediately retrieve verified soil N-P-K & pH distributions, local traditional crop history, and live satellite weather.
- **🧪 Custom Soil Chemistry Lab:** Fine-tune exact laboratory Nitrogen, Phosphorus, Potassium, and pH sliders.
- **🌱 Dynamic Fertilizer Advisory:** Real-time calculation of Urea, Single Superphosphate (SSP), and Muriate of Potash (MOP) required for optimal yield.
- **📄 Instant PDF Reports:** One-click generation of branded agro-technical reports for farmers and field workers.
- **🛒 Direct Agro-Marketplace (`/marketplace/`):** Seed varieties, bio-fertilizers, and organic pest control products.

---

## ⚙️ Environment Configuration (`.env`)

A default `.env` file is automatically maintained at the project root. You can customize settings:

```ini
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=agrismart_secure_random_key_production_2026

# Network configuration
SERVER_HOST=0.0.0.0
SERVER_PORT=5000

# Database URI (SQLite default)
DATABASE_URL=sqlite:///agrismart.db

# Open browser automatically on launch
AUTO_OPEN_BROWSER=true
```

---

## 📦 Manual Installation (Optional)

If setting up on a new machine without pre-existing dependencies:

```bash
# 1. Create a virtual environment
python -m venv .venv

# 2. Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On macOS / Linux:
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Launch project
python app.py
```
