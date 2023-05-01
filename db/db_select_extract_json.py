# -*- coding: utf-8 -*-
import json
import pymysql

con = pymysql.connect(host='localhost', user='ldh', password='doo',
                      db='shop', charset='utf8', # 한글처리 (charset = 'utf8')
                      autocommit=True, # 결과 DB 반영 (Insert or update)
                      cursorclass=pymysql.cursors.DictCursor # DB조회시 컬럼명을 동시에 보여줌
                      )
cur = con.cursor()

sql = "select name, keyword, category from goods_text" # goods_text
cur.execute(sql)
rows = cur.fetchall()
con.close() # DB 연결 종료
print(rows)

FILE_NAME = "./db/json_data.json"

f = open(FILE_NAME, 'w', encoding='utf-8')
f.write(json.dumps(rows, ensure_ascii=False))
f.close()





