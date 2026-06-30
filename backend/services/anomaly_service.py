import numpy as np
from sklearn.ensemble import IsolationForest


def detect_anomaly_ml(amount, category, historical_transactions):
    """
    Detect anomaly using Isolation Forest.
    historical_transactions = list of previous transaction amounts in same category
    """

    if len(historical_transactions) < 5:
        return False, None

    data = np.array(historical_transactions + [amount]).reshape(-1, 1)

    model = IsolationForest(
        contamination=0.15,
        random_state=42
    )

    predictions = model.fit_predict(data)

    latest_prediction = predictions[-1]

    if latest_prediction == -1:
        avg = sum(historical_transactions) / len(historical_transactions)

        return (
            True,
            f"ML anomaly detected: ₹{amount} is unusual compared to your normal {category} spending average of ₹{round(avg, 2)}."
        )

    return False, None