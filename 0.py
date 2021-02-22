import time
from datetime import datetime
start_time = datetime.now()

time.sleep(1)

end_time = datetime.now()
delta = end_time - start_time
delta = delta.total_seconds()
print(delta)