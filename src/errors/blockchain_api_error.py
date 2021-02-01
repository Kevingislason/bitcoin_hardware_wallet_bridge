class BlockchainAPIError(Exception):
    status: int

    def __init__(self, status):
        self.status = status

    def __str__(self):
        return "API error: There was a problem fetching blockchain data"
