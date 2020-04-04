import math

x = -100
y = 100

x = -x
y = -y
deg = math.degrees(math.asin(abs(y) / math.sqrt(x ** 2 + y ** 2)))
if x < 0 and y > 0:
    deg = 180 - deg
elif x < 0 and y < 0:
    deg += 180
elif x > 0 and y < 0:
    deg = 360 - deg
print (deg)