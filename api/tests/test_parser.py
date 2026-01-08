"""
Test script for enhanced receipt parser
"""
import sys
sys.path.insert(0, './api')

from api.parser import (
    extract_store_name,
    extract_date,
    extract_line_items,
    extract_total,
    extract_tax,
    assess_parsing_confidence
)

# Sample receipt text
SAMPLE_RECEIPT = """
WHOLE FOODS MARKET
123 Main Street
San Francisco, CA 94102

Date: 01/08/2026
Time: 14:30

Organic Bananas 2.5 lb    3.75
Almond Milk               4.99
Organic Eggs 12 ct        6.49
Avocados 3 @ 1.99         5.97
Whole Wheat Bread         4.29
Greek Yogurt              5.99

Subtotal                 31.48
Tax                       2.52
Total                    34.00

Thank you for shopping!
"""

def test_store_extraction():
    print("Testing store extraction...")
    store_name, confidence = extract_store_name(SAMPLE_RECEIPT)
    print(f"  Store: {store_name}")
    print(f"  Confidence: {confidence:.2f}")
    assert store_name is not None
    assert confidence > 0.8
    print("  ✓ PASSED\n")

def test_date_extraction():
    print("Testing date extraction...")
    date, confidence = extract_date(SAMPLE_RECEIPT)
    print(f"  Date: {date}")
    print(f"  Confidence: {confidence:.2f}")
    assert date is not None
    assert confidence > 0.8
    print("  ✓ PASSED\n")

def test_line_items_extraction():
    print("Testing line items extraction...")
    items, metadata = extract_line_items(SAMPLE_RECEIPT)
    print(f"  Items extracted: {len(items)}")
    print(f"  Extraction rate: {metadata['matched_lines']}/{metadata['processed_lines']}")
    for product, quantity, price in items[:3]:
        print(f"    - {product} {quantity or ''} ${price}")
    assert len(items) >= 5
    print("  ✓ PASSED\n")

def test_total_extraction():
    print("Testing total extraction...")
    total, confidence = extract_total(SAMPLE_RECEIPT)
    print(f"  Total: ${total}")
    print(f"  Confidence: {confidence:.2f}")
    assert total is not None
    assert confidence > 0.8
    print("  ✓ PASSED\n")

def test_tax_extraction():
    print("Testing tax extraction...")
    tax = extract_tax(SAMPLE_RECEIPT)
    print(f"  Tax: ${tax}")
    assert tax is not None
    print("  ✓ PASSED\n")

def test_confidence_assessment():
    print("Testing confidence assessment...")
    store_name, store_conf = extract_store_name(SAMPLE_RECEIPT)
    date, date_conf = extract_date(SAMPLE_RECEIPT)
    items, items_meta = extract_line_items(SAMPLE_RECEIPT)
    total, total_conf = extract_total(SAMPLE_RECEIPT)
    tax = extract_tax(SAMPLE_RECEIPT)
    
    status, error, details = assess_parsing_confidence(
        store_name, store_conf,
        date, date_conf,
        items, items_meta,
        total, total_conf,
        tax
    )
    
    print(f"  Status: {status.value}")
    print(f"  Overall confidence: {details['overall_confidence']:.2f}")
    print(f"  Issues: {details['issues']}")
    assert details['overall_confidence'] > 0.7
    print("  ✓ PASSED\n")

if __name__ == "__main__":
    print("=" * 60)
    print("Enhanced Receipt Parser Tests")
    print("=" * 60 + "\n")
    
    try:
        test_store_extraction()
        test_date_extraction()
        test_line_items_extraction()
        test_total_extraction()
        test_tax_extraction()
        test_confidence_assessment()
        
        print("=" * 60)
        print("All tests passed! ✓")
        print("=" * 60)
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
