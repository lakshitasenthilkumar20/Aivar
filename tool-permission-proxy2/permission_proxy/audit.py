import os
import uuid
import boto3

from datetime import datetime, timedelta
from boto3.dynamodb.conditions import Attr

dynamodb = boto3.resource(
    "dynamodb",
    region_name="ap-south-1"
)

# Audit Logs table
audit_table = dynamodb.Table(
    os.environ.get("AUDIT_TABLE", "AuditLogs")
)

# Security Alerts table
alerts_table = dynamodb.Table(
    os.environ.get("SECURITY_ALERT_TABLE", "SecurityAlerts")
)


def log_event(user, role, tool, resource, status, reason=None):

    item = {
        "log_id": str(uuid.uuid4()),
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "user": user,
        "role": role,
        "tool": tool,
        "resource": resource,
        "status": status,
        "reason": reason
    }

    audit_table.put_item(Item=item)

    return item


def count_recent_denied_attempts(user, minutes=10):

    response = audit_table.scan(
        FilterExpression=
            Attr("user").eq(user) &
            Attr("status").eq("DENIED")
    )

    items = response.get("Items", [])

    cutoff = datetime.utcnow() - timedelta(minutes=minutes)

    count = 0

    for item in items:

        timestamp = item["timestamp"].replace("Z", "")

        log_time = datetime.fromisoformat(timestamp)

        if log_time >= cutoff:
            count += 1

    return count


def create_security_alert(
        user,
        role,
        tool,
        resource,
        denied_count,
        alert_type="REPEATED_DENIED_ACCESS"
):

    item = {
        "alert_id": str(uuid.uuid4()),
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "user": user,
        "role": role,
        "tool": tool,
        "resource": resource,
        "alert_type": alert_type,
        "denied_count": denied_count,
        "status": "OPEN"
    }

    alerts_table.put_item(Item=item)

    return item