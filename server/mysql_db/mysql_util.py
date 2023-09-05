import pymysql
import json


def get_table_info(type, host, username, password, database):
    try:
        # 连接到MySQL数据库，设置字符集为UTF-8
        conn = pymysql.connect(
            host=host,
            user=username,
            password=password,
            database=database,
            charset="utf8"
        )

        # 创建游标对象
        cursor = conn.cursor()

        # 获取数据库中的所有表名
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()

        table_info = []

        # 遍历所有表格并获取字段信息
        for table in tables:
            table_name = table[0]
            table_data = {"Table Name": table_name, "Table Comment": "", "Columns": []}

            # 获取表格注释
            cursor.execute(f"SHOW TABLE STATUS LIKE '{table_name}'")
            table_status = cursor.fetchone()
            if table_status:
                table_comment = table_status[17]  # 获取表的注释信息
                table_data["Table Comment"] = table_comment

            # 获取表格中的字段信息
            cursor.execute(f"SHOW FULL COLUMNS FROM {table_name}")
            columns = cursor.fetchall()

            # 将字段信息添加到表格数据中，包括字段注释
            print(columns)
            for column in columns:
                column_name = column[0]
                data_type = column[1]
                column_comment = column[8] if len(column) > 8 else ""  # 获取字段的注释信息
                table_data["Columns"].append(
                    {"Column Name": column_name, "Data Type": data_type, "Column Comment": column_comment})

            table_info.append(table_data)

        # 关闭游标和连接
        cursor.close()
        conn.close()

        # 将中文数据编码为JSON
        return json.dumps(table_info, indent=4, ensure_ascii=False)

    except pymysql.Error as err:
        print(f"Error: {err}")
        return ""


def execute_sql_query(type, host, username, password, database, sql_query):
    try:
        # 建立数据库连接
        conn = pymysql.connect(
            host=host,
            user=username,
            password=password,
            database=database
        )

        # 创建游标对象
        cursor = conn.cursor()

        # 执行 SQL 查询
        cursor.execute(sql_query)

        # 获取查询结果
        result = cursor.fetchall()

        return result

    except pymysql.Error as e:
        print(f"Error: {e}")
        return []

    finally:
        # 关闭游标和连接
        cursor.close()
        conn.close()

