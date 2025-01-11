from flask_login import current_user
from flask import request, session  
from src import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, port="80") 




    