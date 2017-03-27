from flask import *
import json
import os

DEBUG = True

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 1024  # 1GB
app.config['PROPAGATE_EXCEPTIONS'] = True

@app.errorhandler(403)
def forbidden(e):
    return redirect("/#403")


@app.errorhandler(404)
def page_not_found(e):
    return redirect("/#404")


@app.route("/")
def index():
    return send_from_directory("./", "index.html")


@app.route("/res/<path:path>")
def static_res(path):
    return send_from_directory("res/", path)


@app.route("/lib/<path:path>")
def static_lib(path):
    return send_from_directory("lib/", path)


@app.route("/io/upload/", methods=["GET", "POST"])
def upload():
    response = {}

    try:
        filename = request.headers.get("filename")
        path = request.headers.get("path")
        data = request.data
    except Exception as e:
        response["error"] = str(e)

    return json.dumps(response)

if __name__ == "__main__":
    import logging
    from logging import FileHandler, Formatter
    file_handler = FileHandler("errors.log")
    file_handler.setLevel(logging.WARNING)
    file_handler.setFormatter(Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    app.logger.addHandler(file_handler)
    app.run(debug=DEBUG)
