import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import pandas as pd
import os

# Inicializar la aplicación Dash con un tema limpio
app = dash.Dash(__name__, external_stylesheets=[
    "https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap"
])
app.title = "Aduana Digital | Supply Chain Operations"

RUTA_CONTROL = 'data/control_envios.csv'
RUTA_AUDITORIA = 'data/auditoria_errores.csv'

# Estilos globales y paleta de colores de alta gama (inspirado en Google Cloud / Vercel)
COLOR_BG = "#0f172a"        # Slate 900 (Dark mode corporativo o fondo ultra limpio)
COLOR_CARD = "#1e293b"      # Slate 800
COLOR_TEXT_MAIN = "#f8fafc" # Slate 50
COLOR_TEXT_MUTED = "#94a3b8"# Slate 400
COLOR_ACCENT = "#3b82f6"    # Blue 500

app.layout = html.Div(
    style={
        'fontFamily': "'Inter', sans-serif', Arial, sans-serif",
        'backgroundColor': "#090d16",
        'color': COLOR_TEXT_MAIN,
        'minHeight': '100vh',
        'padding': '32px'
    },
    children=[
        # Cabecera de alto rendimiento
        html.Header(
            style={
                'display': 'flex',
                'justify-content': 'space-between',
                'align-items': 'center',
                'borderBottom': '1px solid #1e293b',
                'paddingBottom': '20px',
                'marginBottom': '32px'
            },
            children=[
                html.Div([
                    html.H1("Aduana Digital & Logistics", style={
                        'fontSize': '24px', 
                        'fontWeight': '700', 
                        'letterSpacing': '-0.025em',
                        'margin': '0 0 4px 0',
                        'color': '#ffffff'
                    }),
                    html.P("Monitoreo en tiempo real de OVs, empaques y auditoría de errores.", style={
                        'fontSize': '14px', 
                        'color': COLOR_TEXT_MUTED,
                        'margin': '0'
                    }),
                ]),
                # Indicador de estado en tiempo real (Punto parpadeante estilo enterprise)
                html.Div(
                    style={'display': 'flex', 'align-items': 'center', 'gap': '8px', 'background': '#1e293b', 'padding': '8px 16px', 'borderRadius': '9999px', 'border': '1px solid #334155'},
                    children=[
                        html.Span(style={'width': '8px', 'height': '8px', 'backgroundColor': '#10b981', 'borderRadius': '50%', 'display': 'inline-block'}),
                        html.Span("Sistema en Vivo", style={'fontSize': '12px', 'fontWeight': '500', 'color': '#e2e8f0'})
                    ]
                )
            ]
        ),

        # Grid de Métricas Principales (KPI Cards Profesionales)
        html.Div(
            style={
                'display': 'grid',
                'gridTemplateColumns': 'repeat(auto-fit, minmax(240px, 1fr))',
                'gap': '20px',
                'marginBottom': '32px'
            },
            children=[
                html.Div(style={'backgroundColor': COLOR_CARD, 'padding': '20px', 'borderRadius': '12px', 'border': '1px solid #334155'}, children=[
                    html.P("Órdenes Validadas", style={'color': COLOR_TEXT_MUTED, 'fontSize': '13px', 'margin': '0 0 8px 0'}),
                    html.H3("1,428", style={'color': '#ffffff', 'fontSize': '28px', 'fontWeight': '600', 'margin': '0'})
                ]),
                html.Div(style={'backgroundColor': COLOR_CARD, 'padding': '20px', 'borderRadius': '12px', 'border': '1px solid #334155'}, children=[
                    html.P("Errores de Auditoría", style={'color': COLOR_TEXT_MUTED, 'fontSize': '13px', 'margin': '0 0 8px 0'}),
                    html.H3("12", style={'color': '#f43f5e', 'fontSize': '28px', 'fontWeight': '600', 'margin': '0'})
                ]),
                html.Div(style={'backgroundColor': COLOR_CARD, 'padding': '20px', 'borderRadius': '12px', 'border': '1px solid #334155'}, children=[
                    html.P("Eficiencia de Ruta", style={'color': COLOR_TEXT_MUTED, 'fontSize': '13px', 'margin': '0 0 8px 0'}),
                    html.H3("98.4%", style={'color': '#10b981', 'fontSize': '28px', 'fontWeight': '600', 'margin': '0'})
                ]),
            ]
        ),

        # Intervalo de actualización (invisible)
        dcc.Interval(
            id='interval-component',
            interval=5*1000,
            n_intervals=0
        )
    ]
)

