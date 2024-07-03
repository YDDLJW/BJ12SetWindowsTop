from data_models import CurrentWindows, AllWindows


class ModelControl:
    def __init__(self, current_windows: CurrentWindows, all_windows: AllWindows):
        """
        初始化 ModelControl 实例。

        :param current_windows: CurrentWindows 实例
        :param all_windows: AllWindows 实例
        """
        self.current_windows = current_windows
        self.all_windows = all_windows

    def unified_key(self, updated_key, *condition_keys):
        """
        统一两个表中指定键的值。如果 current_windows 表和 all_windows 表中
        符合条件的行的 updated_key 值不一样，则将 current_windows 表中
        updated_key 的值更新为 all_windows 表中的值。

        :param updated_key: 需要统一的键
        :param condition_keys: 用于查询的键
        """
        # 获取 current_windows 和 all_windows 表中的所有行
        current_windows_rows = self.current_windows.get_model_list()
        all_windows_rows = self.all_windows.get_model_list()

        # 将结果统一为列表形式，以便处理
        if isinstance(current_windows_rows, dict):
            current_windows_rows = [current_windows_rows]
        if isinstance(all_windows_rows, dict):
            all_windows_rows = [all_windows_rows]

        # 构建一个 all_windows 表的字典，便于快速查找
        def get_key_tuple(row, keys):
            return tuple(row.get(key) for key in keys if key in row)

        all_windows_dict = {get_key_tuple(row, condition_keys): row for row in all_windows_rows}

        for current_row in current_windows_rows:
            current_key_tuple = get_key_tuple(current_row, condition_keys)
            if current_key_tuple in all_windows_dict:
                all_row = all_windows_dict[current_key_tuple]
                if current_row[updated_key] != all_row[updated_key]:
                    self.current_windows.update_model_row(
                        updated_key,
                        all_row[updated_key],
                        condition_keys[0],  # 使用第一个条件键作为更新条件
                        current_row[condition_keys[0]]
                    )


# 初始化数据库并创建表
def initialize_database():
    current_windows = CurrentWindows()
    current_windows.create_model_table()
    current_windows.delete_all_rows()

    all_windows = AllWindows()
    all_windows.create_model_table()
    all_windows.delete_all_rows()

    return current_windows, all_windows


# 添加测试数据
def add_test_data(current_windows, all_windows):
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
    row_data = [
        {
            "name": "window1",
            "hwnd": "123456",
            "is_set_top": False,
            "notes": "update notes"
        },
        {
            "name": "window2",
            "hwnd": "1234",
            "is_set_top": False,
            "notes": "this is window 2"
        }
    ]
    all_windows.add_model_row(row_data)


# 示例使用
if __name__ == '__main__':
    current_windows, all_windows = initialize_database()
    add_test_data(current_windows, all_windows)

    # 检查更新前的结果
    print("Current Windows:")
    print(current_windows.get_model_list())
    print("All Windows:")
    print(all_windows.get_model_list())

    # 进行更新
    model_control = ModelControl(current_windows, all_windows)
    model_control.unified_key('notes', 'name', 'id')

    # 检查更新后的结果
    print("\nUpdated:")
    print("Current Windows:")
    print(current_windows.get_model_list())
    print("All Windows:")
    print(all_windows.get_model_list())
