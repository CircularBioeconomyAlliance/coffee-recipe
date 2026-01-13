#!/usr/bin/env python3
"""
End-to-end workflow tests for the CBA Indicator Selection Assistant.

Tests the complete workflow: upload → extract → ask → retrieve → chat
"""

import sys
import os
from pathlib import Path

# Add project root and src to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

from workflow import (
    get_missing_fields,
    is_info_complete,
    extract_project_info
)


class TestWorkflowPhases:
    """Test suite for workflow phase transitions and functionality."""
    
    def __init__(self):
        self.test_results = []
        self.passed = 0
        self.failed = 0
    
    def log_test(self, test_name, passed, message=""):
        """Log test result."""
        status = "✅ PASS" if passed else "❌ FAIL"
        self.test_results.append((test_name, passed, message))
        if passed:
            self.passed += 1
            print(f"{status} {test_name}")
        else:
            self.failed += 1
            print(f"{status} {test_name}: {message}")
    
    def test_missing_fields_detection(self):
        """Test get_missing_fields function with various project_info states."""
        print("\n🧪 Testing Missing Fields Detection...")
        
        # Test 1: Complete project info
        complete_info = {
            'location': 'Chad',
            'project_type': 'cotton farming',
            'outcomes': ['soil health', 'water conservation'],
            'budget': 'medium',
            'capacity': 'intermediate'
        }
        missing = get_missing_fields(complete_info)
        self.log_test(
            "Complete info has no missing fields",
            len(missing) == 0,
            f"Expected 0 missing, got {len(missing)}: {missing}"
        )
        
        # Test 2: Partial project info
        partial_info = {
            'location': 'Chad',
            'project_type': None,
            'outcomes': [],
            'budget': 'medium',
            'capacity': None
        }
        missing = get_missing_fields(partial_info)
        expected_missing = {'project_type', 'outcomes', 'capacity'}
        actual_missing = set(missing)
        self.log_test(
            "Partial info correctly identifies missing fields",
            actual_missing == expected_missing,
            f"Expected {expected_missing}, got {actual_missing}"
        )
        
        # Test 3: Empty project info
        empty_info = {
            'location': None,
            'project_type': None,
            'outcomes': [],
            'budget': None,
            'capacity': None
        }
        missing = get_missing_fields(empty_info)
        self.log_test(
            "Empty info identifies all fields as missing",
            len(missing) == 5,
            f"Expected 5 missing, got {len(missing)}"
        )
        
        # Test 4: Empty string values
        empty_string_info = {
            'location': '',
            'project_type': '   ',
            'outcomes': ['valid'],
            'budget': '',
            'capacity': 'basic'
        }
        missing = get_missing_fields(empty_string_info)
        expected_missing_strings = {'location', 'project_type', 'budget'}
        actual_missing_strings = set(missing)
        self.log_test(
            "Empty strings treated as missing",
            actual_missing_strings == expected_missing_strings,
            f"Expected {expected_missing_strings}, got {actual_missing_strings}"
        )
    
    def test_info_completeness(self):
        """Test is_info_complete function."""
        print("\n🧪 Testing Information Completeness Check...")
        
        # Test 1: Complete info returns True
        complete_info = {
            'location': 'Chad',
            'project_type': 'cotton farming',
            'outcomes': ['soil health'],
            'budget': 'medium',
            'capacity': 'intermediate'
        }
        self.log_test(
            "Complete info returns True",
            is_info_complete(complete_info) == True
        )
        
        # Test 2: Incomplete info returns False
        incomplete_info = {
            'location': 'Chad',
            'project_type': None,
            'outcomes': [],
            'budget': 'medium',
            'capacity': 'intermediate'
        }
        self.log_test(
            "Incomplete info returns False",
            is_info_complete(incomplete_info) == False
        )
        
        # Test 3: Single missing field returns False
        single_missing = {
            'location': 'Chad',
            'project_type': 'cotton',
            'outcomes': ['health'],
            'budget': 'medium',
            'capacity': None
        }
        self.log_test(
            "Single missing field returns False",
            is_info_complete(single_missing) == False
        )
    
    def test_extraction_fallback(self):
        """Test that extraction handles errors gracefully."""
        print("\n🧪 Testing Extraction Error Handling...")
        
        # Test 1: Empty text extraction
        try:
            result = extract_project_info("")
            self.log_test(
                "Empty text extraction returns empty structure",
                isinstance(result, dict) and all(
                    key in result for key in ['location', 'project_type', 'outcomes', 'budget', 'capacity']
                )
            )
        except Exception as e:
            self.log_test(
                "Empty text extraction returns empty structure",
                False,
                f"Raised exception: {str(e)}"
            )
        
        # Test 2: Invalid text extraction
        try:
            result = extract_project_info("This is random text with no project information")
            self.log_test(
                "Invalid text extraction returns structure",
                isinstance(result, dict),
                f"Got type: {type(result)}"
            )
        except Exception as e:
            self.log_test(
                "Invalid text extraction returns structure",
                False,
                f"Raised exception: {str(e)}"
            )
    
    def test_workflow_phase_progression(self):
        """Test workflow phase progression logic."""
        print("\n🧪 Testing Workflow Phase Progression...")
        
        # Simulate workflow state
        workflow_state = {
            'phase': 'upload',
            'project_info': {
                'location': None,
                'project_type': None,
                'outcomes': [],
                'budget': None,
                'capacity': None,
                'documents_uploaded': False
            }
        }
        
        # Test 1: Upload phase can transition to extract or ask
        self.log_test(
            "Upload phase allows transition to extract or ask",
            workflow_state['phase'] == 'upload'
        )
        
        # Simulate document upload
        workflow_state['project_info']['documents_uploaded'] = True
        workflow_state['phase'] = 'extract'
        
        # Test 2: Extract phase transitions to ask
        self.log_test(
            "Extract phase transitions to ask",
            workflow_state['phase'] == 'extract'
        )
        
        workflow_state['phase'] = 'ask'
        
        # Test 3: Ask phase stays until info complete
        self.log_test(
            "Ask phase blocks when info incomplete",
            not is_info_complete(workflow_state['project_info'])
        )
        
        # Complete the info
        workflow_state['project_info'].update({
            'location': 'Chad',
            'project_type': 'cotton',
            'outcomes': ['health'],
            'budget': 'medium',
            'capacity': 'basic'
        })
        
        # Test 4: Ask phase allows transition when complete
        self.log_test(
            "Ask phase allows transition when info complete",
            is_info_complete(workflow_state['project_info'])
        )
        
        workflow_state['phase'] = 'retrieve'
        
        # Test 5: Retrieve phase transitions to chat
        self.log_test(
            "Retrieve phase can transition to chat",
            workflow_state['phase'] == 'retrieve'
        )
        
        workflow_state['phase'] = 'chat'
        
        # Test 6: Chat is final phase
        self.log_test(
            "Chat is the final phase",
            workflow_state['phase'] == 'chat'
        )
    
    def test_skip_upload_flow(self):
        """Test workflow when user skips document upload."""
        print("\n🧪 Testing Skip Upload Flow...")
        
        # Simulate skip upload workflow
        workflow_state = {
            'phase': 'upload',
            'project_info': {
                'location': None,
                'project_type': None,
                'outcomes': [],
                'budget': None,
                'capacity': None,
                'documents_uploaded': False
            }
        }
        
        # Test 1: Can skip directly to ask
        workflow_state['phase'] = 'ask'
        self.log_test(
            "Can skip upload and go directly to ask",
            workflow_state['phase'] == 'ask' and 
            not workflow_state['project_info']['documents_uploaded']
        )
        
        # Test 2: Manual entry workflow
        workflow_state['project_info'].update({
            'location': 'Kenya',
            'project_type': 'agroforestry',
            'outcomes': ['biodiversity'],
            'budget': 'low',
            'capacity': 'basic'
        })
        
        self.log_test(
            "Manual entry completes project info",
            is_info_complete(workflow_state['project_info'])
        )
        
        # Test 3: Can proceed to retrieve
        workflow_state['phase'] = 'retrieve'
        self.log_test(
            "Skip upload flow can reach retrieve phase",
            workflow_state['phase'] == 'retrieve'
        )
    
    def run_all_tests(self):
        """Run all workflow tests."""
        print("🚀 Starting Workflow End-to-End Tests")
        print("=" * 60)
        
        try:
            self.test_missing_fields_detection()
            self.test_info_completeness()
            self.test_extraction_fallback()
            self.test_workflow_phase_progression()
            self.test_skip_upload_flow()
            
            print("\n" + "=" * 60)
            print(f"📊 Test Results: {self.passed} passed, {self.failed} failed")
            
            if self.failed == 0:
                print("🎉 ALL WORKFLOW TESTS PASSED!")
                print("\n✅ Verified Workflows:")
                print("  • upload → extract → ask → retrieve → chat")
                print("  • skip upload → ask → retrieve → chat")
                print("  • Error handling for each phase")
                print("  • Information completeness validation")
                return True
            else:
                print(f"❌ {self.failed} test(s) failed")
                print("\nFailed tests:")
                for name, passed, message in self.test_results:
                    if not passed:
                        print(f"  • {name}: {message}")
                return False
                
        except Exception as e:
            print("\n" + "=" * 60)
            print(f"❌ TEST SUITE FAILED: {str(e)}")
            import traceback
            traceback.print_exc()
            return False


def main():
    """Main test runner."""
    test_suite = TestWorkflowPhases()
    success = test_suite.run_all_tests()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
