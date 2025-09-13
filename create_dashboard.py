import os
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from plot_data import load_all_data, calculate_percentage_growth, calculate_correlation_matrix
import plotly.offline as pyo
import webbrowser

def create_comprehensive_dashboard():
    """Create a comprehensive dashboard with all charts in one HTML file"""
    
    # Load data
    print("Loading data for comprehensive dashboard...")
    data_dict = load_all_data()
    
    if len(data_dict) == 0:
        print("No data available for dashboard creation")
        return
    
    # Create HTML structure for dashboard
    dashboard_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Commodities Trading Dashboard - Full Analysis</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body {
            font-family: 'Arial', sans-serif;
            background-color: #1e1e1e;
            color: #ffffff;
            margin: 0;
            padding: 20px;
        }
        .dashboard-container {
            max-width: 1800px;
            margin: 0 auto;
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
            padding: 20px;
            background-color: #2d2d2d;
            border-radius: 10px;
        }
        .chart-section {
            margin-bottom: 40px;
            padding: 20px;
            background-color: #2d2d2d;
            border-radius: 10px;
        }
        .chart-title {
            color: #4ECDC4;
            border-bottom: 2px solid #4ECDC4;
            padding-bottom: 10px;
            margin-bottom: 20px;
            font-size: 24px;
        }
        .chart-container {
            width: 100%;
            height: 950px;
            margin-bottom: 20px;
        }
        .grid-container {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 40px;
        }
        .grid-item {
            background-color: #2d2d2d;
            border-radius: 10px;
            padding: 20px;
        }
        .full-width {
            grid-column: 1 / -1;
        }
        .navigation {
            position: sticky;
            top: 20px;
            background-color: #2d2d2d;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 20px;
            z-index: 1000;
        }
        .nav-links {
            display: flex;
            justify-content: center;
            gap: 20px;
            flex-wrap: wrap;
        }
        .nav-links a {
            color: #4ECDC4;
            text-decoration: none;
            padding: 8px 16px;
            border: 1px solid #4ECDC4;
            border-radius: 5px;
            transition: all 0.3s ease;
        }
        .nav-links a:hover {
            background-color: #4ECDC4;
            color: #1e1e1e;
        }
    </style>
</head>
<body>
    <div class="dashboard-container">
        <div class="header">
            <h1>🛢️ Commodities Trading Dashboard - Complete Analysis</h1>
            <p><strong>Assets:</strong> Crude Oil (CL), NASDAQ, Gold (GC), EUR/USD | <strong>Period:</strong> 20 Years</p>
        </div>
        
        <div class="navigation">
            <div class="nav-links">
                <a href="#overview">Overview</a>
                <a href="#growth">Growth Analysis</a>
                <a href="#correlations">Correlations</a>
                <a href="#candlesticks">Candlesticks</a>
                <a href="#nasdaq-comparison">vs NASDAQ</a>
                <a href="#rolling-corr">Rolling Correlations</a>
            </div>
        </div>

        <div id="overview" class="chart-section">
            <h2 class="chart-title">📊 Price Overview</h2>
            <div id="price-lines" class="chart-container"></div>
        </div>

        <div id="growth" class="chart-section">
            <h2 class="chart-title">📈 Percentage Growth Analysis</h2>
            <div id="percentage-growth" class="chart-container"></div>
        </div>

        <div id="correlations" class="chart-section">
            <h2 class="chart-title">🔗 Correlation Matrix</h2>
            <div id="correlation-heatmap" class="chart-container"></div>
        </div>

        <div id="candlesticks" class="chart-section">
            <h2 class="chart-title">🕯️ Individual Asset Candlesticks</h2>
            <div class="grid-container">
