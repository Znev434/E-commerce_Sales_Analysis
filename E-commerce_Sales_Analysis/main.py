import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import sqlite3


# Wczytanie danych z poprawnym kodowaniem
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

# 1️⃣ Konwersja kolumny 'Order Date' na format daty
df['Order Date'] = pd.to_datetime(df['Order Date'], format="%d-%m-%y")

# 2️⃣ Konwersja 'Postal Code' na string (bo to kod pocztowy, a nie liczba)
df['Postal Code'] = df['Postal Code'].astype(str)

# 3️⃣ Sprawdzenie i usunięcie duplikatów
duplicates = df.duplicated().sum()
print(f"\n🔴 Liczba duplikatów: {duplicates}")

if duplicates > 0:
    df = df.drop_duplicates()
    print("✅ Duplikaty usunięte!")

# 4️⃣ Sprawdzenie efektu zmian
print("\n🟢 Po czyszczeniu danych:")
print(df.info())

# 1️⃣ Grupowanie sprzedaży według miesiąca i roku
df['Year-Month'] = df['Order Date'].dt.to_period('M')  # Tworzymy kolumnę z rokiem i miesiącem
sales_trend = df.groupby('Year-Month')['Sales'].sum()

# 2️⃣ Wykres sprzedaży w czasie
plt.figure(figsize=(12, 6))
sales_trend.plot(marker='o', linestyle='-')
plt.xlabel("Data")
plt.ylabel("Łączna sprzedaż")
plt.title("Trend sprzedaży w czasie")
plt.xticks(rotation=45)
plt.grid()
plt.show()

# 1️⃣ Grupowanie sprzedaży według produktu
top_products = df.groupby('Product Name')['Sales'].sum().sort_values(ascending=False).head(10)

# 2️⃣ Wykres TOP 10 produktów
plt.figure(figsize=(12, 6))
top_products.plot(kind='bar', color='skyblue')
plt.xlabel("Produkt")
plt.ylabel("Łączna sprzedaż")
plt.title("TOP 10 najlepiej sprzedających się produktów")
plt.xticks(rotation=45, ha="right")
plt.grid(axis='y')
plt.show()

# 1️⃣ Grupowanie sprzedaży według klienta
top_customers = df.groupby('Customer ID')['Sales'].sum().sort_values(ascending=False).head(10)

# 2️⃣ Wykres TOP 10 klientów
plt.figure(figsize=(12, 6))
top_customers.plot(kind='bar', color='orange')
plt.xlabel("ID Klienta")
plt.ylabel("Łączna sprzedaż")
plt.title("TOP 10 klientów generujących największą sprzedaż")
plt.xticks(rotation=45, ha="right")
plt.grid(axis='y')
plt.show()


# 1️⃣ Grupowanie danych według rabatu i obliczenie średniego zysku
discount_profit = df.groupby('Discount')['Profit'].mean()

# 2️⃣ Wykres: wpływ rabatów na zysk
plt.figure(figsize=(12, 6))
sns.barplot(x=discount_profit.index, y=discount_profit.values, hue=discount_profit.index, palette="coolwarm", legend=False)
plt.xlabel("Rabat")
plt.ylabel("Średni zysk")
plt.title("Wpływ rabatu na średni zysk")
plt.grid(axis='y')
plt.show()

# 1️⃣ Sumujemy sprzedaż dla każdego klienta
customer_sales = df.groupby('Customer ID')['Sales'].sum().reset_index()

# 2️⃣ Definiujemy przedziały dla segmentów klientów
bins = [0, customer_sales['Sales'].quantile(0.25), customer_sales['Sales'].quantile(0.5), customer_sales['Sales'].quantile(0.75), customer_sales['Sales'].max()]
labels = ['Niski', 'Średni', 'Wysoki', 'VIP']

# 3️⃣ Tworzymy nową kolumnę 'Customer Segment' z przypisanymi przedziałami sprzedaży
customer_sales['Customer Segment'] = pd.cut(customer_sales['Sales'], bins=bins, labels=labels, include_lowest=True)

# 4️⃣ Dołączamy segmenty do głównej tabeli df
df = df.merge(customer_sales[['Customer ID', 'Customer Segment']], on='Customer ID', how='left')

# 5️⃣ Sprawdzenie, czy podział klientów działa poprawnie
print("\n🟢 Podgląd segmentacji klientów:")
print(df[['Customer ID', 'Customer Segment']].drop_duplicates().head(20))  # Wyświetlenie kilku klientów i ich segmentów

# 6️⃣ Sprawdzenie, czy są puste wartości
print("\n🔴 Liczba brakujących wartości w segmentach:", df['Customer Segment'].isnull().sum())

# 7️⃣ Wykres: liczba klientów w każdej grupie
plt.figure(figsize=(8, 5))
df['Customer Segment'].value_counts().plot(kind='bar', color=['red', 'orange', 'blue', 'green'])
plt.xlabel("Segment klienta")
plt.ylabel("Liczba klientów")
plt.title("Podział klientów na segmenty")
plt.xticks(rotation=0)
plt.grid(axis='y')
plt.show()


# 1️⃣ Połączenie z bazą SQLite (tworzy plik "ecommerce_sales.db" w folderze "data/")
conn = sqlite3.connect("data/ecommerce_sales.db")
cursor = conn.cursor()

# 2️⃣ Zapisujemy dane Pandas do tabeli "sales_data"
# Konwersja kolumny 'Year-Month' na string, aby SQLite mógł ją obsłużyć
df['Year-Month'] = df['Year-Month'].astype(str)

# Zapis danych do bazy SQLite
df.to_sql("sales_data", conn, if_exists="replace", index=False)


print("\n✅ Dane zostały zapisane w bazie SQLite!")

# 3️⃣ Zamykamy połączenie
conn.close()

# 1️⃣ Ponowne otwarcie połączenia z bazą SQLite
conn = sqlite3.connect("data/ecommerce_sales.db")
cursor = conn.cursor()

# 2️⃣ Wykonanie zapytania SQL – TOP 10 najlepiej sprzedających się produktów
query = """
SELECT "Product Name", SUM(Sales) AS Total_Sales
FROM sales_data
GROUP BY "Product Name"
ORDER BY Total_Sales DESC
LIMIT 10;
"""
top_products_sql = pd.read_sql(query, conn)

# 3️⃣ Zamknięcie połączenia
conn.close()

# 4️⃣ Wyświetlenie wyników SQL
print("\n🏆 TOP 10 najlepiej sprzedających się produktów (SQL):")
print(top_products_sql)

