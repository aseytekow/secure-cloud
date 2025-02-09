from website import app, conn, cursor

if __name__ == '__main__':
    cursor.execute('CREATE DATABASE IF NOT EXISTS SecureCloud')
    cursor.execute('CREATE TABLE IF NOT EXISTS USERS(ID INTEGER PRIMARY KEY AUTO_INCREMENT, NAME TEXT, EMAIL TEXT, PASSWORD TEXT)')
    conn.commit()
    app.run(debug = True)