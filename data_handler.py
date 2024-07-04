import json
from data_models import DataModel, CurrentWindows, AllWindows
from database import Database


class DataHandler:
    def __init__(self, model: 'DataModel'):
        """
        初始化 DataHandler 实例。
        url将自动被设置为'/{model.model_name}'

        :param model: DataModel 实例
        """
        self.model = model
        self.url = f'/{model.model_name}'

    def get_model_list_json(self) -> str:
        """
        获取由 DataModel 转化成的 JSON 字符串。

        :return: JSON 字符串
        """
        data = self.model.get_model_list()
        return json.dumps(data, ensure_ascii=False, indent=4)

    def get_model_from_json(self, json_data: str) -> str:
        """
        根据 JSON 数据查询模型表，并返回结果的 JSON 字符串。
        只要该行的所有列参数中有一个参数符合查询条件中的一个参数，就返回该行。

        :param json_data: JSON 字符串
        :return: 查询结果的 JSON 字符串
        """
        query_dict = json.loads(json_data)
        result = self.model.get_model(query_dict)

        if not result:  # 检查结果是否为空
            return json.dumps({"error": "No matching records found"}, ensure_ascii=False, indent=4)

        if isinstance(result, list):
            return json.dumps(result, ensure_ascii=False, indent=4)
        return json.dumps(result, ensure_ascii=False, indent=4)

    def update_model_from_json(self, json_data: str, condition: str):
        """
        根据 JSON 数据更新模型表。

        :param json_data: JSON 字符串
        :param condition: 条件列名
        """
        data_dict = json.loads(json_data)
        condition_value = data_dict.get(condition)
        if condition_value is None:
            print(f"Condition '{condition}' not found in the provided data.")
            return

        # 创建更新字典和条件字典
        set_dict = {column: value for column, value in data_dict.items() if column != condition}
        condition_dict = {condition: condition_value}

        # 更新模型表
        self.model.update_model_row(set_dict, condition_dict)

    def toggle_is_set_top(self, condition: str, condition_value: str):
        """
        根据条件切换 is_set_top 字段的值。

        :param condition: 条件列名
        :param condition_value: 条件值
        """
        data = self.model.get_model({condition: condition_value})
        if not data:
            return {"error": "No matching records found"}

        if isinstance(data, list):
            data = data[0]

        current_value = data.get("is_set_top")
        new_value = 0 if current_value else 1

        set_dict = {"is_set_top": new_value}
        condition_dict = {condition: condition_value}

        self.model.update_model_row(set_dict, condition_dict)
        return self.model.get_model(condition_dict)


# 测试
if __name__ == '__main__':
    db = Database("db.sqlite3")

    windows = CurrentWindows()
    windows.create_model_table()
    windows.delete_all_rows()

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

    search_data = {
        "hwnd": "123456"
    }

    windows.add_model_row(row_data)

    # 创建 DataHandler 实例
    dict_list_handler = DataHandler(windows)

    # 获取 JSON
    dict_list_json = dict_list_handler.get_model_list_json()
    print("\nDict List JSON:")
    print(dict_list_json)

    # 更新模型表
    update_json = json.dumps({
        "name": "window1",
        "hwnd": "123456",
        "notes": "updated notes for window1"
    })
    dict_list_handler.update_model_from_json(update_json, "hwnd")

    # 打印更新后的数据
    updated_json = dict_list_handler.get_model_list_json()
    print("\nUpdated Dict List JSON:")
    print(updated_json)

    # 查询模型表
    search_json = json.dumps(search_data)
    search_result_json = dict_list_handler.get_model_from_json(search_json)
    print("\nSearch Result JSON:")
    print(search_result_json)

    windows.delete_all_rows()