"""

    # Generate JavaScript code for charts
    js_code = """
    <script>
    // Price Lines Chart
    """
    
    # Price lines data
    price_data = []
    for name, data in data_dict.items():
        price_data.append({
            'x': data.index.strftime('%Y-%m-%d').tolist(),
            'y': data['Close'].tolist(),
            'name': name,
            'type': 'scatter',
            'mode': 'lines',
            'line': {'width': 2}
        })
    
    js_code += f"""
    var priceData = {price_data};
    var priceLayout = {{
        title: 'All Assets - Price Comparison (20 Years)',
        xaxis: {{title: 'Date'}},
        yaxis: {{title: 'Price'}},
        template: 'plotly_dark',
        height: 900,
        width: 1700,
        hovermode: 'x unified'
    }};
    Plotly.newPlot('price-lines', priceData, priceLayout);
    """
    
    # Percentage growth data
    growth_data = []
    for name, data in data_dict.items():
        pct_growth = calculate_percentage_growth(data)
        growth_data.append({
            'x': data.index.strftime('%Y-%m-%d').tolist(),
            'y': pct_growth.tolist(),
            'name': name,
            'type': 'scatter',
            'mode': 'lines',
            'line': {'width': 2}
        })
    
    js_code += f"""
    // Percentage Growth Chart
    var growthData = {growth_data};
    var growthLayout = {{
        title: 'Percentage Growth from Initial Point (20 Years)',
        xaxis: {{title: 'Date'}},
        yaxis: {{title: 'Percentage Growth (%)'}},
        template: 'plotly_dark',
        height: 900,
        width: 1700,
        hovermode: 'x unified',
        shapes: [{{
            type: 'line',
            x0: growthData[0].x[0],
            x1: growthData[0].x[growthData[0].x.length-1],
            y0: 0,
            y1: 0,
            line: {{color: 'white', dash: 'dash', width: 1}}
        }}]
    }};
    Plotly.newPlot('percentage-growth', growthData, growthLayout);
    """
    
    # Correlation heatmap
    correlation_matrix = calculate_correlation_matrix(data_dict)
    
    js_code += f"""
    // Correlation Heatmap
    var corrData = [{{
        z: {correlation_matrix.values.tolist()},
        x: {list(correlation_matrix.columns)},
        y: {list(correlation_matrix.index)},
        type: 'heatmap',
        colorscale: 'RdBu',
        zmid: 0,
        text: {correlation_matrix.round(3).values.tolist()},
        texttemplate: '%{{text}}',
        textfont: {{size: 12}},
        hoverongaps: false
    }}];
    var corrLayout = {{
        title: 'Assets Correlation Matrix (20 Years)',
        template: 'plotly_dark',
        height: 900,
        width: 1700
    }};
    Plotly.newPlot('correlation-heatmap', corrData, corrLayout);
    """
    
    # Individual candlesticks
    candlestick_divs = ""
    candlestick_js = ""
    
    for i, (name, data) in enumerate(data_dict.items()):
        div_id = name.replace(' ', '').replace('/', '').lower()
        candlestick_divs += f"""
                <div class="grid-item">
                    <h3>{name}</h3>
                    <div id="{div_id}-candlestick" style="height: 400px;"></div>
                </div>
        """
        
        candlestick_js += f"""
        // {name} Candlestick
        var {div_id}Data = [{{
            x: {data.index.strftime('%Y-%m-%d').tolist()},
            open: {data['Open'].tolist()},
            high: {data['High'].tolist()},
            low: {data['Low'].tolist()},
            close: {data['Close'].tolist()},
            type: 'candlestick',
            name: '{name}'
        }}];
        var {div_id}Layout = {{
            title: '{name} - Daily Candlestick',
            xaxis: {{title: 'Date'}},
            yaxis: {{title: 'Price'}},
            template: 'plotly_dark',
            height: 380,
            xaxis: {{rangeslider: {{visible: false}}}}
        }};
        Plotly.newPlot('{div_id}-candlestick', {div_id}Data, {div_id}Layout);
        """
    
    js_code += candlestick_js
    
    # Complete the HTML
    dashboard_html += candlestick_divs + """
            </div>
        </div>
    </div>

    """ + js_code + """
    </script>
</body>
</html>
    """
    
    # Save dashboard
    dashboard_file = 'charts/comprehensive_dashboard.html'
    with open(dashboard_file, 'w', encoding='utf-8') as f:
        f.write(dashboard_html)
    
    print(f"Comprehensive dashboard created: {dashboard_file}")
    return dashboard_file

def open_dashboard():
    """Create and open the comprehensive dashboard"""
    dashboard_file = create_comprehensive_dashboard()
    
    if dashboard_file:
        full_path = os.path.abspath(dashboard_file)
        print(f"Opening dashboard: {full_path}")
        webbrowser.open(f'file://{full_path}')
    
if __name__ == "__main__":
    open_dashboard()