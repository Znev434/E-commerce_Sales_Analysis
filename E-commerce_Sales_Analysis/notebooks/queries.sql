-- 📌 TOP 10 najlepiej sprzedających się produktów
SELECT "Product Name", SUM(Sales) AS Total_Sales
FROM sales_data
GROUP BY "Product Name"
ORDER BY Total_Sales DESC
LIMIT 10;

-- 📌 TOP 10 klientów generujących największą sprzedaż
SELECT "Customer ID", SUM(Sales) AS Total_Sales
FROM sales_data
GROUP BY "Customer ID"
ORDER BY Total_Sales DESC
LIMIT 10;

-- 📌 Średni zysk w zależności od rabatu
SELECT Discount, AVG(Profit) AS Avg_Profit
FROM sales_data
GROUP BY Discount
ORDER BY Discount;
