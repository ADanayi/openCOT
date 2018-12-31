import zmq
import multiprocessing as mp
import threading as thd
import time

class Gate:
    def __init__(self, q_port, qPrime_port, funcName):
        self._QPort = q_port
        self._QPPort = qPrime_port
        
        self.Q = mp.Queue()
        self.QP = mp.Queue()
        
        self.lock = thd.Lock()        
        
        self.proc_Q = mp.Process(target=Gate._wrk_Q, args=(self.Q, self._QPort, funcName), daemon=False)
        self.proc_QP = mp.Process(target=Gate._wrk_QP, args=(self.QP, self._QPPort, funcName), daemon=False)
        
        self.proc_Q.start()
        self.proc_QP.start()
        
    def pr(txt):
        print('AGENT: {}'.format(txt))
        
    def _wrk_Q(Q, QPort, fName):
        Gate.pr('Gate: Creating Push server for {} @ {}'.format(fName, QPort))
        context = zmq.Context()
        socket = context.socket(zmq.REP)
        socket.bind("tcp://0.0.0.0:{}".format(QPort))
        while True:
            msg = socket.recv_string()
            #Gate.pr('Gate: Req for {}'.format(fName))
            if msg == '?':
                if Q.qsize() > 0:
                    obj = Q.get()
                    Gate.pr('Gate: Push: got new FER. Sending it.')
                    socket.send_json(obj)
                else:
                    socket.send_json({'id':-1})
            
        
    def _wrk_Q_push(Q, QPort, fName):
        Gate.pr('Gate: Creating Push server for {} @ {}'.format(fName, QPort))
        context = zmq.Context(4)
        socket = context.socket(zmq.PUSH)
        socket.bind("tcp://0.0.0.0:{}".format(QPort))
        while True:
            obj = Q.get()
            Gate.pr('Gate: Push: got new FER. Sending it.')
            socket.send_json(obj)
                
    def _wrk_QP(QP, QPPort, fName):
        Gate.pr('Creating Pull server for {} @ {}'.format(fName, QPPort))
        context = zmq.Context(4)
        zmq_socket = context.socket(zmq.PULL)
        zmq_socket.bind("tcp://*:{}".format(QPPort))
        while True:
                feu = zmq_socket.recv_json()
                Gate.pr('Gate: Pull: Recieved new RET.')
                QP.put(feu)
