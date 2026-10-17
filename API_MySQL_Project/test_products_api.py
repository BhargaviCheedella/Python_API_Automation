
import os
from decimal import Decimal

import mysql.connector
import pytest
import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://fakestoreapi.com"


def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "127.0.0.1"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME", "api_testing_db"),
    )


def get_expected_products():
    connection = get_db_connection()

    try:
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT id, expected_title, expected_price
                FROM expected_products
                ORDER BY id
                """
            )
            return cursor.fetchall()
        finally:
            cursor.close()
    finally:
        connection.close()


@pytest.fixture(scope="module")
def session():
    with requests.Session() as http:
        yield http


def test_products_endpoint_returns_success(session):
    response = session.get(f"{BASE_URL}/products", timeout=20)

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_product_ids_and_data_match_mysql(session):
    expected_products = get_expected_products()

    assert expected_products, (
        "No expected products found in MySQL. Add verified rows first."
    )

    for expected in expected_products:
        response = session.get(
            f"{BASE_URL}/products/{expected['id']}",
            timeout=20,
        )

        assert response.status_code == 200, (
            f"Product ID {expected['id']}: "
            f"unexpected status {response.status_code}"
        )

        actual = response.json()

        assert actual["id"] == expected["id"]
        assert actual["title"] == expected["expected_title"]

        assert Decimal(str(actual["price"])) == Decimal(
            str(expected["expected_price"])
        ), f"Price mismatch for product ID {expected['id']}"


def test_nonexistent_product_id(session):
    response = session.get(
        f"{BASE_URL}/products/999999",
        timeout=20,
    )

    # Confirm this expected behavior against your live result from Step 1.
    # The common Fake Store API response is HTTP 200 with an empty object.
    assert response.status_code == 200
    assert response.text == "", (
        f"Expected an empty response body, got:{response.text!r}"
    )



def test_malformed_product_id(session):
    response = session.get(
        f"{BASE_URL}/products/abc",
        timeout=20,
    )

    # Confirm this expected behavior against your live result from Step 1.
    assert response.status_code == 200
    assert response.text == "", (
        f"Expected an empty response body, got: {response.text!r}"
    )
