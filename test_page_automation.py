#!/usr/bin/env python3
"""
Quick test script for page automation
Tests individual page automation without running full cycle
"""

from src.agents.automation_controller import AutomationController


def test_technology_automation():
    """Test technology.md automation"""
    print("=" * 60)
    print("Testing Technology Page Automation")
    print("=" * 60)
    
    controller = AutomationController()
    results = controller.run_technology_automation()
    
    if results['success']:
        print("\n✅ Technology automation completed successfully!")
        print(f"\nSummary: {results.get('summary', {})}")
    else:
        print("\n❌ Technology automation failed:")
        for error in results.get('errors', []):
            print(f"  - {error}")
    
    return results['success']


def test_society_automation():
    """Test society.md automation"""
    print("\n" + "=" * 60)
    print("Testing Society Page Automation")
    print("=" * 60)
    
    controller = AutomationController()
    results = controller.run_society_automation()
    
    if results['success']:
        print("\n✅ Society automation completed successfully!")
        print(f"\nSummary: {results.get('summary', {})}")
    else:
        print("\n❌ Society automation failed:")
        for error in results.get('errors', []):
            print(f"  - {error}")
    
    return results['success']


def test_privacy_automation():
    """Test privacy.md automation"""
    print("\n" + "=" * 60)
    print("Testing Privacy Page Automation")
    print("=" * 60)
    
    controller = AutomationController()
    results = controller.run_privacy_automation()
    
    if results['success']:
        print("\n✅ Privacy automation completed successfully!")
        print(f"\nSummary: {results.get('summary', {})}")
    else:
        print("\n❌ Privacy automation failed:")
        for error in results.get('errors', []):
            print(f"  - {error}")
    
    return results['success']


if __name__ == "__main__":
    import sys
    
    print("Testing Page Automation Framework")
    print("=" * 60)
    print("\nThis script tests individual page automation methods")
    print("without running the full automation cycle.\n")
    
    results = []
    
    # Test each page
    results.append(("Technology", test_technology_automation()))
    results.append(("Society", test_society_automation()))
    results.append(("Privacy", test_privacy_automation()))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    for page, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {page}")
    
    all_passed = all(success for _, success in results)
    
    if all_passed:
        print("\n🎉 All page automation tests passed!")
        sys.exit(0)
    else:
        print("\n⚠️  Some page automation tests failed")
        sys.exit(1)
