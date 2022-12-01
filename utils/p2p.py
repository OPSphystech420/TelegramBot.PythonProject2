from pyqiwip2p import QiwiP2P
import config

p2p = QiwiP2P(auth_key = config.config('secret_key'))


def create_pay(bill_id, amount):
	bill = p2p.bill(bill_id = bill_id, amount = amount, lifetime = 15, comment = 'Senior Game')

	return bill.pay_url, bill.bill_id

def check_status_p2p(bill_id):
	status  = p2p.check(bill_id=bill_id).status

	return status

def check_amount(bill_id):
	status  = p2p.check(bill_id=bill_id).amount

	return status