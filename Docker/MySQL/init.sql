DROP DATABASE chatapp;
DROP USER 'testuser';

CREATE USER 'testuser' IDENTIFIED BY 'testuser';
CREATE DATABASE chatapp;
USE chatapp;
GRANT ALL PRIVILEGES ON chatapp.* TO 'testuser';

CREATE TABLE users (
    id VARCHAR(255) NOT NULL PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    category_name VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP 
);

CREATE TABLE prefectures (
    id INT AUTO_INCREMENT PRIMARY KEY,
    prefecture_name VARCHAR(10) UNIQUE NOT NULL
);

CREATE TABLE spots (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cid INT NOT NULL,
    pid INT NOT NULL,
    FOREIGN KEY (cid) REFERENCES categories(id) ON DELETE CASCADE,
    FOREIGN KEY (pid) REFERENCES prefectures(id) ON DELETE CASCADE,
    spot_name VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    uid VARCHAR(255) NOT NULL,
    sid INT NOT NULL,
    FOREIGN KEY (uid) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (sid) REFERENCES spots(id) ON DELETE CASCADE,
    message TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO users(id, name, email, password) VALUES('970af84c-dd40-47ff-af23-282b72b7cca8','テスト','test@gmail.com','37268335dd6931045bdcdf92623ff819a64244b53d0e746d438797349d4da578');
INSERT INTO categories(category_name) VALUES('海'),('川'),('湖');
INSERT INTO prefectures(prefecture_name) VALUES
  ('北海道'),
  ('青森県'),
  ('岩手県'),
  ('宮城県'),
  ('秋田県'),
  ('山形県'),
  ('福島県'),
  ('茨城県'),
  ('栃木県'),
  ('群馬県'),
  ('埼玉県'),
  ('千葉県'),
  ('東京都'),
  ('神奈川県'),
  ('新潟県'),
  ('富山県'),
  ('石川県'),
  ('福井県'),
  ('山梨県'),
  ('長野県'),
  ('岐阜県'),
  ('静岡県'),
  ('愛知県'),
  ('三重県'),
  ('滋賀県'),
  ('京都府'),
  ('大阪府'),
  ('兵庫県'),
  ('奈良県'),
  ('和歌山県'),
  ('鳥取県'),
  ('島根県'),
  ('岡山県'),
  ('広島県'),
  ('山口県'),
  ('徳島県'),
  ('香川県'),
  ('愛媛県'),
  ('高知県'),
  ('福岡県'),
  ('佐賀県'),
  ('長崎県'),
  ('熊本県'),
  ('大分県'),
  ('宮崎県'),
  ('鹿児島県'),
  ('沖縄県');
INSERT INTO spots(id, cid, pid, spot_name) VALUES(1, 1, 1, "知床"), (2, 1, 1, "熊石海岸");
INSERT INTO messages(id, uid, sid, message) VALUES(1, '970af84c-dd40-47ff-af23-282b72b7cca8', 1, '誰かかまってください');


-- 以下は元ファイルの内容. コピーして使用する --
-- DROP DATABASE chatapp;
-- DROP USER 'testuser';

-- CREATE USER 'testuser' IDENTIFIED BY 'testuser';
-- CREATE DATABASE chatapp;
-- USE chatapp
-- GRANT ALL PRIVILEGES ON chatapp.* TO 'testuser';

-- CREATE TABLE users (
--     uid VARCHAR(255) PRIMARY KEY,
--     user_name VARCHAR(255) UNIQUE NOT NULL,
--     email VARCHAR(255) UNIQUE NOT NULL,
--     password VARCHAR(255) NOT NULL
-- );

-- CREATE TABLE channels (
--     id INT AUTO_INCREMENT PRIMARY KEY,
--     uid VARCHAR(255) NOT NULL,
--     name VARCHAR(255) UNIQUE NOT NULL,
--     abstract VARCHAR(255),
--     FOREIGN KEY (uid) REFERENCES users(uid) ON DELETE CASCADE
-- );

-- CREATE TABLE messages (
--     id INT AUTO_INCREMENT PRIMARY KEY,
--     uid VARCHAR(255) NOT NULL,
--     cid INT NOT NULL,
--     message TEXT,
--     created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
--     FOREIGN KEY (uid) REFERENCES users(uid) ON DELETE CASCADE,
--     FOREIGN KEY (cid) REFERENCES channels(id) ON DELETE CASCADE
-- );

-- INSERT INTO users(uid, user_name, email, password) VALUES('970af84c-dd40-47ff-af23-282b72b7cca8','テスト','test@gmail.com','37268335dd6931045bdcdf92623ff819a64244b53d0e746d438797349d4da578');
-- INSERT INTO channels(id, uid, name, abstract) VALUES(1, '970af84c-dd40-47ff-af23-282b72b7cca8','ぼっち部屋','テストさんの孤独な部屋です');
-- INSERT INTO messages(id, uid, cid, message) VALUES(1, '970af84c-dd40-47ff-af23-282b72b7cca8', '1', '誰かかまってください、、')