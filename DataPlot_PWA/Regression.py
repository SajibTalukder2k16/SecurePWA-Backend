import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline

def perform_regression_with_plot(file_path, output_plot_path="regression_fit_plot.pdf"):
    data = pd.read_excel(file_path, sheet_name=0)
    df = data.iloc[2:].reset_index(drop=True)
    df.columns = data.iloc[1]
    df = df.apply(pd.to_numeric, errors='coerce')

    # Features and target
    X = df[['No of User', 'Attack Devices', 'Threshold']]
    y = df['Failed Percentage']

    # ----- Linear Regression -----
    linear_model = LinearRegression()
    linear_model.fit(X, y)
    y_pred_linear = linear_model.predict(X)
    linear_r2 = linear_model.score(X, y)

    # Equation string
    linear_eq = f"Linear: y = {linear_model.intercept_:.4f}"
    for feat, coef in zip(X.columns, linear_model.coef_):
        linear_eq += f" + ({coef:.4f} * {feat})"

    # ----- Polynomial Regression -----
    poly_model = make_pipeline(PolynomialFeatures(degree=2), LinearRegression())
    poly_model.fit(X, y)
    y_pred_poly = poly_model.predict(X)
    poly_r2 = poly_model.score(X, y)

    plt.figure(figsize=(10, 6))
    plt.plot(y, y, 'k--', label='Ideal Fit (y = ŷ)')
    plt.scatter(y, y_pred_linear, color='blue', label=f'Linear Fit (R² = {linear_r2:.3f})')
    plt.scatter(y, y_pred_poly, color='green', label=f'Poly Fit (R² = {poly_r2:.3f})')

    plt.xlabel("Actual Failed Percentage")
    plt.ylabel("Predicted Failed Percentage")
    plt.title("Actual vs Predicted Failed Percentage")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    plt.savefig(output_plot_path)
    plt.show()
    plt.close()
    print(f"Plot saved to {output_plot_path}")

    print(linear_eq)
    print(f"Linear R² = {linear_r2:.4f}")
    print(f"Polynomial R² = {poly_r2:.4f}")

perform_regression_with_plot("MaliciousScenario.xlsx", "regression_fit_plot.pdf")
