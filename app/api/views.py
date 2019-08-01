from flask import request, jsonify, json

from . import api
from app.models import IncomeType


# 收入科目
@api.route("/exists_subject", methods=['POST'])
def exists_subject():
    '''
        判断一个收入科目名称是否存在
    '''
    exists = False
    subject = request.form.get('subject').strip()
    if subject:
        result = IncomeType.query.filter_by(name=subject).first()
        if result:
            exists = True
    return jsonify({"exists":exists})