from mock_crm.app import CUSTOMERS
import boto3
from decimal import Decimal
import json

dynamodb = boto3.resource(
    "dynamodb",
    region_name="ap-south-1"
)

table = dynamodb.Table("Customers")

for customer in CUSTOMERS.values():

    # Convert all floats to Decimal
    item = json.loads(
        json.dumps(customer),
        parse_float=Decimal
    )

    table.put_item(Item=item)

    print(f"Inserted {customer['customer_id']}")

print("Finished loading customers.")