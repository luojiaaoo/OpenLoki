from dash import ClientsideFunction
from dash.dependencies import Input, Output, MATCH,State
from server import app

app.clientside_callback(
    ClientsideFunction(
        namespace='tool_clientside',
        function_name='show_serper_redirect',
    ),
    Output({'type': 'serper-search-exec-js', 'index': MATCH}, 'jsString'),
    Input({'type': 'serper-search-card-grid-btn', 'index': MATCH}, 'nClicks'),
    State({'type': 'serper-search-store-link', 'index': MATCH}, 'data'),
    prevent_initial_call=True,
)
