"""Order support tools for the Arihant Healthcare system."""

import logging
from langchain_core.tools import tool
from src.db.database import run_query_safe

logger = logging.getLogger(__name__)


def _safe_int(value: str, label: str = "value") -> int:
    try:
        return int(value)
    except (ValueError, TypeError):
        raise ValueError(f"Invalid {label}: '{value}'. Please provide a numeric value.")


@tool
def get_orders_by_customer(customer_id: str) -> str:
    """
    Get all orders for a specific customer, sorted by OrderDate DESC.
    Returns OrderId, OrderDate, Status, and TotalAmount.
    """
    logger.info(f"TOOL_CALL: get_orders_by_customer | customer_id={customer_id}")
    try:
        result = run_query_safe(
            """
            SELECT OrderId, OrderDate, Status, TotalAmount
            FROM Orders
            WHERE CustomerId = :customer_id
            ORDER BY OrderDate DESC;
            """,
            {"customer_id": _safe_int(customer_id, "customer ID")},
        )
        logger.info(f"TOOL_RESULT: get_orders_by_customer | result_length={len(result)}")
        if result == "[]":
            return f"No orders found for customer ID: {customer_id}"
        return result
    except Exception as e:
        logger.error(f"Error in get_orders_by_customer: {e}")
        return f"Error looking up orders for customer '{customer_id}'. Please try again."


@tool
def get_order_details(order_id: str, customer_id: str) -> str:
    """
    Get detailed line items for a specific order belonging to a specific customer.
    Returns ProductName, Quantity, UnitPrice for the given order.
    """
    logger.info(f"TOOL_CALL: get_order_details | order_id={order_id} | customer_id={customer_id}")
    try:
        result = run_query_safe(
            """
            SELECT Product.Name AS ProductName,
                   OrderLine.Quantity,
                   OrderLine.UnitPrice
            FROM OrderLine
            JOIN Orders ON OrderLine.OrderId = Orders.OrderId
            JOIN Product ON OrderLine.ProductId = Product.ProductId
            WHERE Orders.OrderId = :order_id AND Orders.CustomerId = :customer_id;
            """,
            {
                "order_id": _safe_int(order_id, "order ID"),
                "customer_id": _safe_int(customer_id, "customer ID"),
            },
        )
        logger.info(f"TOOL_RESULT: get_order_details | result_length={len(result)}")
        if result == "[]":
            return f"No order items found for Order ID {order_id} belonging to Customer ID {customer_id}."
        return result
    except Exception as e:
        logger.error(f"Error in get_order_details: {e}")
        return f"Error looking up details for order '{order_id}'. Please try again."


@tool
def get_employee_by_order_and_customer(order_id: str, customer_id: str) -> str:
    """
    Get the support representative or employee assigned to a specific order for a customer.
    """
    logger.info(f"TOOL_CALL: get_employee_by_order_and_customer | order_id={order_id} | customer_id={customer_id}")
    try:
        result = run_query_safe(
            """
            SELECT Employee.FirstName, Employee.LastName, Employee.Title, Employee.Email
            FROM Orders
            JOIN Employee ON Orders.EmployeeId = Employee.EmployeeId
            WHERE Orders.OrderId = :order_id AND Orders.CustomerId = :customer_id;
            """,
            {
                "order_id": _safe_int(order_id, "order ID"),
                "customer_id": _safe_int(customer_id, "customer ID"),
            },
        )
        logger.info(f"TOOL_RESULT: get_employee_by_order_and_customer | result_length={len(result)}")
        if result == "[]":
            return f"No support representative found for Order ID {order_id} belonging to Customer ID {customer_id}."
        return result
    except Exception as e:
        logger.error(f"Error in get_employee_by_order: {e}")
        return f"Error looking up employee for order '{order_id}'. Please try again."


order_support_tools = [
    get_orders_by_customer,
    get_order_details,
    get_employee_by_order_and_customer,
]
