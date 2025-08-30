import yfinance as yf
import pandas as pd
import os
from datetime import datetime, timedelta

def create_data_folders():
    """Create necessary folder structure"""
    folders = ['data', 'quant_stat', 'charts', 'outputs', 'strat_om']
    for folder in folders:
        if not os.path.exists(folder):
            os.makedirs(folder)
            print(f"Created folder: {folder}")

def get_yahoo_data(symbol, period="20y", interval="1d"):
    """
    Download data from Yahoo Finance
    
    Args:
        symbol (str): Stock/commodity symbol
        period (str): Period to download (20y for 20 years)
        interval (str): Data interval (1d for daily)
    
    Returns:
        pd.DataFrame: Downloaded data
    """
    try:
        ticker = yf.Ticker(symbol)
        data = ticker.history(period=period, interval=interval)
        
        # Filter out weekends (Monday=0, Sunday=6)
        data = data[data.index.dayofweek < 5]
        
        if data.empty:
            print(f"No data found for symbol: {symbol}")
            return None
            
        print(f"Downloaded {len(data)} days of data for {symbol}")
        return data
        
    except Exception as e:
        print(f"Error downloading data for {symbol}: {str(e)}")
        return None

def save_data_to_csv(data, symbol, folder='data'):
    """Save data to CSV file in specified folder"""
    if data is not None and not data.empty:
        filename = f"{folder}/{symbol.replace('=F', '')}.csv"
        data.to_csv(filename)
        print(f"Saved data to: {filename}")
        return filename
    return None

def download_all_commodities():
    """Download all specified commodities and save to CSV"""
    
    # Create folder structure
    create_data_folders()
    
    # Define symbols to download
    symbols = {
        'CL=F': 'Crude Oil',           # WTI Crude Oil
        '^IXIC': 'NASDAQ',             # NASDAQ Composite
        'GC=F': 'Gold',                # Gold Futures
        'SI=F': 'Silver',              # Silver Futures
        'HG=F': 'Copper',              # Copper Futures
        'EURUSD=X': 'EURUSD'           # EUR/USD Currency Pair
    }
    
    downloaded_data = {}
    
    for symbol, name in symbols.items():
        print(f"\nDownloading {name} ({symbol})...")
        data = get_yahoo_data(symbol, period="20y", interval="1d")
        
        if data is not None:
            # Save to CSV
            csv_file = save_data_to_csv(data, symbol)
            downloaded_data[symbol] = {
                'data': data,
                'name': name,
                'csv_file': csv_file
            }
        else:
            print(f"Failed to download {name}")
    
    return downloaded_data

def load_data_from_csv(symbol, folder='data'):
    """Load data from CSV file"""
    try:
        filename = f"{folder}/{symbol.replace('=F', '')}.csv"
        data = pd.read_csv(filename, index_col=0, parse_dates=True)
        print(f"Loaded data from: {filename}")
        return data
    except Exception as e:
        print(f"Error loading data from CSV: {str(e)}")
        return None

if __name__ == "__main__":
    print("Starting data download process...")
    downloaded_data = download_all_commodities()
    
    print(f"\nDownload complete! Downloaded data for {len(downloaded_data)} symbols.")
    for symbol, info in downloaded_data.items():
        print(f"- {info['name']} ({symbol}): {len(info['data'])} days")