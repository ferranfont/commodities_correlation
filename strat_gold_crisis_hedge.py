"""
Gold Crisis Hedging Strategy
Comprar oro (GC) durante períodos de crisis como hedging/refugio seguro
Basado en comportamiento histórico del oro durante turbulencias de mercado
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import webbrowser
import os
from datetime import datetime

class GoldCrisisHedgeStrategy:
    def __init__(self, initial_capital=10000):
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.positions = []
        self.trades = []
        self.equity_curve = []
        self.crisis_periods = self._define_crisis_periods()
        
    def _define_crisis_periods(self):
        """Definir períodos de crisis donde el oro actúa como refugio"""
        return [
            {
                'name': 'Crisis Financiera 2008',
                'start': '2008-09-15',  # Lehman Brothers
                'end': '2009-06-30',    # Recuperación
                'severity': 'high'
            },
            {
                'name': 'Crisis Deuda Europea',
                'start': '2011-05-01',  # Crisis Grecia
                'end': '2012-07-31',    # ECB intervención
                'severity': 'medium'
            },
            {
                'name': 'Crisis del Petróleo',
                'start': '2014-06-01',  # Colapso petróleo
                'end': '2016-02-01',    # Fondo del petróleo
                'severity': 'medium'
            },
            {
                'name': 'COVID-19 Pandemic',
                'start': '2020-02-20',  # Inicio crash
                'end': '2020-12-31',    # Vacunas/recuperación
                'severity': 'high'
            },
            {
                'name': 'Guerra Ucrania/Inflación',
                'start': '2022-02-24',  # Invasión Rusia
                'end': '2024-01-01',    # Período actual
                'severity': 'medium'
            }
        ]
    
    def load_data(self):
        """Cargar datos de oro y NASDAQ para comparación"""
        print("Cargando datos...")
        
        try:
            # Cargar oro (GC)
            gold_df = pd.read_csv('data/GC.csv')
            gold_df['Date'] = pd.to_datetime(gold_df['Date'], utc=True)
            gold_df.set_index('Date', inplace=True)
            gold_df = gold_df[gold_df.index.dayofweek < 5]  # Solo weekdays
            
            # Cargar NASDAQ para comparación
            nasdaq_df = pd.read_csv('data/^IXIC.csv')
            nasdaq_df['Date'] = pd.to_datetime(nasdaq_df['Date'], utc=True)
            nasdaq_df.set_index('Date', inplace=True)
            nasdaq_df = nasdaq_df[nasdaq_df.index.dayofweek < 5]
            
            # Alinear datos
            aligned_gold, aligned_nasdaq = gold_df['Close'].align(nasdaq_df['Close'], join='inner')
            
            # Crear DataFrame combinado
            self.data = pd.DataFrame({
                'gold_close': aligned_gold,
                'nasdaq_close': aligned_nasdaq
            }).dropna()
            
            # Agregar información de crisis
            self.data['crisis_active'] = False
            self.data['crisis_name'] = ''
            self.data['crisis_severity'] = ''
            
            for crisis in self.crisis_periods:
                start_date = pd.to_datetime(crisis['start'], utc=True)
                end_date = pd.to_datetime(crisis['end'], utc=True)
                
                mask = (self.data.index >= start_date) & (self.data.index <= end_date)
                self.data.loc[mask, 'crisis_active'] = True
                self.data.loc[mask, 'crisis_name'] = crisis['name']
                self.data.loc[mask, 'crisis_severity'] = crisis['severity']
            
            print(f"Datos cargados: {len(self.data)} días")
            print(f"Días en crisis: {self.data['crisis_active'].sum()} ({self.data['crisis_active'].sum()/len(self.data)*100:.1f}%)")
            
            return True
            
        except Exception as e:
            print(f"Error cargando datos: {str(e)}")
            return False
    
    def calculate_position_size(self, crisis_severity, available_capital):
        """Calcular tamaño de posición basado en severidad de crisis"""
        # Oro contracts: $100 por punto, mínimo 1 contrato
        
        severity_multipliers = {
            'high': 0.20,    # 20% del capital en crisis severas
            'medium': 0.15,  # 15% del capital en crisis medias
            'low': 0.10      # 10% del capital en crisis leves
        }
        
        multiplier = severity_multipliers.get(crisis_severity, 0.15)
        position_value = available_capital * multiplier
        
        # 1 contrato de oro = $100 por punto
        # Si oro está a $2000, entonces 1 contrato = $200,000 de exposición
        # Usaremos mini contratos (1/10 del tamaño) = $10 por punto
        gold_price = self.data['gold_close'].iloc[-1] if not self.data.empty else 2000
        contract_value = gold_price * 10  # Mini contrato oro
        
        contracts = max(1, int(position_value / contract_value))
        return contracts
    
    def run_backtest(self):
        """Ejecutar backtest de la estrategia"""
        if not self.load_data():
            return None
        
        print("Ejecutando backtest...")
        
        # Variables de trading
        position = 0  # Número de contratos
        entry_price = 0
        entry_date = None
        portfolio_cash = self.initial_capital
        nasdaq_portfolio = self.initial_capital  # Cartera de referencia
        
        # Para la nueva estrategia: todas las líneas reset en crisis
        nasdaq_continuous_return = 0.0  # Línea azul: NASDAQ continuo global
        in_crisis = False
        
        # Variables para cada crisis (reset a 0 en cada crisis)
        crisis_reset_point = 0.0     # Punto donde todas las líneas empiezan en crisis
        crisis_gold_return = 0.0     # Yellow: retorno oro desde reset
        crisis_nasdaq_return = 0.0   # Blue: retorno nasdaq desde reset  
        crisis_combined_return = 0.0 # Green: retorno combinado desde reset
        
        # Iterar por cada día
        for i, (date, row) in enumerate(self.data.iterrows()):
            current_gold = row['gold_close']
            current_nasdaq = row['nasdaq_close']
            crisis_active = row['crisis_active']
            crisis_severity = row['crisis_severity']
            
            # Calcular rendimiento NASDAQ para comparación
            nasdaq_daily_return = 0
            if i > 0:
                nasdaq_return = (current_nasdaq - self.data['nasdaq_close'].iloc[i-1]) / self.data['nasdaq_close'].iloc[i-1]
                nasdaq_portfolio *= (1 + nasdaq_return)
                nasdaq_daily_return = nasdaq_return
            
            # ENTRAR EN POSICIÓN: Al inicio de crisis
            if crisis_active and position == 0:
                contracts = self.calculate_position_size(crisis_severity, portfolio_cash)
                if contracts > 0:
                    position = contracts
                    entry_price = current_gold
                    entry_date = date
                    
                    # El cash queda disponible (no se usa todo para el margen)
                    used_margin = contracts * current_gold * 0.1  # Margen 10%
                    portfolio_cash -= used_margin
                    
                    print(f"[ENTRY] {date.date()}: Comprando {contracts} contratos oro a ${current_gold:.2f}")
                    print(f"[ENTRY] Crisis: {row['crisis_name']} (severidad: {crisis_severity})")
            
            # SALIR DE POSICIÓN: Al final de crisis o stop loss
            elif position > 0 and (not crisis_active or current_gold < entry_price * 0.95):  # Stop loss 5%
                # Calcular P&L
                price_diff = current_gold - entry_price
                trade_pnl = position * price_diff * 10  # $10 por punto por contrato
                
                # Devolver margen y agregar P&L
                used_margin = position * entry_price * 0.1
                portfolio_cash += used_margin + trade_pnl
                
                # Registrar trade
                self.trades.append({
                    'entry_date': entry_date,
                    'exit_date': date,
                    'entry_price': entry_price,
                    'exit_price': current_gold,
                    'contracts': position,
                    'pnl': trade_pnl,
                    'days_held': (date - entry_date).days,
                    'crisis_name': row['crisis_name'],
                    'exit_reason': 'crisis_end' if not crisis_active else 'stop_loss'
                })
                
                action = "Crisis terminada" if not crisis_active else "Stop Loss activado"
                print(f"[EXIT] {date.date()}: {action} - P&L: ${trade_pnl:,.0f}")
                
                position = 0
                entry_price = 0
                entry_date = None
            
            # Actualizar P&L no realizado si hay posición
            current_portfolio_value = portfolio_cash
            if position > 0:
                unrealized_pnl = position * (current_gold - entry_price) * 10
                current_portfolio_value += unrealized_pnl
            
            # Calcular retorno del día para oro
            gold_daily_return = 0
            if i > 0:
                prev_gold_value = self.equity_curve[i-1]['gold_strategy'] if i > 0 and len(self.equity_curve) > 0 else self.initial_capital
                gold_daily_return = (current_portfolio_value - prev_gold_value) / prev_gold_value if prev_gold_value > 0 else 0
            
            # La línea azul SIEMPRE continúa (NASDAQ real global)
            nasdaq_continuous_return += nasdaq_daily_return * 100
            
            # Detectar inicio/fin de crisis
            if crisis_active and not in_crisis:
                # INICIO DE CRISIS - TODAS LAS LÍNEAS EMPIEZAN EN VALOR ACTUAL DEL BLUE
                in_crisis = True
                crisis_reset_point = nasdaq_continuous_return  # Reset al valor actual del blue
                crisis_gold_return = crisis_reset_point        # Yellow empieza desde blue
                crisis_nasdaq_return = crisis_reset_point      # Blue continúa desde su valor
                crisis_combined_return = crisis_reset_point    # Green empieza desde blue
                
            elif not crisis_active and in_crisis:
                # FIN DE CRISIS - Blue continúa desde donde terminó Green
                in_crisis = False
                # Blue line ahora continúa desde el final de la línea verde
                nasdaq_continuous_return = crisis_combined_return
                # Resetear para próxima crisis
                crisis_gold_return = 0.0
                crisis_nasdaq_return = 0.0
                crisis_combined_return = 0.0
            
            # Actualizar valores durante crisis (desde punto reset)
            if in_crisis:
                # Todas las líneas crecen desde el punto de reset (valor blue actual)
                crisis_gold_return += gold_daily_return * 100        # Yellow: oro desde reset
                crisis_nasdaq_return += nasdaq_daily_return * 100    # Blue: nasdaq desde reset
                crisis_combined_return += (gold_daily_return + nasdaq_daily_return) * 100  # Green: oro + nasdaq desde reset
            
            # Calcular returns en porcentaje desde el inicio
            gold_return_pct = (current_portfolio_value / self.initial_capital - 1) * 100
            nasdaq_return_pct = (nasdaq_portfolio / self.initial_capital - 1) * 100
            
            # Preparar datos para gráfico
            current_blue_line = nasdaq_continuous_return  # Línea azul global (fuera de crisis)
            # Durante crisis: usar valores desde reset
            if in_crisis:
                current_blue_line = crisis_nasdaq_return      # Blue desde reset
                yellow_line_return = crisis_gold_return       # Yellow desde reset
                green_line_return = crisis_combined_return    # Green desde reset
            else:
                yellow_line_return = None
                green_line_return = None
            
            # Guardar equity curve
            self.equity_curve.append({
                'date': date,
                'gold_strategy': current_portfolio_value,
                'nasdaq_only': nasdaq_portfolio,
                'combined_strategy': self.initial_capital * (1 + current_blue_line/100),  # Valor equivalente
                'gold_return_pct': gold_return_pct,
                'nasdaq_return_pct': nasdaq_return_pct,
                'blue_line_return': current_blue_line,
                'yellow_line_return': yellow_line_return,  # Solo durante crisis
                'green_line_return': green_line_return,   # Solo durante crisis
                'crisis_active': crisis_active,
                'gold_price': current_gold,
                'position': position
            })
        
        print(f"Backtest completado: {len(self.trades)} trades ejecutados")
        return True
    
    def calculate_metrics(self):
        """Calcular métricas de performance"""
        if not self.equity_curve:
            return None
        
        equity_df = pd.DataFrame(self.equity_curve)
        
        # Métricas de la estrategia
        final_value = equity_df['gold_strategy'].iloc[-1]
        total_return = (final_value / self.initial_capital - 1) * 100
        
        # Métricas vs NASDAQ
        nasdaq_final = equity_df['nasdaq_only'].iloc[-1]
        nasdaq_return = (nasdaq_final / self.initial_capital - 1) * 100
        
        # Métricas estrategia ajustada (línea azul)
        blue_line_final_return = equity_df['blue_line_return'].iloc[-1]
        
        # Volatilidad y Sharpe
        daily_returns = equity_df['gold_strategy'].pct_change().dropna()
        volatility = daily_returns.std() * np.sqrt(252) * 100
        sharpe = (daily_returns.mean() * 252 / daily_returns.std()) if daily_returns.std() > 0 else 0
        
        # Max Drawdown
        rolling_max = equity_df['gold_strategy'].expanding().max()
        drawdown = (equity_df['gold_strategy'] / rolling_max - 1) * 100
        max_drawdown = drawdown.min()
        
        # Métricas de trades
        if self.trades:
            winning_trades = [t for t in self.trades if t['pnl'] > 0]
            win_rate = len(winning_trades) / len(self.trades) * 100
            avg_win = np.mean([t['pnl'] for t in winning_trades]) if winning_trades else 0
            avg_loss = np.mean([t['pnl'] for t in self.trades if t['pnl'] < 0])
            profit_factor = abs(sum(t['pnl'] for t in winning_trades) / sum(t['pnl'] for t in self.trades if t['pnl'] < 0)) if any(t['pnl'] < 0 for t in self.trades) else float('inf')
        else:
            win_rate = avg_win = avg_loss = profit_factor = 0
        
        self.metrics = {
            'final_value': final_value,
            'total_return': total_return,
            'nasdaq_return': nasdaq_return,
            'blue_line_return': blue_line_final_return,
            'alpha': total_return - nasdaq_return,
            'blue_line_alpha': blue_line_final_return - nasdaq_return,
            'volatility': volatility,
            'sharpe_ratio': sharpe,
            'max_drawdown': max_drawdown,
            'total_trades': len(self.trades),
            'win_rate': win_rate,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'profit_factor': profit_factor
        }
        
        return self.metrics
    
    def create_chart(self):
        """Crear gráfico simple de performance"""
        equity_df = pd.DataFrame(self.equity_curve)
        
        fig = go.Figure()
        
        # Línea azul: NASDAQ (segmentada para evitar conexiones entre crisis)
        # Crear segmentos separados de la línea azul
        crisis_dates = []
        for crisis in self.crisis_periods:
            start_date = pd.to_datetime(crisis['start'], utc=True)
            end_date = pd.to_datetime(crisis['end'], utc=True)
            crisis_dates.append((start_date, end_date))
        
        # Ordenar crisis por fecha de inicio
        crisis_dates.sort(key=lambda x: x[0])
        
        # Crear segmentos de línea azul
        current_start = equity_df['date'].iloc[0]
        segment_count = 0
        
        for start_crisis, end_crisis in crisis_dates:
            # Segmento antes de la crisis (width=2, outside crisis)
            pre_crisis_mask = (equity_df['date'] >= current_start) & (equity_df['date'] < start_crisis)
            pre_crisis_segment = equity_df[pre_crisis_mask]
            
            if len(pre_crisis_segment) > 0:
                show_legend = segment_count == 0
                fig.add_trace(go.Scatter(
                    x=pre_crisis_segment['date'],
                    y=pre_crisis_segment['blue_line_return'],
                    mode='lines',
                    name='NASDAQ' if show_legend else None,
                    showlegend=show_legend,
                    line=dict(color='blue', width=2),  # Width 2 outside crisis
                    hovertemplate='<b>NASDAQ Continuous</b><br>' +
                              'Date: %{x}<br>' +
                              'Return: %{y:.1f}%<br>' +
                              '<extra></extra>'
                ))
                segment_count += 1
            
            # Segmento durante la crisis (width=1, inside crisis)
            crisis_mask = (equity_df['date'] >= start_crisis) & (equity_df['date'] <= end_crisis)
            crisis_segment = equity_df[crisis_mask]
            
            if len(crisis_segment) > 0:
                show_legend = segment_count == 0
                fig.add_trace(go.Scatter(
                    x=crisis_segment['date'],
                    y=crisis_segment['blue_line_return'],
                    mode='lines',
                    name='NASDAQ' if show_legend else None,
                    showlegend=show_legend,
                    line=dict(color='blue', width=1),  # Width 1 inside crisis
                    hovertemplate='<b>NASDAQ Continuous</b><br>' +
                              'Date: %{x}<br>' +
                              'Return: %{y:.1f}%<br>' +
                              '<extra></extra>'
                ))
                segment_count += 1
            
            # Actualizar punto de inicio para el siguiente segmento
            current_start = end_crisis
        
        # Segmento después de la última crisis (width=2, outside crisis)
        final_mask = equity_df['date'] >= current_start
        final_segment = equity_df[final_mask]
        
        if len(final_segment) > 0:
            show_legend = segment_count == 0
            fig.add_trace(go.Scatter(
                x=final_segment['date'],
                y=final_segment['blue_line_return'],
                mode='lines',
                name='NASDAQ' if show_legend else None,
                showlegend=show_legend,
                line=dict(color='blue', width=2),  # Width 2 outside crisis
                hovertemplate='<b>NASDAQ Continuous</b><br>' +
                          'Date: %{x}<br>' +
                          'Return: %{y:.1f}%<br>' +
                          '<extra></extra>'
            ))
        
        # Líneas amarilla y verde: Solo durante crisis, por segmentos separados
        for i, crisis in enumerate(self.crisis_periods):
            start_date = pd.to_datetime(crisis['start'], utc=True)
            end_date = pd.to_datetime(crisis['end'], utc=True)
            
            # Filtrar datos solo para esta crisis específica
            crisis_mask = (equity_df['date'] >= start_date) & (equity_df['date'] <= end_date) & (equity_df['crisis_active'] == True)
            crisis_segment = equity_df[crisis_mask]
            
            # Línea amarilla para esta crisis
            yellow_segment = crisis_segment[crisis_segment['yellow_line_return'].notna()]
            if len(yellow_segment) > 0:
                show_legend = i == 0  # Solo mostrar leyenda en el primer segmento
                fig.add_trace(go.Scatter(
                    x=yellow_segment['date'],
                    y=yellow_segment['yellow_line_return'],
                    mode='lines',
                    name='Gold' if show_legend else None,
                    showlegend=show_legend,
                    line=dict(color='gold', width=1),
                    hovertemplate='<b>Gold Strategy</b><br>' +
                              'Date: %{x}<br>' +
                              'Return: %{y:.1f}%<br>' +
                              f'Crisis: {crisis["name"]}<br>' +
                              '<extra></extra>'
                ))
            
            # Línea verde para esta crisis
            green_segment = crisis_segment[crisis_segment['green_line_return'].notna()]
            if len(green_segment) > 0:
                show_legend = i == 0  # Solo mostrar leyenda en el primer segmento
                fig.add_trace(go.Scatter(
                    x=green_segment['date'],
                    y=green_segment['green_line_return'],
                    mode='lines',
                    name='Combined' if show_legend else None,
                    showlegend=show_legend,
                    line=dict(color='green', width=2),
                    hovertemplate='<b>Combined Profit</b><br>' +
                              'Date: %{x}<br>' +
                              'Gold + NASDAQ: %{y:.1f}%<br>' +
                              f'Crisis: {crisis["name"]}<br>' +
                              '<extra></extra>'
                ))
        
        # Zonas de crisis - fondo rojo pálido solo en áreas de crisis
        for crisis in self.crisis_periods:
            start_date = pd.to_datetime(crisis['start'], utc=True)
            end_date = pd.to_datetime(crisis['end'], utc=True)
            
            fig.add_vrect(
                x0=start_date,
                x1=end_date,
                fillcolor='rgba(255, 0, 0, 0.15)',  # Rojo pálido más suave
                opacity=0.4,
                layer="below",
                line_width=0,
                annotation_text=f"<b>{crisis['name']}</b>",
                annotation_position="top left",
                annotation=dict(
                    font=dict(size=10, color="darkred"),
                    bgcolor="rgba(255,255,255,0.8)",
                    bordercolor="darkred",
                    borderwidth=1
                )
            )
        
        # Red dots: Blue line crisis entry points and Green line crisis exit points
        for crisis in self.crisis_periods:
            start_date = pd.to_datetime(crisis['start'], utc=True)
            end_date = pd.to_datetime(crisis['end'], utc=True)
            
            # Find blue line entry point (start of crisis)
            entry_mask = (equity_df['date'] >= start_date) & (equity_df['crisis_active'] == True)
            entry_data = equity_df[entry_mask]
            if len(entry_data) > 0:
                entry_point = entry_data.iloc[0]
                fig.add_trace(go.Scatter(
                    x=[entry_point['date']],
                    y=[entry_point['blue_line_return']],
                    mode='markers',
                    marker=dict(color='red', size=8, symbol='circle'),
                    name='Crisis Entry',
                    showlegend=False,
                    hovertemplate='<b>Crisis Entry</b><br>' +
                              'Date: %{x}<br>' +
                              'Blue Line: %{y:.1f}%<br>' +
                              f'Crisis: {crisis["name"]}<br>' +
                              '<extra></extra>'
                ))
            
            # Find green line exit point (end of crisis)
            exit_mask = (equity_df['date'] <= end_date) & (equity_df['crisis_active'] == True) & (equity_df['green_line_return'].notna())
            exit_data = equity_df[exit_mask]
            if len(exit_data) > 0:
                exit_point = exit_data.iloc[-1]
                fig.add_trace(go.Scatter(
                    x=[exit_point['date']],
                    y=[exit_point['green_line_return']],
                    mode='markers',
                    marker=dict(color='red', size=8, symbol='circle'),
                    name='Crisis Exit',
                    showlegend=False,
                    hovertemplate='<b>Crisis Exit</b><br>' +
                              'Date: %{x}<br>' +
                              'Green Line: %{y:.1f}%<br>' +
                              f'Crisis: {crisis["name"]}<br>' +
                              '<extra></extra>'
                ))
        
        # Añadir línea de referencia en 0%
        fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
        
        # Layout
        fig.update_layout(
            title='Crisis Strategy Analysis: Gold + NASDAQ Combined (% Returns)',
            xaxis_title='Date',
            yaxis_title='Return (%)',
            template='plotly_white',
            height=675,
            width=1275,
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="top",
                y=-0.1,
                xanchor="center",
                x=0.5
            )
        )
        
        # Guardar
        filename = 'charts/gold_crisis_hedge_strategy.html'
        fig.write_html(filename)
        print(f"[OK] Gráfico guardado: {filename}")
        
        # Abrir en navegador
        full_path = os.path.abspath(filename)
        webbrowser.open(f'file://{full_path}')
        
        return filename
    
    def print_results(self):
        """Imprimir resultados detallados"""
        print("\n" + "="*80)
        print("GOLD CRISIS HEDGING STRATEGY - RESULTADOS")
        print("="*80)
        
        metrics = self.calculate_metrics()
        
        print(f"\n[PERFORMANCE] RENDIMIENTO:")
        print(f"  Capital Inicial:       ${self.initial_capital:,}")
        print(f"  Capital Final (Gold):  ${metrics['final_value']:,.0f}")
        print(f"  Retorno Gold Only:     {metrics['total_return']:+.2f}%")
        print(f"  Retorno Blue Line (NASDAQ Continuous): {metrics['blue_line_return']:+.2f}%")
        print(f"  Retorno NASDAQ:        {metrics['nasdaq_return']:+.2f}%")
        print(f"  Alpha Gold vs NASDAQ:  {metrics['alpha']:+.2f}%")
        print(f"  Alpha Blue vs NASDAQ:  {metrics['blue_line_alpha']:+.2f}%")
        print(f"  Volatilidad:           {metrics['volatility']:.2f}%")
        print(f"  Sharpe Ratio:          {metrics['sharpe_ratio']:.3f}")
        print(f"  Max Drawdown:          {metrics['max_drawdown']:.2f}%")
        
        print(f"\n[TRADES] TRADING:")
        print(f"  Total Trades:          {metrics['total_trades']}")
        print(f"  Win Rate:              {metrics['win_rate']:.1f}%")
        print(f"  Ganancia Promedio:     ${metrics['avg_win']:,.0f}")
        print(f"  Pérdida Promedio:      ${metrics['avg_loss']:,.0f}")
        print(f"  Profit Factor:         {metrics['profit_factor']:.2f}")
        
        print(f"\n[TRADES] DETALLE POR CRISIS:")
        for trade in self.trades:
            print(f"  {trade['crisis_name']}:")
            print(f"    Entrada: {trade['entry_date'].date()} a ${trade['entry_price']:.2f}")
            print(f"    Salida:  {trade['exit_date'].date()} a ${trade['exit_price']:.2f}")
            print(f"    P&L:     ${trade['pnl']:+,.0f} ({trade['days_held']} días)")
            print(f"    Razón:   {trade['exit_reason']}")
    
    def create_performance_table(self):
        """Crear tabla de comparación de performance detallada"""
        metrics = self.calculate_metrics()
        
        # Calcular métricas adicionales para la tabla
        equity_df = pd.DataFrame(self.equity_curve)
        
        # NASDAQ Pure (buy and hold)
        nasdaq_pure_return = metrics['nasdaq_return']
        nasdaq_pure_final = self.initial_capital * (1 + nasdaq_pure_return/100)
        nasdaq_absolute_profit = nasdaq_pure_final - self.initial_capital
        
        # NASDAQ + Gold Combined Strategy (Blue Line)
        combined_return = metrics['blue_line_return']
        combined_final = self.initial_capital * (1 + combined_return/100)
        combined_absolute_profit = combined_final - self.initial_capital
        
        # Calcular volatilidad para NASDAQ puro
        nasdaq_daily_returns = equity_df['nasdaq_only'].pct_change().dropna()
        nasdaq_volatility = nasdaq_daily_returns.std() * np.sqrt(252) * 100
        nasdaq_sharpe = (nasdaq_daily_returns.mean() * 252 / nasdaq_daily_returns.std()) if nasdaq_daily_returns.std() > 0 else 0
        
        # Max Drawdown NASDAQ puro
        nasdaq_rolling_max = equity_df['nasdaq_only'].expanding().max()
        nasdaq_drawdown = (equity_df['nasdaq_only'] / nasdaq_rolling_max - 1) * 100
        nasdaq_max_drawdown = nasdaq_drawdown.min()
        
        # Calcular volatilidad para estrategia combinada (blue line)
        combined_daily_returns = equity_df['gold_strategy'].pct_change().dropna() # Usar como proxy
        combined_volatility = metrics['volatility'] # Ya calculado
        combined_sharpe = metrics['sharpe_ratio']
        combined_max_drawdown = metrics['max_drawdown']
        
        # Datos de la tabla (más compacta)
        table_data = {
            'Métrica': [
                'Capital Inicial',
                'Capital Final',
                'Ganancia Absoluta',
                'Retorno Total (%)',
                'Retorno Anual (%)',
                'Volatilidad (%)',
                'Ratio Sharpe',
                'Drawdown Máx (%)',
                'Profit Factor',
                'Tasa Éxito (%)',
                'Total Trades'
            ],
            'NASDAQ Puro': [
                f"${self.initial_capital:,}",
                f"${nasdaq_pure_final:,.0f}",
                f"${nasdaq_absolute_profit:+,.0f}",
                f"{nasdaq_pure_return:+.1f}%",
                f"{(nasdaq_pure_return/20):+.1f}%",
                f"{nasdaq_volatility:.1f}%",
                f"{nasdaq_sharpe:.2f}",
                f"{nasdaq_max_drawdown:.1f}%",
                f"N/A",
                f"N/A",
                f"N/A"
            ],
            'Estrategia Combinada': [
                f"${self.initial_capital:,}",
                f"${combined_final:,.0f}",
                f"${combined_absolute_profit:+,.0f}",
                f"{combined_return:+.1f}%",
                f"{(combined_return/20):+.1f}%",
                f"{combined_volatility:.1f}%",
                f"{combined_sharpe:.2f}",
                f"{combined_max_drawdown:.1f}%",
                f"{metrics['profit_factor']:.1f}",
                f"{metrics['win_rate']:.0f}%",
                f"{metrics['total_trades']}"
            ]
        }
        
        # Crear DataFrame para la tabla
        df_table = pd.DataFrame(table_data)
        
        # Mostrar en terminal con formato mejorado
        print("\n" + "="*85)
        print("TABLA COMPARATIVA - NASDAQ vs ESTRATEGIA COMBINADA")
        print("="*85)
        
        # Formateo manual para terminal
        print(f"{'Métrica':<20} {'NASDAQ Puro':<25} {'Estrategia Combinada':<25}")
        print("-" * 70)
        
        for i, row in df_table.iterrows():
            metric = row['Métrica']
            nasdaq = row['NASDAQ Puro']
            combined = row['Estrategia Combinada']
            print(f"{metric:<20} {nasdaq:<25} {combined:<25}")
        
        # Análisis adicional
        print("\n" + "="*85)
        print("ANÁLISIS COMPARATIVO")
        print("="*85)
        
        outperformance = combined_return - nasdaq_pure_return
        risk_adj_outperformance = (combined_return/combined_volatility) - (nasdaq_pure_return/nasdaq_volatility) if nasdaq_volatility > 0 and combined_volatility > 0 else 0
        
        crisis_periods_pct = len([d for d in equity_df['crisis_active'] if d]) / len(equity_df) * 100
        
        print(f"RENDIMIENTO:")
        print(f"  * Diferencia Retorno:    {outperformance:+.1f}% (${combined_absolute_profit - nasdaq_absolute_profit:+,.0f})")
        print(f"  * Diferencia Volatilidad: {combined_volatility - nasdaq_volatility:+.1f}%")
        print(f"  * Diferencia Sharpe:     {combined_sharpe - nasdaq_sharpe:+.2f}")
        print(f"  * Mejora Drawdown:       {nasdaq_max_drawdown - combined_max_drawdown:+.1f}%")
        print(f"  * Tiempo en Crisis:      {crisis_periods_pct:.1f}%")
        print(f"  * Trades Ejecutados:     {metrics['total_trades']}")
        print(f"  * Días Promedio:         {np.mean([t['days_held'] for t in self.trades]):.0f}")
        
        # Crear archivo HTML con tabla estilizada
        html_content = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>📊 Comparativa Rendimiento - NASDAQ vs Estrategia Crisis</title>
    <style>
        body {{
            font-family: 'Arial', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            margin: 0;
            padding: 20px;
            min-height: 100vh;
        }}
        
        .container {{
            max-width: 900px;
            margin: 0 auto;
            background: rgba(255,255,255,0.95);
            border-radius: 15px;
            box-shadow: 0 15px 30px rgba(0,0,0,0.3);
            padding: 25px;
        }}
        
        .header {{
            text-align: center;
            margin-bottom: 25px;
            padding: 15px;
            background: linear-gradient(135deg, #2c5aa0, #1e3c72);
            border-radius: 10px;
            color: white;
        }}
        
        .header h1 {{
            margin: 0 0 10px 0;
            font-size: 2.2em;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}
        
        .header p {{
            margin: 5px 0;
            opacity: 0.9;
            font-size: 1.1em;
        }}
        
        .performance-table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 40px;
            box-shadow: 0 8px 20px rgba(0,0,0,0.2);
            border-radius: 10px;
            overflow: hidden;
        }}
        
        .performance-table th {{
            background: linear-gradient(135deg, #2c5aa0, #1e3c72);
            color: white;
            padding: 15px;
            text-align: left;
            font-weight: bold;
            font-size: 1.1em;
        }}
        
        .performance-table td {{
            padding: 12px 15px;
            border-bottom: 1px solid #e0e0e0;
            font-size: 1em;
        }}
        
        .performance-table tr:nth-child(even) {{
            background-color: #f8f9fa;
        }}
        
        .performance-table tr:hover {{
            background-color: #e3f2fd;
            transform: scale(1.01);
            transition: all 0.2s ease;
        }}
        
        .metric-cell {{
            font-weight: bold;
            color: #2c5aa0;
        }}
        
        .nasdaq-cell {{
            color: #ff6b35;
            font-weight: 600;
        }}
        
        .strategy-cell {{
            color: #27ae60;
            font-weight: 600;
        }}
        
        .analysis-section {{
            background: linear-gradient(135deg, #f8f9fa, #e9ecef);
            border-radius: 15px;
            padding: 30px;
            margin-top: 30px;
            box-shadow: 0 8px 15px rgba(0,0,0,0.1);
        }}
        
        .analysis-section h2 {{
            color: #2c5aa0;
            margin-bottom: 20px;
            font-size: 1.8em;
            text-align: center;
        }}
        
        .analysis-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }}
        
        .analysis-item {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.1);
            border-left: 4px solid #2c5aa0;
        }}
        
        .analysis-item h3 {{
            color: #2c5aa0;
            margin-top: 0;
            font-size: 1.3em;
        }}
        
        .metric-value {{
            font-size: 1.4em;
            font-weight: bold;
            margin: 10px 0;
        }}
        
        .positive {{
            color: #27ae60;
        }}
        
        .negative {{
            color: #e74c3c;
        }}
        
        .neutral {{
            color: #f39c12;
        }}
        
        .summary-box {{
            background: linear-gradient(135deg, #27ae60, #2ecc71);
            color: white;
            padding: 20px;
            border-radius: 10px;
            margin-top: 20px;
            text-align: center;
        }}
        
        .summary-box h3 {{
            margin: 0 0 15px 0;
            font-size: 1.5em;
        }}
        
        .footer {{
            text-align: center;
            margin-top: 40px;
            padding: 20px;
            color: #666;
            font-style: italic;
        }}
        
        @media (max-width: 768px) {{
            .container {{
                padding: 20px;
            }}
            .performance-table {{
                font-size: 0.9em;
            }}
            .analysis-grid {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Comparativa de Rendimiento</h1>
            <p><strong>NASDAQ Puro vs Estrategia Combinada Crisis</strong></p>
            <p>Período: 20 Años | Capital: ${self.initial_capital:,} | Crisis: {crisis_periods_pct:.1f}% tiempo</p>
        </div>
        
        <table class="performance-table">
            <thead>
                <tr>
                    <th>Métrica</th>
                    <th>🔵 NASDAQ Puro</th>
                    <th>🟢 Estrategia Combinada</th>
                </tr>
            </thead>
            <tbody>
"""

        # Agregar filas de la tabla
        for i, row in df_table.iterrows():
            metric = row['Métrica']
            nasdaq = row['NASDAQ Puro']
            combined = row['Estrategia Combinada']
            html_content += f"""
                <tr>
                    <td class="metric-cell">{metric}</td>
                    <td class="nasdaq-cell">{nasdaq}</td>
                    <td class="strategy-cell">{combined}</td>
                </tr>"""
        
        html_content += f"""
            </tbody>
        </table>
        
        <div class="summary-box">
            <h3>🏆 Resumen Estrategia</h3>
            <p><strong>Estrategia Combinada</strong> {'superó a' if outperformance > 0 else 'no superó a'} NASDAQ puro por <strong>{abs(outperformance):.1f}%</strong>, 
            operando en modo crisis <strong>{crisis_periods_pct:.1f}%</strong> del tiempo.</p>
            <p><strong>Diferencias clave:</strong> Volatilidad {combined_volatility - nasdaq_volatility:+.1f}% | 
            Drawdown {nasdaq_max_drawdown - combined_max_drawdown:+.1f}% | 
            {metrics['total_trades']} trades ({metrics['win_rate']:.0f}% éxito)</p>
        </div>
        
        <div class="footer">
            <p>📊 Análisis Estrategia Crisis Oro | 
            Basado en 20 años datos históricos ({len(equity_df):,} días trading)</p>
            <p>🚀 Estrategia para trading descorrelacionado en períodos crisis</p>
        </div>
    </div>
</body>
</html>"""
        
        # Guardar archivo HTML
        table_filename = 'charts/performance_comparison_table.html'
        with open(table_filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"\n[OK] Performance table saved: {table_filename}")
        
        # Abrir en navegador
        full_path = os.path.abspath(table_filename)
        webbrowser.open(f'file://{full_path}')
        print(f"[BROWSER] Opening performance comparison table...")
        
        return table_filename

def main():
    """Ejecutar estrategia de hedging con oro"""
    print("GOLD CRISIS HEDGING STRATEGY")
    print("="*40)
    
    strategy = GoldCrisisHedgeStrategy(initial_capital=10000)
    
    if strategy.run_backtest():
        strategy.print_results()
        strategy.create_chart()
        strategy.create_performance_table()
    else:
        print("[ERROR] No se pudo ejecutar el backtest")

if __name__ == "__main__":
    main()