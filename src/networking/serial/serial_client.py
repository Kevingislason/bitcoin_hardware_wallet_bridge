class SerialClient:
    def await_connection(self) -> bool:
        return True

    def authenticate(self) -> bool:
        return True

    def get_master_pubkey(self):
        return 'todo'
