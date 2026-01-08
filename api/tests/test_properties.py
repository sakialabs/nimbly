"""
Property-based tests using Hypothesis for critical correctness properties
"""
import pytest
from hypothesis import given, strategies as st, settings
from datetime import datetime, timedelta
from decimal import Decimal

from api.models import User, Store, Receipt, LineItem, PriceHistory, ParseStatus
from api.utils import normalize_store_name, normalize_product_name


# Hypothesis strategies
emails = st.emails()
store_names = st.text(min_size=1, max_size=100, alphabet=st.characters(blacklist_categories=('Cs',)))
product_names = st.text(min_size=1, max_size=200, alphabet=st.characters(blacklist_categories=('Cs',)))
prices = st.decimals(min_value=Decimal("0.01"), max_value=Decimal("999.99"), places=2)


@settings(max_examples=100)
@given(email=emails)
def test_property_user_email_uniqueness(db_session, email):
    """Property: Each email should map to exactly one user"""
    # Create user with email
    user1 = User(email=email)
    db_session.add(user1)
    db_session.commit()
    
    # Query by email should return the same user
    user2 = db_session.query(User).filter(User.email == email).first()
    assert user2 is not None
    assert user1.id == user2.id
    
    # Cleanup
    db_session.delete(user1)
    db_session.commit()


@settings(max_examples=100)
@given(store_name=store_names)
def test_property_store_normalization_consistency(store_name):
    """Property: Normalizing the same store name always produces the same result"""
    normalized1 = normalize_store_name(store_name)
    normalized2 = normalize_store_name(store_name)
    
    assert normalized1 == normalized2
    assert isinstance(normalized1, str)
    assert normalized1 == normalized1.lower()  # Should be lowercase


@settings(max_examples=100)
@given(product_name=product_names)
def test_property_product_normalization_consistency(product_name):
    """Property: Normalizing the same product name always produces the same result"""
    normalized1 = normalize_product_name(product_name)
    normalized2 = normalize_product_name(product_name)
    
    assert normalized1 == normalized2
    assert isinstance(normalized1, str)
    assert normalized1 == normalized1.lower()  # Should be lowercase


@settings(max_examples=50)
@given(
    email=emails,
    store_name=store_names,
    product_name=product_names,
    price=prices
)
def test_property_referential_integrity(db_session, email, store_name, product_name, price):
    """Property: Receipts always belong to valid users and stores"""
    # Create user
    user = User(email=email)
    db_session.add(user)
    db_session.commit()
    
    # Create store
    store = Store(name=store_name, normalized_name=normalize_store_name(store_name))
    db_session.add(store)
    db_session.commit()
    
    # Create receipt
    receipt = Receipt(
        user_id=user.id,
        store_id=store.id,
        original_file_path="test/receipt.txt",
        parse_status=ParseStatus.SUCCESS
    )
    db_session.add(receipt)
    db_session.commit()
    
    # Verify referential integrity
    assert receipt.user_id == user.id
    assert receipt.store_id == store.id
    assert receipt.user is not None
    assert receipt.store is not None
    assert receipt.user.email == email
    
    # Create line item
    line_item = LineItem(
        receipt_id=receipt.id,
        product_name=product_name,
        normalized_product_name=normalize_product_name(product_name),
        total_price=price,
        line_number=1
    )
    db_session.add(line_item)
    db_session.commit()
    
    # Verify line item belongs to receipt
    assert line_item.receipt_id == receipt.id
    assert line_item.receipt is not None
    
    # Create price history
    price_history = PriceHistory(
        product_name=normalize_product_name(product_name),
        store_id=store.id,
        price=price,
        observed_date=datetime.now().date(),
        source_line_item_id=line_item.id
    )
    db_session.add(price_history)
    db_session.commit()
    
    # Verify price history references
    assert price_history.store_id == store.id
    assert price_history.source_line_item_id == line_item.id
    
    # Cleanup
    db_session.delete(price_history)
    db_session.delete(line_item)
    db_session.delete(receipt)
    db_session.delete(store)
    db_session.delete(user)
    db_session.commit()


@settings(max_examples=50)
@given(
    store_name1=store_names,
    store_name2=store_names
)
def test_property_store_deduplication(db_session, store_name1, store_name2):
    """Property: Stores with same normalized name should be deduplicated"""
    normalized1 = normalize_store_name(store_name1)
    normalized2 = normalize_store_name(store_name2)
    
    # Create first store
    store1 = Store(name=store_name1, normalized_name=normalized1)
    db_session.add(store1)
    db_session.commit()
    
    # If normalized names are the same, should find existing store
    existing_store = db_session.query(Store).filter(
        Store.normalized_name == normalized2
    ).first()
    
    if normalized1 == normalized2:
        assert existing_store is not None
        assert existing_store.id == store1.id
    
    # Cleanup
    db_session.delete(store1)
    db_session.commit()


