import decimal
import hashlib
from urllib import parse
from urllib.parse import urlparse


def calculate_signature(*args) -> str:
    """Create signature MD5.
    """
    print(':'.join(str(arg) for arg in args))
    return hashlib.md5(':'.join(str(arg) for arg in args).encode()).hexdigest()


def parse_response(request: str) -> dict:
    """
    :param request: Link.
    :return: Dictionary.
    """
    params = {}

    for item in urlparse(request).query.split('&'):
        key, value = item.split('=')
        params[key] = value
    return params


def check_signature_result(
    order_number: int,  # invoice number
    received_sum: decimal,  # cost of goods, RU
    received_signature: hex,  # SignatureValue
    password: str,  # Merchant password
    user_id: int | str,
) -> bool:
    signature = calculate_signature(received_sum, order_number, password, user_id)

    if signature.lower() == received_signature.lower():
        return True
    return False


# Формирование URL переадресации пользователя на оплату.

def generate_payment_link(
    merchant_login: str,  # Merchant login
    merchant_password_1: str,  # Merchant password
    cost: decimal,  # Cost of goods, RU
    number: int,  # Invoice number
    description: str,  # Description of the purchase
    shp_user_id: int | str,  # User Telegram ID
    is_test=1,
    robokassa_payment_url='https://auth.robokassa.ru/Merchant/Index.aspx',
) -> str:
    """URL for redirection of the customer to the service.
    """
    signature = calculate_signature(
        merchant_login,
        cost,
        number,
        merchant_password_1,
        f"Shp_userId={shp_user_id}",
    )

    data = {
        'MerchantLogin': merchant_login,
        'OutSum': cost,
        'InvoiceId': number,
        'Description': description,
        'SignatureValue': signature,
        'IsTest': is_test,
        'Shp_userId': shp_user_id,
    }
    return f'{robokassa_payment_url}?{parse.urlencode(data)}'
