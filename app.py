import os
import ast
import json
import pymongo
import logging
from flask import Flask, render_template, request


app = Flask(__name__)
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
URI = 'mongodb://localhost:27017'
client = pymongo.MongoClient(URI)
DB = client['upload_color']
colors = DB.colors


@app.route('/')
@app.route('/index')
def index():
    return render_template("index.html")


def json_extension(input_file):
    if input_file.split('.')[-1] == 'json':
        return True
    logging.error("Uploaded file is not json")
    return False


def convert_to_dict(uploaded_file):
    try:
        return ast.literal_eval(uploaded_file.read().decode("utf-8"))
    except ValueError as e:
        logging.error(e)
        return None


@app.route("/upload", methods=['POST'])
def upload():
    if not json_extension(request.files['file'].filename):
        return render_template("error.html", message="Uploaded file should "
                                                     "have json extension")
    document = convert_to_dict(request.files['file'])
    if not document:
        return render_template("error.html", message="Uploaded JSON couldn't "
                                                     "be parsed")
    colors.insert_one(document)
    return render_template(
        "complete.html", filename=request.files['file'].filename)


@app.route('/colors')
def get_colors():
    output_colors = []
    for doc in colors.find({"colors": {"$exists": True}}):
        output_colors = [clr['color'] for clr in doc['colors']]
    response = json.dumps(output_colors, sort_keys=True, indent=4,
                          separators=(',', ': '))
    return render_template("colors.html", response=response)


@app.route('/rgba')
def get_rgba():
    output_colors = []
    for doc in colors.find({"colors": {"$exists": True}}):
        for clr in doc['colors']:
            output_colors.append({
                'color': clr['color'],
                'rgba': clr['code']['rgba']
            })

    response = json.dumps(output_colors, sort_keys=True, indent=4,
                          separators=(',', ': '))
    return render_template("rgba.html", response=response)


@app.route('/primary')
def get_primary():
    output_colors = []
    for doc in colors.find({"colors": {"$exists": True}}):
        for clr in doc['colors']:
            if 'type' in clr and clr['type'] == 'primary':
                output_colors.append(clr['color'])

    response = json.dumps(output_colors, sort_keys=True, indent=4,
                          separators=(',', ': '))
    return render_template("primary.html", response=response)


if __name__ == '__main__':
    app.run()
