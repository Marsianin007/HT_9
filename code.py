import sqlite3
import time

base = sqlite3.connect("base.db")
cur = base.cursor()

base.execute('CREATE TABLE IF NOT EXISTS users(username text PRIMARY KEY, password text, balance INT)')
base.execute('CREATE TABLE IF NOT EXISTS banknotes(nominal INT PRIMARY KEY, quantity INT)')
base.commit()

global str_name_transactions


def login_menu():
    user_name = input("Введіть Ваш логін: ")
    user_pass = input("Введіть ваш пароль: ")

    if user_name == "admin" and user_pass == "admin":
        admin_menu()
    else:
        entrance_flag = False
        pass_from_sql = cur.execute('SELECT password FROM users WHERE username == ?', (user_name,)).fetchone()
        try:
            pass_from_sql = pass_from_sql[0]
        except TypeError:
            None

        if pass_from_sql == user_pass:
            entrance_flag = True
            print("Вітаємо {}".format(user_name))
            start_menu(user_name)

        if entrance_flag is False:
            print("Перевірте логін та пароль\nАбо якщо бажаєто зареєструватись, натисніть '1', інакше будь-який символ\n")
            num = input("Ваш вибір: \n")
            if num == "1":
                add_new_user()
            else:
                login_menu()


def add_new_user():
    print("Реєстрація \n")
    user_name = input("Введіть логін: ")
    user_pass = input("Введіть ваш пароль:")
    str_name_transactions = str(user_name) + "_transactions"
    username_from_sql = cur.execute('SELECT username FROM users WHERE username == ?', (user_name,)).fetchone()
    if username_from_sql is not None:
        print("Такий логін вже існує")
        add_new_user()

    cur.execute('INSERT INTO users VALUES(?, ?, ?)', (user_name, user_pass, 0))

    time_local = time.localtime()
    time_string = time.strftime("%m/%d/%Y, %H:%M:%S", time_local)
    base.execute('CREATE TABLE IF NOT EXISTS {}(date TEXT, operation TEXT)'.format(str_name_transactions))
    base.commit()
    base.execute('INSERT INTO {} VALUES (?, ?) '.format(str_name_transactions), (time_string, "Date of create",))
    base.commit()

    print("Реєстрація успішна\n")
    login_menu()


def start_menu(user_name):
    print("")
    print("Введіть дію:\n1. Продивитись баланс\n2. Поповнити баланс\n3. Зняти кошти\n4. Вихід")
    number_from_user = input("Ваша дія: ")
    print("")
    if number_from_user.isdigit():
        number_from_user = int(number_from_user)
        if number_from_user == 1:
            check_balance(user_name)
        if number_from_user == 2:
            up_balance(user_name)
        if number_from_user == 3:
            get_money(user_name)
        if number_from_user == 4:
            print("До зустрічі {}!".format(user_name))
            raise SystemExit
        if number_from_user < 1 or number_from_user > 4:
            print("Дії з таким номером не існує")
            start_menu(user_name)
    else:
        print("Введіть буль-ласка число")
        start_menu(user_name)


def check_balance(user_name):
    str_name_transactions = str(user_name) + "_transactions"
    balance = cur.execute('SELECT balance FROM users WHERE username  == ?', (user_name, )).fetchone()
    print(str(balance[0]) + " uah")

    time_local = time.localtime()
    time_string = time.strftime("%m/%d/%Y, %H:%M:%S", time_local)
    cur.execute('INSERT INTO {} VALUES (?, ?) '.format(str_name_transactions), (time_string, "check_balance",))
    base.commit()

    start_menu(user_name)


