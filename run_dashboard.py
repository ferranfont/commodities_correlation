"""
Quick script to run the comprehensive trading dashboard
Execute this to see all charts in one integrated view
"""

from create_embedded_dashboard import open_embedded_dashboard
import webbrowser
import os

def main():
    """Main execution function"""
    print("[LAUNCH] Commodities Trading Dashboard...")
    print("=" * 60)
    print("[LOADING] All charts:")
    print("  * Price Lines Comparison")
    print("  * Percentage Growth Analysis") 
    print("  * Correlation Heatmap")
    print("  * Individual Candlestick Charts")
    print("  * NASDAQ Comparisons")
    print("  * Rolling Correlations")
    print("=" * 60)
    
    # Create and open dashboard
    open_embedded_dashboard()
    
    print("[SUCCESS] Dashboard launched successfully!")
    print("[INFO] Navigate using the top menu bar")
    print("[INFO] All charts are interactive - zoom, hover, and explore!")

def open_existing_dashboard():
    """Open existing dashboard without regenerating"""
    dashboard_path = "charts/full_dashboard.html"
    
    if os.path.exists(dashboard_path):
        full_path = os.path.abspath(dashboard_path)
        print(f"Opening existing dashboard: {full_path}")
        webbrowser.open(f'file://{full_path}')
    else:
        print("Dashboard not found. Creating new one...")
        main()

if __name__ == "__main__":
    # Quick option: just open existing dashboard
    # open_existing_dashboard()
    
    # Full option: regenerate and open
    main()