from StcIntPythonPL import *


class AclPerformanceData:

    def __init__(self):
        self.key = 'spirent.methodology.AclPerformance'
        self.key_exp_pktloss = 'exp_pktloss'
        self.key_exp_avgjitter = 'exp_avgjitter'
        self.key_exp_maxjitter = 'exp_maxjitter'
        self.key_exp_avglatency = 'exp_avglatency'
        self.key_exp_maxlatency = 'exp_maxlatency'
        self.key_exp_maxoop = 'exp_maxoop'
        self.key_exp_maxlatepkt = 'exp_maxlatepkt'
        if not CObjectRefStore.Exists(self.key):
            CObjectRefStore.Put(self.key, {'expectations': {}})
        return

    def set_exp_pktloss(self, exp_pktloss):
        d = CObjectRefStore.Get(self.key)
        d[self.key_exp_pktloss] = exp_pktloss
        return

    def set_exp_avgjitter(self, exp_avgjitter):
        d = CObjectRefStore.Get(self.key)
        d[self.key_exp_avgjitter] = exp_avgjitter
        return

    def set_exp_maxjitter(self, exp_maxjitter):
        d = CObjectRefStore.Get(self.key)
        d[self.key_exp_maxjitter] = exp_maxjitter
        return

    def set_exp_avglatency(self, exp_avglatency):
        d = CObjectRefStore.Get(self.key)
        d[self.key_exp_avglatency] = exp_avglatency
        return

    def set_exp_maxlatency(self, exp_maxlatency):
        d = CObjectRefStore.Get(self.key)
        d[self.key_exp_maxlatency] = exp_maxlatency
        return

    def set_exp_maxoop(self, exp_maxoop):
        d = CObjectRefStore.Get(self.key)
        d[self.key_exp_maxoop] = exp_maxoop
        return

    def set_exp_maxlatepkt(self, exp_maxlatepkt):
        d = CObjectRefStore.Get(self.key)
        d[self.key_exp_maxlatepkt] = exp_maxlatepkt
        return

    def get_exp_pktloss(self):
        d = CObjectRefStore.Get(self.key)
        return d[self.key_exp_pktloss]

    def get_exp_avgjitter(self):
        d = CObjectRefStore.Get(self.key)
        return d[self.key_exp_avgjitter]

    def get_exp_maxjitter(self):
        d = CObjectRefStore.Get(self.key)
        return d[self.key_exp_maxjitter]

    def get_exp_avglatency(self):
        d = CObjectRefStore.Get(self.key)
        return d[self.key_exp_avglatency]

    def get_exp_maxlatency(self):
        d = CObjectRefStore.Get(self.key)
        return d[self.key_exp_maxlatency]

    def get_exp_maxoop(self):
        d = CObjectRefStore.Get(self.key)
        return d[self.key_exp_maxoop]

    def get_exp_maxlatepkt(self):
        d = CObjectRefStore.Get(self.key)
        return d[self.key_exp_maxlatepkt]
