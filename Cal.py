def add(x, y):
    return x + y

def subtract(x, y):
    return x - y

def multiply(x, y):
    return x * y

def divide(x, y):
    if y == 0:
        return "ไม่สามารถหารด้วยศูนย์ได้"
    return x / y

print("=== เครื่องคิดเลข Python ===")
print("เลือกการทำงาน:")
print("1. บวก")
print("2. ลบ")
print("3. คูณ")
print("4. หาร")

choice = input("กรุณาเลือก (1/2/3/4): ")

num1 = float(input("ใส่ตัวเลขแรก: "))
num2 = float(input("ใส่ตัวเลขที่สอง: "))

if choice == '1':
    print("ผลลัพธ์:", add(num1, num2))
elif choice == '2':
    print("ผลลัพธ์:", subtract(num1, num2))
elif choice == '3':
    print("ผลลัพธ์:", multiply(num1, num2))
elif choice == '4':
    print("ผลลัพธ์:", divide(num1, num2))
else:
    print("คุณเลือกไม่ถูกต้อง")