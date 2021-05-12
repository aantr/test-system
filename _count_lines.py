import os
from glob import glob

files = [y for x in os.walk(os.getcwd())
         for y in glob(os.path.join(x[0], '*.py'))]
counter = 0
full_c = 0
n_files = 0
for i in files:
    if 'ignore' in i:
        continue
    if os.path.samefile(i, __file__):
        continue
    n_files += 1
    print(os.path.split(i)[1])
    with open(i, encoding='utf-8') as f:
        lines = f.readlines()
        counter += len(lines)
        full_c += len(lines)
        for i in lines:
            if not i.strip():
                counter -= 1

print('/' + '¯' * 63 + '\\')
print(f'| Lines in {n_files} "*.py" files: <<<---   {counter}   --->>>'.ljust(64, ' ') + '|')
print('-' * 65)
print(f'| With empty lines: <<<---   {full_c}   --->>>'.ljust(64, ' ') + '|')
print('\\' + '_' * 63 + '/')
