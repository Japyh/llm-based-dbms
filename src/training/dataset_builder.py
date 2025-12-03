"""Rule-based NL↔SQL dataset builder for fine-tuning."""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, List

from src.db.core import get_connection, run_query

logger = logging.getLogger(__name__)


SYSTEM_PROMPT = (
    "You are a Text-to-SQL assistant for our SQLite sales database. "
    "Return only a valid SQL SELECT query, with no explanation, no comments, "
    "and no natural language. Never modify data or schema."
)


def get_schema_metadata() -> Dict[str, Any]:
    """
    Introspect the SQLite DB and return a structured schema description.
    Example:
    {
        "tables": {
            "Orders": {"columns": ["ORDERNUMBER", "ORDERDATE", ...]},
            "OrderDetails": {"columns": ["ORDERNUMBER", "PRODUCTCODE", ...]},
            ...
        }
    }
    """
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT name FROM sqlite_master "
        "WHERE type='table' AND name NOT LIKE 'sqlite_%';"
    )
    tables = [row[0] for row in cur.fetchall()]

    meta: Dict[str, Any] = {"tables": {}}
    for table in tables:
        cur.execute(f"PRAGMA table_info({table});")
        cols = [row[1] for row in cur.fetchall()]
        meta["tables"][table] = {"columns": cols}

    conn.close()
    return meta


