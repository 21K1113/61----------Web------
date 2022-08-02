import sys
sys.path.insert(0, 'E:\document\2年a 春学期\61リクエスト集中講義(Webアプリ開発)\server')
from app import app as application
from app import create_app
create_app()