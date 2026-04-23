"""Tests for equipment catalog and order tools."""

import json
import pytest
from src.tools.equipment_catalog import (
    get_products_by_category,
    search_products_by_name,
    get_product_details,
)
from src.tools.order_support import (
    get_orders_by_customer,
    get_order_details,
    get_employee_by_order_and_customer,
)


class TestEquipmentCatalogTools:
    def test_get_products_by_category_found(self):
        result = get_products_by_category.invoke({"category_name": "Respiratory"})
        data = json.loads(result)
        assert len(data) >= 1
        assert any("Respiratory" in prod["CategoryName"] for prod in data)
        assert "ProductId" in data[0]

    def test_get_products_by_category_not_found(self):
        result = get_products_by_category.invoke({"category_name": "NonexistentCategoryXYZ"})
        assert "No products found" in result

    def test_search_products_by_name_found(self):
        result = search_products_by_name.invoke({"product_name": "Oxygen"})
        data = json.loads(result)
        assert len(data) >= 1
        assert "Oxygen" in data[0]["ProductName"]

    def test_search_products_by_name_not_found(self):
        result = search_products_by_name.invoke({"product_name": "NonexistentProductXYZ"})
        assert "No products found" in result

    def test_get_product_details_found(self):
        result = get_product_details.invoke({"product_id": "1"})
        data = json.loads(result)
        assert len(data) == 1
        assert data[0]["ProductId"] == 1
        assert "Description" in data[0]

    def test_get_product_details_not_found(self):
        result = get_product_details.invoke({"product_id": "99999"})
        assert "No product found" in result

    def test_get_product_details_invalid_id(self):
        result = get_product_details.invoke({"product_id": "abc"})
        assert "Error" in result or "Invalid" in result


class TestOrderSupportTools:
    def test_get_orders_by_customer(self):
        result = get_orders_by_customer.invoke({"customer_id": "5"})
        data = json.loads(result)
        assert len(data) >= 1
        assert "OrderId" in data[0]
        # Verify sorted by date DESC
        dates = [d["OrderDate"] for d in data]
        assert dates == sorted(dates, reverse=True)

    def test_get_orders_no_customer(self):
        result = get_orders_by_customer.invoke({"customer_id": "99999"})
        assert "No orders found" in result

    def test_get_employee_by_order(self):
        # First get an order for customer 5
        orders = json.loads(
            get_orders_by_customer.invoke({"customer_id": "5"})
        )
        order_id = str(orders[0]["OrderId"])
        result = get_employee_by_order_and_customer.invoke(
            {"order_id": order_id, "customer_id": "5"}
        )
        data = json.loads(result)
        assert len(data) >= 1
        assert "FirstName" in data[0]

    def test_get_order_details(self):
        orders = json.loads(
            get_orders_by_customer.invoke({"customer_id": "5"})
        )
        order_id = str(orders[0]["OrderId"])
        result = get_order_details.invoke(
            {"order_id": order_id, "customer_id": "5"}
        )
        data = json.loads(result)
        assert len(data) >= 1
        assert "ProductName" in data[0]
        assert "Quantity" in data[0]
