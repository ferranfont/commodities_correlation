import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import webbrowser
import os
from datetime import datetime
import numpy as np

def load_all_data():
    """Load selected assets for portfolio analysis"""
    data_files = {
        'CL': 'Crude Oil',
        '^IXIC': 'NASDAQ',
        'GC': 'Gold',
        'EURUSD=X': 'EURUSD'
        # 'SI': 'Silver',    # Excluded from analysis (data kept)
        # 'HG': 'Copper'    # Excluded from analysis (data kept)
    }
    
    data_dict = {}
    for file_key, name in data_files.items():
        try:
            # Read CSV with proper date parsing
            df = pd.read_csv(f'data/{file_key}.csv')
            
            # Convert Date column to datetime and set as index
            if 'Date' in df.columns:
                df['Date'] = pd.to_datetime(df['Date'], utc=True)
                df.set_index('Date', inplace=True)
            else:
                # If first column is already the date but not named
                df.index = pd.to_datetime(df.index, utc=True)
            
            # Convert to datetime if not already
            if not isinstance(df.index, pd.DatetimeIndex):
                df.index = pd.to_datetime(df.index, utc=True)
            
            # Filter weekdays only (Monday=0, Sunday=6)
            try:
                df = df[df.index.dayofweek < 5]
            except AttributeError:
                # If dayofweek doesn't work, skip filtering
                pass
            
            data_dict[name] = df
            print(f"Loaded {name}: {len(df)} days")
        except Exception as e:
            print(f"Error loading {name}: {str(e)}")
    
    return data_dict

def plot_candlestick_chart(data, title, symbol):
    """Create candlestick chart for a single commodity"""
    fig = go.Figure(data=go.Candlestick(
        x=data.index,
        open=data['Open'],
        high=data['High'],
        low=data['Low'],
        close=data['Close'],
        name=symbol
    ))
    
    fig.update_layout(
        title=f'{title} - Daily Candlestick Chart (20 Years)',
        xaxis_title='Date',
        yaxis_title='Price',
        xaxis_rangeslider_visible=False,
        template='plotly_dark',
        height=600
    )
    
    return fig

def plot_all_candlesticks():
    """Create candlestick charts for all commodities"""
    data_dict = load_all_data()
    
    for name, data in data_dict.items():
        fig = plot_candlestick_chart(data, name, name)
        
        # Save as HTML
        filename = f'charts/{name.replace(" ", "_").lower()}_candlestick.html'
        fig.write_html(filename)
        print(f"Saved candlestick chart: {filename}")

def plot_price_lines():
    """Create line chart with all commodities closing prices"""
    data_dict = load_all_data()
    
    fig = go.Figure()
    
    for name, data in data_dict.items():
        fig.add_trace(go.Scatter(
            x=data.index,
            y=data['Close'],
            mode='lines',
            name=name,
            line=dict(width=2)
        ))
    
    fig.update_layout(
        title='All Commodities - Price Comparison (20 Years)',
        xaxis_title='Date',
        yaxis_title='Price',
        template='plotly_dark',
        height=600,
        hovermode='x unified'
    )
    
    # Save as HTML
    filename = 'charts/all_commodities_lines.html'
    fig.write_html(filename)
    print(f"Saved line chart: {filename}")
    
    return fig

def calculate_percentage_growth(data):
    """Calculate percentage growth from base 0"""
    base_price = data['Close'].iloc[0]
    return ((data['Close'] - base_price) / base_price) * 100

def plot_percentage_growth():
    """Create percentage growth chart with base 0 for all commodities"""
    data_dict = load_all_data()
    
    fig = go.Figure()
    
    for name, data in data_dict.items():
        pct_growth = calculate_percentage_growth(data)
        
        fig.add_trace(go.Scatter(
            x=data.index,
            y=pct_growth,
            mode='lines',
            name=name,
            line=dict(width=2)
        ))
    
    fig.add_hline(y=0, line_dash="dash", line_color="white", opacity=0.5)
    
    fig.update_layout(
        title='Commodities Percentage Growth from Initial Point (20 Years)',
        xaxis_title='Date',
        yaxis_title='Percentage Growth (%)',
        template='plotly_dark',
        height=600,
        hovermode='x unified'
    )
    
    # Save as HTML
    filename = 'charts/percentage_growth.html'
    fig.write_html(filename)
    print(f"Saved percentage growth chart: {filename}")
    
    return fig

def calculate_correlation_matrix(data_dict):
    """Calculate correlation matrix for all commodities"""
    
    # Combine all closing prices into one DataFrame
    combined_data = pd.DataFrame()
    for name, data in data_dict.items():
        combined_data[name] = data['Close']
    
    # Calculate correlation matrix
    correlation_matrix = combined_data.corr()
    
    return correlation_matrix

def plot_correlation_heatmap():
    """Create correlation heatmap"""
    data_dict = load_all_data()
    correlation_matrix = calculate_correlation_matrix(data_dict)
    
    fig = go.Figure(data=go.Heatmap(
        z=correlation_matrix.values,
        x=correlation_matrix.columns,
        y=correlation_matrix.index,
        colorscale='RdBu',
        zmid=0,
        text=correlation_matrix.round(3).values,
        texttemplate="%{text}",
        textfont={"size": 12},
        hoverongaps=False
    ))
    
    fig.update_layout(
        title='Commodities Correlation Matrix (20 Years)',
        template='plotly_dark',
        height=600,
        width=700
    )
    
    # Save as HTML
    filename = 'charts/correlation_heatmap.html'
    fig.write_html(filename)
    print(f"Saved correlation heatmap: {filename}")
    
    return fig

