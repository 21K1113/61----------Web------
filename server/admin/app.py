from flask import Blueprint
from flask import render_template
from flask import request
from flask import make_response
from app import db
from schema.models import DBManager
from datetime import datetime

blueprint = Blueprint(
    "admin",
    __name__,
    template_folder="templates",
    static_folder="static",
    )

@blueprint.route("/")
def index():
    # DB 管理用クラス
    manager = DBManager()

    # 最近の GPS データの取得
    # 複数のバスに対応するため、それぞれのバスの直近データを dict で返却
    locations = manager.getLastGps()

    # 利用者のアクセスログの取得
    logs = manager.getAccessLog()

    """
    table = "<table>"
    for log in logs:
        timeString = log.time.strftime("%Y/%m/%d %H:%M:%S.%f")
        table += "<tr><td>%d</td><td>%s</td></tr>" % (log.userId, timeString)
                     
    table += "</table>"
    """

    response = make_response(render_template("admin/index.html",
                                             logs = logs,
                                             locations = locations))
    
    return response

@blueprint.route("/deleteAll")
def deleteAll():
    # DB 管理用クラス
    manager = DBManager()

    manager.deleteAll()

    return ""
