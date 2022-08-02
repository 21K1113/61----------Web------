from flask import Blueprint
from flask import render_template
from flask import request
from flask import make_response
from app import db
from schema.models import DBManager
from datetime import datetime

blueprint = Blueprint(
    "navi",
    __name__,
    template_folder="templates",
    static_folder="static",
    )

# /navi/ のエンドポイントを作成する関数
@blueprint.route("/")
def index():
    # DB 管理クラス
    manager = DBManager()

    # cookie から利用者IDを取得
    id = request.cookies.get('userId')
    if id == None:
        # 新規利用者の作成
        user = manager.generateUser()
        id = user.id
    else:
        try:
            # 文字列から整数への変換が必要
            id = int(id)
            
            # 利用者の検索
            user = manager.getUser(id)
            if user == None:
                # 利用者の検索に失敗したら、利用者を再作成
                user = manager.generateUser()
                id = user.id
        except Exception as e:
            # id を整数に変換することが失敗した場合
            user = manager.generateUser()
            id = user.id

    # 最近の GPS データの取得
    locations = manager.getLastGps()

    # 利用者のアクセスログの保存
    manager.addAccessLog(user)

    # cookie の期限設定
    expires = int(datetime.now().timestamp()) + 30000000

    response = make_response(render_template("navi/index.html",
                                             locations = locations))
    
    # cookie の設定
    response.set_cookie('userId', value='%d' % id, expires=expires)

    return response

# 定期的に呼び出すバスの位置情報取得用のエンドポイント
@blueprint.route("/getGps")
def getGps():
    # DB 管理クラス
    manager = DBManager()
    
    # 最近の GPS データの取得
    locations = manager.getLastGps()

    # JSON 形式で出力
    answer = '['

    # 配列をつなぐ "," は、for loop の最初だけは不要であることを示すフラグ
    first = True
    
    for location in locations.values():
        if first:
            first = False
        else:
            answer += ','
        answer += (
            '{"bus": %d, "latitude": %f, "longitude": %f}' %
            (location.bus, location.latitude, location.longitude))
    answer += ']'

    # print(answer)

    return answer

