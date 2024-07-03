import json
import threading
import time
from urllib.parse import parse_qs, urlparse
from typing import List
from http.server import BaseHTTPRequestHandler, HTTPServer
from data_handler import DataHandler
from data_models import CurrentWindows, AllWindows
from database import Database
from model_control import ModelControl


class ServerControl:
    def __init__(self, handlers: List[DataHandler], host: str = '127.0.0.1', port: int = 8212):
        """
        初始化 ServerControl 实例。

        :param handlers: 包含多个 DataHandler 的列表
        :param host: 主机地址，默认为 '127.0.0.1'
        :param port: 端口号，默认为 8212
        """
        self.handlers = handlers
        self.host = host
        self.port = port

    def start_server(self):
        """
        启动服务器。
        """
        server_address = (self.host, self.port)
        httpd = HTTPServer(server_address, self.RequestHandlerFactory())
        print(f"Starting server at http://{self.host}:{self.port}")
        httpd.serve_forever()

    def RequestHandlerFactory(self):
        """
        创建一个请求处理程序类，根据请求的路径返回相应的 DataHandler 的 JSON 数据。
        """
        handlers_dict = {f"/SetWindowsTopAPI{handler.url}": handler for handler in self.handlers}

        class CustomHandler(BaseHTTPRequestHandler):
            # 处理GET请求
            def do_GET(self):
                parsed_path = urlparse(self.path)
                if parsed_path.path == "/SetWindowsTopAPI":
                    self.send_response(200)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps({"message": "Welcome to WindowsSetTopAPI"}).encode())
                elif parsed_path.path.endswith("/detail") and parsed_path.path.rstrip("/detail") in handlers_dict:
                    base_path = parsed_path.path.rstrip("/detail")
                    handler = handlers_dict[base_path]
                    query = parse_qs(parsed_path.query)
                    self.handle_get_model_detail_request(handler, query)
                elif parsed_path.path in handlers_dict:
                    handler = handlers_dict[parsed_path.path]
                    self.handle_get_model_list_request(handler)
                else:
                    self.send_response(404)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": "Not found"}).encode())

            # 处理POST请求
            def do_POST(self):
                parsed_path = urlparse(self.path)
                if any(parsed_path.path.startswith(f"{key}/detail") for key in handlers_dict.keys()):
                    base_path = parsed_path.path.split("/detail")[0]
                    handler = handlers_dict.get(base_path)
                    if handler:
                        self.handle_post_request(handler)
                elif parsed_path.path == "/SetWindowsTopAPI/current_windows/toggle_set_top":
                    handler = handlers_dict.get("/SetWindowsTopAPI/current_windows")
                    if handler:
                        self.handle_toggle_set_top_request(handler, parsed_path.query)
                else:
                    self.send_response(404)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": "Not found"}).encode())

            def handle_get_model_list_request(self, handler):
                """
                处理 GET 请求并返回相应的 JSON 数据。

                :param handler: DataHandler 实例
                """
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(handler.get_model_list_json().encode())

            def handle_get_model_detail_request(self, handler, query=None):
                """
                处理详细模型查询请求，根据传入的 JSON 数据调用 handler 的 get_model_from_json 方法。

                :param handler: DataHandler 实例
                :param query: URL 参数字典
                """
                if query:
                    query_dict = {k: v[0].strip('"') for k, v in query.items()}  # 移除多余的引号
                    query_json = json.dumps(query_dict)
                    result_json = handler.get_model_from_json(query_json)
                else:
                    content_length = int(self.headers.get('Content-Length', 0))
                    if content_length > 0:
                        post_data = self.rfile.read(content_length).decode('utf-8')
                        result_json = handler.get_model_from_json(post_data)
                    else:
                        result_json = json.dumps({"error": "No data provided"})

                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(result_json.encode())

            def handle_post_request(self, handler):
                """
                处理 POST 请求，根据传入的 JSON 数据更新模型表。

                :param handler: DataHandler 实例
                """
                parsed_path = urlparse(self.path)
                query = parse_qs(parsed_path.query)
                data_dict = {}

                # 处理 URL 查询参数
                if query:
                    data_dict.update({k: v[0].strip('"') for k, v in query.items()})

                # 处理请求体数据
                content_length = int(self.headers.get('Content-Length', 0))
                if content_length > 0:
                    post_data = self.rfile.read(content_length).decode('utf-8')
                    try:
                        post_data_dict = json.loads(post_data)
                        data_dict.update(post_data_dict)
                    except json.JSONDecodeError:
                        self.send_response(400)
                        self.send_header("Content-type", "application/json")
                        self.end_headers()
                        self.wfile.write(json.dumps({"error": "Invalid JSON"}).encode())
                        return

                if not data_dict:
                    self.send_response(400)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": "No data provided"}).encode())
                    return

                # 更新模型数据
                json_data = json.dumps(data_dict)
                condition = 'hwnd' if 'hwnd' in data_dict else 'name' if 'name' in data_dict else None
                if condition:
                    handler.update_model_from_json(json_data, condition)
                    # 获取并返回更新后的模型数据
                    result_json = handler.get_model_from_json(json_data)
                    self.send_response(200)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    self.wfile.write(result_json.encode())
                else:
                    self.send_response(400)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": "No valid condition provided"}).encode())

            def handle_toggle_set_top_request(self, handler, query):
                """
                处理 POST 请求，根据传入的 JSON 数据切换 is_set_top 字段的值。

                :param handler: DataHandler 实例
                :param query: URL 参数字典
                """
                query_dict = parse_qs(query)
                data_dict = {k: v[0] for k, v in query_dict.items()}

                content_length = int(self.headers.get('Content-Length', 0))
                if content_length > 0:
                    post_data = self.rfile.read(content_length).decode('utf-8')
                    try:
                        post_data_dict = json.loads(post_data)
                        data_dict.update(post_data_dict)
                    except json.JSONDecodeError:
                        self.send_response(400)
                        self.send_header("Content-type", "application/json")
                        self.end_headers()
                        self.wfile.write(json.dumps({"error": "Invalid JSON"}).encode())
                        return

                if not data_dict:
                    self.send_response(400)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": "No data provided"}).encode())
                    return

                # 更新模型数据
                json_data = json.dumps(data_dict)
                condition = 'hwnd' if 'hwnd' in data_dict else 'name' if 'name' in data_dict else None
                if condition:
                    handler.update_model_from_json(json_data, condition)
                    # 获取并返回更新后的模型数据
                    result_json = handler.toggle_is_set_top(condition, data_dict[condition])
                    self.send_response(200)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps(result_json, ensure_ascii=False, indent=4).encode())
                else:
                    self.send_response(400)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": "No valid condition provided"}).encode())

        return CustomHandler


