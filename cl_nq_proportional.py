"""
Análisis Proporcional CL vs NQ
Calcula cuántos lotes de Crude Oil (CL) equivalen al NASDAQ (NQ)
Y análisis de relaciones de subida/bajada entre ambos productos
"""

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import webbrowser
import os
from datetime import datetime

def load_cl_nq_data():
    """Cargar datos de CL y NQ alineados"""
    try:
        # Cargar NASDAQ
        nq_df = pd.read_csv('data/^IXIC.csv')
        nq_df['Date'] = pd.to_datetime(nq_df['Date'], utc=True)
        nq_df.set_index('Date', inplace=True)
        nq_df = nq_df[nq_df.index.dayofweek < 5]  # Solo días laborables
        
        # Cargar Crude Oil
        cl_df = pd.read_csv('data/CL.csv')
        cl_df['Date'] = pd.to_datetime(cl_df['Date'], utc=True)
        cl_df.set_index('Date', inplace=True)
        cl_df = cl_df[cl_df.index.dayofweek < 5]  # Solo días laborables
        
        # Alinear datos por fechas comunes
        aligned_nq, aligned_cl = nq_df['Close'].align(cl_df['Close'], join='inner')
        
        print(f"Datos alineados: {len(aligned_nq)} días")
        print(f"Período: {aligned_nq.index.min().date()} a {aligned_nq.index.max().date()}")
        
        return aligned_nq, aligned_cl
        
    except Exception as e:
        print(f"Error cargando datos: {str(e)}")
        return None, None

def calculate_proportional_analysis(nq_data, cl_data):
    """Calcular análisis proporcional entre CL y NQ"""
    
    # 1. Ratio NQ/CL (cuántos CL por cada punto de NQ)
    ratio_nq_cl = nq_data / cl_data
    
    # 2. Cambios porcentuales diarios
    nq_pct_change = nq_data.pct_change()
    cl_pct_change = cl_data.pct_change()
    
    # 3. Análisis de movimientos direccionales
    nq_up = nq_pct_change > 0
    nq_down = nq_pct_change < 0
    cl_up = cl_pct_change > 0
    cl_down = cl_pct_change < 0
    
    # 4. Coincidencias direccionales
    both_up = nq_up & cl_up
    both_down = nq_down & cl_down
    opposite = (nq_up & cl_down) | (nq_down & cl_up)
    
    # 5. Estadísticas de movimientos
    total_days = len(nq_pct_change.dropna())
    both_up_pct = (both_up.sum() / total_days) * 100
    both_down_pct = (both_down.sum() / total_days) * 100
    opposite_pct = (opposite.sum() / total_days) * 100
    correlation_directional = both_up_pct + both_down_pct
    
    # 6. Magnitudes promedio cuando se mueven en la misma dirección
    avg_nq_up_when_both_up = nq_pct_change[both_up].mean() * 100
    avg_cl_up_when_both_up = cl_pct_change[both_up].mean() * 100
    avg_nq_down_when_both_down = nq_pct_change[both_down].mean() * 100
    avg_cl_down_when_both_down = cl_pct_change[both_down].mean() * 100
    
    # 7. Ratio de volatilidad
    nq_volatility = nq_pct_change.std() * 100
    cl_volatility = cl_pct_change.std() * 100
    volatility_ratio = cl_volatility / nq_volatility
    
    stats = {
        'ratio_promedio': ratio_nq_cl.mean(),
        'ratio_actual': ratio_nq_cl.iloc[-1],
        'ratio_min': ratio_nq_cl.min(),
        'ratio_max': ratio_nq_cl.max(),
        'correlacion_direccional': correlation_directional,
        'ambos_suben_pct': both_up_pct,
        'ambos_bajan_pct': both_down_pct,
        'movimientos_opuestos_pct': opposite_pct,
        'promedio_nq_subida': avg_nq_up_when_both_up,
        'promedio_cl_subida': avg_cl_up_when_both_up,
        'promedio_nq_bajada': avg_nq_down_when_both_down,
        'promedio_cl_bajada': avg_cl_down_when_both_down,
        'volatilidad_nq': nq_volatility,
        'volatilidad_cl': cl_volatility,
        'ratio_volatilidad': volatility_ratio,
        'total_dias': total_days
    }
    
    return ratio_nq_cl, nq_pct_change, cl_pct_change, stats

