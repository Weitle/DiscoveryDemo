from datetime import datetime
import random
from flask import request, jsonify

from . import analysis
from app.data import income_target
from app.config import DISTRICTS

@analysis.route('/getIncomeMonthly', methods=['POST'])
def get_income_monthly():
    year = request.form.get('year').strip()
    month = int(request.form.get('month').strip())
    # 获取年度目标
    target = income_target[year]
    # 随机生成每月收入
    base_income = target/12
    incomes = [int(base_income + (random.random()-0.5) * base_income/5) for i in range(month)]
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

@analysis.route('/getIncomeDistrictMonthly', methods=['POST'])
def get_income_district_monthly():
    year = request.form.get('year').strip()
    month = int(request.form.get('month').strip())
    # 获取本年度各分公司收入指标
    targets = get_targets_by_year(year)
    income_districts = []
    for m in range(month):
        income_districts.append(tuple((target/12*(1+(random.random()-0.5)/10)) for target in targets))
    return jsonify({'districts':DISTRICTS, 'incomes':income_districts, 'targets':targets})


def get_targets_by_year(year):
    #total = income_target[year]
    #return {"和平": 38666, "河东":36367, "南开":39654, "河北":31132, "红桥":28932, "河西":46336, "东丽":29535, "津南":23787, "西青":50838, "北辰":29962, "塘沽":72048, "汉沽":11393, "大港":1618, "蓟州":25575, "宝坻":23489, "武清":32227, "静海":29624, "宁河":15572}
    return (38666, 36367, 46336, 39654, 28932, 31132, 29535, 23787, 50838,29962,72048,11393, 1618, 29624,15572, 32227, 23489,25575)
