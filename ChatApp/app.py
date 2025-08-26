from flask import Flask, request, redirect, render_template, session, flash, abort, url_for
from datetime import timedelta
import hashlib
import uuid
import re
import os

from models import User, Spot, Category, Prefecture, Message
from util.assets import bundle_css_files


# 定数定義　　　正規表現の確認をする
EMAIL_PATTERN = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
SESSION_DAYS = 30

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', uuid.uuid4().hex)
app.permanent_session_lifetime = timedelta(days=SESSION_DAYS)

# ブラウザに静的ファイル（CSSや画像など）を長くキャッシュさせる設定。
# 開発中は変更がすぐ反映されないことがあるため、コメントアウトするのが無難です。
# app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 2678400

# 複数のCSSファイルを1つにまとめて圧縮（バンドル）する処理を実行。
# bundle_css_files(app)


# ルートページのリダイレクト処理
@app.route('/', methods=['GET'])
def index():
    logout()
    uid = session.get('uid')
    if uid is None:
        return redirect(url_for('login_view'))
    return redirect(url_for('categories_view'))


 # 会員登録ページの表示
@app.route('/register', methods=['GET'])
def register_view():
    return render_template('auth/register.html')


# 会員登録処理
@app.route('/register', methods=['POST'])
def register_process():
    name = request.form.get('name')
    email = request.form.get('email')
    password = request.form.get('password')
    passwordConfirmation = request.form.get('password-confirmation')

    if name == '' or email =='' or password == '' or passwordConfirmation == '':
        flash('空のフォームがあるようです')
    elif password != passwordConfirmation:
        flash('二つのパスワードの値が違っています')
    elif re.match(EMAIL_PATTERN, email) is None:
        flash('正しいメールアドレスの形式ではありません')
    else:
        uid = uuid.uuid4()
        password = hashlib.sha256(password.encode('utf-8')).hexdigest()
        registered_user = User.find_by_email(email)

        if registered_user != None:
            flash('既に登録されているようです')
        else:
            User.create(uid, name, email, password)
            UserId = str(uid)
            session['uid'] = UserId
            return redirect(url_for('categories_view'))
    return redirect(url_for('register_view'))


# ログインページの表示
@app.route('/login', methods=['GET'])
def login_view():
    return render_template('auth/login.html')


# ログイン処理
@app.route('/login', methods=['POST'])
def login_process():
    email = request.form.get('email')
    password = request.form.get('password')

    if email =='' or password == '':
        flash('空のフォームがあるようです')
    else:
        user = User.find_by_email(email)
        if user is None:
            flash('このユーザーは存在しません')
        else:
            hashPassword = hashlib.sha256(password.encode('utf-8')).hexdigest()
            if hashPassword != user["password"]:
                flash('パスワードが間違っています！')
            else:
                session['uid'] = user["id"]
                return redirect(url_for('categories_view'))
    return redirect(url_for('login_view'))


# ログアウト
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login_view'))


# カテゴリ画面表示
@app.route('/categories', methods=['GET'])
def categories_view():
    uid = session.get('uid')
    if uid is None:
        return redirect(url_for('login_view'))
    return render_template('auth/categories.html')


# # カテゴリ内の都道府県一覧表示/roku
@app.route('/categories/<cid>', methods=['GET'])
def prefectures_view(cid):
    uid = session.get('uid')
    if uid is None:
        return redirect(url_for('login_view'))
    
    # カテゴリーIDをセッションに保存
    session['cid'] = cid
    
    category = Category.find_by_cid(cid)
    if category is None:
        flash('指定されたカテゴリが見つかりません')
        return redirect(url_for('categories_view'))

    return render_template('auth/prefectures.html', category=category)


# 特定の都道府県内のスポットルーム一覧表示 /やんみー
# @app.route('/spots/<cid>/<pid>', methods=['GET'])
# def spots_view(cid,pid):
#     category_id = session.get(cid)
#     prefecture_id = session.get(pid)
#     if category_id is None or prefecture_id is None:
#         return redirect(url_for('login_view'))
    
