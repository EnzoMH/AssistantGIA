from flask import Blueprint, render_template, request, jsonify, send_file
import os
from io import BytesIO
from app.utils.convert_hwp import convert_hwp_to_txt

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/proposal')
def proposal():
    return render_template('proposal.html')

@main.route('/excel')
def excel():
    return render_template('excel.html')

# HWP 파일 업로드 및 처리 라우트
@main.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    try:
        converted_text = convert_hwp_to_txt(file)

        # 앞에서 500자, 끝에서 500자를 남기고 중간을 중략 처리
        if len(converted_text) > 1000:
            preview_text = converted_text[:500] + "\n...\n" + converted_text[-500:]
        else:
            preview_text = converted_text

        # 텍스트 파일로 저장하기 위해 메모리에 저장
        output = BytesIO()
        output.write(converted_text.encode('utf-8'))
        output.seek(0)

        # 저장된 파일의 경로 설정
        file_url = f"/download/{file.filename.replace('.hwp', '.txt')}"
        save_path = os.path.join('downloads', file.filename.replace('.hwp', '.txt'))

        # 파일을 실제로 저장
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        with open(save_path, 'w', encoding='utf-8') as f:
            f.write(converted_text)

        return jsonify({'prediction': preview_text, 'file_url': file_url})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 변환된 텍스트 파일 다운로드 라우트
@main.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    file_path = os.path.join('downloads', filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        return jsonify({'error': 'File not found'}), 404
