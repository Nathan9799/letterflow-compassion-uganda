#!/usr/bin/env python3
"""
Simple script to revert the design back to the original if needed.
Run this if you want to go back to the old LetterFlow design.
"""

import os
import shutil

def revert_design():
    """Revert the base template back to the original design."""
    
    # Check if backup exists
    if not os.path.exists('templates/base_original.html'):
        print("❌ Backup file not found! Cannot revert.")
        return False
    
    # Backup current design
    if os.path.exists('templates/base.html'):
        shutil.copy('templates/base.html', 'templates/base_new_backup.html')
        print("✅ Current design backed up as 'base_new_backup.html'")
    
    # Restore original design
    shutil.copy('templates/base_original.html', 'templates/base.html')
    print("✅ Design reverted to original LetterFlow design!")
    print("🔄 Refresh your browser to see the changes.")
    
    return True

def restore_new_design():
    """Restore the new design if you want it back."""
    
    if not os.path.exists('templates/base_new_backup.html'):
        print("❌ New design backup not found! Cannot restore.")
        return False
    
    # Restore new design
    shutil.copy('templates/base_new_backup.html', 'templates/base.html')
    print("✅ New design restored!")
    print("🔄 Refresh your browser to see the changes.")
    
    return True

if __name__ == "__main__":
    print("🎨 Design Management Script")
    print("=" * 40)
    print("1. Revert to original design")
    print("2. Restore new design")
    print("3. Exit")
    
    choice = input("\nEnter your choice (1-3): ").strip()
    
    if choice == "1":
        revert_design()
    elif choice == "2":
        restore_new_design()
    elif choice == "3":
        print("👋 Goodbye!")
    else:
        print("❌ Invalid choice!")
