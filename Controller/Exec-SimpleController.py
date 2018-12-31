from ControllerCore import ControllerCore
import time

if __name__ == '__main__':
    cont = ControllerCore(4041, 4040,'./init','./functions')

ctr = 0
def process():
    global ctr
    fname = 'hellocot'
    str = 'Hi!!!'
    ctr += 1
    fer = {'id':ctr, 'x':'{}{}'.format(str, ctr), 'm':{'User':'helloCoT_Test!'}}
    print('Submitting {}'.format(ctr), end='')
    cont.FER_push(fname, fer)
    print('[Submitted]')
    while cont.FER_hasReturned(fname):
        res = cont.FER_pop(fname)
        print('Got: ', res)

if __name__ == '__main__':
    i = input('Press enter to start...')
    while True:
        process()
        time.sleep(1)
