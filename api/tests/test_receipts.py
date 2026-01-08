"""
Integration tests for receipt endpoints
"""
import pytest
import io
from datetime import datetime, timedelta
from jose import jwt
from pathlib import Path

from api.config import settings
from api.models import User, Receipt, Store, LineItem, ParseStatus


@pytest.fixture
def authenticated_user(db_session):
    """Create a test user and return user with session token"""
    user = User(email="testuser@example.com")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    
    # Create session token
    expire = datetime.utcnow() + timedelta(days=30)
    token = jwt.encode(
        {"sub": str(user.id), "email": user.email, "exp": expire, "type": "session"},
        settings.secret_key,
        algorithm=settings.algorithm
    )
    
    return {"user": user, "token": token}


def test_upload_receipt_text_file(client, authenticated_user, tmp_path):
    """Test uploading a text receipt file"""
    # Create test receipt content
    receipt_content = """Whole Foods Market
123 Main St
Date: 01/15/2024

Organic Bananas    1.99
Almond Milk        3.49
Whole Wheat Bread  4.29

Total: 9.77"""
    
    # Create file-like object
    file_data = io.BytesIO(receipt_content.encode())
    
    response = client.post(
        "/api/receipts/upload",
        headers={"Authorization": f"Bearer {authenticated_user['token']}"},
        files={"file": ("receipt.txt", file_data, "text/plain")}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "receipt_id" in data
    assert "status" in data


def test_upload_invalid_file_format(client, authenticated_user):
    """Test that invalid file formats are rejected"""
    file_data = io.BytesIO(b"test content")
    
    response = client.post(
        "/api/receipts/upload",
        headers={"Authorization": f"Bearer {authenticated_user['token']}"},
        files={"file": ("receipt.doc", file_data, "application/msword")}
    )
    
    assert response.status_code == 400
    assert "JPEG, PNG, PDF, or text file" in response.json()["detail"]


def test_upload_without_authentication(client):
    """Test that upload requires authentication"""
    file_data = io.BytesIO(b"test content")
    
    response = client.post(
        "/api/receipts/upload",
        files={"file": ("receipt.txt", file_data, "text/plain")}
    )
    
    assert response.status_code == 422  # Missing required header


def test_list_receipts_empty(client, authenticated_user):
    """Test listing receipts when user has none"""
    response = client.get(
        "/api/receipts",
        headers={"Authorization": f"Bearer {authenticated_user['token']}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["receipts"] == []
    assert data["total"] == 0


def test_list_receipts_with_data(client, authenticated_user, db_session):
    """Test listing receipts with data"""
    user = authenticated_user["user"]
    
    # Create store
    store = Store(name="Test Store", normalized_name="test store")
    db_session.add(store)
    db_session.commit()
    
    # Create receipts
    for i in range(3):
        receipt = Receipt(
            user_id=user.id,
            store_id=store.id,
            original_file_path=f"test/receipt_{i}.txt",
            parse_status=ParseStatus.SUCCESS,
            total_amount=10.00 + i,
            purchase_date=datetime.now().date()
        )
        db_session.add(receipt)
    
    db_session.commit()
    
    response = client.get(
        "/api/receipts",
        headers={"Authorization": f"Bearer {authenticated_user['token']}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["receipts"]) == 3
    assert data["total"] == 3


def test_list_receipts_pagination(client, authenticated_user, db_session):
    """Test receipt listing pagination"""
    user = authenticated_user["user"]
    
    # Create 10 receipts
    for i in range(10):
        receipt = Receipt(
            user_id=user.id,
            original_file_path=f"test/receipt_{i}.txt",
            parse_status=ParseStatus.SUCCESS
        )
        db_session.add(receipt)
    
    db_session.commit()
    
    # Test first page
    response = client.get(
        "/api/receipts?limit=5&offset=0",
        headers={"Authorization": f"Bearer {authenticated_user['token']}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["receipts"]) == 5
    assert data["total"] == 10
    assert data["limit"] == 5
    assert data["offset"] == 0
    
    # Test second page
    response = client.get(
        "/api/receipts?limit=5&offset=5",
        headers={"Authorization": f"Bearer {authenticated_user['token']}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["receipts"]) == 5


def test_user_can_only_see_own_receipts(client, db_session):
    """Test that users can only access their own receipts"""
    # Create two users
    user1 = User(email="user1@example.com")
    user2 = User(email="user2@example.com")
    db_session.add_all([user1, user2])
    db_session.commit()
    
    # Create receipts for user1
    receipt1 = Receipt(
        user_id=user1.id,
        original_file_path="user1/receipt.txt",
        parse_status=ParseStatus.SUCCESS
    )
    db_session.add(receipt1)
    db_session.commit()
    
    # Create token for user2
    expire = datetime.utcnow() + timedelta(days=30)
    token2 = jwt.encode(
        {"sub": str(user2.id), "email": user2.email, "exp": expire, "type": "session"},
        settings.secret_key,
        algorithm=settings.algorithm
    )
    
    # User2 tries to access user1's receipt
    response = client.get(
        f"/api/receipts/{receipt1.id}",
        headers={"Authorization": f"Bearer {token2}"}
    )
    
    assert response.status_code == 404


def test_get_receipt_detail(client, authenticated_user, db_session):
    """Test getting receipt details with line items"""
    user = authenticated_user["user"]
    
    # Create store
    store = Store(name="Test Store", normalized_name="test store")
    db_session.add(store)
    db_session.commit()
    
    # Create receipt
    receipt = Receipt(
        user_id=user.id,
        store_id=store.id,
        original_file_path="test/receipt.txt",
        parse_status=ParseStatus.SUCCESS,
        total_amount=10.00,
        purchase_date=datetime.now().date()
    )
    db_session.add(receipt)
    db_session.commit()
    
    # Add line items
    line_item = LineItem(
        receipt_id=receipt.id,
        product_name="Test Product",
        normalized_product_name="test product",
        total_price=5.00,
        line_number=1
    )
    db_session.add(line_item)
    db_session.commit()
    
    response = client.get(
        f"/api/receipts/{receipt.id}",
        headers={"Authorization": f"Bearer {authenticated_user['token']}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["receipt_id"] == str(receipt.id)
    assert data["store_name"] == "Test Store"
    assert len(data["line_items"]) == 1
    assert data["line_items"][0]["product_name"] == "Test Product"


def test_get_nonexistent_receipt(client, authenticated_user):
    """Test getting a receipt that doesn't exist"""
    import uuid
    fake_id = uuid.uuid4()
    
    response = client.get(
        f"/api/receipts/{fake_id}",
        headers={"Authorization": f"Bearer {authenticated_user['token']}"}
    )
    
    assert response.status_code == 404