if __name__ == '__main__':
    app.run(debug=True)


    html.Div(style={'display': 'flex', 'justifyContent': 'space-around', 'margin': '20px 0'}, children=[
        html.Div(id='card-totales', style={'background': 'white', 'padding': '20px', 'borderRadius': '8px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)', 'width': '30%', 'textAlign': 'center'}),
        html.Div(id='card-validados', style={'background': 'white', 'padding': '20px', 'borderRadius': '8px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)', 'width': '30%', 'textAlign': 'center'}),
        html.Div(id='card-errores', style={'background': 'white', 'padding': '20px', 'borderRadius': '8px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)', 'width': '30%', 'textAlign': 'center'}),
    ]),

    html.Div(style={'display': 'flex', 'flexWrap': 'wrap', 'justifyContent': 'space-between'}, children=[
        html.Div(dcc.Graph(id='grafico-estatus'), style={'width': '48%', 'background': 'white', 'padding': '10px', 'borderRadius': '8px'}),
        html.Div(dcc.Graph(id='grafico-cajas'), style={'width': '48%', 'background': 'white', 'padding': '10px', 'borderRadius': '8px'}),
    ])


@app.callback(
    [Output('card-totales', 'children'),
     Output('card-validados', 'children'),
     Output('card-errores', 'children'),
     Output('grafico-estatus', 'figure'),
     Output('grafico-cajas', 'figure')],
    [Input('interval-component', 'n_intervals')]
)
def actualizar_dashboard(n):
    # Cargar datos
    df_control = pd.read_csv(RUTA_CONTROL) if os.path.exists(RUTA_CONTROL) and os.path.getsize(RUTA_CONTROL) > 0 else pd.DataFrame(columns=['ID_Orden', 'Cliente', 'Cajas', 'Bolsas', 'Estatus', 'Fecha_Hora', 'Usuario'])
    df_auditoria = pd.read_csv(RUTA_AUDITORIA) if os.path.exists(RUTA_AUDITORIA) and os.path.getsize(RUTA_AUDITORIA) > 0 else pd.DataFrame(columns=['ID_Orden', 'Estatus'])

    total_envios = len(df_control)
    validados = len(df_control[df_control['Estatus'].str.contains("VALIDADO", na=False)])
    errores = len(df_auditoria)

    card_t = [html.H3("Total Procesados"), html.H2(str(total_envios), style={'color': '#2980b9'})]
    card_v = [html.H3("Exitosos / Validados"), html.H2(str(validados), style={'color': '#27ae60'})]
    card_e = [html.H3("Discrepancias / Errores"), html.H2(str(errores), style={'color': '#c0392b'})]

    # Gráfico de estatus
    if not df_control.empty:
        fig_estatus = px.pie(df_control, names='Estatus', title='Proporción de Estatus de Envíos', hole=0.4)
    else:
        fig_estatus = px.pie(title='Sin datos registrados')

    # Gráfico de cajas por cliente
    if not df_control.empty and 'Cliente' in df_control.columns:
        fig_cajas = px.bar(df_control, x='Cliente', y='Cajas', color='Estatus', title='Volumen de Cajas por Cliente')
    else:
        fig_cajas = px.bar(title='Sin datos de cajas')

    return card_t, card_v, card_e, fig_estatus, fig_cajas

if __name__ == '__main__':
    app.run(debug=True, port=8050)