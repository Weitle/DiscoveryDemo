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
    year = int(request.form.get('year').strip())
    month = int(request.form.get('month').strip())
    # 获取本年度各分公司收入指标
    targets = get_targets_by_year(year)
    # 获取每个分公司本月以及累计收入
    incomes_this_month = get_incomes_by_month(year, month)
    incomes_this_year = get_current_incomes(year, month)
    # 获取每个分公司上个月收入
    if(month == 1):
        incomes_last_month = get_incomes_by_month(year-1, 12)
    else:
        incomes_last_month = get_incomes_by_month(year, month-1)
    rate_this_month = {}
    rate_this_year = {}
    rate_increment = {}
    for district in targets:
        rate_this_month[district] = round(incomes_this_month[district]['合计']/targets[district]*10000)/100
        rate_this_year[district] = round(incomes_this_year[district]['合计']/targets[district]*10000)/100
        rate_increment[district] = round(incomes_this_month[district]['合计']/incomes_last_month[district]['合计']*10000)/100
    rate_this_year_labels = get_labels_order(rate_this_year)
    rate_this_month_labels = get_labels_order(rate_this_month)
    rate_increment_labels = get_labels_order(rate_increment)  
    return jsonify({'targets':targets, 'incomes_this_year':incomes_this_year, 'incomes_this_month':incomes_this_month, 'incomes_lat_month':incomes_last_month, 'rate_this_year':rate_this_year, 'rate_this_month':rate_this_month, 'rate_increment':rate_increment, 'rate_this_year_labels':rate_this_year_labels, 'rate_this_month_labels':rate_this_month_labels, 'rate_increment_labels':rate_increment_labels})

def get_targets_by_year(year):
    #total = income_target[year]
    return {"和平": 38666, "河东":36367, "南开":39654, "河北":31132, "红桥":28932, "河西":46336, "东丽":29535, "津南":23787, "西青":50838, "北辰":29962, "塘沽":72048, "汉沽":11393, "大港":16118, "蓟州":25575, "宝坻":23489, "武清":32227, "静海":29624, "宁河":15572}
    #return (38666, 36367, 46336, 39654, 28932, 31132, 29535, 23787, 50838,29962,72048,11393, 1618, 29624,15572, 32227, 23489,25575)

# 获取指定月份的收入
def get_incomes_by_month(year, month):
    targets = get_targets_by_year(year)
    incomes = {}
    for district, target in targets.items():
        total = round(target / 12 * (1 + (random.random()-0.5)/10))
        income_2G = round(total / 70 * (1 + (random.random()-0.5)/20))
        income_3G = round(total * 5 / 70 * (1 + (random.random()-0.5)/20))
        income_4G = round(total * 28 / 70 * (1 + (random.random()-0.5)/20))
        income_BB = round(total * 20 / 70 * (1 + (random.random()-0.5)/20))
        income_ICT = round(total * 12 / 70 * (1 + (random.random()-0.5)/20))
        income_others = total - income_2G - income_3G - income_4G - income_BB - income_ICT
        incomes[district] = {'2G': income_2G, '3G': income_3G, '4G':income_4G, '宽带': income_BB, 'ICT': income_ICT, '其它': income_others, '合计': total}
    return incomes

# 获取截至当前各分公司累计收入
def get_current_incomes(year, month):
    targets = get_targets_by_year(year)
    incomes = {}
    #month = datetime.month
    for district, target in targets.items():
        total = round(target*month/12 * (1 + (random.random()-0.5)/10))
        income_2G = round(total / 70 * (1 + (random.random()-0.5)/20))
        income_3G = round(total * 5 / 70 * (1 + (random.random()-0.5)/20))
        income_4G = round(total * 28 / 70 * (1 + (random.random()-0.5)/20))
        income_BB = round(total * 20 / 70 * (1 + (random.random()-0.5)/20))
        income_ICT = round(total * 12 / 70 * (1 + (random.random()-0.5)/20))
        income_others = total - income_2G - income_3G - income_4G - income_BB - income_ICT
        incomes[district] = {'2G': income_2G, '3G': income_3G, '4G':income_4G, '宽带': income_BB, 'ICT': income_ICT, '其它': income_others, '合计':total}
    return incomes

# 获取年收入
def get_incomes_by_year(year):
    targets = get_targets_by_year(year)
    incomes = {}
    #month = datetime.month
    for district, target in targets.items():
        total = round(target * (1 + (random.random()-0.5)/10))
        income_2G = round(total / 70 * (1 + (random.random()-0.5)/20))
        income_3G = round(total * 5 / 70 * (1 + (random.random()-0.5)/20))
        income_4G = round(total * 28 / 70 * (1 + (random.random()-0.5)/20))
        income_BB = round(total * 20 / 70 * (1 + (random.random()-0.5)/20))
        income_ICT = round(total * 12 / 70 * (1 + (random.random()-0.5)/20))
        income_others = total - income_2G - income_3G - income_4G - income_BB - income_ICT
        incomes[district] = {'2G': income_2G, '3G': income_3G, '4G':income_4G, '宽带': income_BB, 'ICT': income_ICT, '其它': income_others, '合计':total}
    return incomes

def get_labels_order(dic_obj):
    labels = list(dic_obj.keys())
    values = list(dic_obj.values())
    #冒泡排序，降序
    for i in range(0, len(labels)-1):
        for j in range(i+1, len(labels)):
            if values[i] < values[j]:
                tmp = values[i]
                label_tmp = labels[i]
                values[i] = values[j]
                labels[i] = labels[j]
                values[j] = tmp
                labels[j] = label_tmp
    return labels





