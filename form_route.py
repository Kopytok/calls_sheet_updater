from app_file import app
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import SubmitField, SelectField
from werkzeug.utils import secure_filename
from flask import render_template, request, url_for, redirect, flash

from calls.update import CallsSheetUpdater
from calls.constants import *

@app.route("/upload", methods=["GET", "POST"])
def upload():
    form = CsvForm()

    if request.method == "GET":
        return render_template("upload.html", form=form)

    if not form.validate_on_submit():
        flash("Форма не была валидирована, попробуйте снова")
        return

    platform = form.platform.data
    file_object = form.csv_file.data
    file_name = secure_filename(file_object.filename)

    if file_name.rsplit(".", 1)[1] != "csv":
        flash("Это не CSV-файл")
        return redirect(url_for("upload"))

    CallsSheetUpdater(SPREADSHEET, platform).update(file_object)
    flash(f"Файл '{file_name}' ({platform}) успешно загружен")
    return redirect(url_for("upload"))


class CsvForm(FlaskForm):
    platform = SelectField(u"Платформа", choices=[
        ("betman", "BetMan"),
        ("natasha", "Natasha"),
    ])
    csv_file = FileField(validators=[FileRequired()])
    submit = SubmitField("Загрузить")
