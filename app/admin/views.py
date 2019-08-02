import os
import random

from datetime import datetime
from flask import render_template, request, flash, redirect, url_for
from sqlalchemy import func, and_, desc
import xlsxwriter, xlrd

from app.admin import admin
from app.models import IncomeType, Income
from app.db import db
from app.config import DOWNLOAD_FOLDER, UPLOAD_FOLDER, ALLOWED_EXTENSIONS


@admin.route('/subjects')
def subjects():
    '''
        显示所有收入科目信息
    '''
    subjects = IncomeType.query.all()
    return render_template('admin/subjects.html', subjects=subjects)

@admin.route('/addsubject',methods=['GET', 'POST'])
def addsubject():
    '''添加收入科目信息，收入科目名称唯一，添加到相应的上一层级科目下'''
    if request.method == 'POST':
        name = request.form.get('name').strip()
        sname = request.form.get('sname').strip()
        sid = request.form.get('sid')
        if sid:
            sid = int(sid.strip())
        errors = []
        if name == '':
            errors.append(u'新增收入科目名称为空。')
        else:
            if exists_subject(name):
                errors.append(u'新增收入科目名称已经存在。')
            if sname and not exists_subject(sname):
                errors.append(u'上一层级科目名称不存在。')
        if errors:
            for error in errors:
                flash(error, 'error')
            return redirect(url_for('admin.addsubject'))
        else:
            # 数据校验通过后写入数据库
            try:
                if sname == '':
                    type_to_add = IncomeType(name=name, level=0)
                    db.session.add(type_to_add)
                    db.session.commit()
                else:
                    sup_type = get_subject_by_name(sname)
                    sub_type = IncomeType(name=name, level=sup_type.level+1)
                    sup_type.sub_types.append(sub_type)
                    db.session.add(sub_type)
                    db.session.add(sup_type)
                    db.session.commit()
            except Exception as e:
                flash(u'添加收入科目失败，请重试。', 'error')
                return redirect(url_for('admin.addsubject'))
            else:
                flash(u'成功添加收入科目。', 'info')
                return redirect(url_for('admin.subjects'))
    else:
        sname = request.args.get('sname')
        if sname:
            sname = sname.strip()
        return render_template('admin/addsubject.html', sname=sname)

@admin.route('/incomes')
def incomes():
    # 根据账期获取各专业收入
    acct_month = "201906"
    acct_year = "2019"
    total_incomes = db.session.query(Income.acct_month, Income.income).filter(and_(Income.acct_month.like(acct_year + '%'), IncomeType.level==0, Income.subject==IncomeType.id)).all()
    #subject_incomes = db.session.query(Income.acct_month, Income.subject, IncomeType.name, IncomeType.level, Income.income, Income.tax).filter(and_(Income.subject==IncomeType.id, IncomeType.level<=1, Income.acct_month.like(acct_year+'%'))).order_by(desc(Income.acct_month), Income.subject).all()
    incomes_month = db.session.query(Income.subject, IncomeType.name, Income.income, Income.tax).filter(and_(Income.subject==IncomeType.id, IncomeType.level==1, Income.acct_month==acct_month)).all()
    return render_template('admin/incomes.html', total_incomes=total_incomes, incomes_month=incomes_month)

@admin.route("/addincomes", methods=['GET', 'POST'])
def addincomes():
    '''按月份录入当月各科目收入信息'''
    if request.method =='POST':
        if 'income_file' not in request.files:
            flash(u'未找到上传文件，请重试。', 'error')
            return redirect(url_for('admin.addincomes'))
        uploadfile = request.files['income_file']
        if uploadfile.filename == '':
            flash(u'没有选择上传文件，请重试。', 'error')
            return redirect(url_for('admin.addincomes'))
        if uploadfile and allowed_file(uploadfile.filename):
            filename = os.path.join(UPLOAD_FOLDER, make_filename(uploadfile.filename))
            uploadfile.save(filename)
            acct_month = request.form.get('income_month').strip()
            # 添加收入
            successed = add_incomes_from_file(acct_month, filename)
            if successed != -1:
                add_supincomes(acct_month)
                flash(u"账期 {} 业务收入已成功保存。".format(acct_month), 'info')
                return redirect(url_for('admin.incomes'))
            else:
                flash(u"数据库写入失败，请重试。", 'error')
                return redirect(url_for('admin.addincomes'))
        else:
            flash(u'文件格式错误，请重试！', 'error')
            return redirect(url_for('admin.addincomes'))
    return render_template('admin/addincomes.html')

# 判断上传文件类型是否合法
def allowed_file(filename):
    return '.' in filename and filename.split('.')[-1].lower() in ALLOWED_EXTENSIONS
# 生成上传文件名，添加时间戳
def make_filename(filename):
    fname_arr = filename.split(".")
    now = datetime.now()
    return "{}_{}.{}".format(fname_arr[0], now.strftime('%Y%m%d%H%M%S'), fname_arr[-1])
