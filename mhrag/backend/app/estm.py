from flask import render_template, request, send_file
import pandas as pd
from io import BytesIO

def preview_excel():
    rows = int(request.form['rows'])
    cols = int(request.form['cols'])
    return render_template('excel.html', preview=True, rows=rows, cols=cols)

def create_excel():
    rows = int(request.form['rows'])
    cols = int(request.form['cols'])
    data = []
    for row in range(rows):
        row_data = []
        for col in range(cols):
            cell_name = f'cell_{row}_{col}'
            row_data.append(request.form.get(cell_name, ''))
        data.append(row_data)
    
    df = pd.DataFrame(data, columns=[f'Column {i+1}' for i in range(cols)])
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    output.seek(0)
    return send_file(output, download_name="example.xlsx", as_attachment=True)
