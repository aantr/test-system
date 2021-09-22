import random
import uuid

used4 = set()


def get_code4():
    code = uuid.uuid4().hex[:4].lower()
    counter = 0
    max_iter = 10

    while code in used4 and counter < max_iter:
        counter += 1
        if counter == max_iter:
            used4.clear()
        else:
            code = uuid.uuid4().hex[:4].lower()

    used4.add(code)
    return code


used6 = set()


def get_code6():
    code = str(random.randint(100000, 999999))
    counter = 0
    max_iter = 10

    while code in used6 and counter < max_iter:
        counter += 1
        if counter == max_iter:
            used6.clear()
        else:
            code = str(random.randint(100000, 1000000))

    used6.add(code)
    return code
