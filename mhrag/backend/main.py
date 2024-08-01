from flask import Flask, render_template, request, send_file, abort
import os
import pandas as pd
from backend.app.prmk.section import create_presentation  # 경로 수정
from backend.app.estm import preview_excel, create_excel  # 경로 수정

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/proposal')
def proposal():
    return render_template('proposal.html')

@app.route('/excel')
def excel():
    return render_template('excel.html')

@app.route('/create_presentation', methods=['POST'])
def create_presentation_route():
    try:
        slide_count = int(request.form['slide_count'])
        head_title = request.form['head_title']
        subtitle = request.form['subtitle']
        section0 = request.form['section0']
        section1 = request.form['section1']
        subsections1 = [request.form[f'subsection1_{i}'] for i in range(1, 11) if request.form.get(f'subsection1_{i}')]
        section2 = request.form['section2']
        subsections2 = [request.form[f'subsection2_{i}'] for i in range(1, 11) if request.form.get(f'subsection2_{i}')]
        section3 = request.form['section3']
        subsections3 = [request.form[f'subsection3_{i}'] for i in range(1, 11) if request.form.get(f'subsection3_{i}')]
        section4 = request.form['section4']
        subsections4 = [request.form[f'subsection4_{i}'] for i in range(1, 11) if request.form.get(f'subsection4_{i}')]
        add_additional_page = int(request.form['add_additional_page'])
        save_path = 'presentations'
        os.makedirs(save_path, exist_ok=True)
        output_file = os.path.join(save_path, 'proposal.pptx')
        create_presentation(slide_count, save_path, head_title, subtitle, section0, section1, subsections1, section2, subsections2, section3, subsections3, section4, subsections4, add_additional_page)
        
        if not os.path.exists(output_file):
            abort(404, description="File not found")
        
        return send_file(output_file, as_attachment=True)
    except ValueError:
        return "유효한 숫자를 입력하세요.", 400
    except Exception as e:
        return str(e), 500

@app.route('/preview_excel', methods=['POST'])
def route_preview_excel():
    return preview_excel()

@app.route('/create_excel', methods=['POST'])
def route_create_excel():
    return create_excel()

if __name__ == '__main__':
    app.run(debug=True)
