from flask import render_template

from app.admin import admin

@admin.route('/addsubject')
def addsubject():
    return render_template('admin/addsubject.html')