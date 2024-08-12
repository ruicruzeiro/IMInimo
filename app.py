from flask import Flask, flash, redirect, render_template, request

app = Flask(__name__)

@app.route("/")
def index():
    """Homepage/Short app presentation to the user"""
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
