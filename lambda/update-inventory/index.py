import json
import boto3
from datetime import datetime, timezone
import os
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# INVENTORY_TABLE=os.environ["INVENTORY_TABLE"]
EVENT_BUS = os.environ["EVENT_BUS"]

dynamodb = boto3.resource("dynamodb")
# inventory_table = dynamodb.Table(INVENTORY_TABLE)
eventbridge = boto3.client("events")

def lambda_handler(event, context):
    logger.info("Inside update-inventory lambda function")
    logger.info("Received event: %s", json.dumps(event))

    for record in event["Records"]:
        body = json.loads(record["body"])
        detail = body["detail"]

        order_id = detail["order_id"]
        items = detail.get("items", [])

        logger.info(f"Updating inventory for order {order_id}")

        for item in items:
            product_id = item["product_id"]
            quantity = item["quantity"]

            logger.info(
                "Would update inventory for product_id=%s quantity=%s",
                product_id,
                quantity
            )

            # inventory_table.update_item(
            #     Key={"product_id": product_id},
            #     UpdateExpression="SET stock = stock - :qty",
            #     ConditionExpression="stock >= :qty",
            #     ExpressionAttributeValues={
            #         ":qty": quantity
            #     }
            # )

        eventbridge.put_events(
            Entries=[
                {
                    "Source": "ecommerce.inventory",
                    "DetailType": "InventoryUpdated",
                    "Detail": json.dumps({
                        "order_id": order_id,
                        "updated_at": datetime.now(timezone.utc).isoformat()
                    }),
                    "EventBusName": EVENT_BUS
                }
            ]
        )

    return {
        "statusCode": 200,
        "body": json.dumps({
            "order_id": order_id,
            "status": "INVENTORY_UPDATED"
        })
    }