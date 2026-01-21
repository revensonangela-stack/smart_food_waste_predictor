# Smart Food Waste Predictor

## Overview

Smart Food Waste Predictor is a web-based application designed to help kitchens, restaurants, and food operations **track ingredient usage, measure waste, and gain actionable insights** to reduce food wastage.

This project represents **Phase 1** of the system, focusing on accurate data tracking, visualization, and rule-based smart recommendations.

---

## Key Features

* **Ingredient Management**

  * Add, edit, and delete ingredients with categories

* **Daily Usage & Waste Tracking**

  * Record used and wasted quantities per ingredient
  * Automatic unit normalization for accurate calculations

* **Interactive Dashboard**

  * Total used vs wasted KPIs
  * Daily usage vs waste trends
  * Waste percentage per ingredient

* **Smart Recommendations (Rule-Based)**

  * Weekly insights based on usage and waste trends
  * Practical suggestions to reduce food waste

* **User Roles & Authentication**

  * Admin and Staff roles
  * Secure login system

---

## Tech Stack

* **Backend:** Python, Flask
* **Frontend:** HTML, CSS, Bootstrap, JavaScript
* **Database:** SQLite (via SQLAlchemy ORM)
* **Charts:** Chart.js
* **Authentication:** Flask-Login

---

## Project Structure

```
smart_food_waste_predictor/
│
├── app.py
├── models.py
├── requirements.txt
├── instance/
│   └── database.db
├── static/
│   ├── css/
│   └── js/
│       └── charts.js
├── templates/
│   ├── dashboard.html
│   ├── ingredients.html
│   ├── admin.html
│   └── ...
└── README.md
```

---

## Setup Instructions

1. **Clone the repository**

   ```bash
   git clone https://github.com/YOUR_USERNAME/smart-food-waste-predictor.git
   cd smart-food-waste-predictor
   ```

2. **Create a virtual environment**

   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**

   ```bash
   python app.py
   ```

5. Open your browser and visit:

   ```
   http://127.0.0.1:5000/login
   ```

---

## Phase 1 Scope

* Data entry and management
* Dashboard analytics and charts
* Rule-based smart recommendations
* No machine learning models (planned for Phase 2)

---

## Future Enhancements (Phase 2)

* Machine learning–based waste prediction
* Demand forecasting
* Supplier optimization insights
* Exportable reports
* Cloud database integration

---

## Demo

A short demo video is included in the LinkedIn post showcasing:

* Ingredient management
* Waste tracking
* Dashboard analytics
* Smart recommendations

---

## Author

Developed by **Angela Raveendraraj**

---

## License

This project is for educational and portfolio purposes.
