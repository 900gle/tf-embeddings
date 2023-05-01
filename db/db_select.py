import pymysql
import pandas as pd
import plotly.express as px


con = pymysql.connect(host='localhost', user='ldh', password='doo',
                      db='shop', charset='utf8', # 한글처리 (charset = 'utf8')
                      autocommit=True, # 결과 DB 반영 (Insert or update)
                      cursorclass=pymysql.cursors.DictCursor # DB조회시 컬럼명을 동시에 보여줌
                      )
cur = con.cursor()


sql = "select * from goods_text order by id desc limit 10" # goods_text
cur.execute(sql)
rows = cur.fetchall()
con.close() # DB 연결 종료
# print(rows)


goods = pd.DataFrame(rows)

idx = goods[(goods['keyword'] != 1) & (goods['name'] != 2)].index
goods.drop(idx, inplace=True) #행 제거

goods.loc[goods['keyword'] == 1, 'name'] = '남성' # 1 ==> 남성
goods.loc[goods['keyword'] == 2, 'name'] = '여성' # 2 ==> 여성

fig = px.histogram(goods, x="keyword", y="price", color="name", marginal="rug")
fig.show()