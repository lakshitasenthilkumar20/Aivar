import json
import requests

from auth import decode_token
from permissions import is_allowed
from audit import (
    log_event,
    count_recent_denied_attempts,
    create_security_alert
)

CRM_BASE_URL = "http://host.docker.internal:3000"


def lambda_handler(event, context):

    # -----------------------------
    # Authentication
    # -----------------------------
    headers = event.get("headers", {})

    auth_header = (
    headers.get("Authorization")
    or headers.get("authorization")
)

    if not auth_header:
        return {
            "statusCode": 401,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": json.dumps({
                "status": "DENIED",
                "reason": "Missing Authorization header",
                "role": None,
                "data": None
            })
        }
    token = auth_header.replace("Bearer ", "")

    try:
        payload = decode_token(token)
    except Exception:
        return {
            "statusCode": 401,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": json.dumps({
                "status": "DENIED",
                "reason": "Invalid JWT",
                "role": None,
                "data": None
            })
        }

    user = payload["user"]
    role = payload["role"]

    # -----------------------------
    # Request Details
    # -----------------------------
    method = event["httpMethod"]

    path = event.get("pathParameters", {}).get("proxy")

    if not path:
        return {
            "statusCode":400,
            "body":json.dumps({
                "status":"ERROR",
                "reason":"Missing proxy path."
            })
        }

    query_params = event.get("queryStringParameters") or {}

    resource = path

    if query_params:
        resource += "?" + "&".join(
            f"{k}={v}" for k, v in query_params.items()
        )

    # -----------------------------
    # Map HTTP Method to Permission
    # -----------------------------
    if method == "GET":
        tool = "GET_CUSTOMER"

    elif method == "PUT":
        tool = "UPDATE_CUSTOMER"

    elif method == "DELETE":
        tool = "DELETE_CUSTOMER"

    else:
        return {
            "statusCode": 405,
            "body": json.dumps({
                "message": "Method Not Allowed"
            })
        }

    # -----------------------------
    # Authorization
    # -----------------------------
    if not is_allowed(role, tool):

        log_event(
            user=user,
            role=role,
            tool=tool,
            resource=resource,
            status="DENIED",
            reason="Role does not have permission"
        )

        denied = count_recent_denied_attempts(user)

        if denied >= 3:

            create_security_alert(
                user=user,
                role=role,
                tool=tool,
                resource=resource,
                denied_count=denied
            )

            print(
                f"SECURITY ALERT: {user} has {denied} denied attempts."
            )

        return {
            "statusCode":403,
            "headers":{
                "Content-Type":"application/json"
            },
            "body":json.dumps({

                "status":"DENIED",

                "reason":f"{tool} is not permitted for {role}",

                "role":role,

                "data":None

            })
        }

    # -----------------------------
    # Forward Request to CRM
    # -----------------------------
    url = f"{CRM_BASE_URL}/crm/{path}"

    if method == "GET":

        response = requests.get(
            url,
            params=query_params
        )

    elif method == "PUT":

        body = json.loads(event.get("body") or "{}")

        response = requests.put(
            url,
            json=body
        )

    elif method == "DELETE":

        response = requests.delete(url)

    # -----------------------------
    # Audit Log
    # -----------------------------
    audit_status = "ALLOWED"
    audit_reason = None

    if response.status_code >= 400:
        audit_status = "FAILED"
        audit_reason = f"CRM returned {response.status_code}"

    log_event(
        user=user,
        role=role,
        tool=tool,
        resource=resource,
        status=audit_status,
        reason=audit_reason
    )

    # -----------------------------
    # Return CRM Response
    # -----------------------------
    try:
        crm_data = response.json()
        status = "ALLOWED"
        reason = "Permission granted"

        if response.status_code >= 400:
            status = "FAILED"
            reason = "CRM request failed"
    except Exception:
        crm_data = response.text

    return {

        "statusCode": response.status_code,

        "headers":{
            "Content-Type":"application/json"
        },

        "body":json.dumps({

            "status":"ALLOWED",

            "reason":"Permission granted",

            "role":role,

            "data":crm_data

        })

    }