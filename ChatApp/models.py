from flask import abort
import pymysql
from util.DB import DB


# 初期起動時にコネクションプールを作成し接続を確立
db_pool = DB.init_db_pool()


# ユーザークラス
class User:
    @classmethod
    def create(cls, id, name, email, password):
        # データベース接続プールからコネクションを取得する
        conn = db_pool.get_conn()
        try:
            # コネクションからカーソル（操作用のオブジェクト）を取得する
            with conn.cursor() as cur:
                sql = "INSERT INTO users (id, name, email, password) VALUES (%s, %s, %s, %s);"
                # SQLを実行し、パラメータ（id, name, email, password）を埋め込む
                cur.execute(sql, (id, name, email, password))
                # データベースに変更を反映（保存）する
                conn.commit()
        except pymysql.Error as e:
            print(f'エラーが発生しています：{e}')
            abort(500)
        finally:
            db_pool.release(conn)

    @classmethod
    def find_by_email(cls, email):
        conn = db_pool.get_conn()
        try:
            with conn.cursor() as cur:
                sql = "SELECT * FROM users WHERE email=%s;"
                cur.execute(sql, (email,))
                user = cur.fetchone()
            return user
        except pymysql.Error as e:
            print(f'エラーが発生しています：{e}')
            abort(500)
        finally:
            db_pool.release(conn)

    @classmethod
    def find_by_id(cls, user_id):
        conn = db_pool.get_conn()
        try:
            with conn.cursor() as cur:
                sql = "SELECT * FROM users WHERE id=%s;"
                cur.execute(sql, (user_id,))
                user = cur.fetchone()
            return user
        except pymysql.Error as e:
            print(f'エラーが発生しています：{e}')
            abort(500)
        finally:
            db_pool.release(conn)


# スポットクラス
class Spot:
    @classmethod
    def create(cls, cid, pid, new_spot_name):
        conn = db_pool.get_conn()
        try:
            with conn.cursor() as cur:
                sql = "INSERT INTO spots (cid, pid, spot_name) VALUES (%s, %s, %s);"
                cur.execute(sql, (cid, pid, new_spot_name,))
                conn.commit()
        except pymysql.Error as e:
            print(f'エラーが発生しています: {e}')
            abort(500)
        finally:
            db_pool.release(conn)
    
    @classmethod
    def get_all(cls):
        conn = db_pool.get_conn()
        try:
            with conn.cursor() as cur:
                sql = "SELECT * FROM spots;"
                cur.execute(sql)
                spots = cur.fetchall()
                return spots
        except pymysql.Error as e:
            print(f'エラーが発生しています : {e}')
            abort(500)
        finally:
            db_pool.release(conn)

    @classmethod
    def find_by_sid(cls, sid):
        conn = db_pool.get_conn()
        try:
            with conn.cursor() as cur:
                sql = "SELECT * FROM spots WHERE id=%s;"
                cur.execute(sql, (sid,))
                spot = cur.fetchone()
                return spot
        except pymysql.Error as e:
            print(f'エラーが発生しています:{e}')
            abort(500)
        finally:
            db_pool.release(conn)

    @classmethod
    def find_by_name(cls, spot_name):
        conn = db_pool.get_conn()
        try:
            with conn.cursor() as cur:
                sql = "SELECT * FROM spots WHERE spot_name=%s;"
                cur.execute(sql, (spot_name,))
                spot = cur.fetchone()
                return spot
        except pymysql.Error as e:
            print(f'エラーが発生しています:{e}')
            abort(500)
        finally:
            db_pool.release(conn)

    @classmethod
    def find_by_pid(cls, pid):
        conn = db_pool.get_conn()
        try:
            with conn.cursor() as cur:
                sql = "SELECT * FROM spots WHERE pid=%s;"
                cur.execute(sql, (pid,))
                spots = cur.fetchall()
                return spots
        except pymysql.Error as e:
            print(f'エラーが発生しています:{e}')
            abort(500)
        finally:
            db_pool.release(conn)

    @classmethod
    def find_by_cid_and_pid(cls, cid, pid):
        conn = db_pool.get_conn()
        try:
            with conn.cursor() as cur:
                sql = "SELECT * FROM spots WHERE cid=%s AND pid=%s;"
                cur.execute(sql, (cid, pid))
                spots = cur.fetchall()
                return spots
        except pymysql.Error as e:
            print(f'エラーが発生しています:{e}')
            abort(500)
        finally:
            db_pool.release(conn)

    @classmethod
    def update(cls, cid, pid, new_spot_name, sid):
        conn = db_pool.get_conn()
        try:
            with conn.cursor() as cur:
                sql = "UPDATE spots SET cid=%s, pid=%s, spot_name=%s WHERE id=%s"
                cur.execute(sql, (cid, pid, new_spot_name, sid))
                conn.commit()
        except pymysql.Error as e:
            print(f'エラーが発生しています:{e}')
            abort(500)
        finally:
            db_pool.release(conn)
    
    @classmethod
    def delete(cls, sid):
        conn = db_pool.get_conn()
        try:
            with conn.cursor() as cur:
                sql = "DELETE FROM spots WHERE id=%s;"
                cur.execute(sql, (sid,))
                conn.commit()
        except pymysql.Error as e:
            print(f'エラーが発生しています:{e}')
            abort(500)
        finally:
            db_pool.release(conn)


