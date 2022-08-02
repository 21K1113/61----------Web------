from flask import Blueprint
from flask import render_template
from flask import request
from app import db
from schema.models import DBManager

blueprint = Blueprint(
    "gps",
    __name__,
    template_folder="templates",
    static_folder="static",
    )

# GPS の送信データを模擬的に生成するテスト入力用ページ
# 本番システムでは削除
@blueprint.route("/")
def index():
    return render_template("gps/index.html")

# GPS データの登録用のエンドポイントの実装
# GET, POST のいずれも受付ける。
# 下記の引数を受け付ける
#  bus: バスID
#  longitude: 経度
#  latitude: 緯度
#  stop: バスの停止状態(0:走行中 or 1:停止中)
@blueprint.route("/register", methods=["GET", "POST"])
def register():
    # DB 管理用のクラス
    manager = DBManager()

    if request.method == "GET":
        # GET 用の引数抽出
        bus = request.args.get("bus")
        longitude = request.args.get("longitude")
        latitude = request.args.get("latitude")
        stop = request.args.get("stop")
    elif request.method == "POST":
        # POST 用の引数抽出
        bus = request.form.get("bus")
        longitude = request.form.get("longitude")
        latitude = request.form.get("latitude")
        stop = request.form.get("stop")

    # manager を使って、GPS データを登録
    manager.registerGPS(bus, longitude, latitude, stop)

    # 返却値は、gps/index.html を送信
    return render_template("gps/index.html")