def up_balance(user_name):
    str_name_transactions = str(user_name) + "_transactions"
    old_balance = cur.execute('SELECT balance FROM users WHERE username = ?', (user_name,)).fetchone()
    sum_to_put = input("Введіть сумму, на яку хочете поповнити картку: ")
    if sum_to_put.isdigit():
        new_balance = old_balance[0] + int(sum_to_put)
    else:
        print("Введіть будь-ласка додатнж число")
        up_balance(user_name)
    cur.execute('UPDATE users SET balance = ? WHERE username = ?', (new_balance, user_name))
    print("Поповненя успішне")

    time_local = time.localtime()
    time_string = time.strftime("%m/%d/%Y, %H:%M:%S", time_local)
    cur.execute('INSERT INTO {} VALUES (?, ?) '.format(str_name_transactions), (time_string, "up_balance",))
    base.commit()

    start_menu(user_name)


def get_money(user_name):
    str_name_transactions = str(user_name) + "_transactions"
    print("Введіть сумму кратну '10', яку потрібно зняти\n Мінімальна сумма 10")
    sum_to_get = input("Ваша сумма: ")
    if sum_to_get.isdigit() is False:
        print("Введіть коректну сумму\n")
        get_money(user_name)
    sum_to_get = int(sum_to_get)
    if sum_to_get < 10 or sum_to_get % 10 != 0:
        print("Введіть коректну сумму:\n")
        get_money(user_name)
    sum_to_get_copy = sum_to_get
    user_balance = cur.execute('SELECT balance FROM users WHERE username == ?', (user_name,)).fetchone()
    user_balance = int(user_balance[0])
    if sum_to_get > int(user_balance):
        print("Недостятньо коштів...")
        start_menu(user_name)

    time_local = time.localtime()
    time_string = time.strftime("%m/%d/%Y, %H:%M:%S", time_local)
    cur.execute('INSERT INTO {} VALUES (?, ?) '.format(str_name_transactions), (time_string, "down_balance",))
    base.commit()

    banknotes_to_get(sum_to_get, user_name, sum_to_get_copy)


def banknotes_to_get(sum_to_get, user_name, sum_to_get_copy):
    copy_sum_to_get = sum_to_get
    banknotes_dict = {}
    tmp = cur.execute('SELECT * FROM banknotes')
    for i in tmp:
        temp_dict = {i[0]: i[1]}
        banknotes_dict.update(temp_dict)
    list = [1000, 500, 200, 100, 50, 20, 10]
    uah_10 = uah_20 = uah_50 = uah_100 = uah_200 = uah_500 = uah_1000 = 0
    print(sum_to_get)

    while sum_to_get >= 1000 and int(banknotes_dict[1000]) > 0:
        uah_1000 += 1
        banknotes_dict[1000] = int(banknotes_dict[1000]) - 1
        sum_to_get -= 1000
    sum_to_get, uah_1000 = exit_from_func(sum_to_get, 1000, uah_1000)

    while sum_to_get >= 500 and int(banknotes_dict[500]) > 0:
        uah_500 += 1
        banknotes_dict[500] = int(banknotes_dict[500]) - 1
        sum_to_get -= 500
    sum_to_get, uah_500 = exit_from_func(sum_to_get, 500, uah_500)

    while sum_to_get >= 200 and int(banknotes_dict[200]) > 0:
        uah_200 += 1
        banknotes_dict[200] = int(banknotes_dict[200]) - 1
        sum_to_get -= 200
    sum_to_get, uah_200 = exit_from_func(sum_to_get, 200, uah_200)

    while sum_to_get >= 100 and int(banknotes_dict[100]) > 0:
        uah_100 += 1
        banknotes_dict[100] = int(banknotes_dict[100]) - 1
        sum_to_get -= 100
    sum_to_get, uah_100 = exit_from_func(sum_to_get, 100, uah_100)

    while sum_to_get >= 50 and int(banknotes_dict[50]) > 0:
        uah_50 += 1
        banknotes_dict[50] = int(banknotes_dict[50]) - 1
        sum_to_get -= 50
    sum_to_get, uah_50 = exit_from_func(sum_to_get, 50, uah_50)

    while sum_to_get >= 20 and int(banknotes_dict[20]) > 0:
        uah_20 += 1
        banknotes_dict[20] = int(banknotes_dict[20]) - 1
        sum_to_get -= 20
    sum_to_get, uah_20 = exit_from_func(sum_to_get, 20, uah_20)

    while sum_to_get >= 10 and int(banknotes_dict[10]) > 0:
        uah_10 += 1
        banknotes_dict[10] = int(banknotes_dict[10]) - 1
        sum_to_get -= 10
    sum_to_get, uah_10 = exit_from_func(sum_to_get, 10, uah_10)

    if sum_to_get != 0:
        greedy_method(copy_sum_to_get, user_name, sum_to_get_copy)
    else:
        user_balance = cur.execute('SELECT balance FROM users WHERE username == ?', (user_name,)).fetchone()
        user_balance = int(user_balance[0])
        new_balance = int(user_balance) - copy_sum_to_get
        cur.execute('UPDATE users SET balance == ? WHERE username == ?', (new_balance, user_name))
        banknotes_list = []
        cur.execute('DELETE  FROM banknotes')
        base.commit()
        for i in list:
            tmp = []
            tmp.append(i)
            tmp.append(banknotes_dict[i])
            banknotes_list.append(tmp)
        cur.executemany('INSERT INTO banknotes VALUES (?, ?)', (banknotes_list))
        base.commit()
        if uah_1000 != 0: print("1000 - " + str(uah_1000))
        if uah_500 != 0: print("500 - " + str(uah_500))
        if uah_200 != 0: print("200 - " + str(uah_200))
        if uah_100 != 0: print("100 - " + str(uah_100))
        if uah_50 != 0: print("50 - " + str(uah_50))
        if uah_20 != 0: print("20 - " + str(uah_20))
        if uah_10 != 0: print("10 - " + str(uah_10))
        start_menu(user_name)


