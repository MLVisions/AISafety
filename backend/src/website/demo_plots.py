"""
Demo script to test plot generation
Run this after installing requirements: pip install -r requirements_plotting.txt
"""

from backend.src.website.plot_generator import generate_all_plots

if __name__ == "__main__":
    print("🚀 AI Safety Website Plot Generator Demo")
    print("=" * 50)
    print("This script will generate professional plots matching your website theme.")
    print("")
    print("📋 What this creates:")
    print("• Market trends plot (S&P 500 & Bitcoin)")
    print("• Individual portfolio projections (Persons A, B, C)")
    print("• Comparative wealth analysis")
    print("")
    print("🎨 Features:")
    print("• Website color scheme (#0a1f44, #4da3d8, etc.)")
    print("• Professional styling with glass-morphism effects")
    print("• High-resolution PNG output")
    print("• Responsive design compatibility")
    print("")
    
    try:
        generate_all_plots()
        print("")
        print("🎉 Success! Check the website/images/ folder for new plots.")
        print("💡 Tip: You can replace the original PNGs with these new ones.")
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("💡 Run: pip install -r requirements_plotting.txt")
    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Check that the data/ folder contains the CSV files.")