
from ..agent.base import BaseAgent


class BaseContractStorage:    
    """BaseContractStorage interface"""

    def create_contract(self, kind, version, metadata, payload):
        raise NotImplementedError()

    def get_contract(self, contract_id):
        raise NotImplementedError()

    def list_contracts(self, state=None):
        raise NotImplementedError()

    def get_contract_metadata(self, contract_id):
        raise NotImplementedError()

    def get_contract_payload(self, contract_id):
        raise NotImplementedError()

    def get_contract_state(self, contract_id):
        raise NotImplementedError()

    def get_contract_logs(self, contract_id):
        raise NotImplementedError()

    def update_contract_state(self, contract_id, new_state, log_message=None):
        raise NotImplementedError()

    # Implement interaction with the agent
    def poll_contracts(self, agent: BaseAgent, state=None, new_state=None):
        raise NotImplementedError()