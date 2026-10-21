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
    assert add(num1,num2) == expected

def test_subtract():
    assert subtract(9, 4) == 5

def test_multiply():
    assert multiply(4, 3) == 12

def test_divide():
    assert divide(12, 4) == 3

def test_divide_by_zero():
    with pytest.raises(ZeroDivisionError):
        divide(1, 0)

def test_bank_set_initial_amount(bank_account_with_balance):
    assert bank_account_with_balance.balance == 50

def test_bank_default_amount(bank_account):
    assert bank_account.balance == 0

def test_deposit(bank_account_with_balance):
    bank_account_with_balance.deposit(30)
    assert bank_account_with_balance.balance == 80

def test_withdraw(bank_account_with_balance):
    bank_account_with_balance.withdraw(20)
    assert bank_account_with_balance.balance == 30

def test_collect_interest(bank_account_with_balance):
    bank_account_with_balance.collect_interest(0.5)
    assert bank_account_with_balance.balance == 75
