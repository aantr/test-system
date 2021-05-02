import os
from glob import glob

files = [y for x in os.walk(os.getcwd())
         for y in glob(os.path.join(x[0], '*.py'))]
counter = 0
for i in files:
    if 'ignore' in i:
        continue
    if os.path.samefile(i, __file__):
        continue
    with open(i, encoding='utf-8') as f:
        counter += len(f.readlines())

print('-' * 100)
print(f'Lines in {len(files)} "*.py" files: <<<---   {counter}   --->>>')
print('-' * 100)
