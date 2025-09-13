"""
Estrategia de Trading CL vs NQ - EVENT BASED
Estrategia de pairs trading activada solo durante eventos históricos específicos
Basada en períodos de alta volatilidad y decorrelación
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import webbrowser
import os
from datetime import datetime

class CLNQEventStrategy:
    def __init__(self, initial_capital=10000):
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.positions = []
        self.trades = []
        self.equity_curve = []
        self.event_periods = self._define_event_periods()
        
    def _define_event_periods(self):
        """Definir períodos de eventos históricos para activar trading"""
        return [
            {
                'name': 'Crisis Financiera',
                'start': '2008-09-15',
                'end': '2009-06-30',
                'type': 'crisis',
                'volatility_multiplier': 2.0
            },
            {
                'name': 'Recuperación Post-Crisis',
                'start': '2010-01-01',
                'end': '2012-12-31',
                'type': 'recovery',
                'volatility_multiplier': 1.2
            },
            {
                'name': 'Crisis del Petróleo',
                'start': '2014-06-01',
                'end': '2016-02-01',
                'type': 'oil_crisis',
                'volatility_multiplier': 1.8
            },
            {
                'name': 'COVID-19',
                'start': '2020-02-20',
                'end': '2020-12-31',
                'type': 'pandemic',
                'volatility_multiplier': 2.5
            },
            {
                'name': 'Guerra Ucrania/Inflación',
                'start': '2022-02-24',
                'end': '2024-01-01',
                'type': 'geopolitical',
                'volatility_multiplier': 1.5
            }
        ]
    
    def load_data(self):
        """Cargar y alinear datos de CL, NQ y S&P 500"""
        try:
            # Cargar NASDAQ
            nq_df = pd.read_csv('data/^IXIC.csv')
            nq_df['Date'] = pd.to_datetime(nq_df['Date'], utc=True)
            nq_df.set_index('Date', inplace=True)
            nq_df = nq_df[nq_df.index.dayofweek < 5]
            
            # Cargar Crude Oil
            cl_df = pd.read_csv('data/CL.csv')
            cl_df['Date'] = pd.to_datetime(cl_df['Date'], utc=True)
            cl_df.set_index('Date', inplace=True)
            cl_df = cl_df[cl_df.index.dayofweek < 5]
            
            # Buscar datos de S&P 500 (intentar varios nombres posibles)
            sp_data = None
            sp_files = ['^GSPC.csv', 'SPX.csv', 'SP500.csv']
            
            for sp_file in sp_files:
                try:
                    sp_df = pd.read_csv(f'data/{sp_file}')
                    sp_df['Date'] = pd.to_datetime(sp_df['Date'], utc=True)
                    sp_df.set_index('Date', inplace=True)
                    sp_df = sp_df[sp_df.index.dayofweek < 5]
                    sp_data = sp_df['Close']
                    print(f"S&P 500 cargado desde: {sp_file}")
                    break
                except FileNotFoundError:
                    continue
            
            if sp_data is None:
                print("Archivo S&P 500 no encontrado, usando NASDAQ como proxy")
                sp_data = nq_df['Close'] * 0.25  # Aproximación S&P vs NASDAQ
            
            # Alinear datos
            aligned_nq, aligned_cl = nq_df['Close'].align(cl_df['Close'], join='inner')
            aligned_sp = sp_data.reindex(aligned_nq.index).ffill()
            
            # Crear DataFrame combinado
            self.data = pd.DataFrame({
                'NQ': aligned_nq,
                'CL': aligned_cl,
                'SP': aligned_sp,
                'NQ_pct': aligned_nq.pct_change(),
                'CL_pct': aligned_cl.pct_change(),
                'SP_pct': aligned_sp.pct_change(),
                'NQ_CL_ratio': aligned_nq / aligned_cl
            }).dropna()
            
            # Marcar períodos de eventos
            self.data['event_active'] = False
            self.data['event_type'] = ''
            self.data['volatility_multiplier'] = 1.0
            
            for event in self.event_periods:
                start_date = pd.to_datetime(event['start'], utc=True)
                end_date = pd.to_datetime(event['end'], utc=True)
                mask = (self.data.index >= start_date) & (self.data.index <= end_date)
                self.data.loc[mask, 'event_active'] = True
                self.data.loc[mask, 'event_type'] = event['type']
                self.data.loc[mask, 'volatility_multiplier'] = event['volatility_multiplier']
            
            print(f"Datos cargados: {len(self.data)} dias")
            print(f"Dias con eventos activos: {self.data['event_active'].sum()}")
            print(f"Porcentaje en eventos: {self.data['event_active'].mean()*100:.1f}%")
            
            return True
            
        except Exception as e:
            print(f"Error cargando datos: {str(e)}")
            return False
    
    def generate_signals(self):
        """Generar señales FORZADAS durante todos los eventos históricos"""
        
        # Inicializar señales
        signals = pd.Series(0, index=self.data.index)
        
        # Solo operar durante eventos
        event_mask = self.data['event_active']
        
        if event_mask.sum() == 0:
            print("No hay períodos de eventos definidos")
            self.data['signal'] = signals
            return signals
        
        # FORZAR ENTRADAS al inicio de cada evento
        current_event = None
        days_in_event = 0
        
        for i, row in self.data.iterrows():
            if row['event_active']:
                event_type = row['event_type']
                
                # Detectar nuevo evento
                if current_event != event_type:
                    current_event = event_type
                    days_in_event = 0
                    
                    # ENTRADA FORZADA al inicio de cada evento
                    nq_pct = row['NQ_pct'] if not pd.isna(row['NQ_pct']) else 0
                    cl_pct = row['CL_pct'] if not pd.isna(row['CL_pct']) else 0
                    
                    # Estrategia específica por evento (FORZADA)
                    if event_type == 'crisis':
                        # Crisis: Apostar por CL como refugio vs NQ
                        signals.loc[i] = 1  # Long CL / Short NQ
                    
                    elif event_type == 'recovery':
                        # Recuperación: NQ fuerte, CL moderado
                        signals.loc[i] = -1  # Short CL / Long NQ
                    
                    elif event_type == 'oil_crisis':
                        # Crisis petróleo: Long CL cuando esté barato
                        signals.loc[i] = 1  # Long CL / Short NQ
                    
                    elif event_type == 'pandemic':
                        # Pandemia: Volatilidad extrema, refugio en CL
                        signals.loc[i] = 1  # Long CL / Short NQ
                    
                    elif event_type == 'geopolitical':
                        # Geopolítica: CL beneficiado por tensiones
                        signals.loc[i] = 1  # Long CL / Short NQ
                
                days_in_event += 1
                
                # Mantener posición durante primeros 30 días del evento
                if days_in_event <= 30 and signals.loc[i] == 0:
                    # Mantener la señal del primer día
                    prev_signal = signals[signals != 0].iloc[-1] if (signals != 0).any() else 1
                    signals.loc[i] = prev_signal
                
                # Cambios dinámicos dentro del evento después de 30 días
                elif days_in_event > 30:
                    # Lógica más agresiva para cambios mid-event
                    if abs(nq_pct) > 0.02 or abs(cl_pct) > 0.03:
                        if nq_pct * cl_pct < 0:  # Movimientos opuestos
                            if nq_pct > 0 and cl_pct < 0:
                                signals.loc[i] = -1  # NQ up, CL down -> Short CL
                            elif nq_pct < 0 and cl_pct > 0:
                                signals.loc[i] = 1   # NQ down, CL up -> Long CL
                        
                        # Revertir si movimientos extremos en CL
                        if abs(cl_pct) > 0.08:  # CL movimiento extremo >8%
                            current_signal = signals[signals != 0].iloc[-1] if (signals != 0).any() else 1
                            signals.loc[i] = -current_signal  # Reversar
                
            else:
                # Fuera de eventos, cerrar posiciones
                current_event = None
                days_in_event = 0
        
        # NO suavizar para mantener entradas forzadas
        self.data['signal'] = signals
        
        return signals
    
    def backtest(self):
        """Ejecutar backtest solo durante eventos y calcular curvas comparativas"""
        
        position = 0
        entry_price_cl = 0
        entry_price_nq = 0
        entry_date = None
        days_in_position = 0
        
        # Inicializar carteras comparativas
        nq_portfolio = self.initial_capital  # Solo NASDAQ
        combined_portfolio = self.initial_capital  # NQ + Event Strategy
        sp_portfolio = self.initial_capital  # Solo S&P 500
        
        for i in range(1, len(self.data)):
            current_signal = self.data['signal'].iloc[i]
            prev_signal = self.data['signal'].iloc[i-1]
            
            current_cl = self.data['CL'].iloc[i]
            current_nq = self.data['NQ'].iloc[i]
            current_sp = self.data['SP'].iloc[i]
            prev_cl = self.data['CL'].iloc[i-1]
            prev_nq = self.data['NQ'].iloc[i-1]
            prev_sp = self.data['SP'].iloc[i-1]
            
            date = self.data.index[i]
            event_active = self.data['event_active'].iloc[i]
            
            # Calcular rendimientos diarios
            nq_daily_return = (current_nq - prev_nq) / prev_nq
            sp_daily_return = (current_sp - prev_sp) / prev_sp
            
            # Actualizar carteras de referencia
            nq_portfolio *= (1 + nq_daily_return)
            sp_portfolio *= (1 + sp_daily_return)
            
            # Cartera combinada: 50% NQ + 50% Event Strategy
            nq_component = combined_portfolio * 0.5 * (1 + nq_daily_return)
            
            # Calcular P&L de la estrategia de eventos
            event_pnl = 0
            if position != 0:
                cl_pnl = (current_cl - prev_cl) * position * 1000
                nq_pnl = (current_nq - prev_nq) * (-position) * 20
                event_pnl = cl_pnl + nq_pnl
                self.capital += event_pnl
                days_in_position += 1
            
            # Componente de estrategia de eventos (50% del portfolio combinado)
            event_component = combined_portfolio * 0.5
            if position != 0:
                event_return = event_pnl / (combined_portfolio * 0.5) if combined_portfolio > 0 else 0
                event_component *= (1 + event_return)
            
            combined_portfolio = nq_component + event_component
            
            # Cerrar posición si sale de evento o señal cambia
            if position != 0 and (not event_active or current_signal != prev_signal):
                # Cerrar posición
                cl_exit_pnl = (current_cl - entry_price_cl) * position * 1000
                nq_exit_pnl = (current_nq - entry_price_nq) * (-position) * 20
                trade_pnl = cl_exit_pnl + nq_exit_pnl
                
                self.trades.append({
                    'entry_date': entry_date,  # Usar la fecha de entrada guardada
                    'exit_date': date,
                    'entry_cl': entry_price_cl,
                    'exit_cl': current_cl,
                    'entry_nq': entry_price_nq,
                    'exit_nq': current_nq,
                    'position': position,
                    'pnl': trade_pnl,
                    'days_held': days_in_position,
                    'event_type': self.data['event_type'].iloc[i-1]
                })
                
                position = 0
                days_in_position = 0
            
            # Abrir nueva posición si hay evento activo y señal
            if event_active and current_signal != 0 and position == 0:
                position = current_signal
                entry_price_cl = current_cl
                entry_price_nq = current_nq
                entry_date = date  # Guardar fecha de entrada exacta
                days_in_position = 0
                
                # Entrada registrada
                pass
            
            # Registrar equity con todas las curvas
            self.equity_curve.append({
                'date': date,
                'equity': self.capital,
                'position': position,
                'cl_price': current_cl,
                'nq_price': current_nq,
                'sp_price': current_sp,
                'event_active': event_active,
                'event_type': self.data['event_type'].iloc[i],
                'nq_portfolio': nq_portfolio,
                'combined_portfolio': combined_portfolio,
                'sp_portfolio': sp_portfolio
            })
    
    def calculate_metrics(self):
        """Calcular métricas específicas para estrategia por eventos"""
        equity_df = pd.DataFrame(self.equity_curve)
        trades_df = pd.DataFrame(self.trades)
        
        # Métricas básicas
        total_return = (self.capital - self.initial_capital) / self.initial_capital * 100
        equity_df['returns'] = equity_df['equity'].pct_change()
        
        # Solo considerar días con eventos para métricas activas
        event_days = equity_df[equity_df['event_active']]
        total_event_days = len(event_days)
        active_trading_days = len(equity_df[equity_df['position'] != 0])
        
        # Métricas de riesgo
        if len(equity_df) > 252:
            annual_return = ((self.capital / self.initial_capital) ** (252/len(equity_df)) - 1) * 100
        else:
            annual_return = total_return
            
        volatility = equity_df['returns'].std() * np.sqrt(252) * 100
        sharpe_ratio = annual_return / volatility if volatility > 0 else 0
        
        # Drawdown
        equity_df['peak'] = equity_df['equity'].expanding().max()
        equity_df['drawdown'] = (equity_df['equity'] - equity_df['peak']) / equity_df['peak'] * 100
        max_drawdown = equity_df['drawdown'].min()
        
        # Métricas de trading por evento
        event_performance = {}
        if len(trades_df) > 0:
            for event_type in trades_df['event_type'].unique():
                event_trades = trades_df[trades_df['event_type'] == event_type]
                event_performance[event_type] = {
                    'trades': len(event_trades),
                    'total_pnl': event_trades['pnl'].sum(),
                    'win_rate': (event_trades['pnl'] > 0).mean() * 100,
                    'avg_pnl': event_trades['pnl'].mean()
                }
        
        # Métricas generales de trading
        if len(trades_df) > 0:
            winning_trades = trades_df[trades_df['pnl'] > 0]['pnl']
            losing_trades = trades_df[trades_df['pnl'] < 0]['pnl']
            
            win_rate = len(winning_trades) / len(trades_df) * 100
            avg_win = winning_trades.mean() if len(winning_trades) > 0 else 0
            avg_loss = losing_trades.mean() if len(losing_trades) > 0 else 0
            profit_factor = abs(winning_trades.sum() / losing_trades.sum()) if len(losing_trades) > 0 and losing_trades.sum() != 0 else float('inf')
            avg_days_held = trades_df['days_held'].mean()
        else:
            win_rate = avg_win = avg_loss = profit_factor = avg_days_held = 0
        
        # Calcular métricas para las estrategias comparativas
        final_combined = equity_df['combined_portfolio'].iloc[-1]
        final_sp = equity_df['sp_portfolio'].iloc[-1]
        
        combined_return = (final_combined - self.initial_capital) / self.initial_capital * 100
        sp_return = (final_sp - self.initial_capital) / self.initial_capital * 100
        
        combined_annual = ((final_combined / self.initial_capital) ** (252/len(equity_df)) - 1) * 100 if len(equity_df) > 252 else combined_return
        sp_annual = ((final_sp / self.initial_capital) ** (252/len(equity_df)) - 1) * 100 if len(equity_df) > 252 else sp_return
        
        # Volatilidades
        equity_df['combined_returns'] = equity_df['combined_portfolio'].pct_change()
        equity_df['sp_returns'] = equity_df['sp_portfolio'].pct_change()
        
        combined_vol = equity_df['combined_returns'].std() * np.sqrt(252) * 100
        sp_vol = equity_df['sp_returns'].std() * np.sqrt(252) * 100
        
        # Sharpe ratios
        combined_sharpe = combined_annual / combined_vol if combined_vol > 0 else 0
        sp_sharpe = sp_annual / sp_vol if sp_vol > 0 else 0
        
        # Max drawdowns
        equity_df['combined_peak'] = equity_df['combined_portfolio'].expanding().max()
        equity_df['combined_dd'] = (equity_df['combined_portfolio'] - equity_df['combined_peak']) / equity_df['combined_peak'] * 100
        combined_max_dd = equity_df['combined_dd'].min()
        
        equity_df['sp_peak'] = equity_df['sp_portfolio'].expanding().max()
        equity_df['sp_dd'] = (equity_df['sp_portfolio'] - equity_df['sp_peak']) / equity_df['sp_peak'] * 100
        sp_max_dd = equity_df['sp_dd'].min()

        self.metrics = {
            'total_return': total_return,
            'annual_return': annual_return,
            'volatility': volatility,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'total_trades': len(trades_df),
            'win_rate': win_rate,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'profit_factor': profit_factor,
            'avg_days_held': avg_days_held,
            'total_event_days': total_event_days,
            'active_trading_days': active_trading_days,
            'event_performance': event_performance,
            'final_capital': self.capital,
            # Métricas comparativas
            'combined_return': combined_return,
            'combined_annual': combined_annual,
            'combined_volatility': combined_vol,
            'combined_sharpe': combined_sharpe,
            'combined_max_dd': combined_max_dd,
            'combined_final': final_combined,
            'sp_return': sp_return,
            'sp_annual': sp_annual,
            'sp_volatility': sp_vol,
            'sp_sharpe': sp_sharpe,
            'sp_max_dd': sp_max_dd,
            'sp_final': final_sp
        }
        
        return self.metrics
    
    def create_results_chart(self):
        """Crear gráfico BASICO de equity que funcione"""
        equity_df = pd.DataFrame(self.equity_curve)
        
        # Figura básica
        fig = go.Figure()
        
        # Solo línea de equity - sin relleno ni complejidad
        fig.add_trace(
            go.Scatter(
                x=equity_df['date'],
                y=equity_df['combined_portfolio'],
                mode='lines',
                name='Strategy Performance',
                line=dict(color='green', width=2)
            )
        )
        
        # Layout básico y simple
        fig.update_layout(
            title='CL/NQ Event Strategy - Basic Equity Curve',
            xaxis_title='Date',
            yaxis_title='Portfolio Value ($)',
            template='plotly_white',
            height=600,
            width=1000,
            showlegend=True
        )
        
        # Guardar archivo
        filename = 'charts/cl_nq_basic_equity.html'
        fig.write_html(filename)
        print(f"[OK] Gráfico básico guardado: {filename}")
        
        # Abrir en navegador
        full_path = os.path.abspath(filename)
        webbrowser.open(f'file://{full_path}')
        
        return filename
    
    def print_results(self):
        """Imprimir resultados detallados por eventos y comparación de estrategias"""
        print("\n" + "="*80)
        print("CL vs NQ EVENT STRATEGY - RESULTADOS Y COMPARACION")
        print("="*80)
        
        print(f"\n[COMPARISON] COMPARACION DE ESTRATEGIAS:")
        print(f"{'Metrica':<25} {'NQ + Event (50/50)':<20} {'S&P 500 Only':<15} {'Diferencia':<15}")
        print("-" * 75)
        print(f"{'Capital Final:':<25} ${self.metrics['combined_final']:>15,.0f} ${self.metrics['sp_final']:>13,.0f} {self.metrics['combined_final'] - self.metrics['sp_final']:>+13,.0f}")
        print(f"{'Retorno Total:':<25} {self.metrics['combined_return']:>14.2f}% {self.metrics['sp_return']:>12.2f}% {self.metrics['combined_return'] - self.metrics['sp_return']:>+12.2f}%")
        print(f"{'Retorno Anual:':<25} {self.metrics['combined_annual']:>14.2f}% {self.metrics['sp_annual']:>12.2f}% {self.metrics['combined_annual'] - self.metrics['sp_annual']:>+12.2f}%")
        print(f"{'Volatilidad:':<25} {self.metrics['combined_volatility']:>14.2f}% {self.metrics['sp_volatility']:>12.2f}% {self.metrics['combined_volatility'] - self.metrics['sp_volatility']:>+12.2f}%")
        print(f"{'Sharpe Ratio:':<25} {self.metrics['combined_sharpe']:>18.2f} {self.metrics['sp_sharpe']:>16.2f} {self.metrics['combined_sharpe'] - self.metrics['sp_sharpe']:>+16.2f}")
        print(f"{'Max Drawdown:':<25} {self.metrics['combined_max_dd']:>14.2f}% {self.metrics['sp_max_dd']:>12.2f}% {self.metrics['combined_max_dd'] - self.metrics['sp_max_dd']:>+12.2f}%")
        
        print(f"\n[ACTIVITY] ACTIVIDAD DE TRADING:")
        print(f"  - Total Dias Analizados: {len(self.equity_curve):,}")
        print(f"  - Dias con Eventos Historicos: {self.metrics['total_event_days']:,} ({(self.metrics['total_event_days']/len(self.equity_curve))*100:.1f}%)")
        print(f"  - Dias con Trading Activo: {self.metrics['active_trading_days']:,} ({(self.metrics['active_trading_days']/len(self.equity_curve))*100:.1f}%)")
        print(f"  - Exposicion Real al Pairs Trading: {(self.metrics['active_trading_days']/self.metrics['total_event_days'])*100:.1f}% del tiempo en eventos")
        
        print(f"\n[STRATEGY] DETALLES DE LA ESTRATEGIA DE EVENTOS:")
        print(f"  - Total Trades: {self.metrics['total_trades']}")
        print(f"  - Win Rate: {self.metrics['win_rate']:.1f}%")
        print(f"  - Ganancia Promedio: ${self.metrics['avg_win']:,.2f}")
        print(f"  - Perdida Promedio: ${self.metrics['avg_loss']:,.2f}")
        print(f"  - Profit Factor: {self.metrics['profit_factor']:.2f}")
        print(f"  - Dias Promedio por Trade: {self.metrics['avg_days_held']:.1f}")
        
        print(f"\n[EVENTS] PERFORMANCE POR TIPO DE EVENTO:")
        for event_type, perf in self.metrics['event_performance'].items():
            print(f"  - {event_type.upper()}:")
            print(f"    * Trades Ejecutados: {perf['trades']}")
            print(f"    * P&L Total: ${perf['total_pnl']:+,.2f}")
            print(f"    * Win Rate: {perf['win_rate']:.1f}%")
            print(f"    * P&L Promedio por Trade: ${perf['avg_pnl']:+,.2f}")
        
        # Análisis de valor agregado
        value_added = self.metrics['combined_return'] - self.metrics['sp_return']
        risk_adjusted_value = (self.metrics['combined_sharpe'] - self.metrics['sp_sharpe'])
        
        print(f"\n[VALUE] VALOR AGREGADO DE LA ESTRATEGIA:")
        print(f"  - Alpha vs S&P 500: {value_added:+.2f}% ({value_added/20:.2f}% anual aprox)")
        print(f"  - Diferencia Sharpe: {risk_adjusted_value:+.3f}")
        print(f"  - Reduccion Drawdown: {(self.metrics['sp_max_dd'] - self.metrics['combined_max_dd']):+.2f}%")
        
        if value_added > 0:
            print(f"  [+] La estrategia NQ + Event SUPERA al S&P 500 standalone")
        else:
            print(f"  [-] La estrategia NQ + Event NO supera al S&P 500 standalone")
        
        return self.metrics

def main():
    """Ejecutar estrategia Event Based"""
    print("CL vs NQ EVENT STRATEGY")
    print("="*40)
    
    # Crear instancia de la estrategia
    strategy = CLNQEventStrategy(initial_capital=10000)
    
    # Cargar datos
    if not strategy.load_data():
        return
    
    # Generar señales
    print("\nGenerando senales para eventos...")
    strategy.generate_signals()
    
    # Ejecutar backtest
    print("Ejecutando backtest...")
    strategy.backtest()
    
    # Calcular métricas
    print("Calculando metricas...")
    strategy.calculate_metrics()
    
    # Mostrar resultados
    results = strategy.print_results()
    
    # Crear y guardar gráfico
    print("\nGenerando grafico de resultados...")
    fig = strategy.create_results_chart()
    filename = 'strat_om/cl_nq_event_results.html'
    
    # Crear directorio si no existe
    os.makedirs('strat_om', exist_ok=True)
    
    # El gráfico ya se guarda dentro de create_results_chart()
    print(f"[OK] Resultados completados")
    
    return results

if __name__ == "__main__":
    main()