def create_proportional_chart(nq_data, cl_data, ratio_data, stats):
    """Crear gráfico de análisis proporcional"""
    
    # Crear subplots: 3 filas
    fig = make_subplots(
        rows=3, cols=1,
        subplot_titles=[
            'Ratio NQ/CL: Cuántos Puntos de CL por cada Punto de NQ',
            'Precios Normalizados (Base = 100)',
            'Cambios Porcentuales Diarios Comparados'
        ],
        vertical_spacing=0.08,
        specs=[[{"secondary_y": False}],
               [{"secondary_y": False}],
               [{"secondary_y": False}]]
    )
    
    # 1. Gráfico de Ratio NQ/CL
    fig.add_trace(
        go.Scatter(
            x=ratio_data.index,
            y=ratio_data,
            mode='lines',
            name='Ratio NQ/CL',
            line=dict(color='#FF6B35', width=2),
            hovertemplate='<b>Ratio NQ/CL</b><br>Date: %{x}<br>Ratio: %{y:.1f}<extra></extra>'
        ),
        row=1, col=1
    )
    
    # Línea promedio del ratio
    fig.add_hline(
        y=stats['ratio_promedio'],
        line_dash="dash",
        line_color="gray",
        opacity=0.7,
        annotation_text=f"Promedio: {stats['ratio_promedio']:.1f}",
        row=1, col=1
    )
    
    # 2. Precios Normalizados (base 100)
    nq_normalized = (nq_data / nq_data.iloc[0]) * 100
    cl_normalized = (cl_data / cl_data.iloc[0]) * 100
    
    fig.add_trace(
        go.Scatter(
            x=nq_normalized.index,
            y=nq_normalized,
            mode='lines',
            name='NASDAQ (Normalizado)',
            line=dict(color='#4169E1', width=2),
            hovertemplate='<b>NASDAQ</b><br>Date: %{x}<br>Valor: %{y:.1f}<extra></extra>'
        ),
        row=2, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=cl_normalized.index,
            y=cl_normalized,
            mode='lines',
            name='Crude Oil (Normalizado)',
            line=dict(color='#000000', width=2),
            hovertemplate='<b>Crude Oil</b><br>Date: %{x}<br>Valor: %{y:.1f}<extra></extra>'
        ),
        row=2, col=1
    )
    
    # 3. Cambios porcentuales diarios
    nq_pct = nq_data.pct_change() * 100
    cl_pct = cl_data.pct_change() * 100
    
    fig.add_trace(
        go.Scatter(
            x=nq_pct.index,
            y=nq_pct,
            mode='markers',
            name='NASDAQ % Diario',
            marker=dict(color='#4169E1', size=3, opacity=0.6),
            hovertemplate='<b>NASDAQ</b><br>Date: %{x}<br>Cambio: %{y:.2f}%<extra></extra>'
        ),
        row=3, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=cl_pct.index,
            y=cl_pct,
            mode='markers',
            name='Crude Oil % Diario',
            marker=dict(color='#000000', size=3, opacity=0.6),
            hovertemplate='<b>Crude Oil</b><br>Date: %{x}<br>Cambio: %{y:.2f}%<extra></extra>'
        ),
        row=3, col=1
    )
    
    # Líneas de referencia en 0% para cambios diarios
    fig.add_hline(y=0, line_dash="dot", line_color="gray", opacity=0.5, row=3, col=1)
    
    # Actualizar layout
    fig.update_layout(
        title={
            'text': '<b>Análisis Proporcional CL vs NQ: Ratios y Relaciones</b>',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18}
        },
        template='plotly_white',
        height=900,
        width=1275,
        showlegend=True,
        legend=dict(
            x=1.02,
            y=1,
            bgcolor='rgba(255,255,255,0.8)',
            bordercolor='gray',
            borderwidth=1
        )
    )
    
    # Remover grids
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=False)
    
    return fig

