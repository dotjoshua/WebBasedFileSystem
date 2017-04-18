from flask import *
import json
import io_utils
import hashlib

DEBUG = False
UPLOAD_PASSWORD = "affd85a2baf19499a0ecf7237970343f5287c449dbbfc6015a5228fae8479f7a"

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
        password = hashlib.sha256(request.headers.get("password").encode("ascii")).hexdigest()

        if password != UPLOAD_PASSWORD:
            raise io_utils.IOUtilException("Invalid password")

        path = request.headers.get("path")
        data = request.data
        io_utils.create_file(filename, path, data)
    except Exception as e:
        response["error"] = str(e)

    return json.dumps(response)


@app.route("/io/new_folder/", methods=["GET", "POST"])
def new_folder():
    response = {}

    try:
        new_folder_name = request.args.get("name")
        path = request.args.get("path")
        io_utils.create_new_folder(new_folder_name, path)
    except Exception as e:
        response["error"] = str(e)
    return json.dumps(response)


@app.route("/io/list_dir/", methods=["GET", "POST"])
def list_dir():
    path = request.args.get("path")
    response = io_utils.list_dir(path)
    return json.dumps(response)


@app.route("/io/search/", methods=["GET", "POST"])
def search():
    response = {}
    try:
        query = request.args.get("query")
        response = io_utils.search(query)
    except Exception as e:
        response["error"] = str(e)
    return json.dumps(response)


@app.route("/io/get_file_contents/", methods=["GET", "POST"])
def get_file_contents():
    file = request.args.get("file")
    file_location = io_utils.get_file_contents_location(file)
    return send_from_directory("./file_data/", file_location)


@app.route("/io/delete_item/", methods=["GET", "POST"])
def delete_item():
    path = request.args.get("path")
    io_utils.delete_item(path)
    return ""


if __name__ == "__main__":
    import logging
    from logging import FileHandler, Formatter

    file_handler = FileHandler("errors.log")
    file_handler.setLevel(logging.WARNING)
    file_handler.setFormatter(Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    app.logger.addHandler(file_handler)
    app.run(host="0.0.0.0", debug=DEBUG)
