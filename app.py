from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import pandas as pd
import os
import re
import logging
import sys

# 添加静态文件支持
app = Flask(__name__, static_url_path='', static_folder='.')

# 修改CORS配置，允许所有来源访问
CORS(app, resources={r"/*": {"origins": "*"}})
# 配置
EXCEL_FILE = "验收资源编码清单2011-2021.xlsx"
CAD_DIRECTORY = "cad_files"  # CAD文件存放目录

# 配置日志记录
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# 在应用启动时将Excel文件加载到内存中
try:
    EXCEL_DATAFRAME = pd.read_excel(EXCEL_FILE)
    logging.info("成功加载Excel文件到内存: %s", EXCEL_FILE)
except Exception as e:
    logging.error("加载Excel文件失败: %s", str(e))
    EXCEL_DATAFRAME = None

@app.route('/')
def index():
    return send_file('index.html')

@app.route('/api/search', methods=['GET'])
def search_keyword():
    keyword = request.args.get('keyword', '')
    if not keyword:
        logging.warning("搜索关键字为空")
        return jsonify({"error": "关键字不能为空"}), 400
    
    logging.debug("接收到的搜索关键字: %s", keyword)

    if EXCEL_DATAFRAME is None:
        logging.error("Excel数据未正确加载")
        return jsonify({"error": "Excel数据未正确加载"}), 500

    try:
        # 清理空列
        cleaned_df = EXCEL_DATAFRAME.dropna(how='all', axis=1)

        # 使用矢量化操作进行搜索
        mask = cleaned_df.apply(lambda row: row.astype(str).str.contains(keyword, case=False, na=False).any(), axis=1)
        filtered_df = cleaned_df[mask]

        # 构建结果
        results = []
        for index, row in filtered_df.iterrows():
            filename = str(row.iloc[0])  # 获取第一列的值作为文件名
            row_data = {k: v for k, v in row.items() if pd.notna(v)}  # 仅保留非空值
            results.append({
                "filename": filename,
                "row_data": row_data,
                "row_number": index + 1
            })
        
        if not results:
            logging.info("未找到匹配的结果")
            return jsonify({"message": "未找到匹配的结果", "results": []}), 200

        logging.debug("搜索结果数量: %d", len(results))
        return jsonify({"results": results}), 200
    
    except Exception as e:
        logging.error("搜索关键字时发生错误: %s", str(e))
        return jsonify({"error": str(e)}), 500

@app.route('/api/download/<filename>', methods=['GET'])
def download_cad(filename):
    # 清理文件名，防止目录遍历攻击
    safe_filename = re.sub(r'[^\w\.-]', '_', filename)
    
    # 在CAD目录中查找匹配的文件
    cad_extensions = ['.dwg', '.dxf', '.dwt', '.dws']
    
    logging.info("尝试下载文件: %s", filename)
    for ext in cad_extensions:
        file_path = os.path.join(CAD_DIRECTORY, safe_filename + ext)
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True)
    
    # 如果没有扩展名，尝试查找任何匹配文件名的CAD文件
    matched_files = []
    if os.path.exists(CAD_DIRECTORY):
        for file in os.listdir(CAD_DIRECTORY):
            file_base = os.path.splitext(file)[0]
            if file_base == safe_filename:
                return send_file(os.path.join(CAD_DIRECTORY, file), as_attachment=True)
    
    logging.error("找不到对应的CAD文件: %s", filename)
    return jsonify({"error": "找不到对应的CAD文件"}), 404

@app.route('/api/list_files', methods=['GET'])
def list_files():
    """获取所有CAD文件列表"""
    if not os.path.exists(CAD_DIRECTORY):
        return jsonify({"files": []})
    
    files = [f for f in os.listdir(CAD_DIRECTORY) 
             if f.endswith(('.dwg', '.dxf', '.dwt', '.dws'))]
    
    return jsonify({"files": files})

@app.route('/api/check_environment', methods=['GET'])
def check_environment():
    """检查系统环境是否满足脚本运行的要求"""
    errors = []

    # 检查Python版本
    if sys.version_info < (3, 6):
        errors.append("Python版本过低，需要Python 3.6或更高版本")

    # 检查Excel文件是否存在
    if not os.path.exists(EXCEL_FILE):
        errors.append(f"缺少Excel文件: {EXCEL_FILE}")

    # 检查CAD目录是否存在
    if not os.path.exists(CAD_DIRECTORY):
        errors.append(f"缺少CAD目录: {CAD_DIRECTORY}")

    # 检查必要的Python模块
    try:
        import pandas
    except ImportError:
        errors.append("缺少模块: pandas")

    try:
        import flask
    except ImportError:
        errors.append("缺少模块: flask")

    try:
        import flask_cors
    except ImportError:
        errors.append("缺少模块: flask_cors")

    # 返回检查结果
    if errors:
        logging.error("环境检查失败: %s", errors)
        return jsonify({"status": "error", "errors": errors}), 500

    logging.info("系统环境正常")
    return jsonify({"status": "ok", "message": "系统环境正常"}), 200

@app.route('/api/details', methods=['GET'])
def get_file_details():
    filename = request.args.get('filename', '')
    if not filename:
        return jsonify({"error": "文件名不能为空"}), 400

    if EXCEL_DATAFRAME is None:
        logging.error("Excel数据未正确加载")
        return jsonify({"error": "Excel数据未正确加载"}), 500

    try:
        # 清理空列
        cleaned_df = EXCEL_DATAFRAME.dropna(how='all', axis=1)

        # 查找与文件名匹配的行
        matched_rows = cleaned_df[cleaned_df.iloc[:, 0].astype(str) == filename]
        if matched_rows.empty:
            logging.info("未找到与文件名匹配的行: %s", filename)
            return jsonify({"error": "未找到与文件名匹配的行"}), 404

        # 提取关键字（非空单元格的唯一值）
        keywords = set()
        for _, row in matched_rows.iterrows():
            for cell in row:
                if pd.notna(cell):
                    keywords.update(str(cell).split())

        details = {
            "filename": filename,
            "keywords": list(keywords)  # 转换为列表以便JSON序列化
        }
        logging.info("成功提取文件详情: %s", details)
        return jsonify({"details": details})

    except Exception as e:
        logging.error("获取文件详情时发生错误: %s", str(e))
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # 确保CAD目录存在
    os.makedirs(CAD_DIRECTORY, exist_ok=True)
    logging.info("CAD目录已创建或已存在: %s", CAD_DIRECTORY)
    app.run(debug=True, port=5000)