#     # category = Category.find_by_cid(cid)
#     # prefecture = Prefecture.find_by_pid(pid)
#     spots = Spot.find_by_spot_name(cid, pid)
#     print(f'スポットを表示 : {spots}')
#     return render_template('/auth/spots_id.html', spots=spots)                #←ここ確認

# """
@app.route('/spots/<pid>', methods=['GET'])
def spots_view(pid):
    uid = session.get('uid')
    if uid is None:
        return redirect(url_for('login_view'))
    
    # セッションからカテゴリーIDを取得
    cid = session.get('cid')
    if cid is None:
        flash('カテゴリーが選択されていません')
        return redirect(url_for('categories_view'))
    
    # カテゴリーと都道府県の両方でフィルタリング
    spots = Spot.find_by_cid_and_pid(cid, pid)
    prefecture = Prefecture.find_by_pid(pid)
    category = Category.find_by_cid(cid)
    
    return render_template('auth/spot_id.html', spots=spots, prefecture=prefecture, category=category)  
# """

# スポット作成ページの表示
@app.route('/spots/<pid>/add', methods=['GET'])
def add_spot_view(pid):
    uid = session.get('uid')
    if uid is None:
        return redirect(url_for('login_view'))
    
    prefecture = Prefecture.find_by_pid(pid)
    
    return render_template('auth/spot_add.html', prefecture=prefecture, pid=pid)


# スポット作成処理
@app.route('/spots/<pid>/add', methods=['POST'])
def create_spot(pid):
    uid = session.get('uid')
    if uid is None:
        return redirect(url_for('login_view'))
    
    spot_name = request.form.get('spot_name')
    
    if not spot_name:
        flash('スポット名を入力してください')
        return redirect(url_for('add_spot_view', pid=pid))
    
    # 同じ名前のスポットが存在するかチェック
    # ここは必要ないかも
    existing_spot = Spot.find_by_name(spot_name)
    if existing_spot:
        flash('既に同じ名前のスポットが存在しています')
        return redirect(url_for('add_spot_view', pid=pid))
    
    # カテゴリIDは現在のセッションまたはデフォルト値を使用
    cid = session.get('cid', 1)  # デフォルトで海（cid=1）
    
    try:
        Spot.create(cid, pid, spot_name)
        flash('スポットを作成しました', 'success')
        return redirect(url_for('spots_view', pid=pid))
    except Exception as e:
        flash('スポット作成に失敗しました', 'error')
        print(f'スポット作成エラー: {e}')
        return redirect(url_for('add_spot_view', pid=pid))



# #スポットルームの作成
# @app.route('/spots', methods=['POST'])     #←ここ確認
# def create_spot_room(sid):
#     uid = session.get('uid')
#     if uid is None:
#         return redirect(url_for('login_view'))
    
#     spot_name = request.form.get('spotTitle')                           #←ここ確認
#     spot = Spot.find_by_name(spot_name)
#     if spot == None:
#         Spot.create(cid, pid, spot_name)               #←ここ確認
#         return redirect(url_for('create_view'))
#     else:
#         flash('既に同じ名前のチャンネルが存在しています')                      #←ここ確認


# メッセージルームの表示
@app.route('/spots/<sid>/messages', methods=['GET'])
def spot_room_view(sid):
    uid =session.get('uid')
    if uid is None:
        return redirect(url_for('login_view'))
    
    spot = Spot.find_by_sid(sid)
    messages = Message.get_all(sid)

    return render_template('auth/message.html', messages=messages, spot=spot, uid=uid)

# メッセージの投稿
@app.route('/spots/<sid>/messages', methods=['POST'])
def create_message(sid):
    uid = session.get('uid')
    if uid is None:
        return redirect(url_for('login_view'))
    
    message = request.form.get('message')
    
    if message:
        try:
            Message.create(uid, sid, message)
        except Exception as e:
            print(f'Error creating message: {e}')
            flash('メッセージの送信に失敗しました')

    return redirect(url_for('spot_room_view', sid=sid))    


# @app.route('/messages/<sid>', methods=['GET'])                      #←ここ確認
# def spot_room_view(sid):
#     spot_id = session.get(spot_id)
#     if spot_id is None:
#         return redirect(url_for('login_view'))
    
