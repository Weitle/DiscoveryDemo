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
    incomes = [int(base_income + (random.random()-0.5) * base_income/5) if i < month else 0 for i in range(12)]
    return jsonify({'target':target, 'incomes':incomes})

@analysis.route('/getIncomeBusinessMonthly', methods=['POST'])
def get_income_business_monthly():
    year = request.form.get('year').strip()
    month = int(request.form.get('month').strip())
    incomes = []
    for i in range(month):
        income_2G = int(2000 + 200 * (random.random()-0.5))
        income_3G = int(8000 + 800 * (random.random()-0.5))
        income_4G = int(30000 + 3000 * (random.random()-0.5))
        income_bb = int(20000 + 2000 * (random.random()-0.5))
        income_idc = int(8000 + 800 * (random.random()-0.5))
        incomes.append({'2G':income_2G, '3G':income_3G, '4G':income_4G, 'BB':income_bb, 'IDC':income_idc})
    return jsonify({'incomes':incomes})