# CLAUDE.md - Commodities Correlation Analysis Project

## Project Overview
**Descorrelaciona tu Trading y Opera Materias Primas: El Impacto de la Divisa sobre el Sistema**

This is an active trading analysis project focused on developing decorrelated trading strategies for commodities, considering the critical impact of currencies on trading systems.

## Quick Commands

### Data Management
```bash
# Download all data (initial setup)
python get_yahoo_data.py

# Download only EURUSD data
python download_eurusd.py

# Test data loading and create sample charts
python test_charts.py
```

### Chart Generation
```bash
# Generate all analysis charts
python plot_data.py

# Open charts dashboard in browser
start charts/index.html
```

### Development Commands
```bash
# Install dependencies
pip install -r requirements.txt

# Run linting (if available)
# python -m flake8 *.py

# Run type checking (if available)
# python -m mypy *.py
```

## Project Structure

```
commodities_correlation/
├── data/                   # CSV data files
│   ├── CL.csv             # Crude Oil data
│   ├── ^IXIC.csv          # NASDAQ data
│   ├── GC.csv             # Gold data
│   ├── EURUSD=X.csv       # EUR/USD data
│   ├── SI.csv             # Silver data (excluded from analysis)
│   └── HG.csv             # Copper data (excluded from analysis)
├── charts/                # Generated HTML charts
├── quant_stat/           # Quantitative statistics
├── outputs/              # Analysis outputs
├── strat_om/            # Trading strategy outputs
├── get_yahoo_data.py    # Main data download API
├── plot_data.py         # Chart generation system
├── test_charts.py       # Testing and validation
└── download_eurusd.py   # EURUSD-specific downloader
```

## Current Portfolio Assets
- **Crude Oil (CL)** - WTI Crude Oil Futures (~5,031 days)
- **NASDAQ (^IXIC)** - NASDAQ Composite Index (~5,032 days)
- **Gold (GC)** - Gold Futures (~5,030 days)
- **EUR/USD** - Euro/US Dollar Currency Pair (~4,583 days)

*Note: Silver and Copper data are preserved but excluded from current analysis*

## Generated Charts
1. **Individual Candlestick Charts** - Daily OHLC for each asset
2. **Price Comparison Lines** - All assets overlaid
3. **Percentage Growth Analysis** - Normalized base-0 comparison
4. **Correlation Heatmap** - 4x4 correlation matrix
5. **Assets vs NASDAQ** - Individual comparisons with NASDAQ
6. **Rolling Correlations** - Time-varying correlation analysis (252-day window)

## Key Features
- **Weekend Filtering** - Automatically excludes weekend data
- **20-Year Historical Data** - Comprehensive long-term analysis
- **Interactive Charts** - Plotly-based HTML charts with dark theme
- **Multi-Asset Analysis** - Stocks, commodities, and forex correlation
- **Currency Impact Analysis** - EUR/USD vs USD-denominated assets

## Trading Strategy Focus
- **Decorrelation Analysis** - Identify periods of low correlation for diversification
- **Currency Hedging** - EUR/USD as hedge against USD strength
- **Cross-Asset Risk Management** - Position sizing based on correlations
- **Seasonal Pattern Recognition** - Identify recurring market cycles

## Data Sources
- **Yahoo Finance API** via yfinance library
- **Daily OHLC Data** with volume and dividend information
- **Timezone-aware** data handling (UTC standardized)
- **Error handling** for missing or incomplete data

## Next Steps for Trading System
1. **Correlation Thresholds** - Define low/high correlation periods
2. **Position Sizing Model** - Based on correlation metrics
3. **Entry/Exit Signals** - Multi-asset signal generation
4. **Backtesting Framework** - Historical strategy validation
5. **Risk Management Rules** - Stop-loss and position limits

## Troubleshooting

### Common Issues
- **Missing data**: Check internet connection and Yahoo Finance availability
- **Chart generation errors**: Ensure all CSV files exist in data/ folder
- **Browser compatibility**: Use modern browsers (Chrome, Firefox, Edge)

### Data Refresh
```bash
# Re-download specific asset
python -c "from get_yahoo_data import get_yahoo_data, save_data_to_csv; data = get_yahoo_data('CL=F'); save_data_to_csv(data, 'CL=F')"
```

## Performance Notes
- **Data loading**: ~5,000+ days per asset
- **Chart generation**: ~10 HTML files created
- **Browser memory**: Charts are interactive and may use significant RAM
- **File sizes**: Each chart ~500KB-2MB depending on complexity

---
*Generated for Claude Code - Active Trading System Development*