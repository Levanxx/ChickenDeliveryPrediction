import pandas as pd

df = pd.read_csv("generator/ventas_diarias_2026.csv")

print(df.head())
print("\nColumnas:", df.columns)
print("\nValores nulos:\n", df.isnull().sum())