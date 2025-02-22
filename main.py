import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import sqlite3


# Wczytanie danych
file_path = "data/sales_data.csv"  # Ścieżka do pliku
df = pd.read_csv(file_path, encoding="ISO-8859-1")  # Możesz też użyć 'latin1'

# Wyświetlenie pierwszych 5 wierszy
print(df.head())

# Wyświetlenie podstawowych informacji o danych
print("\n🟢 Podstawowe informacje o zbiorze:")
print(df.info())

# Sprawdzenie liczby brakujących wartości w każdej kolumnie
print("\n🟡 Brakujące wartości w zbiorze:")
print(df.isnull().sum())

# Wyświetlenie statystyk numerycznych
print("\n🔵 Podstawowe statystyki:")
print(df.describe())

# Konwersja kolumny 'Order Date' na format daty
df['Order Date'] = pd.to_datetime(df['Order Date'], format="%d-%m-%y")

# Konwersja 'Postal Code' na string (bo to kod pocztowy, a nie liczba)
df['Postal Code'] = df['Postal Code'].astype(str)

# Sprawdzenie i usunięcie duplikatów
duplicates = df.duplicated().sum()
print(f"\n🔴 Liczba duplikatów: {duplicates}")

if duplicates > 0:
    df = df.drop_duplicates()
    print("✅ Duplikaty usunięte!")

# Sprawdzenie efektu zmian
print("\n🟢 Po czyszczeniu danych:")
print(df.info())

# Grupowanie sprzedaży według miesiąca i roku
df['Year-Month'] = df['Order Date'].dt.to_period('M')  # Tworzymy kolumnę z rokiem i miesiącem
sales_trend = df.groupby('Year-Month')['Sales'].sum()

# Wykres sprzedaży w czasie
plt.figure(figsize=(12, 6))
sales_trend.plot(marker='o', linestyle='-')
plt.xlabel("Data")
plt.ylabel("Łączna sprzedaż")
plt.title("Trend sprzedaży w czasie")
plt.xticks(rotation=45)
plt.grid()
plt.show()

# Grupowanie sprzedaży według produktu
top_products = df.groupby('Product Name')['Sales'].sum().sort_values(ascending=False).head(10)

# Wykres TOP 10 produktów
plt.figure(figsize=(12, 6))
top_products.plot(kind='bar', color='skyblue')
plt.xlabel("Produkt")
plt.ylabel("Łączna sprzedaż")
plt.title("TOP 10 najlepiej sprzedających się produktów")
plt.xticks(rotation=45, ha="right")
plt.grid(axis='y')
plt.show()

# Grupowanie sprzedaży według klienta
top_customers = df.groupby('Customer ID')['Sales'].sum().sort_values(ascending=False).head(10)

# Wykres TOP 10 klientów
plt.figure(figsize=(12, 6))
top_customers.plot(kind='bar', color='orange')
plt.xlabel("ID Klienta")
plt.ylabel("Łączna sprzedaż")
plt.title("TOP 10 klientów generujących największą sprzedaż")
plt.xticks(rotation=45, ha="right")
plt.grid(axis='y')
plt.show()


# Grupowanie danych według rabatu i obliczenie średniego zysku
discount_profit = df.groupby('Discount')['Profit'].mean()

# Wykres: wpływ rabatów na zysk
plt.figure(figsize=(12, 6))
sns.barplot(x=discount_profit.index, y=discount_profit.values, hue=discount_profit.index, palette="coolwarm", legend=False)
plt.xlabel("Rabat")
plt.ylabel("Średni zysk")
plt.title("Wpływ rabatu na średni zysk")
plt.grid(axis='y')
plt.show()

# Sumujemy sprzedaż dla każdego klienta
customer_sales = df.groupby('Customer ID')['Sales'].sum().reset_index()

# Definiujemy przedziały dla segmentów klientów
bins = [0, customer_sales['Sales'].quantile(0.25), customer_sales['Sales'].quantile(0.5), customer_sales['Sales'].quantile(0.75), customer_sales['Sales'].max()]
labels = ['Niski', 'Średni', 'Wysoki', 'VIP']

# Tworzymy nową kolumnę 'Customer Segment' z przypisanymi przedziałami sprzedaży
customer_sales['Customer Segment'] = pd.cut(customer_sales['Sales'], bins=bins, labels=labels, include_lowest=True)

# Dołączamy segmenty do głównej tabeli df
df = df.merge(customer_sales[['Customer ID', 'Customer Segment']], on='Customer ID', how='left')

# Sprawdzenie, czy podział klientów działa poprawnie
print("\n🟢 Podgląd segmentacji klientów:")
print(df[['Customer ID', 'Customer Segment']].drop_duplicates().head(20))  # Wyświetlenie kilku klientów i ich segmentów

# Sprawdzenie, czy są puste wartości
print("\n🔴 Liczba brakujących wartości w segmentach:", df['Customer Segment'].isnull().sum())

# Wykres: liczba klientów w każdej grupie
plt.figure(figsize=(8, 5))
df['Customer Segment'].value_counts().plot(kind='bar', color=['red', 'orange', 'blue', 'green'])
plt.xlabel("Segment klienta")
plt.ylabel("Liczba klientów")
plt.title("Podział klientów na segmenty")
plt.xticks(rotation=0)
plt.grid(axis='y')
plt.show()


# Połączenie z bazą SQLite
conn = sqlite3.connect("data/ecommerce_sales.db")
cursor = conn.cursor()

# Zapisujemy dane Pandas do tabeli "sales_data"
# Konwersja kolumny 'Year-Month' na string, aby SQLite mógł ją obsłużyć
df['Year-Month'] = df['Year-Month'].astype(str)

# Zapis danych do bazy SQLite
df.to_sql("sales_data", conn, if_exists="replace", index=False)


print("\n✅ Dane zostały zapisane w bazie SQLite!")

conn.close()

conn = sqlite3.connect("data/ecommerce_sales.db")
cursor = conn.cursor()

#  TOP 10 najlepiej sprzedających się produktów
query = """
SELECT "Product Name", SUM(Sales) AS Total_Sales
FROM sales_data
GROUP BY "Product Name"
ORDER BY Total_Sales DESC
LIMIT 10;
"""
top_products_sql = pd.read_sql(query, conn)

# Zamknięcie połączenia
conn.close()

# Wyświetlenie wyników SQL
print("\n🏆 TOP 10 najlepiej sprzedających się produktów (SQL):")
print(top_products_sql)

