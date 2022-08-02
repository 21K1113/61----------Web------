from datetime import datetime
from app import db

# DB関係のスキーマ定義と、DB管理クラス DBManager を定義するためのプログラム

# 利用者管理スキーマ ("users")
#  id: 利用者ID
#  count: アクセス回数
class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    count = db.Column(db.Integer, default=0)

# 利用者の個別アクセスログのスキーマ ("access")
#  id: アクセスログID
#  userId: 利用者ID
#  time: アクセス時刻
class AccessLog(db.Model):
    __tablename__ = "access"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    userId = db.Column(db.Integer, default=0)
    time = db.Column(db.DateTime)

# バスから発信されるGPSログのスキーマ ("gps")
#  id: GPSログID
#  time: 登録時刻
#  bus: バスID
#  latitude: 緯度
#  longitude: 経度
#  stop: 走行中(0)、停止中(1)
class GPSLog(db.Model):
    __tablename__ = "gps"
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.DateTime)
    bus = db.Column(db.Integer, default=0)
    latitude = db.Column(db.Float, default=0.0)
    longitude = db.Column(db.Float, default=0.0)
    stop = db.Column(db.SmallInteger, default=0)

# 直近のGPS登録データをバスID単位で管理するスキーマ ("current_location")
#  id: バスID
#  gpsId: 直近のGPS情報を示す GPSログID
class CurrentLocation(db.Model):
    __tablename__ = "current_location"
    # id <= bus id
    id = db.Column(db.Integer, primary_key=True)
    gpsId = db.Column(db.Integer, default=0)

# システム変数を管理するスキーマ ("system")
#  id: 常に1
#  lastGpsId: 直近のGPSログID
class System(db.Model):
    __tablename__ = "system"
    id = db.Column(db.Integer, primary_key=True)
    lastGpsId = db.Column(db.Integer, default=1)

# DB 管理用のユーティリティ関数を管理するクラス
class DBManager:
    # コンストラクタ
    def __init__(self):
        systems = db.session.query(System)
        if systems.count() == 0:
            # System テーブルが初期状態の時の設定
            # primary key の id は、1 以上の整数値であることが必要
            self.system = System()
            self.system.id = 1
            self.system.lastGpsId = 1
            gps = GPSLog()
            gps.id = 1
            gps.bus = 1
            self.lastGps = { gps.bus: gps }
            db.session.add(self.system)
            db.session.add(gps)
            db.session.commit()
        else:
            # 運用時は、ここが実行される
            self.system = systems.first()
            
            # 現在位置の情報をDBから復帰させる
            locs = db.session.query(CurrentLocation).all()
            
            # 最新のGPS位置情報を dict で格納 (バスID、GPS情報)
            self.lastGps = {}
            if len(locs) == 0:
                # GPS位置情報の登録がない場合は、バスID=1 でdummy 登録
                gps = db.session.query(GPSLog).get(1)
                self.lastGps[1] = gps
            else:
                for loc in locs:
                    gps = db.session.query(GPSLog).get(loc.gpsId)
                    self.lastGps[loc.id] = gps
                # self.lastGps = db.session.query(GPSLog).get(self.system.lastGpsId)
                # self.lastGps.id = self.system.lastGpsId

            
    # 新規利用者の作成
    # User テーブルへの登録
    def generateUser(self):
        user = User()
        db.session.add(user)
        db.session.commit()
        return user

    
    # 既存利用者の検索
    def getUser(self, id):
        user = db.session.query(User).get(id)
        return user


    # アクセスログの登録
    # AccessLog と User テーブルの更新
    def addAccessLog(self, user):
        log = AccessLog()
        log.userId = user.id
        log.time = datetime.now()
        user.count += 1
        db.session.add(log)
        db.session.add(user)
        db.session.commit()
        return user.count

    # アクセスログの取得
    def getAccessLog(self):
        logs = db.session.query(AccessLog).all()
        return logs

    
    # GPS ログの最後のIDを取得
    def getLastGpsId(self):
        id = self.system.lastGpsId
        # self.system.lastGpsId += 1
        # db.session.add(self.system)
        # db.session.commit()
        return id

    # GPS ログの最後ののIDを取得しつつ、+1 する
    def incrementLastGpsId(self):
        id = self.system.lastGpsId
        self.system.lastGpsId += 1
        db.session.add(self.system)
        db.session.commit()
        return id

    # バスごとの最新のGPSデータを取得
    def getLastGps(self):
        return self.lastGps

    # GPS データの登録
    def registerGPS(self, bus, longitude, latitude, stop):
        self.system.lastGpsId += 1
        gps = GPSLog()
        gps.id = self.system.lastGpsId
        gps.bus = bus
        gps.time = datetime.now()
        gps.longitude = longitude
        gps.latitude = latitude
        gps.stop = stop

        # print(self.lastGps)
        # バスIDは、整数に変換
        currentId = self.lastGps.get(int(bus))
        if currentId == None:
            # 登録がないバスの場合、CurrentLocation オブジェクトを生成
            current = CurrentLocation()
            current.id = bus
            current.gpsId = gps.id
        else:
            current = db.session.query(CurrentLocation).get(bus)
            if current == None:
                current = CurrentLocation()
                current.id = bus
            current.gpsId = gps.id

        db.session.add(gps)
        db.session.add(self.system)
        db.session.add(current)
        db.session.commit()
        
        return gps

    # システム情報の取得
    def getSystem(self):
        return self.system

    # DB の全データ消去
    # 注意して実行すること
    def deleteAll(self):
        db.session.query(User).delete()
        db.session.query(AccessLog).delete()
        db.session.query(GPSLog).delete()
        db.session.query(CurrentLocation).delete()
        db.session.query(System).delete()
        db.session.commit()

# manager = DBManager()

"""
    def getLastUserId(self):
        id = self.system.userId
        self.system.userId += 1
        db.session.add(self.system)
        db.session.commit()
        return id
"""
