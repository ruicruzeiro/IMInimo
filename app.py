from flask import Flask, flash, redirect, render_template, request, url_for


app = Flask(__name__)


@app.route("/")
def index():
    """Homepage/Short app presentation to the user"""
    return render_template("index.html")

@app.route("/upload")
def upload():
    """Page for loading of CPU document"""
    return render_template("upload.html")

@app.route("/input")
def input():
    """Page for manual input of CPU data"""
    return render_template("input.html")


if __name__ == "__main__":
    app.run(debug=True)
