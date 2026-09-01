from langchain_core.tools import tool
from database import get_connection

@tool
def get_order_status(order_id:str)->dict:
    """
    Retrieve the current status and details of an order.

    Use this tool when the customer asks about a specific order and provides an order
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            order_id,
            customer_id,
            product,
            price,
            status,
            order_date,
            estimated_delivery
        FROM orders
        WHERE order_id = ?
    """, (order_id,))

    order = cursor.fetchone()

    connection.close()

    if order is None:
        return {
            "found": False,
            "message": f"Order {order_id} was not found."
        }

    return {
        "found": True,
        "order_id": order[0],
        "customer_id":order[1],
        "product": order[2],
        "price": order[3],
        "status": order[4],
        "order_date": order[5],
        "estimated_delivery": order[6]
    }

if __name__ == "__main__":
    result = get_order_status.invoke({"order_id": "ORD001"})
    print(result)