def generate_sql_templates(schema_meta: Dict[str, Any]) -> List[str]:
    """
    Generate SQL SELECT queries based on the actual sales.db schema.
    Tables: RawSales, Customers, Products, Orders, OrderDetails
    """
    tables = schema_meta["tables"]
    sqls: List[str] = []

    # ========== 1. SIMPLE BROWSING QUERIES ==========
    if "Products" in tables:
        sqls.append("SELECT * FROM Products LIMIT 10;")
        sqls.append("SELECT * FROM Products LIMIT 5;")
        sqls.append("SELECT PRODUCTCODE, PRODUCTLINE, MSRP FROM Products ORDER BY MSRP DESC LIMIT 10;")
        sqls.append("SELECT PRODUCTCODE, PRODUCTLINE FROM Products WHERE PRODUCTLINE = 'Motorcycles';")
        sqls.append("SELECT PRODUCTCODE, PRODUCTLINE FROM Products WHERE PRODUCTLINE = 'Classic Cars';")
        sqls.append("SELECT * FROM Products WHERE MSRP > 100 ORDER BY MSRP DESC;")

    if "Customers" in tables:
        sqls.append("SELECT * FROM Customers LIMIT 10;")
        sqls.append("SELECT * FROM Customers LIMIT 20;")
        sqls.append("SELECT CUSTOMERNAME, CITY, COUNTRY FROM Customers WHERE COUNTRY = 'USA';")
        sqls.append("SELECT CUSTOMERNAME, CITY, COUNTRY FROM Customers WHERE COUNTRY = 'France';")
        sqls.append("SELECT CUSTOMERNAME, PHONE, CITY FROM Customers WHERE CITY = 'Paris';")
        sqls.append("SELECT * FROM Customers WHERE STATE = 'CA';")

    if "Orders" in tables:
        sqls.append("SELECT * FROM Orders LIMIT 10;")
        sqls.append("SELECT * FROM Orders WHERE STATUS = 'Shipped' LIMIT 20;")
        sqls.append("SELECT * FROM Orders WHERE STATUS = 'Cancelled';")
        sqls.append("SELECT * FROM Orders WHERE YEAR_ID = 2003;")
        sqls.append("SELECT * FROM Orders WHERE YEAR_ID = 2004;")
        sqls.append("SELECT ORDERNUMBER, ORDERDATE, STATUS, CUSTOMERNAME FROM Orders WHERE YEAR_ID = 2003 AND STATUS = 'Shipped';")

    if "OrderDetails" in tables:
        sqls.append("SELECT * FROM OrderDetails LIMIT 10;")
        sqls.append("SELECT * FROM OrderDetails WHERE DEALSIZE = 'Large';")
        sqls.append("SELECT * FROM OrderDetails WHERE DEALSIZE = 'Medium';")
        sqls.append("SELECT * FROM OrderDetails WHERE REVIEWRATING >= 4;")
        sqls.append("SELECT * FROM OrderDetails WHERE REVIEWRATING = 5 LIMIT 20;")

    # ========== 2. AGGREGATION QUERIES ==========
    if "Products" in tables:
        sqls.append("SELECT COUNT(*) AS total_products FROM Products;")
        sqls.append("SELECT PRODUCTLINE, COUNT(*) AS product_count FROM Products GROUP BY PRODUCTLINE ORDER BY product_count DESC;")
        sqls.append("SELECT PRODUCTLINE, AVG(MSRP) AS avg_price FROM Products GROUP BY PRODUCTLINE ORDER BY avg_price DESC;")
        sqls.append("SELECT PRODUCTLINE, MIN(MSRP) AS min_price, MAX(MSRP) AS max_price FROM Products GROUP BY PRODUCTLINE;")
        sqls.append("SELECT AVG(MSRP) AS average_msrp FROM Products;")

    if "Customers" in tables:
        sqls.append("SELECT COUNT(*) AS total_customers FROM Customers;")
        sqls.append("SELECT COUNTRY, COUNT(*) AS customer_count FROM Customers GROUP BY COUNTRY ORDER BY customer_count DESC;")
        sqls.append("SELECT CITY, STATE, COUNT(*) AS customers FROM Customers WHERE COUNTRY = 'USA' GROUP BY CITY, STATE ORDER BY customers DESC;")
        sqls.append("SELECT TERRITORY, COUNT(*) AS customer_count FROM Customers WHERE TERRITORY IS NOT NULL GROUP BY TERRITORY;")

    if "Orders" in tables:
        sqls.append("SELECT COUNT(*) AS total_orders FROM Orders;")
        sqls.append("SELECT STATUS, COUNT(*) AS order_count FROM Orders GROUP BY STATUS;")
        sqls.append("SELECT YEAR_ID, COUNT(*) AS yearly_orders FROM Orders GROUP BY YEAR_ID ORDER BY YEAR_ID;")
        sqls.append("SELECT YEAR_ID, MONTH_ID, COUNT(*) AS order_count FROM Orders GROUP BY YEAR_ID, MONTH_ID ORDER BY YEAR_ID, MONTH_ID;")
        sqls.append("SELECT YEAR_ID, QTR_ID, COUNT(*) AS orders FROM Orders GROUP BY YEAR_ID, QTR_ID ORDER BY YEAR_ID, QTR_ID;")
        sqls.append("SELECT CUSTOMERNAME, COUNT(*) AS order_count FROM Orders GROUP BY CUSTOMERNAME ORDER BY order_count DESC LIMIT 10;")

    if "OrderDetails" in tables:
        sqls.append("SELECT COUNT(*) AS total_order_lines FROM OrderDetails;")
        sqls.append("SELECT SUM(SALES) AS total_revenue FROM OrderDetails;")
        sqls.append("SELECT AVG(SALES) AS avg_sale_amount FROM OrderDetails;")
        sqls.append("SELECT SUM(QUANTITYORDERED) AS total_quantity_sold FROM OrderDetails;")
        sqls.append("SELECT PRODUCTCODE, SUM(SALES) AS total_sales FROM OrderDetails GROUP BY PRODUCTCODE ORDER BY total_sales DESC LIMIT 10;")
        sqls.append("SELECT PRODUCTCODE, SUM(SALES) AS total_sales FROM OrderDetails GROUP BY PRODUCTCODE ORDER BY total_sales DESC LIMIT 5;")
        sqls.append("SELECT PRODUCTCODE, SUM(QUANTITYORDERED) AS total_quantity FROM OrderDetails GROUP BY PRODUCTCODE ORDER BY total_quantity DESC LIMIT 10;")
        sqls.append("SELECT DEALSIZE, COUNT(*) AS deal_count, SUM(SALES) AS total_sales FROM OrderDetails GROUP BY DEALSIZE ORDER BY total_sales DESC;")
        sqls.append("SELECT DEALSIZE, AVG(SALES) AS avg_sales FROM OrderDetails GROUP BY DEALSIZE ORDER BY avg_sales DESC;")
        sqls.append("SELECT PRODUCTCODE, AVG(REVIEWRATING) AS avg_rating, COUNT(*) AS review_count FROM OrderDetails GROUP BY PRODUCTCODE HAVING review_count >= 5 ORDER BY avg_rating DESC LIMIT 10;")
        sqls.append("SELECT REVIEWRATING, COUNT(*) AS review_count FROM OrderDetails GROUP BY REVIEWRATING ORDER BY REVIEWRATING;")
        sqls.append("SELECT AVG(REVIEWRATING) AS avg_rating FROM OrderDetails;")

    # ========== 3. TIME-BASED QUERIES ==========
    if "Orders" in tables and "OrderDetails" in tables:
        sqls.append(
            "SELECT o.YEAR_ID, SUM(od.SALES) AS yearly_revenue "
            "FROM Orders o "
            "JOIN OrderDetails od ON o.ORDERNUMBER = od.ORDERNUMBER "
            "GROUP BY o.YEAR_ID "
            "ORDER BY o.YEAR_ID;"
        )
        sqls.append(
            "SELECT o.YEAR_ID, o.MONTH_ID, SUM(od.SALES) AS monthly_revenue "
            "FROM Orders o "
            "JOIN OrderDetails od ON o.ORDERNUMBER = od.ORDERNUMBER "
            "GROUP BY o.YEAR_ID, o.MONTH_ID "
            "ORDER BY o.YEAR_ID, o.MONTH_ID;"
        )
        sqls.append(
            "SELECT o.YEAR_ID, o.QTR_ID, SUM(od.SALES) AS quarterly_revenue "
            "FROM Orders o "
            "JOIN OrderDetails od ON o.ORDERNUMBER = od.ORDERNUMBER "
            "GROUP BY o.YEAR_ID, o.QTR_ID "
            "ORDER BY o.YEAR_ID, o.QTR_ID;"
        )
        sqls.append(
            "SELECT o.YEAR_ID, o.MONTH_ID, SUM(od.SALES) AS monthly_revenue "
            "FROM Orders o "
            "JOIN OrderDetails od ON o.ORDERNUMBER = od.ORDERNUMBER "
            "WHERE o.YEAR_ID = 2003 "
            "GROUP BY o.YEAR_ID, o.MONTH_ID "
            "ORDER BY o.MONTH_ID;"
        )
        sqls.append(
            "SELECT o.YEAR_ID, o.MONTH_ID, SUM(od.SALES) AS monthly_revenue "
            "FROM Orders o "
            "JOIN OrderDetails od ON o.ORDERNUMBER = od.ORDERNUMBER "
            "WHERE o.YEAR_ID = 2004 "
            "GROUP BY o.YEAR_ID, o.MONTH_ID "
            "ORDER BY o.MONTH_ID;"
        )
        sqls.append(
            "SELECT o.YEAR_ID, o.MONTH_ID, SUM(od.SALES) AS revenue "
            "FROM Orders o "
            "JOIN OrderDetails od ON o.ORDERNUMBER = od.ORDERNUMBER "
            "GROUP BY o.YEAR_ID, o.MONTH_ID "
            "ORDER BY revenue DESC "
            "LIMIT 10;"
        )

    # ========== 4. JOIN QUERIES - ORDERS + ORDERDETAILS ==========
    if "Orders" in tables and "OrderDetails" in tables:
        sqls.append(
            "SELECT o.CUSTOMERNAME, SUM(od.SALES) AS total_sales "
            "FROM Orders o "
            "JOIN OrderDetails od ON o.ORDERNUMBER = od.ORDERNUMBER "
            "GROUP BY o.CUSTOMERNAME "
            "ORDER BY total_sales DESC "
            "LIMIT 10;"
        )
        sqls.append(
            "SELECT o.CUSTOMERNAME, SUM(od.SALES) AS total_sales "
            "FROM Orders o "
            "JOIN OrderDetails od ON o.ORDERNUMBER = od.ORDERNUMBER "
            "GROUP BY o.CUSTOMERNAME "
            "ORDER BY total_sales DESC "
            "LIMIT 5;"
        )
        sqls.append(
            "SELECT o.CUSTOMERNAME, COUNT(DISTINCT o.ORDERNUMBER) AS order_count, SUM(od.SALES) AS total_sales "
            "FROM Orders o "
            "JOIN OrderDetails od ON o.ORDERNUMBER = od.ORDERNUMBER "
            "GROUP BY o.CUSTOMERNAME "
            "ORDER BY total_sales DESC "
            "LIMIT 10;"
        )
        sqls.append(
            "SELECT o.STATUS, COUNT(DISTINCT o.ORDERNUMBER) AS order_count, SUM(od.SALES) AS total_sales "
            "FROM Orders o "
            "JOIN OrderDetails od ON o.ORDERNUMBER = od.ORDERNUMBER "
            "GROUP BY o.STATUS;"
        )
        sqls.append(
            "SELECT o.ORDERNUMBER, o.CUSTOMERNAME, SUM(od.SALES) AS order_total "
            "FROM Orders o "
            "JOIN OrderDetails od ON o.ORDERNUMBER = od.ORDERNUMBER "
            "GROUP BY o.ORDERNUMBER, o.CUSTOMERNAME "
            "ORDER BY order_total DESC "
            "LIMIT 10;"
        )
        sqls.append(
            "SELECT o.CUSTOMERNAME, AVG(od.SALES) AS avg_sale_per_line "
            "FROM Orders o "
            "JOIN OrderDetails od ON o.ORDERNUMBER = od.ORDERNUMBER "
            "GROUP BY o.CUSTOMERNAME "
            "ORDER BY avg_sale_per_line DESC "
            "LIMIT 10;"
        )

    # ========== 5. JOIN QUERIES - PRODUCTS + ORDERDETAILS ==========
    if "Products" in tables and "OrderDetails" in tables:
        sqls.append(
            "SELECT p.PRODUCTLINE, SUM(od.SALES) AS total_sales "
            "FROM Products p "
            "JOIN OrderDetails od ON p.PRODUCTCODE = od.PRODUCTCODE "
            "GROUP BY p.PRODUCTLINE "
            "ORDER BY total_sales DESC;"
        )
        sqls.append(
            "SELECT p.PRODUCTLINE, COUNT(*) AS line_count, SUM(od.SALES) AS total_sales "
            "FROM Products p "
            "JOIN OrderDetails od ON p.PRODUCTCODE = od.PRODUCTCODE "
            "GROUP BY p.PRODUCTLINE "
            "ORDER BY total_sales DESC;"
        )
        sqls.append(
            "SELECT p.PRODUCTCODE, p.PRODUCTLINE, SUM(od.QUANTITYORDERED) AS total_quantity "
            "FROM Products p "
            "JOIN OrderDetails od ON p.PRODUCTCODE = od.PRODUCTCODE "
            "GROUP BY p.PRODUCTCODE, p.PRODUCTLINE "
            "ORDER BY total_quantity DESC "
            "LIMIT 10;"
        )
        sqls.append(
            "SELECT p.PRODUCTLINE, SUM(od.QUANTITYORDERED) AS total_quantity "
            "FROM Products p "
            "JOIN OrderDetails od ON p.PRODUCTCODE = od.PRODUCTCODE "
            "GROUP BY p.PRODUCTLINE "
            "ORDER BY total_quantity DESC;"
        )
        sqls.append(
            "SELECT p.PRODUCTLINE, AVG(od.REVIEWRATING) AS avg_rating "
            "FROM Products p "
            "JOIN OrderDetails od ON p.PRODUCTCODE = od.PRODUCTCODE "
            "GROUP BY p.PRODUCTLINE "
            "ORDER BY avg_rating DESC;"
        )

    # ========== 6. 3-WAY JOINS ==========
    if "Orders" in tables and "OrderDetails" in tables and "Products" in tables:
        sqls.append(
            "SELECT o.YEAR_ID, p.PRODUCTLINE, SUM(od.SALES) AS total_sales "
            "FROM Orders o "
            "JOIN OrderDetails od ON o.ORDERNUMBER = od.ORDERNUMBER "
            "JOIN Products p ON od.PRODUCTCODE = p.PRODUCTCODE "
            "GROUP BY o.YEAR_ID, p.PRODUCTLINE "
            "ORDER BY o.YEAR_ID, total_sales DESC;"
        )
        sqls.append(
            "SELECT o.CUSTOMERNAME, p.PRODUCTLINE, SUM(od.SALES) AS total_sales "
            "FROM Orders o "
            "JOIN OrderDetails od ON o.ORDERNUMBER = od.ORDERNUMBER "
            "JOIN Products p ON od.PRODUCTCODE = p.PRODUCTCODE "
            "GROUP BY o.CUSTOMERNAME, p.PRODUCTLINE "
            "ORDER BY total_sales DESC "
            "LIMIT 20;"
        )
        sqls.append(
            "SELECT o.YEAR_ID, o.MONTH_ID, p.PRODUCTLINE, SUM(od.SALES) AS total_sales "
            "FROM Orders o "
            "JOIN OrderDetails od ON o.ORDERNUMBER = od.ORDERNUMBER "
            "JOIN Products p ON od.PRODUCTCODE = p.PRODUCTCODE "
            "WHERE o.YEAR_ID = 2003 "
            "GROUP BY o.YEAR_ID, o.MONTH_ID, p.PRODUCTLINE "
            "ORDER BY o.MONTH_ID, total_sales DESC;"
        )

    # ========== 7. CUSTOMER + ORDERS JOINS ==========
    if "Orders" in tables and "Customers" in tables:
        sqls.append(
            "SELECT c.COUNTRY, COUNT(DISTINCT o.ORDERNUMBER) AS order_count "
            "FROM Customers c "
            "JOIN Orders o ON c.CUSTOMERNAME = o.CUSTOMERNAME "
            "GROUP BY c.COUNTRY "
            "ORDER BY order_count DESC;"
        )
        sqls.append(
            "SELECT c.CITY, COUNT(DISTINCT o.ORDERNUMBER) AS order_count "
            "FROM Customers c "
            "JOIN Orders o ON c.CUSTOMERNAME = o.CUSTOMERNAME "
            "WHERE c.COUNTRY = 'USA' "
            "GROUP BY c.CITY "
            "ORDER BY order_count DESC;"
        )

    # ========== 8. REVIEW ANALYSIS ==========
    if "OrderDetails" in tables:
        sqls.append(
            "SELECT REVIEWRATING, COUNT(*) AS review_count, AVG(SALES) AS avg_sale_amount "
            "FROM OrderDetails "
            "GROUP BY REVIEWRATING "
            "ORDER BY REVIEWRATING;"
        )
        sqls.append(
            "SELECT PRODUCTCODE, AVG(REVIEWRATING) AS avg_rating "
            "FROM OrderDetails "
            "GROUP BY PRODUCTCODE "
            "HAVING COUNT(*) >= 10 "
            "ORDER BY avg_rating DESC "
            "LIMIT 10;"
        )

    return sqls


