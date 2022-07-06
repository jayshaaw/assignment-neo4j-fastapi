import os
import logging

from dotenv import load_dotenv, find_dotenv
from neo4j import GraphDatabase

env_loc = find_dotenv('../.env')
load_dotenv(env_loc)

URI = os.environ["URI"]
USER = os.environ["USER"]
PASSWORD = os.environ["PASSWORD"]
DATABASE = os.environ["DATABASE"]
driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))

nodes_list = {'Address', 'Customer', 'Order', 'Person', 'Product'}


#
# def test_connection():
#     with driver.session(database=DATABASE) as session:
#         if session:
#             return True
#         else:
#             return False


def _get_nodes(tx, name):
    query = (
        "MATCH (n:{node_name} ) "
        "RETURN n AS nodes "
        "LIMIT 1 "
    ).format(node_name=name)
    result = tx.run(query, node_name=name)

    return [(row["nodes"]) for row in result]


def test_nodes():
    for node in nodes_list:
        with driver.session(database=DATABASE) as session:
            result = session.read_transaction(_get_nodes, node)
        return result
        # if result:
        #     logging.log(msg=f'{node} exists in the database')
        #     print(f'{node} exists in the database')
        # else:
        #     return False


if __name__ == '__main__':
    test_nodes()
