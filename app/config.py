import os

DISTRICTS = ('和平', '河东', '河西', '南开', '红桥', '河北', '东丽', '津南', '西青', '北辰', '塘沽', '汉沽', '大港', '静海', '宁河', '武清', '宝坻', '蓟州')

# 上传h和下载文件保存路径
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static/uploads')
DOWNLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static/templates')
# 允许上传的文件类型
ALLOWED_EXTENSIONS = set(['xlsx', 'xls'])