def exit_from_func(sum_to_get, nominal, variable):
    banknotes_dict = {}
    tmp = cur.execute('SELECT * FROM banknotes')
    for i in tmp:
        temp_dict = {i[0]: i[1]}
        banknotes_dict.update(temp_dict)
    list = [10, 20, 50, 100, 200, 500, 1000]
    check = True
    while check and variable != 0:
        for i in list:
            if sum_to_get % i == 0 and int(banknotes_dict[i]) > 0:
                check = False

        if check: sum_to_get += nominal; variable -= 1

    if check:
        return sum_to_get, 0
    else:
        return sum_to_get, variable


def greedy_method(sum_to_get, user_name, sum_to_get_copy):
    list = [1000, 500, 200, 100, 50, 20, 10]
    banknotes_dict = {}
    tmp = cur.execute('SELECT * FROM banknotes')
    for i in tmp:
        temp_dict = {i[0]: i[1]}
        banknotes_dict.update(temp_dict)
    uah_10 = uah_20 = uah_50 = uah_100 = uah_200 = uah_500 = uah_1000 = 0

    while sum_to_get >= 1000 and int(banknotes_dict[1000]) > 0:
        uah_1000 += 1
        banknotes_dict[1000] = int(banknotes_dict[1000]) - 1
        sum_to_get -= 1000

    while sum_to_get >= 500 and int(banknotes_dict[500]) > 0:
        uah_500 += 1
        banknotes_dict[500] = int(banknotes_dict[500]) - 1
        sum_to_get -= 500

    while sum_to_get >= 200 and int(banknotes_dict[200]) > 0:
        uah_200 += 1
        banknotes_dict[200] = int(banknotes_dict[200]) - 1
        sum_to_get -= 200

    while sum_to_get >= 100 and int(banknotes_dict[100]) > 0:
        uah_100 += 1
        banknotes_dict[100] = int(banknotes_dict[100]) - 1
        sum_to_get -= 100

    while sum_to_get >= 50 and int(banknotes_dict[50]) > 0:
        uah_50 += 1
        banknotes_dict[50] = int(banknotes_dict[50]) - 1
        sum_to_get -= 50

    while sum_to_get >= 20 and int(banknotes_dict[20]) > 0:
        uah_20 += 1
        banknotes_dict[20] = int(banknotes_dict[20]) - 1
        sum_to_get -= 20

    while sum_to_get >= 10 and int(banknotes_dict[10]) > 0:
        uah_10 += 1
        banknotes_dict[10] = int(banknotes_dict[10]) - 1
        sum_to_get -= 10
    if sum_to_get == 0:
        user_balance = cur.execute('SELECT balance FROM users WHERE username == ?', (user_name,)).fetchone()
        user_balance = int(user_balance[0])
        new_balance = int(user_balance) - sum_to_get_copy
        cur.execute('UPDATE users SET balance == ? WHERE username == ?', (new_balance, user_name))
        banknotes_list = []
        cur.execute('DELETE  FROM banknotes')
        base.commit()
        for i in list:
            tmp = []
            tmp.append(i)
            tmp.append(banknotes_dict[i])
            banknotes_list.append(tmp)
        cur.executemany('INSERT INTO banknotes VALUES (?, ?)', (banknotes_list))
        base.commit()

        if uah_1000 != 0: print("1000 - " + str(uah_1000))
        if uah_500 != 0: print("500 - " + str(uah_500))
        if uah_200 != 0: print("200 - " + str(uah_200))
        if uah_100 != 0: print("100 - " + str(uah_100))
        if uah_50 != 0: print("50 - " + str(uah_50))
        if uah_20 != 0: print("20 - " + str(uah_20))
        if uah_10 != 0: print("10 - " + str(uah_10))

    value = 0
    list_of_values = cur.execute('SELECT * FROM banknotes')
    for i in list_of_values:
        value += i[1]

    if sum_to_get != 0 and value != 0:
        print("Нажаль банкомат не може видасти потрібну сумму, спробуйте змінити сумму\n")
        num = input("Якщо бажаєте вийти, натисніть '1', інакше будь який символ: ")
        if num == "1":
            start_menu(user_name)
        get_money(user_name)

    elif sum_to_get != 0 and value == 0:
        print("Нажаль банкомат не має грошей\n")
        start_menu(user_name)


