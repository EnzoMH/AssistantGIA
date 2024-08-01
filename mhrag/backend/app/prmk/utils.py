def set_font(text_shape, font_name, font_size, bold=False, color=None):
    text_frame = text_shape.text_frame
    for paragraph in text_frame.paragraphs:
        for run in paragraph.runs:
            run.font.name = font_name
            run.font.size = font_size
            run.font.bold = bold
            if color:
                run.font.color.rgb = color
