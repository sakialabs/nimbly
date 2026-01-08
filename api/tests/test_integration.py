"""
End-to-end integration tests for complete workflows
"""
import pytest
import io
from datetime import datetime, timedelta
from jose import jwt

from api.config import settings
from api.models import User


def test_complete_auth_flow(client, db_session):
    """Test complete authentication flow: request → verify → authenticated request"""
    email = "workflow@example.com"
    
    # Step 1: Request magic link
    response = client.post(
        "/api/auth/request-magic-link",
        json={"email": email}
    )
    assert response.status_code == 200
    
    # Step 2: Create and verify magic link token
    expire = datetime.utcnow() + timedelta(seconds=900)
    magic_token = jwt.encode(
        {"sub": email, "exp": expire, "type": "magic_link"},
        settings.secret_key,
        algorithm=settings.algorithm
    )
    
    response = client.get(f"/api/auth/verify?token={magic_token}")
    assert response.status_code == 200
    data = response.json()
    session_token = data["session_token"]
    
    # Step 3: Use session token for authenticated request
    response = client.get(
        "/api/receipts",
        headers={"Authorization": f"Bearer {session_token}"}
    )
    assert response.status_code == 200


def test_complete_receipt_workflow(client, db_session):
    """Test complete receipt workflow: upload → parse → retrieve details"""
    # Create user and token
    user = User(email="receiptflow@example.com")
    db_session.add(user)
    db_session.commit()
    
    expire = datetime.utcnow() + timedelta(days=30)
    token = jwt.encode(
        {"sub": str(user.id), "email": user.email, "exp": expire, "type": "session"},
        settings.secret_key,
        algorithm=settings.algorithm
    )
    
    # Step 1: Upload receipt
    receipt_content = """Whole Foods Market
Date: 01/15/2024

Organic Bananas    1.99
Almond Milk        3.49

Total: 5.48"""
    
    file_data = io.BytesIO(receipt_content.encode())
    
    response = client.post(
        "/api/receipts/upload",
        headers={"Authorization": f"Bearer {token}"},
        files={"file": ("receipt.txt", file_data, "text/plain")}
    )
    assert response.status_code == 200
    receipt_id = response.json()["receipt_id"]
    
    # Step 2: List receipts
    response = client.get(
        "/api/receipts",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    receipts = response.json()["receipts"]
    assert len(receipts) == 1
    assert receipts[0]["receipt_id"] == receipt_id
    
    # Step 3: Get receipt details
    response = client.get(
        f"/api/receipts/{receipt_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    details = response.json()
    assert details["receipt_id"] == receipt_id
    assert "line_items" in details


def test_complete_insights_workflow(client, db_session):
    """Test complete insights workflow: upload multiple receipts → generate insights"""
    from api.models import Store, Receipt, LineItem, PriceHistory, ParseStatus
    from decimal import Decimal
    
    # Create user
    user = User(email="insightflow@example.com")
    db_session.add(user)
    db_session.commit()
    
    expire = datetime.utcnow() + timedelta(days=30)
    token = jwt.encode(
        {"sub": str(user.id), "email": user.email, "exp": expire, "type": "session"},
        settings.secret_key,
        algorithm=settings.algorithm
    )
    
    # Create store
    store = Store(name="Test Store", normalized_name="test store")
    db_session.add(store)
    db_session.commit()
    
    # Create multiple receipts with line items
    base_date = datetime.now() - timedelta(days=30)
    
    for i in range(6):
        purchase_date = base_date + timedelta(days=i * 5)
        
        receipt = Receipt(
            user_id=user.id,
            store_id=store.id,
            original_file_path=f"test/receipt_{i}.txt",
            parse_status=ParseStatus.SUCCESS,
            purchase_date=purchase_date.date(),
            total_amount=Decimal("15.00")
        )
        db_session.add(receipt)
        db_session.flush()
        
        # Add line items
        products = [
            ("Bananas", Decimal("1.99")),
            ("Milk", Decimal("3.49")),
            ("Bread", Decimal("2.99"))
        ]
        
        for idx, (product_name, price) in enumerate(products):
            line_item = LineItem(
                receipt_id=receipt.id,
                product_name=product_name,
                normalized_product_name=product_name.lower(),
                total_price=price,
                line_number=idx + 1
            )
            db_session.add(line_item)
            db_session.flush()
            
            # Create price history
            price_history = PriceHistory(
                product_name=product_name.lower(),
                store_id=store.id,
                price=price,
                observed_date=purchase_date.date(),
                source_line_item_id=line_item.id
            )
            db_session.add(price_history)
    
    db_session.commit()
    
    # Generate insights
    response = client.get(
        "/api/insights",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["insights"]) > 0
    
    # Verify we have different insight types
    insight_types = {insight["type"] for insight in data["insights"]}
    assert "purchase_frequency" in insight_types
    assert "common_purchase" in insight_types


def test_multi_user_isolation(client, db_session):
    """Test that multiple users' data remains isolated"""
    from api.models import Store, Receipt, ParseStatus
    
    # Create two users
    user1 = User(email="user1@isolation.com")
    user2 = User(email="user2@isolation.com")
    db_session.add_all([user1, user2])
    db_session.commit()
    
    # Create tokens
    expire = datetime.utcnow() + timedelta(days=30)
    token1 = jwt.encode(
        {"sub": str(user1.id), "email": user1.email, "exp": expire, "type": "session"},
        settings.secret_key,
        algorithm=settings.algorithm
    )
    token2 = jwt.encode(
        {"sub": str(user2.id), "email": user2.email, "exp": expire, "type": "session"},
        settings.secret_key,
        algorithm=settings.algorithm
    )
    
    # Create store
    store = Store(name="Test Store", normalized_name="test store")
    db_session.add(store)
    db_session.commit()
    
    # Create receipts for user1
    for i in range(3):
        receipt = Receipt(
            user_id=user1.id,
            store_id=store.id,
            original_file_path=f"user1/receipt_{i}.txt",
            parse_status=ParseStatus.SUCCESS
        )
        db_session.add(receipt)
    
    # Create receipts for user2
    for i in range(2):
        receipt = Receipt(
            user_id=user2.id,
            store_id=store.id,
            original_file_path=f"user2/receipt_{i}.txt",
            parse_status=ParseStatus.SUCCESS
        )
        db_session.add(receipt)
    
    db_session.commit()
    
    # User1 should see only their receipts
    response = client.get(
        "/api/receipts",
        headers={"Authorization": f"Bearer {token1}"}
    )
    assert response.status_code == 200
    assert response.json()["total"] == 3
    
    # User2 should see only their receipts
    response = client.get(
        "/api/receipts",
        headers={"Authorization": f"Bearer {token2}"}
    )
    assert response.status_code == 200
    assert response.json()["total"] == 2
