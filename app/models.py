from app.db import db

from sqlalchemy.dialects.mysql import INTEGER, SMALLINT, TINYINT, DOUBLE

class Product(db.Model):
    __tablename__ = "products"
    # 系统定义的产品 id 由 product_id + 3位序列编码组成
    # 如果原始产品是融合产品，可能对应多个内部 id
    prod_id_internal = db.Column(db.String(11), primary_key=True)
    # 产品 id，对应 B 侧系统的 product_id
    product_id = db.Column(db.String(8), nullable=False, index=True)
    # 产品名称，与 B 侧系统的产品名称相同
    product_name = db.Column(db.String(100), nullable=False, index=True)
    # 是否是融合产品（是否可省略？通过内部 Id 来判断？）
    flusion_flag = db.Column(db.Boolean, default=False)
    # 系统来源，0 - BSS, 1 - CBSS, ...
    system = db.Column(TINYINT(unsigned=True), default=0)
    # 上线时间
    online_date = db.Column(db.Date, nullable=False)
    # 停售时间
    offline_date = db.Column(db.Date, nullable=True)
    # 适用地市编码，默认为 '0'，即全部都使用
    city_code = db.Column(db.String(8), nullable=False, index=True, default='0')
    # 适用网别或业务大类
    net_type_code = db.Column(db.String(8), nullable=False, index=True)
    price = db.Column(db.Float, nullable=False, default=0.0)
    voice = db.Column(db.SmallInteger, nullable=False, default=-1)
    sms = db.Column(db.SmallInteger, nullable=False, default=-1)
    data = db.Column(db.SmallInteger, nullable=False, default=-1)
    # 融合产品可以捆绑的固话数量
    fix_line_num = db.Column(db.SmallInteger, nullable=False, default=0)
    # 融合产品可以捆绑的宽带数量
    broad_band_num = db.Column(db.SmallInteger, nullable=False, default=0)
    # 融合产品和以捆绑的手机数量
    mobile_num = db.Column(db.SmallInteger, nullable=False, default=0)
    #discount = db.Column(db.Float, nullable=False, default=1.0)
    # 前两个字母表示类型，后六个字母表示存费或者合约的费用等
    pre_fee = db.Column(db.String(8), nullable= False, default='00000000')

# 渠道关联
channel_relation = db.Table('channel_relation',
    db.Column('sub_chnl_no', db.String(12), db.ForeignKey('channels.chnl_no')),
    db.Column('sup_chnl_no', db.String(12), db.ForeignKey('channels.chnl_no'))
)
# 渠道
class Channel(db.Model):
    __tablename__ = "channels"
    chnl_no = db.Column(db.String(12), primary_key=True)
    chnl_name = db.Column(db.String(200), nullable=False)
    chnl_cat_1 = db.Column(db.SmallInteger, nullable=False)
    chnl_cat_2 = db.Column(db.SmallInteger, nullable=False)
    chnl_cat_3 = db.Column(db.SmallInteger, nullable=False)
    # 经纬度，默认 -1，表示非线下渠道
    longitude = db.Column(db.String(20), nullable=False, default='-1')
    latitude = db.Column(db.String(20), nullable=False, default='-1')
    contract_life = db.Column(db.Date, nullable=False)
    # 归属分公司，线上渠道是否不归属于分公司？（可使用默认值0）
    city_code = db.Column(db.String(8), nullable=False, index=True, default='0')
    # 下一层级渠道
    sub_channels = db.relationship(
        # 关联的模型，自关联
        'Channel', 
        # 关联的表，定义的 channel_relation 表，存储各个渠道之间的关系
        secondary = 'channel_relation', 
        primaryjoin = (channel_relation.c.sup_chnl_no == chnl_no),
        secondaryjoin = (channel_relation.c.sub_chnl_no == chnl_no),
        backref = db.backref('sup_channel', lazy='dynamic'),
        lazy = 'dynamic'
    )

# 收入展示
# 收入科目关联表
income_type_relation = db.Table(
    'income_type_relation',
    # 上一层级
    db.Column('sup_type', SMALLINT(unsigned=True), db.ForeignKey('income_types.id')),
    # 下一层级
    db.Column('sub_type', SMALLINT(unsigned=True), db.ForeignKey('income_types.id'))
)
class IncomeType(db.Model):
    __tablename__ = "income_types"
    id = db.Column(SMALLINT(unsigned=True), primary_key=True)
    # 收入科目名称
    name = db.Column(db.String(50), nullable=False)
    # 收入科目层级，主营业务收入层级为 0
    level = db.Column(TINYINT(unsigned=True), nullable=False, default=0)
    # 本科目的下一层级科目
    sub_types = db.relationship(
        'IncomeType',
        secondary = 'income_type_relation',
        primaryjoin = (income_type_relation.c.sup_type == id),
        secondaryjoin = (income_type_relation.c.sub_type == id),
        backref = db.backref('sup_type', lazy='dynamic'),
        lazy = 'dynamic'
    )
    # 本科目下的收入
    incomes = db.relationship('Income', backref='incomes', lazy='dynamic')

# 收入
class Income(db.Model):
    __tablename__ = "incomes"
    # 收入账期
    acct_month = db.Column(db.String(6), primary_key=True)
    # 收入科目
    subject = db.Column(SMALLINT(unsigned=True), db.ForeignKey('income_types.id'), primary_key=True)
    # 收入
    income = db.Column(DOUBLE(16, 2), default=0.0)
    # 税额
    tax = db.Column(DOUBLE(16, 2), default=0.0)