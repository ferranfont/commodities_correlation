# Descorrelaciona tu Trading y Opera Materias Primas: El Impacto de la Divisa sobre el Sistema

## Descripción del Proyecto

Este proyecto de **Active Trades** se enfoca en el análisis y desarrollo de estrategias de trading descorrelacionadas para materias primas, considerando especialmente el impacto crítico que las divisas ejercen sobre los sistemas de trading.

## Objetivos Principales

### 1. Descorrelación de Estrategias
- Implementación de algoritmos para identificar y reducir correlaciones entre activos
- Desarrollo de portfolios diversificados de materias primas
- Análisis de correlaciones dinámicas en diferentes condiciones de mercado

### 2. Trading de Materias Primas
- Estrategias específicas para commodities (energía, metales, agricultura)
- Análisis de patrones estacionales y ciclos económicos
- Gestión de riesgo adaptada a la volatilidad de materias primas

### 3. Impacto de Divisas en el Sistema
- Análisis del efecto del dólar estadounidense (DXY) en precios de commodities
- Hedging de exposición cambiaria en trading de materias primas
- Correlación entre fortaleza/debilidad de divisas y performance de commodities

## Componentes del Sistema

### Análisis de Correlaciones
- Matrices de correlación dinámicas
- Identificación de períodos de alta/baja correlación
- Métricas de descorrelación efectiva

### Gestión de Riesgo
- Value at Risk (VaR) ajustado por correlaciones
- Dimensionamiento de posiciones basado en volatilidad
- Stop-loss adaptativos según condiciones de mercado

### Impacto Cambiario
- Monitoreo del índice del dólar (DXY)
- Análisis de elasticidad precio-divisa por commodity
- Estrategias de cobertura cambiaria

## Tecnologías Utilizadas

- **Python**: Lenguaje principal de desarrollo
- **Pandas/NumPy**: Manipulación y análisis de datos
- **Plotly**: Visualización interactiva de datos (charts HTML)
- **yfinance**: API para datos históricos de Yahoo Finance
- **Webbrowser**: Apertura automática de charts en navegador

## Metodología

1. **Recopilación de Datos**: Precios históricos de commodities y divisas
2. **Análisis Estadístico**: Cálculo de correlaciones y métricas de riesgo
3. **Modelado**: Desarrollo de modelos predictivos y de correlación
4. **Backtesting**: Validación histórica de estrategias
5. **Implementación**: Sistema de trading automatizado

## Beneficios Esperados

- **Reducción de Riesgo**: Menor exposición a movimientos correlacionados del mercado
- **Mayor Consistencia**: Returns más estables a través de la diversificación
- **Mejor Performance**: Aprovechamiento de oportunidades en diferentes condiciones de mercado
- **Control Cambiario**: Gestión efectiva del riesgo de divisa en trading internacional

## Consideraciones de Riesgo

- Volatilidad inherente de materias primas
- Cambios en correlaciones durante crisis de mercado
- Riesgo de liquidez en algunos commodities
- Exposición a eventos geopolíticos y climáticos

## Sistema Implementado

### Portfolio de Activos Analizados
- **Petróleo Crudo (CL)** - Futures WTI (~5,031 días)
- **NASDAQ (^IXIC)** - Índice Composite (~5,032 días)  
- **Oro (GC)** - Futures de Oro (~5,030 días)
- **EUR/USD** - Par de divisas (~4,583 días)

*Datos de plata y cobre conservados pero excluidos del análisis actual*

### Estructura del Proyecto
```
commodities_correlation/
├── data/           # Archivos CSV con datos históricos (20 años)
├── charts/         # Gráficos HTML interactivos generados
├── quant_stat/     # Estadísticas cuantitativas
├── outputs/        # Resultados de análisis
└── strat_om/       # Estrategias de trading
```

### Charts Generados
1. **Candlesticks Individuales** - OHLC diario para cada activo
2. **Comparación de Precios** - Líneas superpuestas de todos los activos
3. **Crecimiento Porcentual** - Análisis normalizado desde base 0
4. **Mapa de Calor de Correlaciones** - Matriz 4x4 de correlaciones
5. **Comparaciones vs NASDAQ** - Cada activo vs índice bursátil
6. **Correlaciones Rodantes** - Análisis temporal con ventana de 1 año

### Comandos Principales
```bash
# Descargar todos los datos
python get_yahoo_data.py

# Generar todos los gráficos
python plot_data.py

# Abrir dashboard de charts
start charts/index.html

# Instalar dependencias
pip install -r requirements.txt
```

### Características del Sistema
- **Datos de 20 años** de historia para cada activo
- **Filtrado automático** de fines de semana
- **Charts interactivos** con Plotly y tema oscuro
- **Análisis multi-activo** (commodities, equity, forex)
- **Dashboard centralizado** para navegación de gráficos

---

*Proyecto desarrollado para optimizar estrategias de trading en materias primas mediante técnicas avanzadas de descorrelación y gestión del riesgo cambiario.*