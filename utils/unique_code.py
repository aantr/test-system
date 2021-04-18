import uuid

used = set()


def get_code():
    code = uuid.uuid4().hex[:4].upper()
    counter = 0
    max_iter = 10

    while code in used and counter < max_iter:
        counter += 1
        if counter == max_iter:
            used.clear()
        else:
            code = uuid.uuid4().hex[:4]

    used.add(code)
    return code
