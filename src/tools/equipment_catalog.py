"""Equipment catalog tools for the Arihant Healthcare system."""

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
def get_products_by_category(category_name: str) -> str:
    """
    Get products belonging to a specific category (e.g. 'Respiratory', 'ICU', 'Consumables').
    Uses fuzzy matching on category name.
    """
    logger.info(f"TOOL_CALL: get_products_by_category | category={category_name}")
    try:
        result = run_query_safe(
            """
            SELECT Product.ProductId, Product.Name AS ProductName, ProductCategory.Name AS CategoryName, Product.Price, Product.StockQuantity
            FROM Product
            JOIN ProductCategory ON Product.CategoryId = ProductCategory.CategoryId
            WHERE ProductCategory.Name LIKE :pattern
            ORDER BY Product.Name;
            """,
            {"pattern": f"%{category_name}%"},
        )
        logger.info(f"TOOL_RESULT: get_products_by_category | result_length={len(result)}")
        if result == "[]":
            return f"No products found in category: {category_name}"
        return result
    except Exception as e:
        logger.error(f"Error in get_products_by_category: {e}")
        return f"Error looking up category '{category_name}'. Please try again."


@tool
def search_products_by_name(product_name: str) -> str:
    """
    Search for a product by its name using fuzzy matching (e.g. 'Oxygen Concentrator', 'BiPAP').
    Returns a list of matching products with their Price and Stock availability.
    """
    logger.info(f"TOOL_CALL: search_products_by_name | product_name={product_name}")
    try:
        result = run_query_safe(
            """
            SELECT Product.ProductId,
                   Product.Name AS ProductName,
                   ProductCategory.Name AS CategoryName,
                   Product.Price,
                   Product.StockQuantity
            FROM Product
            JOIN ProductCategory ON Product.CategoryId = ProductCategory.CategoryId
            WHERE Product.Name LIKE :pattern
            ORDER BY Product.Name
            LIMIT 10;
            """,
            {"pattern": f"%{product_name}%"},
        )
        logger.info(f"TOOL_RESULT: search_products_by_name | result_length={len(result)}")
        if result == "[]":
            return f"No products found matching: {product_name}"
        return result
    except Exception as e:
        logger.error(f"Error in search_products_by_name: {e}")
        return f"Error looking up product '{product_name}'. Please try again."


@tool
def get_product_details(product_id: str) -> str:
    """
    Get complete details for a specific product by its ProductId, including description.
    """
    logger.info(f"TOOL_CALL: get_product_details | product_id={product_id}")
    try:
        result = run_query_safe(
            """
            SELECT Product.ProductId,
                   Product.Name AS ProductName,
                   ProductCategory.Name AS CategoryName,
                   Product.Description,
                   Product.Price,
                   Product.StockQuantity
            FROM Product
            LEFT JOIN ProductCategory ON Product.CategoryId = ProductCategory.CategoryId
            WHERE Product.ProductId = :product_id;
            """,
            {"product_id": _safe_int(product_id, "product ID")},
        )
        logger.info(f"TOOL_RESULT: get_product_details | result_length={len(result)}")
        if result == "[]":
            return f"No product found with ProductId: {product_id}"
        return result
    except Exception as e:
        logger.error(f"Error in get_product_details: {e}")
        return f"Error looking up product {product_id}. Please try again."


equipment_tools = [
    get_products_by_category,
    search_products_by_name,
    get_product_details,
]
