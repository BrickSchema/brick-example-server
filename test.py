import stopit
import pdb
import time

try:
    with stopit.ThreadingTimeout(1, swallow_exc=False) as ctx:
        time.sleep(10)
        print('success')
except stopit.TimeoutException:
    print('failed')

print('ended')
