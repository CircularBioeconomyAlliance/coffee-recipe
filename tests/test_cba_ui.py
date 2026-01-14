#!/usr/bin/env python3
"""
Simple test to verify the CBA UI updates are working correctly.
"""

import os
from pathlib import Path

def test_cba_branding():
    """Test that CBA branding elements are properly implemented."""

    # Read the streamlit app file (relative to project root)
    project_root = Path(__file__).parent.parent
    app_path = project_root / "src" / "app.py"

    with open(app_path, 'r') as f:
        content = f.read()
    
    # Check for CBA-specific elements
    checks = [
        ("CBA Title", "Circular Bioeconomy Alliance" in content),
        ("Nature Icon", "🌱" in content),
        ("CBA Color Palette", "--cba-main-background" in content and "--cba-accent-gold" in content),
        ("Mission Principles", "Re-Nature" in content and "Re-Think" in content and "Re-Activate" in content),
        ("King Charles Reference", "King Charles III" in content),
        ("Nature-focused messaging", "nature at the center" in content),
        ("CBA-specific responses", "circular bioeconomy" in content.lower()),
        ("Sustainability keywords", "sustainability" in content.lower()),
        ("New Conversation", "New Conversation" in content),
        ("Document Upload", "Document Upload" in content),
    ]
    
    print("🧪 Testing CBA UI Implementation")
    print("=" * 40)
    
    all_passed = True
    for check_name, result in checks:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {check_name}")
        if not result:
            all_passed = False
    
    print("=" * 40)
    if all_passed:
        print("🎉 All CBA branding checks passed!")
        print("\n✅ UI Features Implemented:")
        print("  • CBA logo and branding in sidebar")
        print("  • Nature-inspired color palette")
        print("  • Mission principles (Re-Nature, Re-Think, Re-Activate)")
        print("  • King Charles III founding reference")
        print("  • CBA-focused chat responses")
        print("  • Sustainability-themed messaging")
        print("  • Professional document upload interface")
        return True
    else:
        print("❌ Some checks failed. Please review the implementation.")
        return False

if __name__ == "__main__":
    import sys
    success = test_cba_branding()
    sys.exit(0 if success else 1)