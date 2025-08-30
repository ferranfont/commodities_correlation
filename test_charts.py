from plot_data import *
import webbrowser
import os

def test_data_loading():
    """Test if data loading works properly"""
    print("Testing data loading...")
    data_dict = load_all_data()
    
    print(f"\nLoaded {len(data_dict)} datasets:")
    for name, data in data_dict.items():
        print(f"- {name}: {len(data)} rows, columns: {list(data.columns)}")
        print(f"  Date range: {data.index.min()} to {data.index.max()}")
        print(f"  Sample close prices: {data['Close'].head(3).tolist()}")
    
    return data_dict

def generate_and_open_charts():
    """Generate charts and open in browser"""
    print("\nGenerating individual charts...")
    
    # Test data loading first
    data_dict = test_data_loading()
    
    if len(data_dict) == 0:
        print("No data loaded, cannot generate charts")
        return
    
    # Generate line chart
    print("\nGenerating price lines chart...")
    plot_price_lines()
    
    # Generate percentage growth chart
    print("\nGenerating percentage growth chart...")
    plot_percentage_growth()
    
    # Generate correlation heatmap
    print("\nGenerating correlation heatmap...")
    plot_correlation_heatmap()
    
    # Try candlestick charts for each commodity
    print("\nGenerating candlestick charts...")
    for name, data in data_dict.items():
        try:
            fig = plot_candlestick_chart(data, name, name)
            filename = f'charts/{name.replace(" ", "_").lower()}_candlestick.html'
            fig.write_html(filename)
            print(f"Saved: {filename}")
        except Exception as e:
            print(f"Error creating candlestick for {name}: {str(e)}")
    
    # Open percentage growth chart
    file_path = os.path.abspath('charts/percentage_growth.html')
    if os.path.exists(file_path):
        print(f"\nOpening chart in browser: {file_path}")
        webbrowser.open(f'file://{file_path}')
    
    print("\nAll charts generated!")

if __name__ == "__main__":
    generate_and_open_charts()