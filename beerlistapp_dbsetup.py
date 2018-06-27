
import pymysql
import dbconfig
connection = pymysql.connect(host='localhost',
                             user=dbconfig.db_user,
                             passwd=dbconfig.db_password)

try:
    with connection.cursor() as cursor:
        sql = "CREATE DATABASE IF NOT EXISTS myflaskapp"
        cursor.execute(sql)
        sql = """CREATE TABLE IF NOT EXISTS myflaskapp.users (
                id INT(11) NOT NULL AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100),
                username VARCHAR(30),
                password VARCHAR(100),
                email VARCHAR(100),
                register_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )"""
        cursor.execute(sql)

        sql = """CREATE TABLE IF NOT EXISTS myflaskapp.beerlist_main (
                id INT(11) NOT NULL AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100),
                style VARCHAR(50),
                abv VARCHAR(10),
                ibu VARCHAR(10),
                brewery VARCHAR(100),
                location VARCHAR(255),
                website VARCHAR(255),
                description TEXT,
                create_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )"""
        cursor.execute(sql)

        sql = """CREATE TABLE IF NOT EXISTS myflaskapp.beerlist_current (
                id int NOT NULL AUTO_INCREMENT PRIMARY KEY,
                beerlist_main_id INT(100)
                )"""
        cursor.execute(sql)
        connection.commit()

finally:
        connection.close()

