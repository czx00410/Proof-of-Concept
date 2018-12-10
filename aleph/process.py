import asyncio
import concurrent
import multiprocessing
import random

from aleph.data_structures.unit import Unit
from aleph.data_structures.poset import Poset
from aleph.data_structures.user_base import User_base
from aleph.crypto.keys import SigningKey, VerifyKey
from aleph.network import listener, sync
from aleph.config import CREATE_FREQ, SYNC_INIT_FREQ


class Process:
    '''This class is the main component of the Aleph protocol.'''


    def __init__(self, n_processes, process_id, secret_key, public_key, address_list, public_key_list):
        '''
        :param int n_processes: the committee size
        :param int process_id: the id of the current process
        :param string secret_key: the private key of the current process
        :param list addresses: the list of length n_processes containing addresses (host, port) of all committee members
        :param list public_keys: the list of public keys of all committee members
        '''

        self.n_processes = n_processes
        self.process_id = process_id

        self.secret_key = secret_key
        self.public_key = public_key

        self.public_key_list = public_key_list
        self.address_list = address_list
        self.host = address_list[process_id][0]
        self.port = address_list[process_id][1]

        self.poset = Poset(self.n_processes)
        self.user_base = User_base()

        # a bitmap specifying for every process whether he has been detected forking
        self.is_forker = [False for _ in range(self.n_processes)]


    def sign_unit(self, U):
        '''
        Signs the unit.
        '''

        message = U.to_message()
        U.signature = self.secret_key.sign(message)


    async def create_add(self):
    #while True:
        for _ in range(5):
            new_unit = self.poset.create_unit(self.process_id, [], strategy = "link_self_predecessor", num_parents = 2)
            if new_unit is not None:
                assert self.poset.check_compliance(new_unit), "A unit created by our process is not passing the compliance test!"
                self.sign_unit(new_unit)
                self.poset.add_unit(new_unit)

            await asyncio.sleep(CREATE_FREQ)


    async def keep_syncing(self, executor):
        await asyncio.sleep(0.7)
        #while True:
        for _ in range(5):
            sync_candidates = list(range(self.n_processes))
            sync_candidates.remove(self.process_id)
            target_id = random.choice(sync_candidates)
            asyncio.create_task(sync(self.poset, self.process_id, target_id, self.address_list[target_id], self.public_key_list, executor))

            await asyncio.sleep(SYNC_INIT_FREQ)


    async def prepare_txs(self):
        pass


    def get_txs(self):
        queue = multiprocessing.Queue()
        pipe = multiprocessing.Pipe()
        tx_listener = multiprocessing.Process(target=f, args=(queue, pipe))
        tx_listener.start()
        tx_listener.join()



    async def run(self):
        #tasks = []
        executor = concurrent.futures.ProcessPoolExecutor(max_workers=3)
        creator_task = asyncio.create_task(self.create_add())
        listener_task = asyncio.create_task(listener(self.poset, self.process_id, self.address_list, self.public_key_list, executor))
        syncing_task = asyncio.create_task(self.keep_syncing(executor))
        await asyncio.gather(creator_task, syncing_task )
        listener_task.cancel()
