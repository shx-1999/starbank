import os
import json

BASE_DB = os.path.dirname(__file__)  # 用户文件的路径


def select(name):
    """
   查询用户文件.
    :param name: str --> 用户名
    :return: None, user_dic
    """
    user_path = os.path.join(BASE_DB, '%s.json' % name)
    if os.path.exists(user_path):
        with open(user_path, 'r', encoding='utf-8')as f:
            user_dic = json.load(f)
            return user_dic
    else:
        return None


def save(user_dic):
    '''
    保存用户信息文件.
    :param user_dic: 用户信息
    :return:
    '''
    user_path = os.path.join(BASE_DB, '%s.json' % user_dic['name'])
    with open(user_path, 'w', encoding='utf-8')as f:
        json.dump(user_dic, f)
        f.flush()


# ============================================================
# ============================================================
# ============================================================
# ============================================================
# 判断用户是否登入
user_data = {
    "name": None,
}


# 登入验证装饰器
def login_auth(func):
    '''
    装饰器
    :param func: 函数名
    :return: wrapper
    '''

    def wrapper(*args, **kwargs):
        if not user_data['name']:
            login()
        else:
            return func(*args, **kwargs)

    return wrapper


# ==================================================================
# ==================================================================
# ==================================================================
# ==================================================================


def register_interface(name, password, balance=15000):
    '''
    注册接口.
    :param name:用户名
    :param password: 密码
    :param balance: 确认密码
    :return:True,False
    '''
    user_dic = select(name)
    if user_dic:
        return False, '用户已存在'
    else:
        user_dic = {'name': name, 'password': password, 'balance': balance,
                    'locked': False, 'shoppingcart': {}}
        save(user_dic)
        return True, '注册成功'


def login_interface(name, password):
    '''
    登入接口.
    :param name:用户名
    :param password: 用户密码
    :return:True,False
    '''
    user_dic = select(name)
    if user_dic:  # {'name': 'song', 'password': '123'}
        if password == user_dic['password'] and not user_dic['locked']:
            return True, '登入成功'
        else:
            return False, '用户名密码错误或被锁定'
    else:
        return False, '用户不存在'


def locked_interface(name):
    '''
    锁定接口.
    :param name:用户名
    :return:
    '''
    user_dic = select(name)
    if user_dic:
        user_dic['locked'] = True
        save(user_dic)


def transfer_interface(from_name, to_name, balance):
    '''
    转账接口.
    :param from_name:转账用户
    :param to_name: 收款用户
    :param balance: 转账金额
    :return:True,False
    '''
    if from_name == to_name:
        return False, '不能给自己转账'
    to_dic = select(to_name)
    if to_dic:
        from_dic = select(from_name)
        if from_dic['balance'] >= balance:
            to_dic['balance'] += balance
            from_dic['balance'] -= balance
            save(from_dic)
            save(to_dic)
            return True, '转账成功'
        else:
            return False, '余额不足'
    else:
        return False, '用户不存在'


def withdraw_interface(name, balance):
    '''
    取款接口.
    :param name: 取款用户
    :param balance: 取款金额
    :return:True,False
    '''
    user_dic = select(name)
    if user_dic['balance'] >= balance * 1.05:  # 0.5%的手续费
        user_dic['balance'] -= balance * 1.0
        save(user_dic)
        return True, '取款成功，取出金额%s,手续费%s' % (balance, balance * 0.05)
    else:
        return False, '余额不足'


def check_balance_interface(name):
    '''
    查询余额接口.
    :param name:账户名
    :return:balance
    '''
    user_dic = select(name)
    balance = user_dic['balance']
    return balance


def recharge_interface(name, money):
    '''
    充值接口
    :param moner:充值金额
    :return:
    '''
    user_dic = select(name)
    user_dic["balance"] += money
    return user_dic


# ================================================================
# ================================================================
# ================================================================
# ================================================================


def logout():
    '''
    退出.
    :return:
    '''
    user_data['name'] = None


def register():
    '''
    注册.
    :return:
    '''
    print('注册。。。')
    if user_data['name']:
        print('你已经登入过了')
    while True:
        name = input('请输入用户名>>:').strip()
        if name.lower() == 'q': break
        password = input('请输入密码>>:').strip()
        password2 = input('再次输入密码>>:').strip()
        if password == password2:
            flag, msg = register_interface(name, password)
            if flag:
                print(msg)
                break
            else:
                print('用户已存在')
        else:
            print('两次密码不一致')


def login():
    '''
    登入.
    :return:
    '''
    print('登录。。。')
    if user_data['name']:
        print('你已经登入过了')
    count = 0
    while True:
        name = input('请输入用户名>>:').strip()
        if name.lower() == 'q': break
        password = input('请输入密码>>:').strip()
        flag, msg = login_interface(name, password)
        if flag:
            user_data['name'] = name
            print(msg)
            break
        else:
            count += 1
            if count == 3:
                locked_interface(name)
                print('错误次数过多，已锁定')
            else:

                print(msg)


@login_auth
def recharge():
    '''
    充值
    :return:
    '''
    print("充值...")
    while True:
        to_money = input("请输入充值金额>>:").strip()
        if to_money.isdigit():
            to_money = int(to_money)
            user_dic = recharge_interface(user_data["name"], to_money)
            save(user_dic)
            print("充值成功")
            break
        elif to_money.lower() == "q":
            break
        else:
            print("请输入数字")


@login_auth
def transfer():
    '''
    转账.
    :return:
    '''
    print('转账...')
    while True:
        to_name = input('输入转账的用户>>:').strip()
        balance = input('输入转账金额>>:').strip()
        if balance.isdigit():
            balance = int(balance)
            flag, msg = transfer_interface(user_data['name'], to_name, balance)
            if flag:
                print(msg)
                break
            else:
                print(msg)
        else:
            print('必须输入数字')


@login_auth
def withdraw():
    '''
    提现.
    :return:
    '''
    print('提现...')
    balance = input('输入提现金额>>:').strip()
    if balance.isdigit():
        balance = int(balance)
        falg, msg = withdraw_interface(user_data['name'], balance)
        if falg:
            print(msg)
        else:
            print(msg)
    else:
        print('必须输入数字')


@login_auth
def check_balance():
    '''
    查看余额.
    :return:
    '''
    print('查看余额...')
    balance = check_balance_interface(user_data['name'])
    print(balance)


msg_dic = {
    "0": [register, "注册"],
    "1": [login, "登入"],
    "2": [recharge, "充值"],
    "3": [transfer, "转账"],
    "4": [withdraw, "提现"],
    "5": [check_balance, "查询余额"]
}

bs = '''
　〓〓〓◣　◢〓〓◣
　〓▌  〓　〓
　〓〓〓【　◥〓〓◣
　〓▌  〓　　　　〓
　〓〓〓◤　◥〓〓◤
'''


def run():
    '''
    程序入口
    :return:
    '''
    print(f"欢迎光临法外银行\n{bs}")
    while True:
        for ii in (f"{i:^5}:  {msg_dic[i][1]:<4}" for i in msg_dic): print(ii)
        count = input("请选择服务编号>>:").strip()
        if count in msg_dic:
            msg_dic[count][0]()
        else:
            print("输入的编号不存在")


run()