# 从上传文件读取问题更新进度
def get_incomes_from_file(filename):
    book = xlrd.open_workbook(filename)
    sheet = book.sheet_by_name(u'各业务收入')
    row = 1
    while row<sheet.nrows:
        incomes = sheet.row_values(row)
        yield incomes
        row += 1
# 从文件中读取数据批量添加业务收入
def add_incomes_from_file(month, filename):
    incomes = get_incomes_from_file(filename)
    added = 0
    for income in incomes:
        subject = income[0]
        inc = income[2]
        tax = income[3]
        if inc != 0:
            db.session.add(Income(acct_month=month, subject=subject, income=inc, tax=tax))
            added += 1
    # 批量写入到数据库
    try:
        db.session.commit()
    except Exception as e:
        print(e)
        db.session.rollback()
        added = -1
    return added

# 添加层级为 0 和 1 的业务收入
def add_supincomes(month):
    total_income = 0
    total_tax = 0
    # 查询层级为 1 的业务
    subjects = IncomeType.query.filter(IncomeType.level==1).all()
    for subject in subjects:
        subject_income = 0
        subject_tax = 0
        # 查询每个层级为 1 的业务的子业务
        subtypes = subject.sub_types.all()
        subids = tuple((subtype.id for subtype in subtypes))
        subincomes = Income.query.filter(and_(Income.subject.in_(subids), Income.acct_month==month)).all()
        for subincome in subincomes:
            subject_income += subincome.income
            subject_tax += subincome.tax
        total_income += subject_income
        total_tax += subject_tax
        income = Income(acct_month=month, subject=subject.id, income=subject_income, tax=subject_tax)
        db.session.add(income)
        db.session.commit()
    total = Income(acct_month=month, subject=1, income=total_income, tax=total_tax)
    db.session.add(total)
    db.session.commit()
    return render_template('admin/incomes.html')

@admin.route('/makeincometemp')
def make_income_temp():
    '''生成收入录入模板文件'''
    subjects = IncomeType.query.filter(IncomeType.level==2).all()
    # 生成收入录入模板文件
    savefile(u"收入录入模板.xlsx", subjects)
    return redirect(url_for('admin.addincomes'))

# 保存收入录入模板文件
def savefile(filename, subjects):
    filename = os.path.join(DOWNLOAD_FOLDER, filename)
    titles = (u'收入序号', u'收入科目', u'收入/元', u'税款/元')
    book = xlsxwriter.Workbook(filename)
    sheet = book.add_worksheet(u'各业务收入')
    # 设置格式
    basicFormat = book.add_format({'border':1, 'align': 'center', 'valign': 'vcenter', 'text_wrap': True})
    #lockedFormat = book.add_format({'border':1, 'align': 'center', 'valign': 'vcenter', 'text_wrap': True, 'locked':True})
    bgColorFormat = book.add_format({'border':1, 'align': 'center', 'valign': 'vcenter', 'text_wrap': True, 'bg_color': 'yellow'})
    dateFormat = book.add_format({'border':1, 'align': 'center', 'valign': 'vcenter', 'text_wrap': True, 'num_format':'yyyy-mm-dd'})
    sheet.set_column("A:A", 10)
    sheet.set_column("B:B", 50)
    sheet.set_column("C:D", 30)
    #sheet.protect()
    # 写入表头
    for col in range(len(titles)):
        sheet.write(0, col, titles[col], basicFormat)
        #sheet.write_row(0, 0, titles, basicFormat)
    # 写入内容
    row = 1
    basicFormat.set_locked(True)
    locked = book.add_format({'border':1, 'align': 'center', 'valign': 'vcenter', 'text_wrap': True})
    basicFormat.set_locked(False)
    for subject in subjects:
        # 写入一行
        sheet.protect()
        sheet.write(row, 0, subject.id, locked)
        sheet.write(row, 1, subject.name, locked)
        sheet.write(row, 2, '', basicFormat)
        sheet.write(row, 3, '', basicFormat)
        row += 1
    book.close()

def exists_subject(subject):
    '''
        判断收入科目名称是否已存在
    '''
    result = IncomeType.query.filter_by(name=subject).first()
    if result:
        return True
    return False

def get_level_by_subject(subject):
    '''
        根据收入科目名称返回相应的层级
    '''
    result = IncomeType.query(IncomeType.level).filter_by(name=subject).first()
    return result[0]

def get_subject_by_name(name):
    '''
        根据名称查询收入科目
    '''
    subject = IncomeType.query.filter_by(name=name).first()
    return subject

#@admin.route('/generate_incomes')
#def generate_incomes():
#    incomes = db.session.query(Income.subject, Income.income, Income.tax).filter(and_(Income.acct_month=="201905", IncomeType.level>=2, Income.subject==IncomeType.id)).all()
#    months = ["201901", "201902", "201903", "201904", "201906"]
#    for month in months:
#        for record in incomes:
#            income = float(record[1]) * (1 + random.randint(0, 100)/1000)
#            tax = float(record[2]) * (1 + random.randint(0, 100)/1000)
#            subject_income = Income(acct_month=month, subject=record[0], income=income, tax=tax)
#            db.session.add(subject_income)
#        db.session.commit()
#        add_supincomes(month)