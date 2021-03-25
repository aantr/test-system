import uuid

used = set()


def get_code():
    code = uuid.uuid4().hex[:4].upper()
    counter = 0
    max_iter = 10

    while code in used and counter < max_iter:
        counter += 1
        if counter == max_iter:
            print('qw')
            used.clear()
        else:
            code = uuid.uuid4().hex[:4].upper()

    used.add(code)
    return code


used_test = set()
while 1:
    code = get_code()
    if code in used_test:
        break
    print(len(used_test))
    used_test.add(code)

print(36 ** 4)
