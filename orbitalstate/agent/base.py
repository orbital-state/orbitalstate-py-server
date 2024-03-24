import logging


class BaseAgent:
    logger = logging.getLogger(__name__)

    def process_contract(self, contract):
        self.logger.info("Processing contract: {}".format(contract["id"]))
        if contract["state"] == "pending":
            return self._exec_contract(contract)
        if contract["state"] == "drifted":
            return self._repair_contract(contract)
        if contract["state"] == "terminating":
            return self._terminate_contract(contract)
        self.logger.error("Invalid contract state: {}".format(contract["state"]))
        return False

    def _exec_contract(self, contract):
        """Execute contract"""
        self.logger.info("Executing contract: {}".format(contract["id"]))
        # TODO: Implement contract execution
        return True

    def _repair_contract(self, contract):
        """Repair contract"""
        self.logger.info("Repairing contract: {}".format(contract["id"]))
        # TODO: Implement contract repair
        return True

    def _terminate_contract(self, contract):
        """Terminate contract"""
        self.logger.info("Terminating contract: {}".format(contract["id"]))
        # TODO: Implement contract termination
        return True
