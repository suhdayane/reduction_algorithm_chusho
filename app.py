import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import networkx as nx
import glob
import pydot
import numpy as np
import util

# List .dot files inside ./dots path
dots = glob.glob('./dots/*.dot')

options = []
for dot in dots:
    options.append({'label': dot.split('/')[-1], 'value': dot})

app = dash.Dash(__name__, external_stylesheets=['app.css'])

app.layout = html.Div([
    html.Div([
        html.H1("Reduction Algorithm", style={'color': 'white'})
    ], className='nine columns'),

    html.Div([
        # caixa de seleção
        dcc.Dropdown(
            id='dropdown',
            options=options,
            value=None,
            style={'position': 'absolute', 'left':'10px', 'top':'40px', 'width': '500px', 'margin': '10px', 'color': 'black', 'background-color': 'white'}
        ),

        # caixa de seleção
        dcc.Dropdown(
            id='dropdown2',
            options=[
                {'label': 'Aplicar Regra 1', 'value': 'rule_1'},
                {'label': 'Aplicar até Regra 2', 'value': 'rule_2'},
                {'label': 'Aplicar até Regra 3', 'value': 'rule_3'},
                {'label': 'Aplicar até Regra 4', 'value': 'rule_4'},
            ],
            value=None,
            style={'position': 'absolute', 'right':'10px', 'top':'40px', 'width': '500px', 'margin': '10px', 'color': 'black', 'background-color': 'white'}
        ),

        html.Div([
            # gráfico original
            html.Div([
                dcc.Graph(id='original-graph', style={'height': '600px'})
            ], className='six columns', style={'width': '48%', 'display': 'inline-block', 'vertical-align': 'top', 'background-color': 'white', 'padding': '10px'}),

            # gráfico atualizado
            html.Div([
                dcc.Graph(id='updated-graph', style={'height': '600px'})
            ], className='six columns', style={'width': '48%', 'display': 'inline-block', 'vertical-align': 'top', 'background-color': 'white', 'padding': '10px'}),

        ], className='row')
    ], className='row', style={'padding-top': '20px'}),
], style={'background-color': 'white', 'margin': '0px', 'padding': '20px'})

@app.callback(
    [Output('original-graph', 'figure'),
     Output('updated-graph', 'figure')],
    [Input('dropdown', 'value'),
     Input('dropdown2', 'value')]
)
def update_graph(dropdown_value, dropdown2_value):
    if dropdown_value:
        # carrega o grafo
        (pydot_graph, ) = pydot.graph_from_dot_file(dropdown_value)
        G = nx.drawing.nx_pydot.from_pydot(pydot_graph)
        pos = nx.spring_layout(G)

        dropdown_value = dropdown_value.split('/')[-1]

        # adiciona a posição de cada nó ao atributo 'pos' do nó
        for node in G.nodes:
            G.nodes[node]['pos'] = pos[node]

        # plota o grafo original
        trace_original = []
        for node in G.nodes:
            x, y = G.nodes[node]['pos']
            trace_original.append(dict(
                type='scatter',
                x=[x],
                y=[y],
                mode='markers',
                marker=dict(size=50),
                text=node,
                hoverinfo='text'
            ))
        for edge in G.edges:
            x0, y0 = G.nodes[edge[0]]['pos']
            x1, y1 = G.nodes[edge[1]]['pos']
            trace_original.append(dict(
                type='scatter',
                x=[x0, x1, None],
                y=[y0, y1, None],
                mode='lines',
                line=dict(width=5),
                hoverinfo='none'
            ))
        fig_original = dict(data=trace_original, layout=dict(
            title=f'Grafo original do arquivo {dropdown_value}',
            showlegend=False,
            width=800,
            height=600,
            margin=dict(b=20, l=5, r=5, t=40),
            hovermode='closest',
            annotations=[dict(
                text="",
                showarrow=False,
                xref="paper", yref="paper",
                x=0.005, y=-0.002)],
            xaxis=dict(showgrid=False, zeroline=False,
                       showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
        )
        
        if dropdown2_value != None:
            if dropdown2_value == 'rule_1':
                G = util.apply_rule1(G)
            elif dropdown2_value == 'rule_2':
                G = util.apply_rule2(G)
            
            # adiciona a posição de cada nó ao atributo 'pos' do nó
            pos = nx.spring_layout(G)
            for node in G.nodes:
                G.nodes[node]['pos'] = pos[node]

            # plota o grafo atualizado
            trace_updated = []
            for node in G.nodes:
                x, y = G.nodes[node]['pos']
                trace_updated.append(dict(
                    type='scatter',
                    x=[x],
                    y=[y],
                    mode='markers',
                    marker=dict(size=50),
                    text=node,
                    hoverinfo='text'
                ))
            for edge in G.edges:
                x0, y0 = G.nodes[edge[0]]['pos']
                x1, y1 = G.nodes[edge[1]]['pos']
                trace_updated.append(dict(
                    type='scatter',
                    x=[x0, x1, None],
                    y=[y0, y1, None],
                    mode='lines',
                    line=dict(width=5, arrowhead=2, arrowsize=1),
                    text=f"{edge[0]}->{edge[1]}",
                    hoverinfo='text'
                ))
            fig_updated = dict(data=trace_updated, layout=dict(
                title=f'Grafo atualizado do arquivo {dropdown_value}',
                showlegend=False,
                width=800,
                height=600,
                margin=dict(b=20, l=5, r=5, t=40),
                hovermode='closest',
                annotations=[dict(
                    text="",
                    showarrow=False,
                    xref="paper", yref="paper",
                    x=0.005, y=-0.002)],
                xaxis=dict(showgrid=False, zeroline=False,
                        showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
            )
        else:
            fig_updated = fig_original

        return fig_original, fig_updated

    else:
        return {}, {}
    

if __name__ == '__main__':
    app.run_server(debug=True)