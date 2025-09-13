"""
NASDAQ vs Crude Oil Historical Analysis
Dual-axis chart with historical period highlighting
"""

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import webbrowser
import os
from datetime import datetime

def load_nasdaq_cl_data():
    """Load NASDAQ and Crude Oil data"""
    try:
        # Load NASDAQ data
        nasdaq_df = pd.read_csv('data/^IXIC.csv')
        nasdaq_df['Date'] = pd.to_datetime(nasdaq_df['Date'], utc=True)
        nasdaq_df.set_index('Date', inplace=True)
        nasdaq_df = nasdaq_df[nasdaq_df.index.dayofweek < 5]  # Weekdays only
        
        # Load Crude Oil data
        cl_df = pd.read_csv('data/CL.csv')
        cl_df['Date'] = pd.to_datetime(cl_df['Date'], utc=True)
        cl_df.set_index('Date', inplace=True)
        cl_df = cl_df[cl_df.index.dayofweek < 5]  # Weekdays only
        
        print(f"NASDAQ loaded: {len(nasdaq_df)} days")
        print(f"Crude Oil loaded: {len(cl_df)} days")
        
        return nasdaq_df, cl_df
        
    except Exception as e:
        print(f"Error loading data: {str(e)}")
        return None, None

def create_nq_cl_chart():
    """Create NASDAQ vs Crude Oil dual-axis chart with historical periods"""
    
    nasdaq_df, cl_df = load_nasdaq_cl_data()
    if nasdaq_df is None or cl_df is None:
        print("Failed to load data")
        return None
    
    # Calculate percentage growth from first value (base 0)
    def calculate_percentage_growth(data):
        base_price = data['Close'].iloc[0]
        return ((data['Close'] - base_price) / base_price) * 100
    
    nasdaq_pct = calculate_percentage_growth(nasdaq_df)
    cl_pct = calculate_percentage_growth(cl_df)
    
    # Create single axis plot (both series in percentage)
    fig = go.Figure()
    
    # Add NASDAQ percentage line
    fig.add_trace(
        go.Scatter(
            x=nasdaq_df.index,
            y=nasdaq_pct,
            mode='lines',
            name='NASDAQ Composite',
            line=dict(color='#4169E1', width=2),  # Royal Blue
            hovertemplate='<b>NASDAQ</b><br>Date: %{x}<br>Growth: %{y:.1f}%<extra></extra>'
        )
    )
    
    # Add Crude Oil percentage line
    fig.add_trace(
        go.Scatter(
            x=cl_df.index,
            y=cl_pct,
            mode='lines',
            name='Crude Oil (WTI)',
            line=dict(color='#000000', width=2),  # Black
            hovertemplate='<b>Crude Oil</b><br>Date: %{x}<br>Growth: %{y:.1f}%<extra></extra>'
        )
    )
    
    # Historical periods with more precise dates
    historical_periods = [
        {
            'name': 'Crisis Financiera',
            'start': '2008-09-15',  # Lehman Brothers collapse
            'end': '2009-06-30',    # Market recovery start
            'color': 'rgba(255, 99, 71, 0.35)',  # Light red less transparent
            'description': 'Crisis Subprime/Lehman'
        },
        {
            'name': 'Recuperación Post-Crisis',
            'start': '2010-01-01',
            'end': '2012-12-31',
            'color': 'rgba(50, 205, 50, 0.35)',  # Light green less transparent
            'description': 'QE y Estímulos Masivos'
        },
        {
            'name': 'Crisis del Petróleo',
            'start': '2014-06-01',  # Oil price peak before collapse
            'end': '2016-02-01',    # Oil price bottom
            'color': 'rgba(255, 140, 0, 0.35)',  # Light orange less transparent
            'description': 'Colapso Petróleo -75%'
        },
        {
            'name': 'COVID-19',
            'start': '2020-02-20',  # Market peak before crash
            'end': '2020-12-31',    # Vaccine rollout
            'color': 'rgba(138, 43, 226, 0.35)',  # Light purple less transparent
            'description': 'Pandemia y Estímulos'
        },
        {
            'name': 'Guerra Ucrania/Inflación',
            'start': '2022-02-24',  # Russia invasion
            'end': '2024-01-01',    # Current period
            'color': 'rgba(255, 215, 0, 0.35)',  # Light gold less transparent
            'description': 'Inflación y Geopolítica'
        }
    ]
    
    # Add shaded vertical areas for historical periods
    for period in historical_periods:
        fig.add_vrect(
            x0=period['start'],
            x1=period['end'],
            fillcolor=period['color'],
            opacity=0.3,
            layer="below",
            line_width=0
        )
        
        # Add separate annotation for each period
        fig.add_annotation(
            x=pd.to_datetime(period['start']) + (pd.to_datetime(period['end']) - pd.to_datetime(period['start'])) / 2,
            y=1,
            yref="paper",
            text=f"<b>{period['name']}</b><br><span style='font-size:9px'>{period['description']}</span>",
            showarrow=False,
            bgcolor="rgba(255,255,255,0.8)",
            bordercolor="gray",
            borderwidth=1,
            font=dict(size=10),
            yanchor="top"
        )
    
    # Update y-axis for percentage growth
    fig.update_yaxes(
        title_text="<b>Crecimiento Porcentual (%)</b>",
        title_font=dict(size=14),
        showgrid=False,  # Remove grid lines
        zeroline=True,
        zerolinecolor='gray',
        zerolinewidth=1
    )
    
    # Update x-axis
    fig.update_xaxes(
        title_text="<b>Fecha</b>",
        title_font=dict(size=14),
        showgrid=False  # Remove grid lines
    )
    
    # Update layout
    fig.update_layout(
        title={
            'text': '<b>NASDAQ vs Petróleo Crudo: Análisis Histórico con Períodos Clave</b>',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18}
        },
        template='plotly_white',
        height=675,
        width=1275,
        hovermode='x unified',
        legend=dict(
            x=0.5,
            y=-0.15,
            xanchor='center',
            yanchor='top',
            bgcolor='rgba(255,255,255,0.8)',
            bordercolor='gray',
            borderwidth=1,
            orientation='h'
        ),
        margin=dict(t=80, b=60, l=80, r=80),
        showlegend=True
    )
    
    # Add subtitle with correlation info
    fig.add_annotation(
        text="<i>Períodos sombreados muestran eventos históricos clave que afectaron las correlaciones entre activos</i>",
        x=0.5,
        y=-0.12,
        xref="paper",
        yref="paper",
        showarrow=False,
        font=dict(size=11, color="gray"),
        xanchor="center"
    )
    
    return fig

def main():
    """Generate and save the NASDAQ vs Crude Oil chart"""
    print("Generando gráfico NASDAQ vs Petróleo Crudo...")
    print("=" * 50)
    
    fig = create_nq_cl_chart()
    
    if fig:
        # Save chart
        filename = 'charts/nasdaq_vs_crude_oil_historical.html'
        fig.write_html(filename)
        print(f"[OK] Grafico guardado: {filename}")
        
        # Open in browser
        full_path = os.path.abspath(filename)
        webbrowser.open(f'file://{full_path}')
        print(f"[BROWSER] Abriendo en navegador: {full_path}")
        
        print("\n[PERIODS] Periodos historicos marcados:")
        periods = [
            "- Crisis Financiera (Sep 2008 - Jun 2009)",
            "- Recuperacion Post-Crisis (2010-2012)", 
            "- Crisis del Petroleo (Jun 2014 - Feb 2016)",
            "- COVID-19 (Feb-Dec 2020)",
            "- Guerra Ucrania/Inflacion (Feb 2022-2024)"
        ]
        for period in periods:
            print(f"  {period}")
            
    else:
        print("[ERROR] Error al generar el grafico")

if __name__ == "__main__":
    main()