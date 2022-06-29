from functools import lru_cache
from fastapi import FastAPI, Depends
from neo4j import GraphDatabase
from neo4j.exceptions import ClientError
import os
import logging
from config import Settings
from models.models import Supplier, Order, Product, Customer
from fastapi.responses import RedirectResponse

app = FastAPI()


@lru_cache
def get_settings():
    return Settings()


URI = os.environ["URI"]
USER = os.environ["USER"]
PASSWORD = os.environ["PASSWORD"]
DATABASE = os.environ["DATABASE"]
driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))


@app.get("/")
async def root(settings: Settings = Depends(get_settings)):
    return RedirectResponse(url='/docs')


def _add_products(tx, product):
    query = (
        "MERGE (p:Product { productID: $prod_id, productName: $prod_name }) "
        "RETURN p AS products "
    )
    result = tx.run(query, prod_id=product.productID, prod_name=product.productName)
    try:
        return [(row["products"]) for row in result]
    except ClientError as exception:
        logging.error("{query} raised an error: \n {exception}".format(
            query=query, exception=exception))
        raise exception


@app.post("/add_product/", tags=["insert-node"])
async def add_products(product: Product):
    with driver.session(database=DATABASE) as session:
        result = session.write_transaction(
            _add_products, product)
    return result


def _delete_products(tx, product):
    query = (
        "MATCH (p:Product { productID: $prod_id }) "
        "DETACH DELETE p "
    )
    result = tx.run(query, prod_id=product.productID, prod_name=product.productName)
    try:
        return {"message": "Product {} has been deleted ".format(product.productID)}
    except ClientError as exception:
        logging.error("{query} raised an error: \n {exception}".format(
            query=query, exception=exception))
        raise exception


@app.post("/delete_product/", tags=["delete-node"])
async def delete_products(product: Product):
    with driver.session(database=DATABASE) as session:
        result = session.write_transaction(
            _delete_products, product)
    return result


def _get_nodes(tx, name):
    query = (
        "MATCH (n:{node_name} ) "
        "RETURN n AS nodes "
        "LIMIT 25 "
    ).format(node_name=name)
    result = tx.run(query, node_name=name)

    return [(row["nodes"]) for row in result]


@app.get("/nodes/{name}")
async def get_nodes(name: str):
    with driver.session(database=DATABASE) as session:
        result = session.read_transaction(_get_nodes, name)
    return result


def _get_sales_employee(tx, emp_id):
    query = (
        "MATCH(e:Employee) - [:SOLD] -> (o:Order) "
        "WHERE e.employeeId = $emp_id "
        "RETURN count(o.orderID) AS OrderCount "
    )
    result = tx.run(query, emp_id=emp_id)

    return [(row["OrderCount"]) for row in result]


@app.get("/sales/{employeeId}")
async def get_sales_employee(employeeId: int):
    with driver.session(database=DATABASE) as session:
        result = session.read_transaction(_get_sales_employee, employeeId)
    return result


def _get_product_supplier(tx, prod_id):
    query = (
        "MATCH (s:Supplier)-[:SUPPLY]->(p:Product) "
        "WHERE p.productID = $prod_id "
        "RETURN s.companyName AS company,  s.contactName AS contact, s.phone AS phone"
    )
    result = tx.run(query, prod_id=prod_id)
    return [{"company": row["company"], "contact": row["contact"], "phone": row["phone"]} for row in result]


@app.get("/supplier/{prod_id}")
async def get_product_supplier(prod_id: int):
    with driver.session(database=DATABASE) as session:
        result = session.read_transaction(_get_product_supplier, prod_id)
    return result


def _add_supplier(tx, supplier):
    query = (
        "MERGE (s:Supplier { supplierID:$sup_id, companyName: $comp_name, contactName: $cont_name, contactTitle: $cont_title, fax: $supp_cont, phone: $supp_phone, supp_homepage: $homepage}) "
        "RETURN s AS sup "
    )
    result = tx.run(query, sup_id=supplier.supplierID, comp_name=supplier.companyName, cont_name=supplier.contactName,
                    cont_title=supplier.contactTitle, supp_cont=supplier.fax, supp_phone=supplier.phone,
                    supp_homepage=supplier.homepage)
    try:
        return [row["sup"] for row in result]
    except ClientError as exception:
        logging.error("{query} raised an error: \n {exception}".format(
            query=query, exception=exception))
        raise exception


@app.post("/supplier/", tags=["insert-node"])
async def add_supplier(supplier: Supplier):
    with driver.session(database=DATABASE) as session:
        result = session.write_transaction(
            _add_supplier, supplier)
    return result


def _add_customer_purchase_order(tx, order, customer):
    query = (
        "MATCH (c:Customer { customerID:$cust_id }) "
        "MERGE (o:Order { orderId: $ord_id, orderDate: datetime() }) "
        "MERGE (c) - [:PLACED] -> (o) "
        "RETURN o AS ord "
    )
    result = tx.run(query, cust_id=customer.customerID, ord_id=order.orderID)
    try:
        return [row["ord"] for row in result]
    except ClientError as exception:
        logging.error("{query} raised an error: \n {exception}".format(
            query=query, exception=exception))
        raise exception


@app.post("/purchase_order/", tags=["insert-relationship"])
async def add_customer_purchase_order(order: Order, customer: Customer):
    with driver.session(database=DATABASE) as session:
        result = session.write_transaction(
            _add_customer_purchase_order, order, customer)
    return result
