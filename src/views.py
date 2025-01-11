from flask import Blueprint, render_template, request, flash, jsonify, session
from .models import Message
from . import db

views = Blueprint('views', __name__)

@views.route('/', methods=['GET', 'POST'])
def index():    
    if request.method == "POST":
        pass

    return render_template("index.html"
                                        )
