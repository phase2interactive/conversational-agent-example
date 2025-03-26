from langchain_core.tools import tool
from typing import List, Dict, Any
import json
from datetime import datetime, timedelta
import random

# Simulated inventory database
INVENTORY_DATA = {
    "products": [
        {
            "id": "P001",
            "name": "iPhone 15 Pro",
            "category": "Electronics",
            "current_stock": 157,
            "reorder_point": 75,
            "optimal_stock": 250,
            "cost_per_unit": 999.99,
            "lead_time_days": 14,
            "shelf_life_days": 730,
            "daily_sales_rate": 5.3,
            "monthly_sales": [145, 158, 167, 175, 189, 201],
            "supplier": "Apple Inc."
        },
        {
            "id": "P002",
            "name": "Samsung Galaxy S24",
            "category": "Electronics",
            "current_stock": 34,
            "reorder_point": 50,
            "optimal_stock": 150,
            "cost_per_unit": 799.99,
            "lead_time_days": 7,
            "shelf_life_days": 365,
            "daily_sales_rate": 7.8,
            "monthly_sales": [210, 235, 228, 240, 252, 268],
            "supplier": "Samsung Electronics"
        },
        {
            "id": "P003",
            "name": "MacBook Pro 16",
            "category": "Computers",
            "current_stock": 412,
            "reorder_point": 200,
            "optimal_stock": 600,
            "cost_per_unit": 2499.99,
            "lead_time_days": 21,
            "shelf_life_days": 1825,
            "daily_sales_rate": 8.2,
            "monthly_sales": [225, 238, 245, 260, 272, 290],
            "supplier": "Apple Inc."
        },
        {
            "id": "P004",
            "name": "Dell XPS 15",
            "category": "Computers",
            "current_stock": 873,
            "reorder_point": 400,
            "optimal_stock": 1000,
            "cost_per_unit": 1299.99,
            "lead_time_days": 10,
            "shelf_life_days": 1095,
            "daily_sales_rate": 18.5,
            "monthly_sales": [520, 535, 548, 562, 580, 603],
            "supplier": "Dell Technologies"
        },
        {
            "id": "P005",
            "name": "AirPods Pro",
            "category": "Accessories",
            "current_stock": 42,
            "reorder_point": 30,
            "optimal_stock": 100,
            "cost_per_unit": 249.99,
            "lead_time_days": 14,
            "shelf_life_days": 730,
            "daily_sales_rate": 1.2,
            "monthly_sales": [35, 38, 36, 40, 42, 45],
            "supplier": "Apple Inc."
        }
    ],
    "warehouse": {
        "max_capacity_units": 2500,
        "current_utilization_units": 1518,
        "storage_cost_per_unit": 1.25
    },
    "business_constraints": {
        "monthly_procurement_budget": 25000,
        "target_service_level": 0.95,
        "max_days_inventory_held": 90
    }
}

@tool("get_inventory_status")
def get_inventory_status() -> Dict[str, Any]:
    """Get current inventory status for all products including stock levels, alerts, and warehouse utilization."""
    today = datetime.now()
    status = {
        "overview": {
            "total_products": len(INVENTORY_DATA["products"]),
            "total_stock_value": sum(p["current_stock"] * p["cost_per_unit"] for p in INVENTORY_DATA["products"]),
            "warehouse_utilization": f"{(INVENTORY_DATA['warehouse']['current_utilization_units'] / INVENTORY_DATA['warehouse']['max_capacity_units']) * 100:.1f}%",
            "as_of_date": today.strftime("%Y-%m-%d")
        },
        "alerts": [],
        "product_status": []
    }

    for product in INVENTORY_DATA["products"]:
        # Calculate days until stockout based on daily sales rate
        if product["daily_sales_rate"] > 0:
            days_until_stockout = product["current_stock"] / product["daily_sales_rate"]
        else:
            days_until_stockout = float("inf")

        # Check if below reorder point
        if product["current_stock"] <= product["reorder_point"]:
            status["alerts"].append(f"REORDER NEEDED: {product['name']} is below reorder point")

        # Check if stockout imminent (will happen before lead time)
        if days_until_stockout <= product["lead_time_days"]:
            status["alerts"].append(f"URGENT: {product['name']} will stockout in {int(days_until_stockout)} days")

        # Check for overstock
        days_of_supply = days_until_stockout
        if days_of_supply > INVENTORY_DATA["business_constraints"]["max_days_inventory_held"]:
            status["alerts"].append(f"OVERSTOCK: {product['name']} has {int(days_of_supply)} days of supply")

        # Add to product status
        status["product_status"].append({
            "id": product["id"],
            "name": product["name"],
            "current_stock": product["current_stock"],
            "days_until_stockout": int(days_until_stockout),
            "stock_status": "Low" if product["current_stock"] <= product["reorder_point"] else
                           "Overstock" if days_of_supply > INVENTORY_DATA["business_constraints"]["max_days_inventory_held"] else
                           "Adequate"
        })

    return status

