from datetime import datetime, timedelta
import random



now = datetime.now()
print("현재 :" , now)


for i in range (1,10000):

    h = random.randint(1,1000)
    m = random.randint(1,1000)
    new_date = now - timedelta( hours= h , minutes= m)

    print(new_date)






# before_one_microsecond = now - timedelta(days=3, hours=2, minutes=1)
# print("1 microsecond 전 :", before_one_microsecond)
# after_one_microsecond = now + timedelta(microseconds=1)
# print("1 microsecond 후 :", after_one_microsecond)




timedelta(weeks=1, days=3, hours=2)