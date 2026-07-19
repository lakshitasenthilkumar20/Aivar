import json
import boto3
import os
from decimal import Decimal
from boto3.dynamodb.conditions import Attr

dynamodb = boto3.resource("dynamodb")

table = dynamodb.Table(
    os.environ["CUSTOMERS_TABLE"]
)

def lambda_handler(event, context):

    method = event["httpMethod"]

    if method == "GET":
        return get_customer(event)

    elif method == "PUT":
        return update_customer(event)

    elif method == "DELETE":
        return delete_customer(event)

    return {
        "statusCode": 405,
        "body": json.dumps({"message": "Method Not Allowed"})
    }


def get_customer(event):

    path_parameters = event.get("pathParameters") or {}
    query_parameters = event.get("queryStringParameters") or {}

    customer_id = path_parameters.get("id")

    # Get one customer
    if customer_id:

        response = table.get_item(
            Key={
                "customer_id": customer_id
            }
        )

        customer = response.get("Item")

        if customer:

            return {
                "statusCode": 200,
                "body": json.dumps(customer, default=str)
            }

        return {
            "statusCode": 404,
            "body": json.dumps({
                "message": "Customer not found"
            })
        }

    # List / Filter customers
    if query_parameters:

        filter_expression = None

        for key, value in query_parameters.items():

            condition = Attr(key).eq(value)

            if filter_expression is None:
                filter_expression = condition
            else:
                filter_expression &= condition

        response = table.scan(
            FilterExpression=filter_expression
        )

    else:

        response = table.scan()

    return {
        "statusCode": 200,
        "body": json.dumps(
            response.get("Items", []),
            default=str
        )
    }

def update_customer(event):

    customer_id = event["pathParameters"]["id"]

    updates = json.loads(event["body"])

    update_expression = "SET "
    expression_values = {}
    expression_names = {}

    parts = []

    for key, value in updates.items():

        parts.append(f"#{key}=:{key}")

        expression_names[f"#{key}"] = key

        if isinstance(value, float):
            value = Decimal(str(value))

        expression_values[f":{key}"] = value

    update_expression += ", ".join(parts)

    response = table.update_item(
        Key={
            "customer_id": customer_id
        },
        UpdateExpression=update_expression,
        ExpressionAttributeNames=expression_names,
        ExpressionAttributeValues=expression_values,
        ReturnValues="ALL_NEW"
    )

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "Customer updated successfully",
            "customer": response["Attributes"]
        }, default=str)
    }

def delete_customer(event):

    customer_id = event["pathParameters"]["id"]

    response = table.delete_item(
        Key={
            "customer_id": customer_id
        },
        ReturnValues="ALL_OLD"
    )

    if "Attributes" not in response:

        return {
            "statusCode": 404,
            "body": json.dumps({
                "message": "Customer not found"
            })
        }

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": f"Customer {customer_id} deleted successfully"
        })
    }