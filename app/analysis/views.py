from datetime import datetime
import random
from flask import request, jsonify

from . import analysis
from app.data import income_target

@analysis.route('/getIncomeMonthly', methods=['POST'])
def get_income_monthly():
    year = request.form.get('year').strip()
    # 获取年度目标
    target = income_target[year]
    # 随机生成每月收入
    base_income = target/12
    now = datetime.now()
    month = now.month
    incomes = [int(base_income + (random.random()-0.5) * base_income/20) if i < month else 0 for i in range(12)]
    return jsonify({'target':target, 'incomes':incomes})