#     messages = Message.get_all(spot_id)

#     return render_template('/auth/<spot_id>.html')                        #←ここ確認


# # メッセージの投稿
# @app.route('/messages/<spot_id>', methods=['POST'])
# def create_message(spot_id):
#     uid = session.get('uid')
#     if uid is None:
#         return redirect(url_for('login_view'))
    
#     message = request.form.get('message')

#     if message:
#         Message.create(uid, spot_id, message, created_at)

#     return redirect(url_for('spot_room_view(spot_id)'))


# アカウント情報表示画面
@app.route('/information', methods=['GET'])
def information_view():
    uid = session.get('uid')
    if uid is None:
        return redirect(url_for('login_view'))
    
    # 現在のユーザー情報を取得
    user = User.find_by_id(uid)
    if user is None:
        flash('ユーザー情報が見つかりません')
        return redirect(url_for('login_view'))
    
    return render_template('auth/information.html', user=user)

# # パスワード変更                                                            #←ここ確認
# @app.route('/information', methods=['POST'])
# def change_pass():
#     password = request.form.get('password')
#     passwordConfirmation = request.form.get('password_Confirmation')

#     if password != passwordConfirmation:
#         flash('パスワードが一致しません')
#     else:
#         password = hashlib.sha256(password.encode('utf-8')).hexdigest()
#         return redirect(url_for('information_view'))


# # メールアドレス変更                                                        #←ここ確認　新しい変数定義必要？
# @app.route('/information', methods=['POST'])
# def change_email():



# # アカウント名変更                                                          #←ここ確認　新しい変数定義必要？
# @app.route('/information', methods=['POST'])
# def change_name():





#本体の起動
if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)










############ 以下は元ファイルでコピーして使う ########################
# from flask import Flask, request, redirect, render_template, session, flash, abort, url_for
# from datetime import timedelta
# import hashlib
# import uuid
# import re
# import os

# from models import User, Channel, Message
# from util.assets import bundle_css_files


# # 定数定義
# EMAIL_PATTERN = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
# SESSION_DAYS = 30

# app = Flask(__name__)
# app.secret_key = os.getenv('SECRET_KEY', uuid.uuid4().hex)
# app.permanent_session_lifetime = timedelta(days=SESSION_DAYS)

# # ブラウザに静的ファイル（CSSや画像など）を長くキャッシュさせる設定。
# # 開発中は変更がすぐ反映されないことがあるため、コメントアウトするのが無難です。
# app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 2678400

# # 複数のCSSファイルを1つにまとめて圧縮（バンドル）する処理を実行。
# bundle_css_files(app)


# # ルートページのリダイレクト処理
# @app.route('/', methods=['GET'])
# def index():
#     uid = session.get('uid')
#     if uid is None:
#         return redirect(url_for('login_view'))
#     return redirect(url_for('channels_view'))


# # サインアップページの表示
# @app.route('/signup', methods=['GET'])
# def signup_view():
#     return render_template('auth/signup.html')


# # サインアップ処理
# @app.route('/signup', methods=['POST'])
# def signup_process():
#     name = request.form.get('name')
#     email = request.form.get('email')
#     password = request.form.get('password')
#     passwordConfirmation = request.form.get('password-confirmation')

#     if name == '' or email =='' or password == '' or passwordConfirmation == '':
#         flash('空のフォームがあるようです')
#     elif password != passwordConfirmation:
#         flash('二つのパスワードの値が違っています')
#     elif re.match(EMAIL_PATTERN, email) is None:
#         flash('正しいメールアドレスの形式ではありません')
#     else:
#         uid = uuid.uuid4()
#         password = hashlib.sha256(password.encode('utf-8')).hexdigest()
#         registered_user = User.find_by_email(email)

#         if registered_user != None:
#             flash('既に登録されているようです')
#         else:
#             User.create(uid, name, email, password)
#             UserId = str(uid)
#             session['uid'] = UserId
#             return redirect(url_for('channels_view'))
#     return redirect(url_for('signup_process'))


# # ログインページの表示
# @app.route('/login', methods=['GET'])
# def login_view():
#     return render_template('auth/login.html')


