import pytest
from app.calculations import add, subtract, multiply, divide, BankAccount


@pytest.fixture
def bank_account():
    return BankAccount(0)

@pytest.fixture
def bank_account_with_balance():
    return BankAccount(50)

@pytest.mark.parametrize("num1, num2, expected", [(3,2,5), (5,3,8), (2,2,4)])
def test_add(num1, num2, expected):
    print("test_add")
    assert add(num1,num2) == expected 

def test_bank_set_initial_amount(bank_account_with_balance):
    assert bank_account_with_balance.balance == 50

