from flask import request, session, render_template
from src import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, port="5000") 




    