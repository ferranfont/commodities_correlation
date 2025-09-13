"""
Create a comprehensive dashboard with all charts embedded and visible
This creates a single HTML file with all charts displayed inline
"""

import os
import webbrowser

def create_embedded_dashboard():
    """Create dashboard with all charts embedded using iframes"""
    
    # Check if chart files exist
    chart_files = {
        'all_commodities_lines.html': 'All Assets Price Comparison',
        'percentage_growth.html': 'Percentage Growth Analysis',
        'correlation_heatmap.html': 'Correlation Matrix Heatmap',
        'crude_oil_candlestick.html': 'Crude Oil Candlestick',
        'nasdaq_candlestick.html': 'NASDAQ Candlestick',
        'gold_candlestick.html': 'Gold Candlestick',
        'eurusd_candlestick.html': 'EUR/USD Candlestick',
        'commodities_vs_nasdaq.html': 'Assets vs NASDAQ Comparison',
        'rolling_correlations.html': 'Rolling Correlations'
    }
    
    # Verify chart files exist
    missing_charts = []
    for chart_file in chart_files.keys():
        if not os.path.exists(f'charts/{chart_file}'):
            missing_charts.append(chart_file)
    
    if missing_charts:
        print(f"Missing chart files: {missing_charts}")
        print("Please run 'python plot_data.py' first to generate all charts")
        return None
    
    dashboard_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>📊 Commodities Trading Dashboard - All Charts Embedded</title>
    <style>
        body {
            font-family: 'Arial', sans-serif;
            background-color: #ffffff;
            color: #333333;
            margin: 0;
            padding: 15px;
            line-height: 1.6;
        }
        
        .dashboard-container {
            max-width: 1800px;
            margin: 0 auto;
        }
        
        .header {
            text-align: center;
            margin-bottom: 30px;
            padding: 20px;
            background: linear-gradient(135deg, #f8f9fa, #e9ecef);
            border-radius: 15px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        }
        
        .header h1 {
            margin: 0 0 10px 0;
            color: #2c5aa0;
            font-size: 2.5em;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
        }
        
        .header p {
            margin: 5px 0;
            font-size: 1.1em;
            opacity: 0.9;
        }
        
        .navigation {
            position: sticky;
            top: 15px;
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 25px;
            z-index: 1000;
            box-shadow: 0 2px 10px rgba(0,0,0,0.3);
        }
        
        .nav-links {
            display: flex;
            justify-content: center;
            gap: 15px;
            flex-wrap: wrap;
        }
        
        .nav-links a {
            color: #2c5aa0;
            text-decoration: none;
            padding: 8px 16px;
            border: 2px solid #2c5aa0;
            border-radius: 25px;
            transition: all 0.3s ease;
            font-weight: bold;
            font-size: 14px;
        }
        
        .nav-links a:hover {
            background-color: #2c5aa0;
            color: #ffffff;
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(44, 90, 160, 0.3);
        }
        
        .chart-section {
            margin-bottom: 40px;
            background-color: #f8f9fa;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        }
        
        .section-title {
            color: #2c5aa0;
            border-bottom: 3px solid #2c5aa0;
            padding-bottom: 15px;
            margin-bottom: 25px;
            font-size: 1.8em;
            text-align: center;
        }
        
        .chart-frame {
            width: 100%;
            height: 950px;
            border: none;
            border-radius: 10px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.3);
            background-color: #ffffff;
        }
        
        .chart-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 25px;
        }
        
        .chart-grid-item {
            background-color: #e9ecef;
            border-radius: 10px;
            padding: 15px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.2);
        }
        
        .chart-grid-item h4 {
            margin: 0 0 15px 0;
            color: #2c5aa0;
            text-align: center;
            font-size: 1.2em;
        }
        
        .chart-grid-frame {
            width: 100%;
            height: 500px;
            border: none;
            border-radius: 8px;
            background-color: #ffffff;
        }
        
        .stats-box {
            background-color: #e9ecef;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            text-align: center;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 30px;
        }
        
        .stat-item {
            background-color: #dee2e6;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
        }
        
        .stat-value {
            font-size: 1.5em;
            font-weight: bold;
            color: #2c5aa0;
        }
        
        .stat-label {
            font-size: 0.9em;
            opacity: 0.8;
            margin-top: 5px;
        }
        
        .loading {
            text-align: center;
            padding: 50px;
            font-size: 1.2em;
            color: #2c5aa0;
        }
        
        @media (max-width: 768px) {
            .chart-grid {
                grid-template-columns: 1fr;
            }
            .nav-links {
                gap: 10px;
            }
            .nav-links a {
                padding: 6px 12px;
                font-size: 12px;
            }
        }
    </style>