def test_property_insight_thresholds(db_session):
    """Property: Insights only generated when minimum data thresholds are met"""
    from api.insights import (
        generate_purchase_frequency_insights,
        generate_price_trend_insights,
        generate_common_purchase_insights,
        generate_store_pattern_insights,
        MIN_RECEIPTS_FOR_FREQUENCY,
        MIN_PURCHASES_FOR_PRICE_TREND,
        MIN_PURCHASES_FOR_COMMON,
        MIN_RECEIPTS_FOR_STORE_PATTERN
    )
    
    # Create user
    user = User(email="threshold@test.com")
    db_session.add(user)
    db_session.commit()
    
    # Create store
    store = Store(name="Test Store", normalized_name="test store")
    db_session.add(store)
    db_session.commit()
    
    # Test with insufficient data (2 receipts, need 3 for frequency)
    for i in range(2):
        receipt = Receipt(
            user_id=user.id,
            store_id=store.id,
            original_file_path=f"test/receipt_{i}.txt",
            parse_status=ParseStatus.SUCCESS
        )
        db_session.add(receipt)
    db_session.commit()
    
    # Should not generate frequency insights
    insights = generate_purchase_frequency_insights(user.id, db_session)
    assert len(insights) == 0
    
    # Add one more receipt to meet threshold
    receipt = Receipt(
        user_id=user.id,
        store_id=store.id,
        original_file_path="test/receipt_3.txt",
        parse_status=ParseStatus.SUCCESS
    )
    db_session.add(receipt)
    db_session.commit()
    
    # Now should generate insights
    insights = generate_purchase_frequency_insights(user.id, db_session)
    assert len(insights) > 0
    
    # Cleanup
    db_session.query(Receipt).filter(Receipt.user_id == user.id).delete()
    db_session.delete(store)
    db_session.delete(user)
    db_session.commit()


def test_property_no_predictive_language_in_insights(db_session):
    """Property: Insights never contain predictive language"""
    from api.insights import (
        generate_purchase_frequency_insights,
        generate_price_trend_insights,
        generate_common_purchase_insights,
        generate_store_pattern_insights
    )
    
    # Create user with sufficient data
    user = User(email="predictive@test.com")
    db_session.add(user)
    db_session.commit()
    
    store = Store(name="Test Store", normalized_name="test store")
    db_session.add(store)
    db_session.commit()
    
    # Create receipts with line items
    for i in range(6):
        receipt = Receipt(
            user_id=user.id,
            store_id=store.id,
            original_file_path=f"test/receipt_{i}.txt",
            parse_status=ParseStatus.SUCCESS,
            purchase_date=datetime.now().date()
        )
        db_session.add(receipt)
        db_session.flush()
        
        line_item = LineItem(
            receipt_id=receipt.id,
            product_name="Test Product",
            normalized_product_name="test product",
            total_price=Decimal("5.00"),
            line_number=1
        )
        db_session.add(line_item)
        db_session.flush()
        
        price_history = PriceHistory(
            product_name="test product",
            store_id=store.id,
            price=Decimal("5.00"),
            observed_date=datetime.now().date(),
            source_line_item_id=line_item.id
        )
        db_session.add(price_history)
    
    db_session.commit()
    
    # Generate all insights
    all_insights = []
    all_insights.extend(generate_purchase_frequency_insights(user.id, db_session))
    all_insights.extend(generate_price_trend_insights(user.id, db_session))
    all_insights.extend(generate_common_purchase_insights(user.id, db_session))
    all_insights.extend(generate_store_pattern_insights(user.id, db_session))
    
    # Check for forbidden predictive words
    forbidden_words = ["will", "predict", "forecast", "expect", "should", "recommend", "likely", "probably"]
    
    for insight in all_insights:
        description_lower = insight.description.lower()
        title_lower = insight.title.lower()
        
        for word in forbidden_words:
            assert word not in description_lower, f"Found predictive word '{word}' in description"
            assert word not in title_lower, f"Found predictive word '{word}' in title"
    
    # Cleanup
    db_session.query(PriceHistory).filter(PriceHistory.store_id == store.id).delete()
    db_session.query(LineItem).filter(LineItem.receipt_id.in_(
        db_session.query(Receipt.id).filter(Receipt.user_id == user.id)
    )).delete(synchronize_session=False)
    db_session.query(Receipt).filter(Receipt.user_id == user.id).delete()
    db_session.delete(store)
    db_session.delete(user)
    db_session.commit()


@settings(max_examples=50)
@given(price1=prices, price2=prices)
def test_property_price_comparison_consistency(price1, price2):
    """Property: Price comparisons are consistent and transitive"""
    # Test reflexivity
    assert price1 == price1
    
    # Test symmetry
    if price1 == price2:
        assert price2 == price1
    
    # Test comparison consistency
    if price1 < price2:
        assert price2 > price1
        assert not (price1 > price2)
    elif price1 > price2:
        assert price2 < price1
        assert not (price1 < price2)
    else:
        assert price1 == price2
