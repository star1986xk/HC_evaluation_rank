# -*- coding: utf-8 -*-
import pymysql
import pymssql
import logging
from DBUtils.PooledDB import PooledDB

logger = logging.getLogger('my')

DB_MAPPINGS = {
    'mysql': pymysql,
    'sqlserver': pymssql
}


class DBClass(object):
    def __init__(self, config=None, db_type='mysql'):
        """
        数据库操作类
        :param config: sql连接字典
        :param db_type: 切换驱动 mysql/sqlserver
        """
        self.pool = PooledDB(DB_MAPPINGS.get(db_type), maxcached=50, maxconnections=100, maxusage=100, **config)

    def __del__(self):
        self.pool.close()

    # 通用查询
    def dql(self, sql_str: str) -> list:
        """
        通用查询
        :param sql_str: sql语句
        :return:
        """
        con = self.pool.connection()
        cur = con.cursor()
        try:
            cur.execute(sql_str)
            result = cur.fetchall()
            return result
        except Exception as e:
            con.rollback()  # 事务回滚
            logger.warning(str(e))
            raise e
        finally:
            cur.close()
            con.close()

    # 通用增删改
    def dml(self, sql_str: str) -> int:
        """
        通用增删改
        :param sql_str: sql语句
        :return:
        """
        con = self.pool.connection()
        cur = con.cursor()
        try:
            cur.execute(sql_str)
            con.commit()
            return cur.rowcount
        except Exception as e:
            con.rollback()  # 事务回滚
            logger.warning(str(e))
            raise e
        finally:
            cur.close()
            con.close()

    def insert_or_update(self, table_name: str, fields: str, obj_list: list):
        """
        通过主键、唯一索引 判断 插入或更新
        :param table_name: 表名
        :param fields: 字段名
        :param obj_list: 数据
        :return:
        """
        update = ','.join([li + "=VALUES(" + li + ")" for li in fields.split(',')])
        con = self.pool.connection()
        cur = con.cursor()
        sql_str = 'INSERT INTO {table_name} ({fields}) VALUES ({values}) ON DUPLICATE KEY UPDATE {update};'.format(
            table_name=table_name,
            fields=fields,
            values=','.join(['%s' for li in fields.split(',')]),
            update=update
        )
        data = tuple(tuple(v for v in li.values()) for li in obj_list)
        try:
            cur.executemany(sql_str, data)
            con.commit()
            return cur.lastrowid
        except Exception as e:
            con.rollback()  # 事务回滚
            logger.warning(str(e))
            raise e
        finally:
            cur.close()
            con.close()

    # 生成条件语句及参数
    @staticmethod
    def get_where(condition: list) -> (str, tuple):
        """
        生成条件语句及参数
        :param condition: 条件列表 [[字段,符号,值],[]...]
        :return: 条件语句,条件参数
        """
        return (' where ' + ' and '.join([li[0] + ' ' + li[1] + ' %s' for li in condition]),
                tuple([str(li[2]) for li in condition])) if condition else ('', ())

    # 生成排序语句
    @staticmethod
    def get_order(order: list, by: str) -> str:
        """
        生成排序语句
        :param order: 排序字段列表['字段1','字段2',...]
        :param by: ASC升序/DESC降序
        :return: 排序语句
        """
        return ' ORDER BY ' + ','.join(order) + ' ' + by if order else ''

    # 查询
    def select_condition(self, table_name: str, fields: str, condition: list = None, order: list = None,
                         by: str = 'ASC') -> list:
        """
        条件查询\n
        如:select id,name from table1 where id=1 and name like '%xx%';\n
        传参数：[['id','=','1'],['name','like','%xx%']]\n
        :param table_name: 表名
        :param fields: 字段名
        :param condition: 条件[[字段,符号,值],[]...]
        :param order: 排序字段列表['字段1','字段2',...]
        :param by: ASC升序/DESC降序
        :return: 查询后的数据集合
        """
        con = self.pool.connection()
        cur = con.cursor()
        try:
            (where_str, data) = self.get_where(condition)
            order_str = self.get_order(order, by)
            sql_str = 'SELECT ' + fields + ' FROM ' + table_name + where_str + order_str + ';'
            cur.execute(sql_str, data)
            result = cur.fetchall()
            return result
        except Exception as e:
            con.rollback()  # 事务回滚
            logger.warning(str(e))
            raise e
        finally:
            cur.close()
            con.close()

    # 批量插入
    def insert_many(self, table_name, obj_list) -> int:
        """
        批量插入\n
        如:\n
        insert table1(name,age) values('小明',30);\n
        insert table1(name,age) values('老王',30);\n
        可传参数:\n
        obj_list = [{'name':'小明','age':'10'},{'name':'老王','age':'30'}]\n
        :param table_name: 表名
        :param obj_list: [{'字段'：'值',,,},,,]
        :return: 插入数据最后一行的ID
        """
        con = self.pool.connection()
        cur = con.cursor()
        try:
            sql_str = 'INSERT INTO {table_name}({fields}) VALUES({values});'.format(
                table_name=table_name,
                fields=','.join(obj_list[0]),
                values=','.join(['%s'] * len(obj_list[0]))
            )
            data = tuple(tuple(v for v in li.values()) for li in obj_list)
            cur.executemany(sql_str, data)
            con.commit()
            return cur.lastrowid
        except Exception as e:
            con.rollback()  # 事务回滚
            logger.warning(str(e))
            raise e
        finally:
            cur.close()
            con.close()

    # 批量更新
    def update_many(self, table_name: str, obj_list: list, condition_list: list) -> int:
        """
        批量更新\n
        如: \n
        update table1 set name='小明',age=10 where id=1;\n
        update table1 set name='老王',age=30 where id=2;\n
        可这样传参数:\n
        obj_list = [{'name':'小明','age':'10'},{'name':'老王','age':'30'}]\n
        condition_list = [{'id':'1'},{'id':'2'}]
        :param table_name: 表名
        :param obj_list: [{'字段'：'值',,,},,,]
        :param condition_list: [{'字段'：'值',,,},,,]
        :param: 更新行数
        """
        con = self.pool.connection()
        cur = con.cursor()
        try:
            sql_str = 'UPDATE {table_name} SET {update_str} WHERE {where_str};'.format(
                table_name=table_name,
                update_str=','.join([k + '=%s' for k in obj_list[0]]),
                where_str=' and '.join([k + '=%s' for k in condition_list[0]])
            )
            data = tuple(tuple(v for v in obj.values()) + tuple(v for v in condition.values())
                         for obj, condition in zip(obj_list, condition_list))
            cur.executemany(sql_str, data)
            con.commit()
            return cur.rowcount
        except Exception as e:
            con.rollback()  # 事务回滚
            logger.warning(str(e))
            raise e
        finally:
            cur.close()
            con.close()

    # 批量删除
    def delete_many(self, table_name: str, condition_list: list) -> int:
        """
        批量删除\n
        如：\n
        delete from table1 where id=1 and name='xxx'\n
        delete from table1 where id=3 and name='yy'\n
        可传参数\n
        condition_list = [{id:'1','name':'xxx'},{id:'3','name':'yy'}]
        :param table_name: 表名
        :param condition_list: [{'字段': '值',,,},,,]
        :return: 删除行数
        """
        con = self.pool.connection()
        cur = con.cursor()
        try:
            sql_str = 'DELETE FROM {table_name} WHERE {where_str};'.format(
                table_name=table_name,
                where_str=' and '.join([k + '=%s' for k in condition_list[0]])
            )
            data = tuple(tuple(v for v in condition.values()) for condition in condition_list)
            cur.executemany(sql_str, data)
            con.commit()
            return cur.rowcount
        except Exception as e:
            con.rollback()  # 事务回滚
            logger.warning(str(e))
            raise e
        finally:
            cur.close()
            con.close()

    # 清空表
    def truncate_table(self, table_name: str) -> bool:
        """
        清空表
        :param table_name: 表名
        :return:True
        """
        con = self.pool.connection()
        cur = con.cursor()
        try:
            sql_str = 'TRUNCATE TABLE {table_name};'.format(table_name=table_name)
            cur.execute(sql_str)
            con.commit()
            return True
        except Exception as e:
            con.rollback()  # 事务回滚
            logger.warning(str(e))
            raise e
        finally:
            cur.close()
            con.close()
