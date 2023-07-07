import requests
import json
from datetime import datetime, datetime, timedelta
import config
import random
import typing
from requests import Response

class Bill:
	def __init__(self, response: typing.Union[Response, dict]):
		self.r_json = response if type(response) is Response else response
		try:
			self.r_json = self.r_json.json()
		except json.decoder.JSONDecodeError as e:
			raise ValueError("Qiwi response is not JSON. This is Qiwi-side bug. Please try again later.")
		if "errorCode" in self.r_json:
			raise QiwiError(self.r_json)
		else:
			self.site_id: int = self.r_json["siteId"]
			self.bill_id: int = self.r_json["billId"]
			self.amount: float = self.r_json["amount"]["value"]
			self.currency: str = self.r_json["amount"]["currency"]
			self.status: str = self.r_json["status"]["value"]
			self.status_changed: str = self.r_json["status"]["changedDateTime"]
			self.creation: str = self.r_json["creationDateTime"]
			self.expiration: str = self.r_json["expirationDateTime"]
			self.pay_url: str = self.r_json["payUrl"]
			self.comment: str = self.r_json["comment"] if "comment" in self.r_json else None
			self.json = self.r_json
	
def create_bill(amount):
	time = datetime.now() + timedelta(minutes=15)
	life_time = time.strftime("%Y-%m-%dT%H:%M:%S+03:00")
	headers = {"Accept": "application/json",
		"Content-Type": "application/json",
		"Authorization": f"Bearer {config.config('secret_key')}"
	}

	params = {'amount': {'value': float(amount), 'currency': 'RUB'},
		'comment': 'Пополнение Senior Game',
		'expirationDateTime': life_time,
		'customer': {},
		'customFields': {},
	}
	bill_id = random.randint(11111111, 99999999)
	data = json.dumps(params)
	p2p = requests.put(f"https://api.qiwi.com/partner/bill/v1/bills/{bill_id}",
										  json=params, headers=headers)
	#p2p = requests.put('https://api.qiwi.com/partner/bill/v1/bills/' + str(bill_id),
	#	headers = headers,
	#	data = data)
	url = p2p.json()["payUrl"]

	return url, bill_id

def check_p2p(bill_id):
		qiwi_request_headers = {
			"Content-Type": "application/json",
			"Authorization": f"Bearer {config.config('secret_key')}"
		}
		p2p = Bill(requests.get(f"https://api.qiwi.com/partner/bill/v1/bills/{bill_id}",
										  headers=qiwi_request_headers))

		return p2p

def reject_p2p(bill_id):
		qiwi_request_headers = {
			"Content-Type": "application/json",
			"Authorization": f"Bearer {config.config('secret_key')}"
		}
		p2p = Bill(requests.post(f"https://api.qiwi.com/partner/bill/v1/bills/{bill_id}/reject",
										   headers=qiwi_request_headers))
		return p2p
