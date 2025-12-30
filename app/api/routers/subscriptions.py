"""Subscription API routes."""
import sqlite3
from typing import List

from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import (
    get_db,
    get_subscription_instance_service,
    get_subscription_service,
)
from app.api.schemas import (
    MarkInstancePaid,
    SubscriptionCreate,
    SubscriptionInstanceResponse,
    SubscriptionResponse,
)


router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])


@router.post("/", response_model=SubscriptionResponse)
def create_subscription(
    sub_data: SubscriptionCreate,
    conn: sqlite3.Connection = Depends(get_db)
):
    service = get_subscription_service(conn=conn)
    subscription = service.create_subscription(
        name=sub_data.name,
        subscription_type=sub_data.type,
        frequency=sub_data.frequency,
        due_day=sub_data.due_day,
        expected_amount=sub_data.expected_amount,
        start_date=sub_data.start_date,
        end_date=sub_data.end_date,
        notes=sub_data.notes,
        generate_instances=sub_data.generate_instances
    )
    return SubscriptionResponse(
        id=subscription.id,
        name=subscription.name,
        type=subscription.type,
        frequency=subscription.frequency,
        due_day=subscription.due_day,
        expected_amount=subscription.expected_amount,
        start_date=subscription.start_date,
        end_date=subscription.end_date,
        notes=subscription.notes
    )


@router.get("/", response_model=List[SubscriptionResponse])
def list_subscriptions(conn: sqlite3.Connection = Depends(get_db)):
    service = get_subscription_service(conn=conn)
    subscriptions = service.list_subscriptions()
    return [
        SubscriptionResponse(
            id=sub.id,
            name=sub.name,
            type=sub.type,
            frequency=sub.frequency,
            due_day=sub.due_day,
            expected_amount=sub.expected_amount,
            start_date=sub.start_date,
            end_date=sub.end_date,
            notes=sub.notes
        )
        for sub in subscriptions
    ]


@router.get("/active", response_model=List[SubscriptionResponse])
def list_active_subscriptions(conn: sqlite3.Connection = Depends(get_db)):
    service = get_subscription_service(conn=conn)
    subscriptions = service.list_active_subscriptions()
    return [
        SubscriptionResponse(
            id=sub.id,
            name=sub.name,
            type=sub.type,
            frequency=sub.frequency,
            due_day=sub.due_day,
            expected_amount=sub.expected_amount,
            start_date=sub.start_date,
            end_date=sub.end_date,
            notes=sub.notes
        )
        for sub in subscriptions
    ]


@router.get("/instances/due", response_model=List[SubscriptionInstanceResponse])
def list_due_instances(conn: sqlite3.Connection = Depends(get_db)):
    service = get_subscription_instance_service(conn=conn)
    instances = service.list_due_instances()
    return [
        SubscriptionInstanceResponse(
            id=inst.id,
            subscription_id=inst.subscription_id,
            period=inst.period,
            due_date=inst.due_date,
            amount=inst.amount,
            status=inst.status,
            paid_date=inst.paid_date
        )
        for inst in instances
    ]


@router.post("/instances/{instance_id}/mark-paid")
def mark_instance_paid(
    instance_id: str,
    data: MarkInstancePaid,
    conn: sqlite3.Connection = Depends(get_db)
):
    service = get_subscription_instance_service(conn=conn)
    service.mark_as_paid(
        instance_id=instance_id,
        paid_date=data.paid_date,
        actual_amount=data.actual_amount
    )
    return {"message": "Instance marked as paid"}


@router.post("/instances/{instance_id}/mark-due")
def mark_instance_due(
    instance_id: str,
    conn: sqlite3.Connection = Depends(get_db)
):
    service = get_subscription_instance_service(conn=conn)
    service.mark_as_due(instance_id=instance_id)
    return {"message": "Instance marked as due"}

@router.get("/export/csv")
def export_subscriptions_csv(conn: sqlite3.Connection = Depends(get_db)):
    """Export all subscriptions to CSV format"""
    import csv
    from io import StringIO
    from fastapi.responses import Response
    
    service = get_subscription_service(conn=conn)
    subscriptions = service.list_subscriptions()
    
    output = StringIO()
    writer = csv.writer(output)
    
    writer.writerow(['name', 'type', 'frequency', 'due_day', 'expected_amount', 'start_date', 'end_date', 'notes'])
    
    for sub in subscriptions:
        writer.writerow([
            sub.name,
            sub.type,
            sub.frequency,
            sub.due_day,
            sub.expected_amount,
            sub.start_date,
            sub.end_date if sub.end_date else '',
            sub.notes if sub.notes else ''
        ])
    
    return Response(content=output.getvalue(), media_type="text/csv")


@router.post("/import/csv")
def import_subscriptions_csv(
    file_data: dict,
    conn: sqlite3.Connection = Depends(get_db)
):
    """Import subscriptions from CSV format"""
    import csv
    from io import StringIO
    from decimal import Decimal
    from datetime import datetime
    
    service = get_subscription_service(conn=conn)
    csv_content = file_data.get('file_content', '')
    
    reader = csv.DictReader(StringIO(csv_content))
    
    created = 0
    errors = []
    
    for row_num, row in enumerate(reader, start=2):
        try:
            name = row.get('name', '').strip()
            sub_type = row.get('type', '').strip().upper()
            frequency = row.get('frequency', '').strip().upper()
            due_day = int(row.get('due_day', 0))
            expected_amount = Decimal(str(row.get('expected_amount', 0)))
            start_date_str = row.get('start_date', '').strip()
            end_date_str = row.get('end_date', '').strip()
            notes = row.get('notes', '').strip() or None
            
            if not name:
                errors.append(f"Row {row_num}: Name is required")
                continue
            
            if sub_type not in ['BILL', 'INSURANCE', 'OTHER']:
                errors.append(f"Row {row_num}: Invalid type. Must be one of BILL, INSURANCE, OTHER")
                continue
            
            if frequency not in ['MONTHLY', 'YEARLY']:
                errors.append(f"Row {row_num}: Frequency must be MONTHLY or YEARLY")
                continue
            
            if due_day < 1 or due_day > 31:
                errors.append(f"Row {row_num}: Due day must be between 1 and 31")
                continue
            
            if expected_amount <= 0:
                errors.append(f"Row {row_num}: Expected amount must be positive")
                continue
            
            start_date = datetime.fromisoformat(start_date_str).date()
            end_date = datetime.fromisoformat(end_date_str).date() if end_date_str else None
            
            service.create_subscription(
                name=name,
                subscription_type=sub_type,  # type: ignore
                frequency=frequency,  # type: ignore
                due_day=due_day,
                expected_amount=expected_amount,
                start_date=start_date,
                end_date=end_date,
                notes=notes,
                generate_instances=True
            )
            created += 1
            
        except Exception as e:
            errors.append(f"Row {row_num}: {str(e)}")
    
    return {
        "created": created,
        "errors": errors,
        "total_rows": created + len(errors)
    }

# Made with Bob
