from get_yahoo_data import get_yahoo_data, save_data_to_csv

def download_eurusd_only():
    """Download only EURUSD data"""
    print("Downloading EURUSD data...")
    
    # Download EURUSD data
    eurusd_data = get_yahoo_data('EURUSD=X', period="20y", interval="1d")
    
    if eurusd_data is not None:
        # Save to CSV
        csv_file = save_data_to_csv(eurusd_data, 'EURUSD=X')
        print(f"EURUSD data successfully downloaded and saved: {csv_file}")
        print(f"Data range: {eurusd_data.index.min()} to {eurusd_data.index.max()}")
        print(f"Total days: {len(eurusd_data)}")
        print(f"Sample rates: {eurusd_data['Close'].head(3).tolist()}")
    else:
        print("Failed to download EURUSD data")

if __name__ == "__main__":
    download_eurusd_only()