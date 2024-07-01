from database import Database


class DataModel:
    model_name = "DataModel"

    def __init__(self, model_table_name, **columns):
        """
        初始化 DataModel 实例。

        :param name: 模型名称，将作为表名。
        :param columns: 列定义，以关键字参数的形式传入，键为列名，值为列类型。
                        支持的列类型包括：
                        - NULL: 空值
                        - INTEGER: 整数
                        - REAL: 浮点数
                        - TEXT: 文本字符串
                        - BLOB: 二进制大对象
                        - BOOLEAN: 布尔值（映射为 INTEGER）
                        - DATE: 日期（映射为 TEXT）
                        - DATETIME: 日期和时间（映射为 TEXT）
                        - FLOAT: 浮点数（映射为 REAL）
                        - DOUBLE: 双精度浮点数（映射为 REAL）
                        - VARCHAR(N): 可变长度字符串（映射为 TEXT）
        """
        self.model_name = model_table_name
        self.columns = columns

    def create_model_table(self):
        database = Database("db.sqlite3")
        database.create_table(self.model_name, **self.columns)
        database.close_connection()

    def get_model_list(self):
        """
        获取模型表中的所有行，如果只有一行则返回一个字典，如果有多行则返回一个包含字典的列表。

        :return: 包含表中所有行的字典列表或单个字典
        """
        database = Database("db.sqlite3")
        cur = database.conn.cursor()
        cur.execute(f"PRAGMA table_info({self.model_name})")
        table_columns = [col[1] for col in cur.fetchall()]

        cur.execute(f"SELECT * FROM {self.model_name}")
        rows = cur.fetchall()

        result = []
        for row in rows:
            row_dict = {table_columns[i]: row[i] for i in range(len(table_columns))}
            result.append(row_dict)

        cur.close()
        database.close_connection()

        if len(result) == 1:
            return result[0]
        else:
            return result

    def get_model(self, query_dict):
        """
        根据查询条件获取模型表中的一行或多行数据。
        只要该行中有一个参数的值匹配查询条件中的任意一个同名属性的值，则返回该行。

        :param query_dict: 包含查询条件的字典，键为列名，值为查询值
        :return: 包含查询结果的字典或字典列表
        """
        database = Database("db.sqlite3")
        table_data = database.get_table(self.model_name)
        table_columns = database.get_columns(self.model_name)

        if not table_data or not table_columns:
            print(f"No valid data or columns for table '{self.model_name}'")
            return None

        def row_matches_query(row, query):
            for col, val in query.items():
                if col in table_columns and str(row[table_columns.index(col)]) == str(val):
                    return True
            return False

        result = []
        for row in table_data:
            if row_matches_query(row, query_dict):
                result.append({table_columns[i]: row[i] for i in range(len(table_columns))})

        return result[0] if len(result) == 1 else result if result else None

    def add_model_row(self, *model_row_data_list):
        """
        添加多行数据到模型表中。

        :param model_row_data_list: 包含列名和对应值的字典，可以是多个字典或一个字典的列表
        """
        database = Database("db.sqlite3")
        cur = database.conn.cursor()
        cur.execute(f"PRAGMA table_info({self.model_name})")
        table_columns = [col[1] for col in cur.fetchall()]

        # 处理单个字典或字典的列表
        if len(model_row_data_list) == 1 and isinstance(model_row_data_list[0], list):
            model_row_data_list = model_row_data_list[0]

        for model_row_data in model_row_data_list:
            # 过滤掉字典中表中没有的列名
            filtered_data = {k: v for k, v in model_row_data.items() if k in table_columns}

            # 检查字典中的列名是否包含表中的所有必需列（除id外）
            if all(col in filtered_data for col in table_columns if col != 'id'):
                values = [filtered_data.get(col) for col in table_columns if col != 'id']
                database.add_row(self.model_name, *values)
            else:
                print(f"Some required columns are missing in the provided data for table '{self.model_name}'")

        cur.close()
        database.close_connection()

    def update_model_row(self, set_column, set_value, condition_column, condition_value):
        """
        更新模型表中符合条件的行。

        :param set_column: 需要更新的列名
        :param set_value: 更新后的值
        :param condition_column: 条件列名
        :param condition_value: 条件值
        """
        database = Database("db.sqlite3")
        database.update_row(self.model_name, set_column, set_value, condition_column, condition_value)
        database.close_connection()

    def delete_model_row(self, condition_column, condition_value):
        """
        删除模型表中符合条件的行。

        :param condition_column: 条件列名
        :param condition_value: 条件值
        """
        database = Database("db.sqlite3")
        database.delete_row(self.model_name, condition_column, condition_value)
        database.close_connection()

    def delete_all_rows(self):
        """
        删除模型表中的所有数据。
        """
        database = Database("db.sqlite3")
        database.delete_all_rows(self.model_name)
        database.close_connection()


class CurrentWindows(DataModel):
    def __init__(self):
        super().__init__(
            "current_windows",
            name="TEXT",
            hwnd="TEXT",
            is_set_top="BOOLEAN",
            notes="TEXT"
        )

    def get_model(self, query_dict):
        """
        根据查询条件获取模型表中的一行或多行数据。
        优先以hwnd查询，如果查询参数有hwnd并且有匹配的项，则仅返回该行。
        否则，调用父类的方法返回匹配项。

        :param query_dict: 包含查询条件的字典，键为列名，值为查询值
        :return: 包含查询结果的字典或字典列表
        """
        if "hwnd" in query_dict:
            hwnd_value = query_dict["hwnd"]
            database = Database("db.sqlite3")
            result = database.get_row_by_column_value(self.model_name, "hwnd", hwnd_value)
            if result:
                table_columns = database.get_columns(self.model_name)
                return {table_columns[i]: result[i] for i in range(len(table_columns))}
        return super().get_model(query_dict)


class AllWindows(DataModel):
    def __init__(self):
        super().__init__(
            "all_windows",
            name="TEXT",
            notes="TEXT"
        )


if __name__ == '__main__':
    db = Database("db.sqlite3")

    windows = AllWindows()
    windows.create_model_table()

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
        "name": "window2",
        "hwnd": "1234"
    }

    windows.add_model_row(row_data)
    print(windows.get_model_list())

    windows.update_model_row("notes", "this is window 1", "name", "window1")
    print(windows.get_model_list())

    print(windows.get_model(search_data))

    windows.delete_model_row("notes", "this is window 1")
    print(windows.get_model_list())

    windows.delete_all_rows()
    print(windows.get_model_list())