def generate_nl_variants_for_sql(sql: str) -> List[str]:
    """
    Generate multiple natural language variants for a SQL query.
    Returns 2-3 different phrasings for the same SQL to expand the dataset.
    """
    s = sql.lower()
    nls: List[str] = []

    # ========== SIMPLE BROWSING ==========
    if "select * from products limit 10" in s:
        nls.extend([
            "Show me the first 10 products.",
            "List the first ten products in the database.",
            "Display 10 products from the products table."
        ])
    elif "select * from products limit 5" in s:
        nls.extend([
            "Show me 5 products.",
            "List the first 5 products.",
            "Display five products."
        ])
    elif "productcode, productline, msrp from products order by msrp desc limit 10" in s:
        nls.extend([
            "Show the 10 most expensive products.",
            "List the top 10 products by price.",
            "Which products have the highest MSRP?"
        ])
    elif "productline = 'motorcycles'" in s:
        nls.extend([
            "Show all motorcycle products.",
            "List products in the Motorcycles product line.",
            "Which products are motorcycles?"
        ])
    elif "productline = 'classic cars'" in s:
        nls.extend([
            "Show all classic car products.",
            "List products in the Classic Cars category.",
            "Which products are classic cars?"
        ])
    elif "from products where msrp > 100" in s:
        nls.extend([
            "Show products with MSRP over 100.",
            "List all products priced above $100.",
            "Which products cost more than 100?"
        ])
    elif "select * from customers limit 10" in s:
        nls.extend([
            "Show me the first 10 customers.",
            "List 10 customers from the database.",
            "Display the first ten customers."
        ])
    elif "select * from customers limit 20" in s:
        nls.extend([
            "Show me 20 customers.",
            "List the first 20 customers.",
            "Display twenty customers."
        ])
    elif "from customers where country = 'usa'" in s:
        nls.extend([
            "Show all customers from the USA.",
            "List American customers.",
            "Which customers are located in the United States?"
        ])
    elif "from customers where country = 'france'" in s:
        nls.extend([
            "Show all customers from France.",
            "List French customers.",
            "Which customers are in France?"
        ])
    elif "from customers where city = 'paris'" in s:
        nls.extend([
            "Show customers in Paris.",
            "List all Paris-based customers.",
            "Which customers are from Paris?"
        ])
    elif "from customers where state = 'ca'" in s:
        nls.extend([
            "Show customers in California.",
            "List all California customers.",
            "Which customers are from CA?"
        ])
    elif "select * from orders limit 10" in s:
        nls.extend([
            "Show me the first 10 orders.",
            "List 10 orders.",
            "Display the first ten orders."
        ])
    elif "where status = 'shipped' limit 20" in s:
        nls.extend([
            "Show 20 shipped orders.",
            "List orders that have been shipped.",
            "Which orders have shipping status?"
        ])
    elif "where status = 'cancelled'" in s:
        nls.extend([
            "Show cancelled orders.",
            "List all orders that were cancelled.",
            "Which orders have been cancelled?"
        ])
    elif "from orders where year_id = 2003" in s and "shipped" not in s:
        nls.extend([
            "Show all orders from 2003.",
            "List orders placed in 2003.",
            "Which orders were made in the year 2003?"
        ])
    elif "from orders where year_id = 2004" in s:
        nls.extend([
            "Show all orders from 2004.",
            "List orders placed in 2004.",
            "Which orders were made in 2004?"
        ])
    elif "year_id = 2003 and status = 'shipped'" in s:
        nls.extend([
            "Show shipped orders from 2003.",
            "List all orders shipped in 2003.",
            "Which 2003 orders were shipped?"
        ])
    elif "select * from orderdetails limit 10" in s:
        nls.extend([
            "Show me the first 10 order details.",
            "List 10 order line items.",
            "Display the first ten order details."
        ])
    elif "where dealsize = 'large'" in s:
        nls.extend([
            "Show large deals.",
            "List all large-sized deals.",
            "Which order details are for large deals?"
        ])
    elif "where dealsize = 'medium'" in s:
        nls.extend([
            "Show medium-sized deals.",
            "List all medium deals.",
            "Which orders are medium-sized?"
        ])
    elif "where reviewrating >= 4" in s and "limit 20" in s:
        nls.extend([
            "Show highly rated orders.",
            "List order details with ratings of 4 or higher.",
            "Which products have good reviews?"
        ])
    elif "where reviewrating = 5 limit 20" in s:
        nls.extend([
            "Show 5-star rated orders.",
            "List all order details with perfect ratings.",
            "Which products got the highest review rating?"
        ])

    # ========== AGGREGATIONS ==========
    elif "count(*) as total_products from products" in s:
        nls.extend([
            "How many products are there in total?",
            "What is the total product count?",
            "Count all products in the database."
        ])
    elif "productline, count(*) as product_count from products group by productline" in s:
        nls.extend([
            "How many products are in each product line?",
            "Show product count by product line.",
            "Break down products by category."
        ])
    elif "productline, avg(msrp) as avg_price from products group by productline" in s:
        nls.extend([
            "What is the average MSRP for each product line?",
            "Show average price by product line.",
            "Calculate mean price for each product category."
        ])
    elif "productline, min(msrp) as min_price, max(msrp) as max_price from products" in s:
        nls.extend([
            "What are the min and max prices for each product line?",
            "Show price range by product line.",
            "Display minimum and maximum MSRP for each category."
        ])
    elif "avg(msrp) as average_msrp from products" in s:
        nls.extend([
            "What is the average MSRP across all products?",
            "Calculate the mean product price.",
            "What's the average price of products?"
        ])
    elif "count(*) as total_customers from customers" in s:
        nls.extend([
            "How many customers are there?",
            "What is the total customer count?",
            "Count all customers."
        ])
    elif "country, count(*) as customer_count from customers group by country" in s:
        nls.extend([
            "How many customers are in each country?",
            "Show customer count by country.",
            "Break down customers by country."
        ])
    elif "city, state, count(*) as customers from customers where country = 'usa'" in s:
        nls.extend([
            "Show customer counts by city and state in the USA.",
            "How many customers are in each US city?",
            "Break down American customers by location."
        ])
    elif "territory, count(*) as customer_count from customers where territory is not null" in s:
        nls.extend([
            "Show customer count by territory.",
            "How many customers are in each territory?",
            "Break down customers by sales territory."
        ])
    elif "count(*) as total_orders from orders" in s:
        nls.extend([
            "How many orders are there in total?",
            "What is the total order count?",
            "Count all orders."
        ])
    elif "status, count(*) as order_count from orders group by status" in s and "join" not in s:
        nls.extend([
            "How many orders are in each status?",
            "Show order count by status.",
            "Break down orders by their status."
        ])
    elif "year_id, count(*) as yearly_orders from orders group by year_id" in s:
        nls.extend([
            "How many orders per year?",
            "Show order count by year.",
            "Break down orders by year."
        ])
    elif "year_id, month_id, count(*) as order_count from orders group by year_id, month_id" in s and "join" not in s:
        nls.extend([
            "Show the number of orders by year and month.",
            "How many orders per month?",
            "Break down order count by month and year."
        ])
    elif "year_id, qtr_id, count(*) as orders from orders group by year_id, qtr_id" in s:
        nls.extend([
            "How many orders were placed in each quarter by year?",
            "Show quarterly order counts.",
            "Break down orders by quarter."
        ])
    elif "customername, count(*) as order_count from orders group by customername" in s and "join" not in s:
        nls.extend([
            "Which customers placed the most orders?",
            "Show order count per customer.",
            "List customers ranked by number of orders."
        ])
    elif "count(*) as total_order_lines from orderdetails" in s:
        nls.extend([
            "How many order line items are there?",
            "What is the total count of order details?",
            "Count all order detail records."
        ])
    elif "sum(sales) as total_revenue from orderdetails" in s and "group by" not in s:
        nls.extend([
            "What is the total revenue?",
            "Calculate total sales amount.",
            "What are the total sales across all orders?"
        ])
    elif "avg(sales) as avg_sale_amount from orderdetails" in s and "group by" not in s:
        nls.extend([
            "What is the average sale amount?",
            "Calculate the mean sales value.",
            "What's the average revenue per order line?"
        ])
    elif "sum(quantityordered) as total_quantity_sold from orderdetails" in s:
        nls.extend([
            "What is the total quantity sold?",
            "How many units were sold in total?",
            "Calculate total quantity ordered."
        ])
    elif "productcode, sum(sales) as total_sales from orderdetails group by productcode" in s and "limit 10" in s:
        nls.extend([
            "What are the top 10 products by total sales?",
            "Show the best-selling products.",
            "List the 10 products with highest revenue."
        ])
    elif "productcode, sum(sales) as total_sales from orderdetails group by productcode" in s and "limit 5" in s:
        nls.extend([
            "What are the top 5 products by sales?",
            "Show the 5 best-selling products.",
            "List the top five products by revenue."
        ])
    elif "productcode, sum(quantityordered) as total_quantity from orderdetails group by productcode" in s and "limit 10" in s:
        nls.extend([
            "Which products have the highest quantity ordered?",
            "Show top 10 products by units sold.",
            "List products with most units ordered."
        ])
    elif "dealsize, count(*) as deal_count, sum(sales) as total_sales from orderdetails group by dealsize" in s and "order by total_sales" in s:
        nls.extend([
            "Show sales summary by deal size.",
            "Break down sales by deal size.",
            "What are the sales for each deal size category?"
        ])
    elif "dealsize, avg(sales) as avg_sales from orderdetails group by dealsize" in s:
        nls.extend([
            "What is the average sale amount by deal size?",
            "Show mean sales for each deal size.",
            "Calculate average revenue by deal size."
        ])
    elif "avg(reviewrating) as avg_rating, count(*) as review_count from orderdetails group by productcode having review_count >= 5" in s:
        nls.extend([
            "Which products have the highest average ratings (with at least 5 reviews)?",
            "Show top-rated products with sufficient reviews.",
            "List products with best ratings (minimum 5 reviews)."
        ])
    elif "reviewrating, count(*) as review_count from orderdetails group by reviewrating" in s and "avg" not in s:
        nls.extend([
            "How many reviews for each rating level?",
            "Show review count by rating.",
            "Break down reviews by rating score."
        ])
    elif "avg(reviewrating) as avg_rating from orderdetails" in s and "group by" not in s:
        nls.extend([
            "What is the average review rating?",
            "Calculate mean rating across all reviews.",
            "What's the overall average rating?"
        ])

    # ========== TIME-BASED JOINS ==========
    elif "o.year_id, sum(od.sales) as yearly_revenue" in s and "month" not in s and "qtr" not in s:
        nls.extend([
            "Show yearly revenue.",
            "What is the total sales for each year?",
            "Break down revenue by year."
        ])
    elif "o.year_id, o.month_id, sum(od.sales) as monthly_revenue" in s and "where" not in s:
        nls.extend([
            "Show the total sales revenue for each month.",
            "What is the monthly revenue?",
            "Break down sales by month and year."
        ])
    elif "o.year_id, o.qtr_id, sum(od.sales) as quarterly_revenue" in s:
        nls.extend([
            "Show quarterly revenue.",
            "What is the total sales for each quarter?",
            "Break down revenue by quarter and year."
        ])
    elif "where o.year_id = 2003" in s and "month_id" in s and "sum(od.sales)" in s and "productline" not in s:
        nls.extend([
            "Show monthly revenue for 2003.",
            "What were the sales for each month in 2003?",
            "Break down 2003 sales by month."
        ])
    elif "where o.year_id = 2004" in s and "month_id" in s:
        nls.extend([
            "Show monthly revenue for 2004.",
            "What were the sales for each month in 2004?",
            "Break down 2004 sales by month."
        ])
    elif "order by revenue desc" in s and "limit 10" in s and "year_id, o.month_id" in s:
        nls.extend([
            "Which months had the highest sales?",
            "Show top 10 months by revenue.",
            "List the best-performing months."
        ])

    # ========== CUSTOMER-FOCUSED JOINS ==========
    elif "o.customername, sum(od.sales) as total_sales" in s and "limit 10" in s and "count" not in s:
        nls.extend([
            "Who are the top 10 customers by total sales amount?",
            "Show the best customers by revenue.",
            "List the 10 customers with highest spending."
        ])
    elif "o.customername, sum(od.sales) as total_sales" in s and "limit 5" in s:
        nls.extend([
            "Who are the top 5 customers by sales?",
            "Show the 5 best customers.",
            "List top five customers by revenue."
        ])
    elif "o.customername, count(distinct o.ordernumber) as order_count, sum(od.sales) as total_sales" in s:
        nls.extend([
            "Show customer sales and order counts.",
            "List customers with their total sales and number of orders.",
            "Which customers have the most orders and highest sales?"
        ])
    elif "o.status, count(distinct o.ordernumber) as order_count, sum(od.sales) as total_sales" in s:
        nls.extend([
            "What are the total sales and order counts by order status?",
            "Show sales breakdown by status.",
            "Break down orders and revenue by status."
        ])
    elif "o.ordernumber, o.customername, sum(od.sales) as order_total" in s:
        nls.extend([
            "Show the largest orders by total value.",
            "Which orders have the highest total amount?",
            "List top 10 orders by revenue."
        ])
    elif "o.customername, avg(od.sales) as avg_sale_per_line" in s:
        nls.extend([
            "Which customers have the highest average sale per line item?",
            "Show customers by average sale amount.",
            "List customers with highest mean order line value."
        ])

    # ========== PRODUCT-FOCUSED JOINS ==========
    elif "p.productline, sum(od.sales) as total_sales" in s and "count" not in s and "quantityordered" not in s:
        nls.extend([
            "What are the total sales for each product line?",
            "Show revenue by product line.",
            "Break down sales by product category."
        ])
    elif "p.productline, count(*) as line_count, sum(od.sales) as total_sales" in s:
        nls.extend([
            "Show sales and order counts for each product line.",
            "Break down product lines by sales and count.",
            "What are the sales and transaction counts per product line?"
        ])
    elif "p.productcode, p.productline, sum(od.quantityordered) as total_quantity" in s:
        nls.extend([
            "Which products have the highest quantity ordered?",
            "Show top 10 products by units sold.",
            "List products with most quantity ordered."
        ])
    elif "p.productline, sum(od.quantityordered) as total_quantity" in s:
        nls.extend([
            "What is the total quantity ordered by product line?",
            "Show units sold per product line.",
            "Break down quantity ordered by category."
        ])
    elif "p.productline, avg(od.reviewrating) as avg_rating" in s:
        nls.extend([
            "What is the average rating for each product line?",
            "Show average review ratings by product line.",
            "Which product lines have the best ratings?"
        ])

    # ========== 3-WAY JOINS ==========
    elif "o.year_id, p.productline, sum(od.sales) as total_sales" in s and "month" not in s and "customername" not in s:
        nls.extend([
            "Show sales by product line for each year.",
            "Break down yearly sales by product category.",
            "What are the sales for each product line per year?"
        ])
    elif "o.customername, p.productline, sum(od.sales) as total_sales" in s:
        nls.extend([
            "Show customer sales by product line.",
            "Which customers buy which product lines?",
            "Break down customer spending by product category."
        ])
    elif "o.year_id, o.month_id, p.productline, sum(od.sales)" in s and "where o.year_id = 2003" in s:
        nls.extend([
            "Show 2003 monthly sales by product line.",
            "Break down 2003 sales by month and product line.",
            "What were the monthly sales per product line in 2003?"
        ])

    # ========== CUSTOMER + ORDERS ==========
    elif "c.country, count(distinct o.ordernumber) as order_count" in s and "city" not in s:
        nls.extend([
            "How many orders came from each country?",
            "Show order count by country.",
            "Break down orders by customer country."
        ])
    elif "c.city, count(distinct o.ordernumber) as order_count" in s and "where c.country = 'usa'" in s:
        nls.extend([
            "How many orders came from each US city?",
            "Show order count by city in the USA.",
            "Which American cities generated the most orders?"
        ])

    # ========== REVIEW ANALYSIS ==========
    elif "reviewrating, count(*) as review_count, avg(sales) as avg_sale_amount" in s:
        nls.extend([
            "What is the relationship between review ratings and average sale amounts?",
            "Show average sales by review rating.",
            "Do higher ratings correlate with higher sales?"
        ])
    elif "avg(reviewrating) as avg_rating" in s and "having count(*) >= 10" in s:
        nls.extend([
            "Which products have the best ratings (minimum 10 reviews)?",
            "Show top-rated products with at least 10 reviews.",
            "List products with highest average ratings and sufficient review count."
        ])

    # Default fallback
    if not nls:
        nls.append("Execute this query on the sales database.")

    return nls