</head>
<body>
    <div class="dashboard-container">
        <!-- Header -->
        <div class="header">
            <h1>🛢️ Commodities Trading Dashboard</h1>
            <p><strong>Assets:</strong> Crude Oil (CL), NASDAQ, Gold (GC), EUR/USD</p>
            <p><strong>Analysis Period:</strong> 20 Years | <strong>Format:</strong> 1275x675 Charts</p>
        </div>
        
        <!-- Navigation -->
        <div class="navigation">
            <div class="nav-links">
                <a href="#overview">📊 Overview</a>
                <a href="#growth">📈 Growth</a>
                <a href="#correlations">🔗 Correlations</a>
                <a href="#candlesticks">🕯️ Candlesticks</a>
                <a href="#nasdaq-vs">🔀 vs NASDAQ</a>
                <a href="#rolling">📈 Rolling</a>
            </div>
        </div>
        
        <!-- Stats Overview -->
        <div class="stats-box">
            <h3>📈 Portfolio Statistics</h3>
            <div class="stats-grid">
                <div class="stat-item">
                    <div class="stat-value">4</div>
                    <div class="stat-label">Active Assets</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">~5,000</div>
                    <div class="stat-label">Days of Data</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">20</div>
                    <div class="stat-label">Years Analysis</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">1275×675</div>
                    <div class="stat-label">Chart Resolution</div>
                </div>
            </div>
        </div>

        <!-- Price Overview Section -->
        <div id="overview" class="chart-section">
            <h2 class="section-title">📊 Assets Price Comparison</h2>
            <iframe src="all_commodities_lines.html" class="chart-frame"></iframe>
        </div>

        <!-- Growth Analysis Section -->
        <div id="growth" class="chart-section">
            <h2 class="section-title">📈 Percentage Growth Analysis</h2>
            <iframe src="percentage_growth.html" class="chart-frame"></iframe>
        </div>

        <!-- Correlations Section -->
        <div id="correlations" class="chart-section">
            <h2 class="section-title">🔗 Correlation Matrix Heatmap</h2>
            <iframe src="correlation_heatmap.html" class="chart-frame"></iframe>
        </div>

        <!-- Individual Candlesticks Section -->
        <div id="candlesticks" class="chart-section">
            <h2 class="section-title">🕯️ Individual Asset Candlesticks</h2>
            <div class="chart-grid">
                <div class="chart-grid-item">
                    <h4>Crude Oil (CL)</h4>
                    <iframe src="crude_oil_candlestick.html" class="chart-grid-frame"></iframe>
                </div>
                <div class="chart-grid-item">
                    <h4>NASDAQ Composite</h4>
                    <iframe src="nasdaq_candlestick.html" class="chart-grid-frame"></iframe>
                </div>
                <div class="chart-grid-item">
                    <h4>Gold (GC)</h4>
                    <iframe src="gold_candlestick.html" class="chart-grid-frame"></iframe>
                </div>
                <div class="chart-grid-item">
                    <h4>EUR/USD Currency Pair</h4>
                    <iframe src="eurusd_candlestick.html" class="chart-grid-frame"></iframe>
                </div>
            </div>
        </div>

        <!-- NASDAQ Comparison Section -->
        <div id="nasdaq-vs" class="chart-section">
            <h2 class="section-title">🔀 Assets vs NASDAQ Comparison</h2>
            <iframe src="commodities_vs_nasdaq.html" class="chart-frame"></iframe>
        </div>

        <!-- Rolling Correlations Section -->
        <div id="rolling" class="chart-section">
            <h2 class="section-title">📈 Rolling Correlations (252-Day Window)</h2>
            <iframe src="rolling_correlations.html" class="chart-frame"></iframe>
        </div>

        <!-- Footer -->
        <div class="stats-box">
            <h3>🎯 Trading Insights</h3>
            <p><strong>Use this dashboard to identify:</strong></p>
            <div class="stats-grid">
                <div class="stat-item">
                    <div class="stat-label">Low correlation periods for diversification</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">EUR/USD strength vs USD assets</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">Cross-asset momentum patterns</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">Risk management opportunities</div>
                </div>
            </div>
        </div>
    </div>

    <script>
        // Smooth scrolling for navigation links
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });

        // Add loading indicators
        document.querySelectorAll('iframe').forEach(iframe => {
            iframe.addEventListener('load', function() {
                console.log('Chart loaded:', this.src);
            });
        });

        console.log('🚀 Commodities Trading Dashboard loaded successfully!');
        console.log('📊 All charts are interactive - zoom, pan, and hover for details');
    </script>
</body>
</html>"""

    # Save the dashboard
    dashboard_file = 'charts/full_dashboard.html'
    with open(dashboard_file, 'w', encoding='utf-8') as f:
        f.write(dashboard_html)
    
    print(f"[OK] Embedded dashboard created: {dashboard_file}")
    return dashboard_file

def open_embedded_dashboard():
    """Create and open the embedded dashboard"""
    dashboard_file = create_embedded_dashboard()
    
    if dashboard_file:
        full_path = os.path.abspath(dashboard_file)
        print(f"[OPENING] Dashboard: {full_path}")
        webbrowser.open(f'file://{full_path}')
        print("[SUCCESS] All charts should now be visible in your browser!")
    else:
        print("[ERROR] Failed to create dashboard")

if __name__ == "__main__":
    open_embedded_dashboard()