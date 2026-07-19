import json
import os
import requests

from google import genai
from google.genai import types

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY environment variable is not set")

client = genai.Client(api_key=api_key)

get_customer_tool = types.FunctionDeclaration(
    name="GET_CUSTOMER",
    description="""
Retrieve customer information.

Use this tool whenever the user asks to:

- show customer
- find customer
- search customer
- display customer
- retrieve customer
- list customers

Search may be by:

customer_id
name
city
country
membership
occupation
account_status
""",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "customer_id": types.Schema(type=types.Type.STRING),
            "name": types.Schema(type=types.Type.STRING),
            "city": types.Schema(type=types.Type.STRING),
            "country": types.Schema(type=types.Type.STRING),
            "membership": types.Schema(type=types.Type.STRING),
            "occupation": types.Schema(type=types.Type.STRING),
            "account_status": types.Schema(type=types.Type.STRING)
        },
        required=[]
    )
)
update_customer_tool = types.FunctionDeclaration(
    name="UPDATE_CUSTOMER",
    description="""
Update customer information.

Examples:

Update customer 1004 city to Chennai

Change customer 1004's membership to Gold

Modify customer 1004 occupation to Doctor
""",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "customer_id": types.Schema(type=types.Type.STRING),

            "name": types.Schema(type=types.Type.STRING),

            "city": types.Schema(type=types.Type.STRING),

            "country": types.Schema(type=types.Type.STRING),

            "membership": types.Schema(type=types.Type.STRING),

            "occupation": types.Schema(type=types.Type.STRING),

            "account_status": types.Schema(type=types.Type.STRING)
        },
        required=["customer_id"]
    )
)
delete_customer_tool = types.FunctionDeclaration(
    name="DELETE_CUSTOMER",
    description="""
Delete a customer.

Examples

Delete customer 1004

Remove customer 1004
""",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "customer_id": types.Schema(
                type=types.Type.STRING
            )
        },
        required=["customer_id"]
    )
)
tool = types.Tool(
    function_declarations=[
        get_customer_tool,
        update_customer_tool,
        delete_customer_tool
    ]
)

PROXY_URL = "http://host.docker.internal:3000/proxy"



def lambda_handler(event, context):

    body = json.loads(event["body"])
    headers = event.get("headers", {})

    authorization = (
        headers.get("Authorization")
        or headers.get("authorization")
)
    query = body["prompt"]

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=query,
        config=types.GenerateContentConfig(

            system_instruction="""
        You are an AI CRM assistant.

        You NEVER answer CRM questions directly.

        Your only job is to select exactly one tool.

        Supported tools:

        GET_CUSTOMER

        UPDATE_CUSTOMER

        DELETE_CUSTOMER

        Examples:

        Show customer 1001
        → GET_CUSTOMER

        Find Gold members
        → GET_CUSTOMER

        Update customer 1004 city to Chennai
        → UPDATE_CUSTOMER

        Delete customer 1004
        → DELETE_CUSTOMER

        Never invent customer data.

        Always return a function call.
        """,

            tools=[tool]

        )
    )

    candidate = response.candidates[0]


    if not candidate.content.parts:
        return {
            "statusCode": 400,
            "body": json.dumps({"message": "Gemini returned no content."})
        }

    part = candidate.content.parts[0]

    if hasattr(part, "function_call") and part.function_call:

        print(part.function_call)

        
        

        args = dict(part.function_call.args)
        tool_name = part.function_call.name

        print("Selected Tool:", tool_name)

        print("Arguments:", args)
        print("Function arguments:", args)

        headers = {
            "Authorization": authorization,
            "Content-Type": "application/json"
        }

        # Search by customer ID
        if tool_name == "GET_CUSTOMER":

            if args.get("customer_id"):

                response = requests.get(
                    f"{PROXY_URL}/customers/{args['customer_id']}",
                    headers=headers
                )

            else:

                filters = {
                    k: v
                    for k, v in args.items()
                    if v is not None
                }

                response = requests.get(
                    f"{PROXY_URL}/customers",
                    params=filters,
                    headers=headers
                )

        elif tool_name == "UPDATE_CUSTOMER":

            customer_id = args.pop("customer_id")

            response = requests.put(
                f"{PROXY_URL}/customers/{customer_id}",
                json=args,
                headers=headers
            )

        elif tool_name == "DELETE_CUSTOMER":

            response = requests.delete(
                f"{PROXY_URL}/customers/{args['customer_id']}",
                headers=headers
            )

        else:

            return {
                "statusCode":400,
                "body":json.dumps({
                    "status":"ERROR",
                    "reason":"Unsupported tool."
                })
            }

            

        try:
            proxy_result = response.json()
        except Exception:
            proxy_result = {
                "status": "ERROR",
                "reason": response.text
    }

        return {

            "statusCode": response.status_code,

            "body": json.dumps({

                "intent": tool_name.replace("_", " ").title(),

                "tool": tool_name,

                "status": proxy_result.get("status"),

                "reason": proxy_result.get("reason"),

                "permission": proxy_result.get("role"),

                "result": proxy_result.get("data", proxy_result)

            })

        }

    print(response.text)
    print(candidate.content)
    return {
        "statusCode": 400,
        "body": json.dumps({
            "message": "No tool selected."
        })
    }