def make_chat_example(nl: str, sql: str) -> Dict[str, Any]:
    """
    Wrap one (NL, SQL) pair into a chat-style training example.
    """
    return {
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": nl},
            {"role": "assistant", "content": sql.strip()},
        ]
    }


def build_chat_dataset(limit: int | None = None) -> List[Dict[str, Any]]:
    """
    Build a list of chat-style examples and skip any SQL that fails on sales.db.
    For each valid SQL, generate multiple NL variants to expand the dataset.
    """
    schema_meta = get_schema_metadata()
    sql_list = generate_sql_templates(schema_meta)

    if limit is not None:
        sql_list = sql_list[:limit]

    dataset: List[Dict[str, Any]] = []
    for sql in sql_list:
        try:
            # Validate SQL is executable
            run_query(sql)
        except Exception as e:
            print(f"Skipping invalid SQL: {e}\n{sql}\n")
            continue

        # Generate multiple NL variants for this SQL
        nl_variants = generate_nl_variants_for_sql(sql)
        for nl in nl_variants:
            dataset.append(make_chat_example(nl, sql))

    return dataset


def export_chat_jsonl(dataset: List[Dict[str, Any]], path: str | Path) -> None:
    """
    Save the dataset as a JSONL file where each line is one example.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as f:
        for ex in dataset:
            f.write(json.dumps(ex, ensure_ascii=False) + "\n")


def main() -> None:  # pragma: no cover - convenience script
    dataset = build_chat_dataset(limit=None)
    export_chat_jsonl(dataset, "data/nl2sql_train_chat_raw.jsonl")
    print(f"Exported {len(dataset)} examples to data/nl2sql_train_chat_raw.jsonl")


if __name__ == "__main__":  # pragma: no cover
    main()


if __name__ == "__main__":  # pragma: no cover
    main()