def print_analysis_summary(stats):
    """Imprimir resumen del análisis"""
    print("\n" + "="*60)
    print("ANALISIS PROPORCIONAL CL vs NQ - RESUMEN")
    print("="*60)
    
    print(f"\n[RATIOS] RATIOS BASICOS:")
    print(f"  - Ratio Promedio NQ/CL: {stats['ratio_promedio']:.1f}")
    print(f"  - Ratio Actual NQ/CL: {stats['ratio_actual']:.1f}")
    print(f"  - Rango: {stats['ratio_min']:.1f} - {stats['ratio_max']:.1f}")
    print(f"  -> INTERPRETACION: 1 punto de NQ = {stats['ratio_promedio']:.1f} puntos de CL")
    
    print(f"\n[DIRECCION] CORRELACION DIRECCIONAL:")
    print(f"  - Ambos Suben: {stats['ambos_suben_pct']:.1f}%")
    print(f"  - Ambos Bajan: {stats['ambos_bajan_pct']:.1f}%")
    print(f"  - Movimientos Opuestos: {stats['movimientos_opuestos_pct']:.1f}%")
    print(f"  - Correlacion Total: {stats['correlacion_direccional']:.1f}%")
    
    print(f"\n[MAGNITUDES] MAGNITUDES PROMEDIO (cuando coinciden):")
    print(f"  - NQ sube: +{stats['promedio_nq_subida']:.2f}%")
    print(f"  - CL sube: +{stats['promedio_cl_subida']:.2f}%")
    print(f"  - NQ baja: {stats['promedio_nq_bajada']:.2f}%")
    print(f"  - CL baja: {stats['promedio_cl_bajada']:.2f}%")
    
    print(f"\n[VOLATILIDAD] VOLATILIDAD:")
    print(f"  - NASDAQ: {stats['volatilidad_nq']:.2f}%")
    print(f"  - Crude Oil: {stats['volatilidad_cl']:.2f}%")
    print(f"  - Ratio CL/NQ: {stats['ratio_volatilidad']:.2f}x")
    print(f"  -> CL es {stats['ratio_volatilidad']:.1f}x mas volatil que NQ")
    
    print(f"\n[EQUIVALENCIA] EQUIVALENCIA DE LOTES:")
    avg_cl_price = 70  # Precio promedio aproximado del CL
    avg_nq_price = stats['ratio_promedio'] * avg_cl_price
    print(f"  - Si CL = ${avg_cl_price}, entonces NQ = ${avg_nq_price:.0f}")
    print(f"  - 1 lote NQ = {stats['ratio_promedio']:.1f} lotes CL (en terminos de precio)")
    
    print(f"\n[STATS] ESTADISTICAS:")
    print(f"  - Total dias analizados: {stats['total_dias']:,}")
    print(f"  - Periodo completo de datos disponibles")

def main():
    """Función principal"""
    print("Análisis Proporcional CL vs NQ")
    print("="*40)
    
    # Cargar datos
    nq_data, cl_data = load_cl_nq_data()
    if nq_data is None or cl_data is None:
        print("Error cargando datos")
        return
    
    # Calcular análisis proporcional
    ratio_data, nq_pct, cl_pct, stats = calculate_proportional_analysis(nq_data, cl_data)
    
    # Crear gráfico
    fig = create_proportional_chart(nq_data, cl_data, ratio_data, stats)
    
    # Guardar y mostrar
    filename = 'charts/cl_nq_proportional_analysis.html'
    fig.write_html(filename)
    print(f"\n[OK] Gráfico guardado: {filename}")
    
    # Mostrar resumen
    print_analysis_summary(stats)
    
    # Abrir en navegador
    full_path = os.path.abspath(filename)
    webbrowser.open(f'file://{full_path}')
    print(f"\n[BROWSER] Abriendo análisis en navegador...")

if __name__ == "__main__":
    main()