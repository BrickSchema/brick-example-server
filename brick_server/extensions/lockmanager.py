from contextlib import contextmanager
import hashlib
import pdb

import psycopg2

class LockManager(object):
    def __init__(self,
                 host='localhost',
                 port=6001,
                 dbname='brick',
                 user='bricker',
                 pw='brick-demo',
                 ):
        self.entity_lock_table = 'entity_locks'
        self.global_lock_id = 0

        conn_str = "dbname='{dbname}' host='{host}' port='{port}' " \
            .format(dbname=dbname, host=host, port=port) + \
            "password='{pw}' user='{user}'".format(user=user, pw=pw)
        self.conn = psycopg2.connect(conn_str)
        try:
            self.create_lock_table()
        except psycopg2.errors.UniqueViolation:
            pass


    def create_lock_id(self, entity_id, lock_id=None):
        cursor = self.conn.cursor()
        if lock_id == None:
            lock_id = int(hashlib.sha1(entity_id.encode('utf-8')).hexdigest(), 16) % 2147483648
            #TODO: Find an empty lock_id instead of this random one.
        qstr = """
        INSERT INTO {table_name}(lock_id, entity_id)
        VALUES
          ({lock_id}, '{entity_id}')
        ON CONFLICT (entity_id)
        DO
          UPDATE
            SET lock_id = {lock_id}
        ;
        """.format(table_name = self.entity_lock_table,
                   lock_id = lock_id,
                   entity_id = entity_id
                   )
        cursor.execute(qstr)
        cursor.close()
        self.conn.commit()
        return lock_id

    def create_lock_table(self):
        # Create table if not exists
        qstr = """
        CREATE TABLE IF NOT EXISTS {0} (
            lock_id INT UNIQUE NOT NULL,
            entity_id CHAR(36) UNIQUE NOT NULL PRIMARY KEY
        );
        """.format(self.entity_lock_table)
        cursor = self.conn.cursor()
        cursor.execute(qstr)
        cursor.close()
        self.conn.commit()
        self.create_lock_id('GLOBAL', self.global_lock_id)

    @contextmanager
    def advisory_lock(self, entity_id, shared=False, wait=True, using=None):

        # Assemble the function name based on the options.

        function_name = 'pg_'

        if not wait:
            function_name += 'try_'

        function_name += 'advisory_lock'

        if shared:
            function_name += '_shared'

        release_function_name = 'pg_advisory_unlock'
        if shared:
            release_function_name += '_shared'

        # Format up the parameters.


        # Generates an id within postgres integer range (-2^31 to 2^31 - 1).
        # crc32 generates an unsigned integer in Py3, we convert it into
        # a signed integer using 2's complement (this is a noop in Py2)

        base = "SELECT {0}(q.lock_id)".format(function_name)

        command = base + """, q.lock_id FROM
        (
          SELECT lock_id FROM {0} WHERE
          entity_id = '{1}' LIMIT 1
        ) q;
        """.format(self.entity_lock_table, entity_id)

        cursor = self.conn.cursor()

        acquired = False
        if not wait:
            prit('WARNING: nonsynchronous lock has not been fully validated yet')
            cursor.execute(command)
            (acquired, lock_id) = cursor.fetchone()
            acquired = res[0]
        else:
            while not acquired:
                cursor.execute(command)
                res = cursor.fetchone()
                if not res:
                    self.create_lock_id(entity_id)
                else:
                    lock_id = res[1]
                    acquired = True
        try:
            yield acquired
        finally:
            if acquired:
                qstr = 'SELECT {0}({1})'.format(release_function_name, lock_id)
                cursor.execute(qstr)

            cursor.close()

if __name__ == '__main__':
    entity_id = 'znt_1'
    lock_man = LockManager()
    with lock_man.advisory_lock(entity_id, shared=False, wait=True, using=None) as al:
        print('GOT LOCK')
