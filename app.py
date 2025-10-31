import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from shiny import App
from ui import create_ui
from logica import setup_server

app_ui = create_ui()

def app_server(input, output, session):
    setup_server(input, output, session)

app = App(app_ui, app_server)

if __name__ == "__main__":
    app.run(port=0)