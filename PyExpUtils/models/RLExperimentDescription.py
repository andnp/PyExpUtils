from PyExpUtils.models.ExperimentDescription import ExperimentDescription

class RLExperimentDescription(ExperimentDescription):
    def __init__(self, d):
        super().__init__(d)

        self.agent = d['agent']
        self.environment = d['environment']
        self.env_params = d['envParameters']