def admin_menu():
    banknotes_dict = {}
    tmp = cur.execute('SELECT * FROM banknotes')
    for i in tmp:
        temp_dict = {i[0]: i[1]}
        banknotes_dict.update(temp_dict)
    banknotes_list = [10, 20, 50, 100, 200, 500, 1000]
    print("")
    print("Выберіть дію\n1. Переглянути наявні купюри\n2. Змінити кількість купюр")
    num = input("Ваш вибір: ")
    if num.isdigit() is False:
        print("Невірне значення")
        admin_menu()
    num = int(num)
    if num == 1:
        for i in banknotes_list:
            print(str(i) + " - " + str(banknotes_dict[i]))
        admin_menu()
    if num == 2:
        change_quantity()
    else:
        print("Такої дії не існує")
        admin_menu()


def change_quantity():
    banknotes_list = ["10", "20", "50", "100", "200", "500", "1000"]
    nominal = input("Введіть номінал купюру, кількість якої треба змінити: ")
    quantity = input("Введіть потрібну кількість: ")
    if quantity.isdigit():
        quantity = int(quantity)
        if quantity < 0:
            print("Неправильна кількість:")
            change_quantity()
    else:
        print("Введіть будь-ласка число!")
        change_quantity()

    if nominal not in banknotes_list:
        print(nominal)
        print("Такого номіналу не існує")
        change_quantity()

    cur.execute('UPDATE banknotes SET quantity = ? WHERE nominal = ?', (quantity, nominal))
    base.commit()

    do = input("Якщо бажаєте ще внести зміни, натисніть '1': ")

    if do == "1":
        change_quantity()
    else:
        raise SystemExit


login_menu()
