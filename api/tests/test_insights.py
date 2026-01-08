"""
Integration tests for insight generation
"""
import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from jose import jwt

from api.config import settings
from api.models import User, Store, Receipt, LineItem, PriceHistory, ParseStatus


@pytest.fixture
def user_with_receipts(db_session):
    """Create a user with multiple receipts for insight generation"""
    user = User(email="insightuser@example.com")
    db_session.add(user)
    db_session.commit()
    
    # Create stores
    store1 = Store(name="Whole Foods", normalized_name="whole foods")
    store2 = Store(name="Trader Joe's", normalized_name="trader joes")
    db_session.add_all([store1, store2])
    db_session.commit()
    
    # Create receipts with line items
    base_date = datetime.now() - timedelta(days=60)
    
    for i in range(6):
        store = store1 if i % 2 == 0 else store2
        purchase_date = base_date + timedelta(days=i * 10)
        
        receipt = Receipt(
            user_id=user.id,
            store_id=store.id,
            original_file_path=f"test/receipt_{i}.txt",
            parse_status=ParseStatus.SUCCESS,
            purchase_date=purchase_date.date(),
            total_amount=Decimal("20.00")
        )
        db_session.add(receipt)
        db_session.flush()
        
        # Add line items
        products = [
            ("Organic Bananas", Decimal("1.99") + Decimal(str(i * 0.10))),
            ("Almond Milk", Decimal("3.49") + Decimal(str(i * 0.15))),
            ("Greek Yogurt", Decimal("1.29"))
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
    
    # Create session token
    expire = datetime.utcnow() + timedelta(days=30)
    token = jwt.encode(
        {"sub": str(user.id), "email": user.email, "exp": expire, "type": "session"},
        settings.secret_key,
        algorithm=settings.algorithm
    )
    
    return {"user": user, "token": token}


def test_insights_with_sufficient_data(client, user_with_receipts):
    """Test that insights are generated when sufficient data exists"""
    response = client.get(
        "/api/insights",
        headers={"Authorization": f"Bearer {user_with_receipts['token']}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "insights" in data
    assert len(data["insights"]) > 0
    
    # Verify insight structure
    for insight in data["insights"]:
        assert "type" in insight
        assert "title" in insight
        assert "description" in insight
        assert "data_points" in insight
        assert "confidence" in insight
        assert "underlying_data" in insight
        assert "generated_at" in insight


def test_insights_without_data(client, db_session):
    """Test that appropriate message is shown when insufficient data"""
    # Create user with no receipts
    user = User(email="newuser@example.com")
    db_session.add(user)
    db_session.commit()
    
    expire = datetime.utcnow() + timedelta(days=30)
    token = jwt.encode(
        {"sub": str(user.id), "email": user.email, "exp": expire, "type": "session"},
        settings.secret_key,
        algorithm=settings.algorithm
    )
    
    response = client.get(
        "/api/insights",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["insights"] == []
    assert "more receipts" in data["message"].lower()


def test_purchase_frequency_insight(client, user_with_receipts):
    """Test that purchase frequency insights are generated"""
    response = client.get(
        "/api/insights",
        headers={"Authorization": f"Bearer {user_with_receipts['token']}"}
    )
    
    data = response.json()
    frequency_insights = [i for i in data["insights"] if i["type"] == "purchase_frequency"]
    
    assert len(frequency_insights) > 0
    insight = frequency_insights[0]
    assert insight["data_points"] >= 3  # Minimum threshold


def test_price_trend_insight(client, user_with_receipts):
    """Test that price trend insights are generated"""
    response = client.get(
        "/api/insights",
        headers={"Authorization": f"Bearer {user_with_receipts['token']}"}
    )
    
    data = response.json()
    trend_insights = [i for i in data["insights"] if i["type"] == "price_trend"]
    
    assert len(trend_insights) > 0
    insight = trend_insights[0]
    assert insight["data_points"] >= 2  # Minimum threshold
    assert len(insight["underlying_data"]) > 0


def test_common_purchase_insight(client, user_with_receipts):
    """Test that common purchase insights are generated"""
    response = client.get(
        "/api/insights",
        headers={"Authorization": f"Bearer {user_with_receipts['token']}"}
    )
    
    data = response.json()
    common_insights = [i for i in data["insights"] if i["type"] == "common_purchase"]
    
    assert len(common_insights) > 0
    insight = common_insights[0]
    assert insight["data_points"] >= 3  # Minimum threshold


def test_store_pattern_insight(client, user_with_receipts):
    """Test that store pattern insights are generated"""
    response = client.get(
        "/api/insights",
        headers={"Authorization": f"Bearer {user_with_receipts['token']}"}
    )
    
    data = response.json()
    pattern_insights = [i for i in data["insights"] if i["type"] == "store_pattern"]
    
    assert len(pattern_insights) > 0
    insight = pattern_insights[0]
    assert insight["data_points"] >= 5  # Minimum threshold


def test_insights_no_predictive_language(client, user_with_receipts):
    """Test that insights contain no predictive language"""
    response = client.get(
        "/api/insights",
        headers={"Authorization": f"Bearer {user_with_receipts['token']}"}
    )
    
    data = response.json()
    
    # Words that should NOT appear in insights
    forbidden_words = ["will", "predict", "forecast", "expect", "should", "recommend"]
    
    for insight in data["insights"]:
        description_lower = insight["description"].lower()
        for word in forbidden_words:
            assert word not in description_lower, f"Found predictive word '{word}' in insight"


def test_insights_require_authentication(client):
    """Test that insights endpoint requires authentication"""
    response = client.get("/api/insights")
    
    assert response.status_code == 422  # Missing required header


def test_insights_user_isolation(client, db_session):
    """Test that users only see insights from their own data"""
    # Create two users with different data
    user1 = User(email="user1@example.com")
    user2 = User(email="user2@example.com")
    db_session.add_all([user1, user2])
    db_session.commit()
    
    store = Store(name="Test Store", normalized_name="test store")
    db_session.add(store)
    db_session.commit()
    
    # Create receipts only for user1
    for i in range(6):
        receipt = Receipt(
            user_id=user1.id,
            store_id=store.id,
            original_file_path=f"user1/receipt_{i}.txt",
            parse_status=ParseStatus.SUCCESS,
            purchase_date=datetime.now().date()
        )
        db_session.add(receipt)
    
    db_session.commit()
    
    # Create token for user2
    expire = datetime.utcnow() + timedelta(days=30)
    token2 = jwt.encode(
        {"sub": str(user2.id), "email": user2.email, "exp": expire, "type": "session"},
        settings.secret_key,
        algorithm=settings.algorithm
    )
    
    # User2 should have no insights
    response = client.get(
        "/api/insights",
        headers={"Authorization": f"Bearer {token2}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["insights"] == []
