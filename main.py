from flask import Flask, render_template
import requests

app = Flask(__name__)

endpoint = "http://127.0.0.1:5123"


def get_random_cafe():
    endpoint_url = endpoint + "/random"
    response = requests.get(url=endpoint_url)
    response.raise_for_status()
    return response.json()


@app.route("/")
def home():
    page_title = "Here goes the home page title"
    rand_cafe = get_random_cafe()
    return render_template("index.html", page_title=page_title, r_cafe=rand_cafe)


@app.route("/search")
def search():
    page_title = "Search"
    return render_template("search.html", page_title=page_title)


@app.route("/add")
def add():
    page_title = "Add"
    return render_template("add.html", page_title=page_title)


@app.route("/edit")
def edit():
    page_title = "Edit"
    return render_template("edit.html", page_title=page_title)


if __name__ == '__main__':
    app.run(debug=True, port=1234)
