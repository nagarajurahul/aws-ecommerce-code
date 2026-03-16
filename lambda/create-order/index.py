import json
import boto3
import uuid
from datetime import datetime

dynamodb = boto3.resource("dynamodb")
eventbridge = boto3.client("events")

table = dynamodb.Table("orders")

def lambda_handler(event, context):

    body = json.loads(event["body"])

    user_id = body["user_id"]
    items = body["items"]

    order_id = str(uuid.uuid4())

    total_amount = sum(item["price"] * item["quantity"] for item in items)

    order = {
        "order_id": order_id,
        "user_id": user_id,
        "items": items,
        "total_amount": total_amount,
        "status": "PENDING_PAYMENT",
        "created_at": datetime.utcnow().isoformat()
    }

    table.put_item(Item=order)

    # eventbridge.put_events(
    #     Entries=[
    #         {
    #             "Source": "ecommerce.orders",
    #             "DetailType": "OrderPlaced",
    #             "Detail": json.dumps(order),
    #             "EventBusName": "default"
    #         }
    #     ]
    # )

    return {
        "statusCode": 201,
        "body": json.dumps({
            "order_id": order_id,
            "status": "PENDING_PAYMENT"
        })
    }