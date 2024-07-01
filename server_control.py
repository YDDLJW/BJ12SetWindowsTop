import json
from urllib.parse import parse_qs, urlparse
from typing import List
from http.server import BaseHTTPRequestHandler, HTTPServer
from data_handler import DataHandler
from data_models import CurrentWindows, AllWindows
from database import Database


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

            def do_POST(self):
                parsed_path = urlparse(self.path)
                if any(parsed_path.path.startswith(f"{key}/detail") for key in handlers_dict.keys()):
                    base_path = parsed_path.path.split("/detail")[0]
                    handler = handlers_dict.get(base_path)
                    if handler:
                        self.handle_post_request(handler)
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

        return CustomHandler


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
    server.start_server()
