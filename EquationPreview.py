import sublime, sublime_plugin
import hashlib
import os
import re
import requests
import struct
import time


# http://jamesgregson.blogspot.com/2013/06/latex-formulas-as-images-using-python.html
def formula_as_file(formula, file):
    url = 'http://latex.codecogs.com/gif.latex?\dpi{{300}} \\bg_white {}'.format(formula)
    r = requests.get(url)
    path = os.path.dirname(file)
    if path:
        os.makedirs(path, exist_ok = True)
    with open(file, "wb") as f:
        f.write(r.content)

# https://stackoverflow.com/questions/8032642/how-to-obtain-image-size-using-standard-python-class-without-using-external-lib
# gif image
def get_image_size(file):
    width, height = None, None
    with open(file, "rb") as f:
        head = f.read(24)
        if (len(head) == 24):
            # must be gif
            width, height = struct.unpack('<HH', head[6:10])
    return width, height


class EquationPreview(sublime_plugin.TextCommand):
    def run(self, edit, point = None):
        if not point:
            point = self.view.sel()[0].begin()
        self.show_equation(point)

    # First assume that the equation is in a line
    def extract_formula(self, view, point):
        text = view.substr(view.line(point))
        match_obj = re.search(r"\$[^$]*\$", text)
        if not match_obj:
            row, _ = view.rowcol(point)
            row_up, row_down = row, row + 1
            text_up = text

            def text_line(view, row):
                return view.substr(view.line(view.text_point(row, 0)))

            def scope_name_line(view, row):
                return view.scope_name(view.text_point(row, 0))

            text_down = text_line(view, row_down)
            text_combine = ""
            # col must be 0, otherwise 
            while (not re.search(r"\$+", text_up) and
                    "comment" in scope_name_line(view, row_up) and 
                    row_up >= 0):
                text_combine = text_up + text_combine
                row_up = row_up - 1
                text_up = text_line(view, row_up)
            
            max_line_num, _ = view.rowcol(view.size())
            while (not re.search(r"\$+", text_down) and
                    "comment" in scope_name_line(view, row_down) and 
                    row_down <= max_line_num):
                text_combine = text_combine + text_down
                row_down = row_down + 1
                text_down = text_line(view, row_down)
            formula = re.sub(r"#", "", text_combine)
            # if not search two character $, assume that it's not a formula 
            if (not re.search(r"\$+", text_line(view, row_up))
                    or not re.search(r"\$+", text_line(view, row_down))):
                formula = None
        else:
            formula = match_obj.group(0)[1:-1]
        return formula

    def show_equation(self, point):
        formula = self.extract_formula(self.view, point)
        if not formula:
            return
        tmp_path = os.path.join(sublime.packages_path(), "EquationPreview", "tmp")
        file = hashlib.md5(formula.encode('utf-8')).hexdigest() + ".gif"
        path_file = os.path.join(tmp_path, file)
        formula_as_file(formula, path_file)
        width, height = get_image_size(path_file)
        print(width, height)
        content = '<img src="file://{}", width={}, height={}>'.format(path_file, width, height)

        def on_hide():
            os.remove(path_file)

        self.view.show_popup(
            content,
            flags = sublime.HIDE_ON_MOUSE_MOVE_AWAY,
            location = point,
            max_width = self.view.viewport_extent()[0],
            max_height = self.view.viewport_extent()[1],
            on_hide = on_hide)


class EquationPreviewListener(sublime_plugin.EventListener):
    def on_hover(self, view, point, hover_zone):
        if (hover_zone == sublime.HOVER_TEXT):
            # show preview equation in comment scope
            scope = view.scope_name(point)
            if "comment" in scope:
                view.run_command("equation_preview", args = {"point": point})