# # ログイン処理
# @app.route('/login', methods=['POST'])
# def login_process():
#     email = request.form.get('email')
#     password = request.form.get('password')

#     if email =='' or password == '':
#         flash('空のフォームがあるようです')
#     else:
#         user = User.find_by_email(email)
#         if user is None:
#             flash('このユーザーは存在しません')
#         else:
#             hashPassword = hashlib.sha256(password.encode('utf-8')).hexdigest()
#             if hashPassword != user["password"]:
#                 flash('パスワードが間違っています！')
#             else:
#                 session['uid'] = user["uid"]
#                 return redirect(url_for('channels_view'))
#     return redirect(url_for('login_view'))


# # ログアウト
# @app.route('/logout')
# def logout():
#     session.clear()
#     return redirect(url_for('login_view'))


# # チャンネル一覧ページの表示
# @app.route('/channels', methods=['GET'])
# def channels_view():
#     uid = session.get('uid')
#     if uid is None:
#         return redirect(url_for('login_view'))
#     else:
#         channels = Channel.get_all()
#         channels.reverse()
#         return render_template('channels.html', channels=channels, uid=uid)


# # チャンネルの作成
# @app.route('/channels', methods=['POST'])
# def create_channel():
#     uid = session.get('uid')
#     if uid is None:
#         return redirect(url_for('login_view'))

#     channel_name = request.form.get('channelTitle')
#     channel = Channel.find_by_name(channel_name)
#     if channel == None:
#         channel_description = request.form.get('channelDescription')
#         Channel.create(uid, channel_name, channel_description)
#         return redirect(url_for('channels_view'))
#     else:
#         error = '既に同じ名前のチャンネルが存在しています'
#         return render_template('error/error.html', error_message=error)


# # チャンネルの更新
# @app.route('/channels/update/<cid>', methods=['POST'])
# def update_channel(cid):
#     uid = session.get('uid')
#     if uid is None:
#         return redirect(url_for('login_view'))

#     channel_name = request.form.get('channelTitle')
#     channel_description = request.form.get('channelDescription')

#     Channel.update(uid, channel_name, channel_description, cid)
#     return redirect(f'/channels/{cid}/messages')


# # チャンネルの削除
# @app.route('/channels/delete/<cid>', methods=['POST'])
# def delete_channel(cid):
#     uid = session.get('uid')
#     if uid is None:
#         return redirect(url_for('login_view'))

#     channel = Channel.find_by_cid(cid)

#     if channel["uid"] != uid:
#         flash('チャンネルは作成者のみ削除可能です')
#     else:
#         Channel.delete(cid)
#     return redirect(url_for('channels_view'))


# # チャンネル詳細ページの表示（各チャンネル内で、そのチャンネルに属している全メッセージを表示させる）
# @app.route('/channels/<cid>/messages', methods=['GET'])
# def detail(cid):
#     uid = session.get('uid')
#     if uid is None:
#         return redirect(url_for('login_view'))

#     channel = Channel.find_by_cid(cid)
#     messages = Message.get_all(cid)

#     return render_template('messages.html', messages=messages, channel=channel, uid=uid)


# # メッセージの投稿
# @app.route('/channels/<cid>/messages', methods=['POST'])
# def create_message(cid):
#     uid = session.get('uid')
#     if uid is None:
#         return redirect(url_for('login_view'))

#     message = request.form.get('message')

#     if message:
#         Message.create(uid, cid, message)

#     return redirect('/channels/{cid}/messages'.format(cid = cid))


# # メッセージの削除
# @app.route('/channels/<cid>/messages/<message_id>', methods=['POST'])
# def delete_message(cid, message_id):
#     uid = session.get('uid')
#     if uid is None:
#         return redirect(url_for('login_view'))

#     if message_id:
#         Message.delete(message_id)
#     return redirect('/channels/{cid}/messages'.format(cid = cid))


# @app.errorhandler(404)
# def page_not_found(error):
#     return render_template('error/404.html'),404


# @app.errorhandler(500)
# def internal_server_error(error):
#     return render_template('error/500.html'),500


# if __name__ == '__main__':
#     app.run(host="0.0.0.0", debug=True)