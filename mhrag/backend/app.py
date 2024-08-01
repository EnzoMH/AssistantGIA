import sys
import os
from flask import Flask

# 'backend' 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.routes import main  # routes.py에서 main 블루프린트를 가져옵니다.

# Flask 애플리케이션 초기화 시 template_folder 설정
app = Flask(__name__, template_folder="../frontend/templates")
app.register_blueprint(main)

if __name__ == "__main__":
    app.run(debug=True)
