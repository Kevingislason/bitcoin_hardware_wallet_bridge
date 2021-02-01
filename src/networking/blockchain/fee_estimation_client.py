import json

import requests

from errors.fee_estimation_api_error import FeeEstimationAPIError


class FeeEstimationClient:
    URL = "https://api.blockchain.info/mempool/fees"

    # Uses mainnet fee-rate for testnet
    def get_current_fee_per_byte(self, is_priority: bool) -> int:
        response = requests.get(self.URL)
        if response.status_code != 200 and response.status_code != 404:
            raise FeeEstimationAPIError(response.status_code)
        if is_priority:
            return json.loads(response.text)["priority"]
        else:
            return json.loads(response.text)["regular"]
