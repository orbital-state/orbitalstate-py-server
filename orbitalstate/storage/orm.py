import uuid
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import orm, create_engine, Column, Integer, String, DateTime, JSON
from . import TRANSITING_STATES
from ..agent.base import BaseAgent


Base = declarative_base()


def generate_uuid():
    return str(uuid.uuid4())


class Contract(Base):
    __tablename__ = "contracts"
    id = Column(Integer, primary_key=True)
    # Note that 36 byte is sufficient for uuid4 but we reserve 4 byte for future needs
    uuid = Column(String(40), index=True, unique=True, default=generate_uuid) 
    kind = Column(String(50))
    version = Column(String(50))
    metadata_ = Column("metadata", JSON)
    payload = Column(JSON)
    logs = Column(JSON)
    state = Column(String(20), index=True, unique=True, default="pending")
    created_at = Column(DateTime, default=datetime.now)

    def to_dict(self):
        return {
            "id": self.uuid,  # we map internal DB id to external uuid
            "kind": self.kind,
            "version": self.version,
            "metadata": self.metadata_,
            "payload": self.payload,
            "logs": self.logs,
            "state": self.state,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class AlchemyContractStorage:
    def __init__(self, db_url):
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)
        self.session = orm.sessionmaker(bind=self.engine)()

    def _create(self, kind, version, metadata, payload):
        logs = [{
            "timestamp": datetime.now().isoformat(),
            "message": "Contract created"
        }]
        contract = Contract(kind=kind, version=version, metadata_=metadata, payload=payload, logs=logs)
        self.session.add(contract)
        self.session.commit()
        return contract

    def _get(self, contract_id):
        return self.session.query(Contract).filter(Contract.uuid == contract_id).first()

    def _list(self, state=None):
        query = self.session.query(Contract)
        if state:
            query = query.filter(Contract.state == state)
        return [c.to_dict() for c in query.all()]

    def _update(self, contract_id, state, log_message=None):
        if not log_message:
            log_message = "State updated to {}".format(new_state)
        contract = self.get(contract_id)
        contract.state = state
        contract.logs.append({
            "timestamp": datetime.now().isoformat(),
            "message": log_message
        })
        self.session.commit()

    def _close(self):
        self.session.close()
        self.engine.dispose()

    def __del__(self):
        self._close()

    # Implement BaseContractStorage interface
    def create_contract(self, kind, version, metadata, payload):
        return self._create(kind, version, metadata, payload).to_dict()

    def get_contract(self, contract_id):
        return self._get(contract_id).to_dict()

    def list_contracts(self, state=None):
        return self._list(state)

    def get_contract_metadata(self, contract_id):
        return self._get(contract_id).metadata_

    def get_contract_payload(self, contract_id):
        return self._get(contract_id).payload

    def get_contract_state(self, contract_id):
        return self._get(contract_id).state

    def get_contract_logs(self, contract_id):
        return self._get(contract_id).logs

    def update_contract_state(self, contract_id, new_state):
        return self._update(contract_id, new_state).to_dict()

    # Implement interaction with the agent
    def poll_contracts(self, agent: BaseAgent, state=None, new_state=None):
        """
        Poll contracts in state and transit them to new_state if possible.
        """
        # TODO: implement pagination
        # can we transit to new_state from state?
        assert new_state in TRANSITING_STATES[state]
        contracts = self._list(state)
        for contract in contracts:
            try:
                if agent.process_contract(contract):
                    self._update(contract["id"], new_state)
            except Exception as error:
                self._update(
                    contract["id"], "failed", 
                    f"Failed to process contract <{state}> -> <{new_state}>: \n" 
                    + str(error))