@tool("get_product_details")
def get_product_details(product_id: str = None, product_name: str = None) -> Dict[str, Any]:
    """Get detailed information about a specific product by ID or name including stock levels, sales trends, and reorder recommendations."""
    if not product_id and not product_name:
        return {"error": "Must provide either product_id or product_name"}

    product = None
    if product_id:
        product = next((p for p in INVENTORY_DATA["products"] if p["id"] == product_id), None)
    elif product_name:
        # Case-insensitive search that works with partial names
        product_name_lower = product_name.lower()
        candidates = [p for p in INVENTORY_DATA["products"] if product_name_lower in p["name"].lower()]
        if candidates:
            product = candidates[0]  # Take the first match

    if not product:
        return {"error": "Product not found"}

    # Calculate additional metrics
    days_until_stockout = product["current_stock"] / product["daily_sales_rate"] if product["daily_sales_rate"] > 0 else float("inf")
    stockout_date = (datetime.now() + timedelta(days=days_until_stockout)).strftime("%Y-%m-%d") if days_until_stockout != float("inf") else "Never"

    # Calculate trend from monthly sales
    sales_trend = "Increasing" if product["monthly_sales"][-1] > product["monthly_sales"][0] else "Decreasing" if product["monthly_sales"][-1] < product["monthly_sales"][0] else "Stable"
    growth_rate = ((product["monthly_sales"][-1] / product["monthly_sales"][0]) - 1) * 100 if product["monthly_sales"][0] > 0 else 0

    # Add the calculated fields to the product data
    result = product.copy()
    result.update({
        "days_until_stockout": int(days_until_stockout),
        "projected_stockout_date": stockout_date,
        "sales_trend": sales_trend,
        "growth_rate_6mo": f"{growth_rate:.1f}%",
        "inventory_value": product["current_stock"] * product["cost_per_unit"],
        "reorder_recommendation": product["current_stock"] <= product["reorder_point"],
        "optimal_order_quantity": max(0, product["optimal_stock"] - product["current_stock"])
    })

    return result

@tool("get_reorder_recommendations")
def get_reorder_recommendations() -> Dict[str, Any]:
    """Get recommendations for which products need to be reordered, suggested quantities, and budget implications."""
    today = datetime.now()
    recommendations = {
        "as_of_date": today.strftime("%Y-%m-%d"),
        "available_budget": INVENTORY_DATA["business_constraints"]["monthly_procurement_budget"],
        "reorder_recommendations": []
    }

    # Calculate total cost of all recommended reorders
    total_reorder_cost = 0

    for product in INVENTORY_DATA["products"]:
        if product["current_stock"] <= product["reorder_point"]:
            order_quantity = product["optimal_stock"] - product["current_stock"]
            order_cost = order_quantity * product["cost_per_unit"]
            total_reorder_cost += order_cost

            recommendations["reorder_recommendations"].append({
                "id": product["id"],
                "name": product["name"],
                "current_stock": product["current_stock"],
                "reorder_point": product["reorder_point"],
                "recommended_order_quantity": order_quantity,
                "order_cost": order_cost,
                "supplier": product["supplier"],
                "lead_time_days": product["lead_time_days"],
                "priority": "High" if product["current_stock"] / product["daily_sales_rate"] <= product["lead_time_days"] else "Medium"
            })

    # Sort by priority
    recommendations["reorder_recommendations"].sort(key=lambda x: 0 if x["priority"] == "High" else 1)

    # Check if budget constraints are exceeded
    recommendations["total_reorder_cost"] = total_reorder_cost
    recommendations["budget_status"] = "Sufficient" if total_reorder_cost <= INVENTORY_DATA["business_constraints"]["monthly_procurement_budget"] else "Exceeded"

    if recommendations["budget_status"] == "Exceeded":
        recommendations["budget_deficit"] = total_reorder_cost - INVENTORY_DATA["business_constraints"]["monthly_procurement_budget"]

    return recommendations

def create_inventory_tools() -> List:
    """
    Creates and returns the inventory management tools for the agent.
    """
    return [
        get_inventory_status,
        get_product_details,
        get_reorder_recommendations
    ]