class Message:
    @classmethod
    def create(cls, uid, sid, message):
        conn = db_pool.get_conn()
        try:
            with conn.cursor() as cur:
                # 最大IDを取得して+1する
                max_id_sql = "SELECT COALESCE(MAX(id), 0) + 1 AS next_id FROM messages"
                cur.execute(max_id_sql)
                result = cur.fetchone()
                next_id = result['next_id']
                
                sql = "INSERT INTO messages(id, uid, sid, message) VALUES(%s, %s, %s, %s)"
                cur.execute(sql, (next_id, uid, sid, message,))
                conn.commit()
                print(f'Message inserted with id: {next_id}')
        except pymysql.Error as e:
            print(f'エラーが発生しています：{e}')
            abort(500)
        finally:
            db_pool.release(conn)

    @classmethod
    def get_all(cls, sid):
        conn = db_pool.get_conn()
        try:
            with conn.cursor() as cur:
                sql = """
                    SELECT u.id, m.uid, name, message 
                    FROM messages AS m 
                    INNER JOIN users AS u ON m.uid = u.id 
                    WHERE sid = %s 
                    ORDER BY id ASC;
                """
                cur.execute(sql, (sid,))
                messages = cur.fetchall()
                return messages
        except pymysql.Error as e:
            print(f'エラーが発生しています：{e}')
            abort(500)
        finally:
            db_pool.release(conn)

    @classmethod
    def delete(cls, message_id):
        conn = db_pool.get_conn()
        try:
            with conn.cursor() as cur:
                sql = "DELETE FROM messages WHERE id=%s;"
                cur.execute(sql, (message_id,))
                conn.commit()
        except pymysql.Error as e:
            print(f'エラーが発生しています：{e}')
            abort(500)
        finally:
            db_pool.release(conn)


# Categoryクラス
class Category:
    @classmethod
    def get_all(cls):
        conn = db_pool.get_conn()
        try:
            with conn.cursor() as cur:
                sql = "SELECT * FROM categories;"
                cur.execute(sql)
                categories = cur.fetchall()
                return categories
        except pymysql.Error as e:
            print(f'エラーが発生しています:{e}')
            abort(500)
        finally:
            db_pool.release(conn)

    @classmethod
    def find_by_cid(cls, cid):
        conn = db_pool.get_conn()
        try:
            with conn.cursor() as cur:
                sql = "SELECT * FROM categories WHERE id=%s;"
                cur.execute(sql, (cid,))
                category = cur.fetchone()
                return category
        except pymysql.Error as e:
            print(f'エラーが発生しています:{e}')
            abort(500)
        finally:
            db_pool.release(conn)

    @classmethod
    def find_by_name(cls, category_name):
        conn = db_pool.get_conn()
        try:
            with conn.cursor() as cur:
                sql = "SELECT * FROM categories WHERE category_name=%s;"
                cur.execute(sql, (category_name,))
                category = cur.fetchone()
                return category
        except pymysql.Error as e:
            print(f'エラーが発生しています:{e}')
            abort(500)
        finally:
            db_pool.release(conn)


# Prefectureクラス
class Prefecture:
    @classmethod
    def get_all(cls):
        conn = db_pool.get_conn()
        try:
            with conn.cursor() as cur:
                sql = "SELECT * FROM prefectures;"
                cur.execute(sql)
                prefectures = cur.fetchall()
                return prefectures
        except pymysql.Error as e:
            print(f'エラーが発生しています:{e}')
            abort(500)
        finally:
            db_pool.release(conn)

    @classmethod
    def find_by_pid(cls, pid):
        conn = db_pool.get_conn()
        try:
            with conn.cursor() as cur:
                sql = "SELECT * FROM prefectures WHERE id=%s;"
                cur.execute(sql, (pid,))
                prefecture = cur.fetchone()
                return prefecture
        except pymysql.Error as e:
            print(f'エラーが発生しています:{e}')
            abort(500)
        finally:
            db_pool.release(conn)

    @classmethod
    def find_by_name(cls, prefecture_name):
        conn = db_pool.get_conn()
        try:
            with conn.cursor() as cur:
                sql = "SELECT * FROM prefectures WHERE prefecture_name=%s;"
                cur.execute(sql, (prefecture_name,))
                prefecture = cur.fetchone()
                return prefecture
        except pymysql.Error as e:
            print(f'エラーが発生しています:{e}')
            abort(500)
        finally:
            db_pool.release(conn)