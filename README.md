# 项目名称
CAD 文件管理与搜索系统

## 项目简介
这是一个基于 Flask 的 Web 应用程序，用于管理和搜索 CAD 文件。用户可以通过上传的 Excel 文件进行关键字搜索，并下载匹配的 CAD 文件。

## 功能
1. **关键字搜索**：通过 Excel 文件中的数据进行关键字搜索。
2. **文件下载**：支持下载匹配的 CAD 文件。
3. **文件列表**：列出所有可用的 CAD 文件。
4. **环境检查**：检查系统环境是否满足运行要求。
5. **文件详情**：获取指定文件的详细信息，包括相关关键字。

## 文件结构
- `app.py`：主程序文件，包含所有 API 路由。
- `index.html`：前端页面。
- `script.js`：前端交互逻辑。
- `styles.css`：前端样式表。
- `cad_files/`：存放 CAD 文件的目录。

## 环境要求
- Python 3.6 或更高版本
- Flask
- Flask-CORS
- Pandas

## 安装与运行
1. 克隆项目：
   ```bash
   git clone https://github.com/licx506/cadfind.git
   cd cadfind
   ```
2. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```
3. 运行程序：
   ```bash
   python app.py
   ```
4. 打开浏览器访问：`http://127.0.0.1:5000`

## API 接口
### 1. `/api/search`
- **方法**：GET
- **参数**：`keyword` (必填)
- **功能**：根据关键字搜索 Excel 数据。

### 2. `/api/download/<filename>`
- **方法**：GET
- **参数**：`filename` (必填)
- **功能**：下载指定的 CAD 文件。

### 3. `/api/list_files`
- **方法**：GET
- **功能**：列出所有可用的 CAD 文件。

### 4. `/api/check_environment`
- **方法**：GET
- **功能**：检查系统环境是否满足运行要求。

### 5. `/api/details`
- **方法**：GET
- **参数**：`filename` (必填)
- **功能**：获取指定文件的详细信息。

## 日志
日志记录在控制台中，包含调试信息、警告和错误。

## 注意事项
- 确保 Excel 文件和 CAD 文件目录存在。
- Excel 文件的第一列应包含文件名。

## 贡献
欢迎提交 Issue 和 Pull Request 来改进本项目。

## 许可证
MIT License