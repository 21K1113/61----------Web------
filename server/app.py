from flask import Flask
from flask import render_template
from flask import request
from flask import make_response
from pathlib import Path
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# SQLAlchemy の初期化
db = SQLAlchemy()

# app 変数はグローバルで作成
app = Flask(__name__)

# flask から呼ばれる application 生成関数
def create_app():
    # データベースのマッピング
    app.config.from_mapping(
        SECRET_KEY="tama project", # 後で変更
        SQLALCHEMY_DATABASE_URI="mysql://root@localhost/tama", # 後で変更
        SQLALCHEMY_TRACK_MODIFICATIONS=False
        )

    # AQLAlchemy とアプリの連携
    db.init_app(app)

    # Migrate とアプリの連携
    Migrate(app, db)

    # navi フォルダと連携
    from navi import user
    app.register_blueprint(user.blueprint, url_prefix="/navi")

    # gps フォルダと連携
    from gps import app as gpsApp
    app.register_blueprint(gpsApp.blueprint, url_prefix="/gps")

    # admin フォルダと連携
    from admin import app as adminApp
    app.register_blueprint(adminApp.blueprint, url_prefix="/admin")

    # schema フォルダと連携
    # schame フォルダは、データベースの schema を管理
    from schema import blueprint
    app.register_blueprint(blueprint.blueprint, url_prefix="/schema")

    return app

@app.route("/")
def index():
    # test code
    # return render_template('index.html', title = 'Hello World!')

    # import が循環しないように、関数内で import する
    # DBManager は、DB アクセス用の関数群をまとめたクラス
    from schema.models import DBManager
    manager = DBManager()
    
    # cookie から利用者IDを取得
    id = request.cookies.get('userId')
    if id == None:
        # cookie の設定がない場合、新規利用者の作成
        user = manager.generateUser()
        id = user.id
    else:
        # 文字列から整数への変換が必要
        try :
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
            

    # 利用者のアクセスログの保存
    manager.addAccessLog(user)

    # cookie の期限設定
    expires = int(datetime.now().timestamp()) + 30000000
    response = make_response(render_template('index.html',
                                             userId = '%d' % id))
    # cookie の設定
    response.set_cookie('userId', value='%d' % id, expires=expires)

    return response
        
if __name__ == "__main__":
    create_app()
    app.run()
