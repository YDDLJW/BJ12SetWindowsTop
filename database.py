import sqlite3


class Database:
    table_names = []
    columns_list = ['ID']

    def __init__(self, database_name):
        """
        初始化数据库连接。
        :param database_name: 数据库名称
        """
        self.database_name = database_name
        self.conn = sqlite3.connect(self.database_name, check_same_thread=False)

    def get_columns(self, table_name):
        """
        获取指定表的列名。
        :param table_name: 表名
        :return: 列名列表
        """
        cur = self.conn.cursor()
        if table_name not in self.table_names:
            print(f"{table_name} does not exist!")
            return None

        cur.execute(f"PRAGMA table_info({table_name})")
        columns_info = cur.fetchall()
        columns = [info[1] for info in columns_info]
        cur.close()
        return columns

    def get_table(self, table_name="none"):
        """
        获取指定表的数据。
        :param table_name: 表名
        :return: 表数据列表
        """
        cur = self.conn.cursor()
        table = []
        if table_name == "none":
            cur.execute(f"SELECT * FROM {self.table_names[0]}")
        elif table_name in self.table_names:
            cur.execute(f"SELECT * FROM {table_name}")
            table = (cur.fetchall())
        else:
            print(f"{table_name} table does not exist")
        cur.close()
        return table

    def add_row(self, table_name, *values):
        """
        向指定表中添加一行数据。ID 列将根据表内现有的最后一个 ID 进行自增。

        :param table_name: 表名
        :param values: 插入的值，不包括 ID 列的值
        """
        cur = self.conn.cursor()
        cur.execute(f"PRAGMA table_info({table_name})")
        columns_info = cur.fetchall()
        columns_count = len(columns_info)  # 包括id列

        # 检查传递的值数量是否正确
        if len(values) != (columns_count - 1):  # 减去id列
            print(f"Not matched! number of values should be {columns_count - 1}!")
            cur.close()
            return

        # 获取最后一个 ID 值并自增
        cur.execute(f"SELECT MAX(id) FROM {table_name}")
        last_id = cur.fetchone()[0]
        new_id = last_id + 1 if last_id is not None else 1

        placeholders = ', '.join(['?'] * (columns_count - 1))
        row = f"INSERT INTO {table_name} (id, {', '.join([col[1] for col in columns_info if col[1] != 'id'])}) VALUES ({new_id}, {placeholders})"
        cur.execute(row, values)
        self.conn.commit()
        cur.close()

    def update_row(self, table_name, set_column, set_value, condition_column, condition_value):
        """
        更新指定表中符合条件的行。

        :param table_name: 表名
        :param set_column: 需要更新的列名
        :param set_value: 更新后的值
        :param condition_column: 条件列名
        :param condition_value: 条件值
        """
        cur = self.conn.cursor()
        cur.execute(f"PRAGMA table_info({table_name})")
        columns_info = [col[1] for col in cur.fetchall()]

        if set_column not in columns_info or condition_column not in columns_info:
            print(f"One or both columns '{set_column}' or '{condition_column}' do not exist in table '{table_name}'")
            cur.close()
            return

        query = f"UPDATE {table_name} SET {set_column} = ? WHERE {condition_column} = ?"
        cur.execute(query, (set_value, condition_value))
        self.conn.commit()
        cur.close()

    def delete_row(self, table_name, condition_column, condition_value):
        """
        删除指定表中符合条件的行。

        :param table_name: 表名
        :param condition_column: 条件列名
        :param condition_value: 条件值
        """
        cur = self.conn.cursor()
        query = f"DELETE FROM {table_name} WHERE {condition_column} = ?"
        cur.execute(query, (condition_value,))
        self.conn.commit()
        cur.close()

    def delete_row_within_value(self, table_name, column_name, column_value_contained):
        """
        删除指定表中列值包含特定子字符串的行。
        :param table_name: 表名
        :param column_name: 列名
        :param column_value_contained: 列值包含的子字符串
        """
        cur = self.conn.cursor()
        if table_name not in self.table_names:
            print(f"{table_name} does not exist!")
            cur.close()
            return

        query = f"DELETE FROM {table_name} WHERE {column_name} LIKE ?"
        cur.execute(query, ('%' + column_value_contained + '%',))
        self.conn.commit()
        cur.close()
        return

    def delete_row_by_two_conditions(self, table_name, column1, value1, column2, value2):
        """
        删除指定表中同时满足两个条件的行。
        :param table_name: 表名
        :param column1: 第一个条件的列名
        :param value1: 第一个条件的列值
        :param column2: 第二个条件的列名
        :param value2: 第二个条件的列值
        """
        cur = self.conn.cursor()
        if table_name not in self.table_names:
            print(f"{table_name} does not exist!")
            cur.close()
            return

        query = f"DELETE FROM {table_name} WHERE {column1} = ? AND {column2} = ?"
        cur.execute(query, (value1, value2))
        self.conn.commit()
        cur.close()
        return

    def delete_all_rows(self, table_name):
        """
        删除指定表中的所有数据。
        :param table_name: 表名
        """
        cur = self.conn.cursor()
        query = f"DELETE FROM {table_name}"
        cur.execute(query)
        self.conn.commit()
        cur.close()

    def create_table(self, table_name, **columns):
        """
        创建新表。
        :param table_name: 表名
        :param columns: 列定义，格式为 column_name=type
        """
        cur = self.conn.cursor()
        columns_definition = 'id INTEGER PRIMARY KEY'  # 默认添加id列
        for column_name, column_type in columns.items():
            columns_definition += f", {column_name} {column_type}"
        create_table_sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_definition})"
        cur.execute(create_table_sql)
        self.conn.commit()
        cur.close()

        # 更新table_names列表
        if table_name not in self.table_names:
            self.table_names.append(table_name)

    def get_row_by_column_value(self, table_name, column_name, column_value):
        """
        根据列名和值获取行数据。
        :param table_name: 表名
        :param column_name: 列名
        :param column_value: 列值
        :return: 符合条件的行数据
        """
        cur = self.conn.cursor()
        if table_name not in self.table_names:
            print(f"{table_name} does not exist!")
            cur.close()
            return None

        query = f"SELECT * FROM {table_name} WHERE {column_name} = ?"
        cur.execute(query, (column_value,))
        row = cur.fetchone()
        if row:
            cur.close()
            return list(row)
        else:
            print(f"No row found with {column_name} = {column_value}")
            cur.close()
            return None

    def join_tables(self, table1, table2, join_type, join_condition, columns='*'):
        """
        连接两个表。
        :param table1: 第一个表
        :param table2: 第二个表
        :param join_type: 连接类型（INNER, LEFT, RIGHT等）
        :param join_condition: 连接条件
        :param columns: 选择的列
        :return: 连接后的行数据
        """
        cur = self.conn.cursor()
        if table1 not in self.table_names or table2 not in self.table_names:
            print(f"One or both tables do not exist!")
            cur.close()
            return None

        query = f"SELECT {columns} FROM {table1} {join_type} JOIN {table2} ON {join_condition}"
        cur.execute(query)
        rows = cur.fetchall()
        cur.close()
        return rows

    def get_last_row_id(self, table_name):
        """
        获取指定表中最后插入行的ID。
        :param table_name: 表名
        :return: 最后一行的ID
        """
        cur = self.conn.cursor()
        if table_name not in self.table_names:
            print(f"{table_name} does not exist!")
            cur.close()
            return None

        query = f"SELECT ID FROM {table_name} ORDER BY ID DESC LIMIT 1"
        cur.execute(query)
        result = cur.fetchone()
        if result:
            cur.close()
            return result[0]
        else:
            print(f"No rows found in {table_name}")
            cur.close()
            return 0

    def sum_column_values(self, table_name, column_name):
        """
        计算指定列的总和。
        :param table_name: 表名
        :param column_name: 列名
        :return: 总和
        """
        cur = self.conn.cursor()
        if table_name not in self.table_names:
            print(f"{table_name} does not exist!")
            cur.close()
            return None

        query = f"SELECT {column_name} FROM {table_name}"
        cur.execute(query)
        rows = cur.fetchall()
        total_sum = sum(int(row[0]) for row in rows)
        cur.close()
        return total_sum

    def close_connection(self):
        """
        关闭数据库连接。
        """
        self.conn.close()
        return