def plot_correlations_vs_nasdaq():
    """Create individual correlation plots against NASDAQ"""
    data_dict = load_all_data()
    nasdaq_data = data_dict.get('NASDAQ')
    
    if nasdaq_data is None:
        print("NASDAQ data not found, skipping NASDAQ comparison charts")
        return None
    
    # Create subplots for each commodity vs NASDAQ
    commodities = [name for name in data_dict.keys() if name != 'NASDAQ']
    
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=[f'{commodity} vs NASDAQ' for commodity in commodities],
        specs=[[{"secondary_y": True}, {"secondary_y": True}],
               [{"secondary_y": True}, {"secondary_y": True}]]
    )
    
    positions = [(1,1), (1,2), (2,1), (2,2)]
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']
    
    for i, commodity in enumerate(commodities):
        row, col = positions[i]
        commodity_data = data_dict[commodity]
        
        # Add commodity data
        fig.add_trace(
            go.Scatter(x=commodity_data.index, y=commodity_data['Close'],
                      name=commodity, line=dict(color=colors[i], width=2)),
            row=row, col=col
        )
        
        # Add NASDAQ data on secondary y-axis
        fig.add_trace(
            go.Scatter(x=nasdaq_data.index, y=nasdaq_data['Close'],
                      name='NASDAQ', line=dict(color='orange', width=1, dash='dot'),
                      opacity=0.7),
            row=row, col=col, secondary_y=True
        )
    
    fig.update_layout(
        title='Individual Commodities vs NASDAQ Comparison',
        template='plotly_dark',
        height=800,
        showlegend=True
    )
    
    # Save as HTML
    filename = 'charts/commodities_vs_nasdaq.html'
    fig.write_html(filename)
    print(f"Saved NASDAQ comparison chart: {filename}")
    
    return fig

def plot_rolling_correlations():
    """Plot rolling correlations between commodities and NASDAQ"""
    data_dict = load_all_data()
    
    if 'NASDAQ' not in data_dict:
        print("NASDAQ data not found, skipping rolling correlation charts")
        return None
        
    nasdaq_data = data_dict['NASDAQ']['Close']
    
    fig = go.Figure()
    
    # Calculate 252-day (1 year) rolling correlations
    window = 252
    
    for name, data in data_dict.items():
        if name != 'NASDAQ':
            commodity_data = data['Close']
            
            # Align data
            aligned_nasdaq, aligned_commodity = nasdaq_data.align(commodity_data, join='inner')
            
            # Calculate rolling correlation
            rolling_corr = aligned_nasdaq.rolling(window=window).corr(aligned_commodity)
            
            fig.add_trace(go.Scatter(
                x=rolling_corr.index,
                y=rolling_corr,
                mode='lines',
                name=f'{name} vs NASDAQ',
                line=dict(width=2)
            ))
    
    fig.add_hline(y=0, line_dash="dash", line_color="white", opacity=0.3)
    fig.add_hline(y=0.5, line_dash="dot", line_color="green", opacity=0.3)
    fig.add_hline(y=-0.5, line_dash="dot", line_color="red", opacity=0.3)
    
    fig.update_layout(
        title=f'Rolling Correlation vs NASDAQ ({window} days window)',
        xaxis_title='Date',
        yaxis_title='Correlation Coefficient',
        template='plotly_dark',
        height=600,
        hovermode='x unified'
    )
    
    # Save as HTML
    filename = 'charts/rolling_correlations.html'
    fig.write_html(filename)
    print(f"Saved rolling correlations chart: {filename}")
    
    return fig

def generate_all_charts():
    """Generate all charts and open them in browser"""
    print("Generating all charts...")
    
    # Generate all charts
    plot_all_candlesticks()
    plot_price_lines()
    plot_percentage_growth()
    plot_correlation_heatmap()
    
    # Try to generate NASDAQ comparison charts
    try:
        plot_correlations_vs_nasdaq()
    except Exception as e:
        print(f"Could not generate NASDAQ comparison charts: {str(e)}")
    
    try:
        plot_rolling_correlations()
    except Exception as e:
        print(f"Could not generate rolling correlation charts: {str(e)}")
    
    print("\nAll charts generated successfully!")
    print("\nChart files created:")
    
    # List all generated files
    chart_files = [f for f in os.listdir('charts') if f.endswith('.html')]
    for file in chart_files:
        print(f"- charts/{file}")
    
    return chart_files

def open_chart_in_browser(chart_name):
    """Open specific chart in browser"""
    file_path = os.path.abspath(f'charts/{chart_name}')
    if os.path.exists(file_path):
        webbrowser.open(f'file://{file_path}')
        print(f"Opened {chart_name} in browser")
    else:
        print(f"Chart file {chart_name} not found")

if __name__ == "__main__":
    # Generate all charts
    generate_all_charts()
    
    # Optionally open a specific chart
    # open_chart_in_browser('percentage_growth.html')