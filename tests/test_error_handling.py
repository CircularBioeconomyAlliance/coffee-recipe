#!/usr/bin/env python3
"""
Test error handling in workflow functions.
Tests that errors are caught and handled gracefully.
"""

import sys
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from workflow import extract_project_info, get_missing_fields, is_info_complete


def test_extract_project_info_with_invalid_text():
    """Test that extract_project_info handles invalid text gracefully."""
    print("🧪 Testing extract_project_info with invalid text...")
    
    # Test with empty text
    result = extract_project_info("")
    assert isinstance(result, dict), "Should return a dict"
    assert 'location' in result, "Should have location field"
    assert 'project_type' in result, "Should have project_type field"
    print("  ✓ Empty text handled gracefully")
    
    # Test with gibberish text
    result = extract_project_info("asdfghjkl qwertyuiop zxcvbnm")
    assert isinstance(result, dict), "Should return a dict"
    print("  ✓ Gibberish text handled gracefully")
    
    # Test with very long text
    long_text = "test " * 10000
    result = extract_project_info(long_text)
    assert isinstance(result, dict), "Should return a dict"
    print("  ✓ Very long text handled gracefully")
    
    print("✅ extract_project_info error handling: PASSED\n")


def test_get_missing_fields():
    """Test get_missing_fields function."""
    print("🧪 Testing get_missing_fields...")
    
    # Test with complete info
    complete_info = {
        'location': 'Chad',
        'project_type': 'cotton farming',
        'outcomes': ['soil health', 'water conservation'],
        'budget': 'medium',
        'capacity': 'intermediate'
    }
    missing = get_missing_fields(complete_info)
    assert len(missing) == 0, "Complete info should have no missing fields"
    print("  ✓ Complete info: no missing fields")
    
    # Test with partial info
    partial_info = {
        'location': 'Chad',
        'project_type': None,
        'outcomes': [],
        'budget': 'medium',
        'capacity': None
    }
    missing = get_missing_fields(partial_info)
    assert 'project_type' in missing, "Should detect missing project_type"
    assert 'outcomes' in missing, "Should detect empty outcomes"
    assert 'capacity' in missing, "Should detect missing capacity"
    assert 'location' not in missing, "Should not include present fields"
    print(f"  ✓ Partial info: {len(missing)} missing fields detected")
    
    # Test with empty info
    empty_info = {
        'location': None,
        'project_type': None,
        'outcomes': [],
        'budget': None,
        'capacity': None
    }
    missing = get_missing_fields(empty_info)
    assert len(missing) == 5, "Empty info should have all fields missing"
    print(f"  ✓ Empty info: {len(missing)} missing fields detected")
    
    print("✅ get_missing_fields: PASSED\n")


def test_is_info_complete():
    """Test is_info_complete function."""
    print("🧪 Testing is_info_complete...")
    
    # Test with complete info
    complete_info = {
        'location': 'Chad',
        'project_type': 'cotton farming',
        'outcomes': ['soil health'],
        'budget': 'medium',
        'capacity': 'intermediate'
    }
    assert is_info_complete(complete_info) == True, "Complete info should return True"
    print("  ✓ Complete info returns True")
    
    # Test with incomplete info
    incomplete_info = {
        'location': 'Chad',
        'project_type': None,
        'outcomes': ['soil health'],
        'budget': 'medium',
        'capacity': 'intermediate'
    }
    assert is_info_complete(incomplete_info) == False, "Incomplete info should return False"
    print("  ✓ Incomplete info returns False")
    
    # Test with empty info
    empty_info = {
        'location': None,
        'project_type': None,
        'outcomes': [],
        'budget': None,
        'capacity': None
    }
    assert is_info_complete(empty_info) == False, "Empty info should return False"
    print("  ✓ Empty info returns False")
    
    print("✅ is_info_complete: PASSED\n")


def run_all_tests():
    """Run all error handling tests."""
    print("🚀 Starting Error Handling Tests\n")
    print("=" * 50)
    
    try:
        test_extract_project_info_with_invalid_text()
        test_get_missing_fields()
        test_is_info_complete()
        
        print("=" * 50)
        print("🎉 ALL ERROR HANDLING TESTS PASSED!")
        print("\n✅ Test Summary:")
        print("  • extract_project_info error handling: ✅")
        print("  • get_missing_fields: ✅")
        print("  • is_info_complete: ✅")
        print("\n🚀 Error handling is working correctly!")
        
        return True
        
    except Exception as e:
        print("=" * 50)
        print(f"❌ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        print("\n🔧 Please check the implementation and try again.")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
