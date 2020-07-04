from network.network_client_interface import NetworkClientInterface


class NodeClient(NetworkClientInterface):
    NETWORK_CLIENT_TYPE = "Bitcoin node"

    def get_utxos(self, addresses):
        pass
