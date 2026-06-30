from sklearn.linear_model import LinearRegression
import numpy as np


def predict_next_spend(amounts):
    """
    amounts = monthly spending list
    example: [4200, 4600, 5100, 5400]
    """

    if len(amounts) < 2:
        return None

    X = np.array(range(len(amounts))).reshape(-1, 1)
    y = np.array(amounts)

    model = LinearRegression()
    model.fit(X, y)

    next_month = np.array([[len(amounts)]])
    prediction = model.predict(next_month)[0]

    return round(float(prediction), 2)