def backend_self_control(current_windows: CurrentWindows, all_windows: AllWindows):
    """
    后端自动控制程序，在后端进行操作的程序都应该在这里执行。

    :param current_windows: 当前窗口模型数据库表格
    :param all_windows:  所有窗口模型数据库表格
    """

    # 需要循环执行的程序都应该在这里执行
    while True:
        # 该方法内的程序每2s执行一次
        time.sleep(2)

        # 实例化模型控制器
        model_control = ModelControl(current_windows, all_windows)

        # 获取 current_windows 和 all_windows 表中的所有模型（行）
        current_windows_rows = current_windows.get_model_list()
        all_windows_rows = all_windows.get_model_list()

        # 将结果统一为列表形式，以便处理
        if isinstance(current_windows_rows, dict):
            current_windows_rows = [current_windows_rows]
        if isinstance(all_windows_rows, dict):
            all_windows_rows = [all_windows_rows]

        # 构建一个 all_windows 表的字典，便于快速查找
        all_windows_dict = {(row['id'], row['name']): row for row in all_windows_rows if 'id' in row and 'name' in row}

        # 当检测到current_windows和all_windows中id和name参数值相同的模型中的notes变化时，统一两者的notes参数的值
        for current_row in current_windows_rows:
            if 'id' in current_row and 'name' in current_row:
                key = (current_row['id'], current_row['name'])
                if key in all_windows_dict:
                    all_row = all_windows_dict[key]
                    if current_row['notes'] != all_row['notes']:
                        # 以all_windows的值为标准，统一current_windows和all_windows中id和name参数的值相同的模型中的notes参数的值
                        model_control.unified_key('notes', 'id', 'name')


if __name__ == '__main__':
    # 创建数据库模型实例
    db = Database("db.sqlite3")

    # 创建并初始化current_windows表
    current_windows = CurrentWindows()
    current_windows.create_model_table()
    current_windows.delete_all_rows()

    # 创建并初始化all_windows表
    all_windows = AllWindows()
    all_windows.create_model_table()
    all_windows.delete_all_rows()

    # 添加测试数据
    row_data = [
        {
            "name": "window1",
            "hwnd": "123456",
            "is_set_top": False,
            "notes": ""
        },
        {
            "name": "window2",
            "hwnd": "1234",
            "is_set_top": False,
            "notes": "this is window 2"
        }
    ]
    current_windows.add_model_row(row_data)
    all_windows.add_model_row(row_data)

    # 创建 DataHandler 实例
    current_windows_handler = DataHandler(current_windows)
    all_windows_handler = DataHandler(all_windows)

    # 创建 ServerControl 实例
    server = ServerControl([current_windows_handler, all_windows_handler])

    # 启动服务器
    thread_server = threading.Thread(target=server.start_server)
    thread_server.start()

    # 启动后端自动控制
    thread_control = threading.Thread(target=backend_self_control, args=(current_windows, all_windows))
    thread_control.start()

    thread_server.join()
    thread_control.join()
