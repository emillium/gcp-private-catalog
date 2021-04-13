import json
from flask import Blueprint, render_template

bp = Blueprint('catalog', __name__)
with open(bp.root_path + "/assets/catalogs.json", encoding='utf-8') as json_file:
	data = json.load(json_file)

@bp.route('/')
def index():
	return render_template("catalog/index.html", catalogs=data)

