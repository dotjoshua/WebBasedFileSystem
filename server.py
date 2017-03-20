from flask import *

app = Flask(__name__)


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

if __name__ == "__main__":
    import logging
    from logging import FileHandler, Formatter
    file_handler = FileHandler("errors.log")
    file_handler.setLevel(logging.WARNING)
    file_handler.setFormatter(Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    app.logger.addHandler(file_handler)
    app.run()
