import logging


class UserDB:
    '''
    This class is used to store information about user accounts: their balances and last succesful transactions.
    '''


    def __init__(self, initial_balances_and_indices = []):
        '''
        Creates a user data base that contains user balances (by public key) and their last validated transaction.
        :param list initial_balances_and_indices: a list of triples consisting of a user's public key, their intial balance and the index of the last transaction performed by them
        '''
        self.user_balance = {}
        self.user_last_transaction_index = {}
        for public_key, balance, index in initial_balances_and_indices:
            self.user_balance[public_key] = balance
            self.user_last_transaction_index[public_key] = index


    def account_balance(self, user_public_key):
        '''
        Get the balance of the given user.
        :param str user_public_key: the public key of the user
        '''
        return self.user_balance.get(user_public_key, 0)



    def last_transaction(self, user_public_key):
        '''
        Get the index of the last transaction issued by the given user.
        :param str user_public_key: the public key of the user
        '''
        return self.user_last_transaction_index.get(user_public_key, -1)



    def check_transaction_correctness(self, tx):
        '''
        Check the correctness of a given transaction.
        :param Tx tx: the transaction to check
        :returns: True if the transaction has index one higher than the last transaction made by its issuer and the balance allows for the transaction, False otherwise
        '''
        issuer_balance = self.user_balance.get(tx.issuer, 0)
        issuer_last_transaction = self.user_last_transaction_index.get(tx.issuer, -1)
        return tx.amount >= 0 and issuer_balance >= tx.amount and tx.index == issuer_last_transaction + 1



    def apply_transaction(self, tx):
        '''
        Performs the given transaction if it is valid.
        :param Tx tx: the transaction to perform
        '''
        issuer_balance = self.user_balance.get(tx.issuer, 0)
        receiver_balance = self.user_balance.get(tx.receiver, 0)
        issuer_last_transaction = self.user_last_transaction_index.get(tx.issuer, -1)

        assert tx.amount >= 0, "The transaction that is about to be input has negative amount!"

        assert issuer_balance >= tx.amount, "The issuer does not have sufficient funds to perform this transaction."

        assert tx.index == issuer_last_transaction + 1, "The index of the transaction is not equal to the previous plus one."

        issuer_balance -= tx.amount
        receiver_balance += tx.amount

        self.user_balance[tx.issuer] = issuer_balance
        self.user_balance[tx.receiver] = receiver_balance
        self.user_last_transaction_index[tx.issuer] = tx.index
