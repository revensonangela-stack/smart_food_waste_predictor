import numpy as np
from sklearn.linear_model import LinearRegression
from models import IngredientUsage

def predict_required_quantity(ingredient_name):
    records = IngredientUsage.query.filter_by(
        ingredient_name=ingredient_name
    ).all()

    # Not enough data for ML
    if len(records) < 2:
        return None

    used = np.array([r.used_quantity for r in records]).reshape(-1, 1)
    wasted = np.array([r.wasted_quantity for r in records])

    model = LinearRegression()
    model.fit(used, wasted)

    avg_used = np.mean(used)
    predicted_waste = model.predict([[avg_used]])[0]

    recommended_quantity = max(avg_used - predicted_waste, 0)

    return round(recommended_quantity, 2)
