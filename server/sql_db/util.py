import pymysql
import psycopg2
import json


# 连接数据库获取表信息/字段信息
def get_table_info(database_type, host, username, password, database, schema):
    cursor = None
    try:
        if database_type == "MySQL":
            # 连接到MySQL数据库，设置字符集为UTF-8
            conn = pymysql.connect(
                host=host,
                user=username,
                password=password,
                database=database,
                charset="utf8"
            )
            cursor = conn.cursor()
        elif database_type == "PgSQL":
            # 连接到PgSQL数据库（请用您的PgSQL连接信息替换）
            conn = psycopg2.connect(
                host=host,
                user=username,
                password=password,
                database=database,
                options="-c search_path=dbo,"+schema,
            )
            cursor = conn.cursor()

        # 获取数据库中的所有表名
        cursor.execute(f"SELECT table_name FROM information_schema.tables WHERE table_schema = '{schema}'")
        tables = cursor.fetchall()

        table_info = []

        # 遍历所有表格并获取字段信息
        for table in tables:
            table_name = table[0]
            table_data = {"表名": table_name, "表注释": "", "字段": []}

            # 获取表格注释
            if database_type == "MySQL":
                cursor.execute(f"SHOW TABLE STATUS LIKE '{table_name}'")
                table_status = cursor.fetchone()
                if table_status:
                    table_comment = table_status[17]  # 获取表的注释信息
                    table_data["表注释"] = table_comment
            elif database_type == "PgSQL":
                # 获取PgSQL表格注释的代码
                cursor.execute(f"SELECT obj_description(pg_class.oid) AS table_comment FROM pg_class WHERE relkind = 'r' AND relname = '{table_name}'")
                table_comment = cursor.fetchone()[0]
                table_data["表注释"] = table_comment

            # 获取表格中的字段信息
            if database_type == "MySQL":
                cursor.execute(f"SHOW FULL COLUMNS FROM {table_name}")
            elif database_type == "PgSQL":
                # 获取PgSQL字段信息的代码
                cursor.execute(
                    f"SELECT a.attname AS column_name,\n"
                    f"       format_type(a.atttypid, a.atttypmod) AS data_type,\n"
                    f"       col_description(a.attrelid, a.attnum) AS column_comment\n"
                    f"FROM pg_attribute a\n"
                    f"JOIN pg_class c ON a.attrelid = c.oid\n"
                    f"JOIN pg_namespace n ON c.relnamespace = n.oid\n"
                    f"WHERE n.nspname = '{schema}'\n"
                    f"      AND c.relname = '{table_name}'\n"
                    f"      AND a.attnum > 0;")
            columns = cursor.fetchall()

            # 将字段信息添加到表格数据中，包括字段注释
            for column in columns:
                column_name = column[0]
                data_type = column[1]
                if database_type == "MySQL":
                    column_comment = column[8] if len(column) > 8 else ""  # 获取字段的注释信息
                elif database_type == "PgSQL":
                    column_comment = column[2] if len(column) > 2 else ""  # 获取字段的注释信息
                table_data["字段"].append(
                    {"字段名": column_name, "数据类型": data_type, "字段注释": column_comment})

            table_info.append(table_data)

        # 关闭游标和连接
        cursor.close()
        conn.close()

        # 将中文数据编码为JSON
        return json.dumps(table_info, indent=4, ensure_ascii=False)

    except (pymysql.Error, psycopg2.Error) as err:
        print(f"错误：{err}")
        return ""


def execute_sql_query(database_type, host, username, password, database, sql_query, schema):
    cursor = None
    try:
        if database_type == "MySQL":
            # 连接到MySQL数据库
            conn = pymysql.connect(
                host=host,
                user=username,
                password=password,
                database=database,
                charset="utf8"
            )
            cursor = conn.cursor()
        elif database_type == "PgSQL":
            # 连接到PgSQL数据库（请用您的PgSQL连接信息替换）
            conn = psycopg2.connect(
                host=host,
                user=username,
                password=password,
                database=database,
                options="-c search_path=dbo,"+schema,

            )
            cursor = conn.cursor()

        # 执行 SQL 查询
        cursor.execute(sql_query)

        # 获取查询结果
        result = cursor.fetchall()

        return result

    except (pymysql.Error, psycopg2.Error) as e:
        print(f"错误：{e}")
        return []

    finally:
        # 关闭游标和连接
        cursor.close()
        conn.close()


# 解析模型返回获取第一个sql语句
def extract_first_select(sql):
    start_index = sql.find('SELECT')  # 查找 SELECT 的起始位置
    end_index = sql.find(';') + 1  # 查找 ; 的结束位置，并添加 1 以包括 ;

    # 如果找到了 SELECT 和 ;，则提取子字符串
    if start_index != -1 and end_index != 0:
        selected_part = sql[start_index:end_index]
        return selected_part
    else:
        return None
