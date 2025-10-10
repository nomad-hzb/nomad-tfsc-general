from nomad.config.models.plugins import ParserEntryPoint


class TFSCGeneralParserEntryPoint(ParserEntryPoint):
    def load(self):
        from nomad_tfsc_general.parsers.tfsc_general_measurement_parser import (
            TFSCGeneralParser,
        )

        return TFSCGeneralParser(**self.dict())


class TFSCGeneralExperimentParserEntryPoint(ParserEntryPoint):
    def load(self):
        from nomad_tfsc_general.parsers.tfsc_general_batch_parser import (
            TFSCGeneralExperimentParser,
        )

        return TFSCGeneralExperimentParser(**self.dict())


tfsc_general_parser = TFSCGeneralParserEntryPoint(
    name='TFSCGeneralParser',
    description='Parser for TFSC General files',
    mainfile_name_re='^((.+\.jv\.(txt|csv|IV))|(.+\.(IV|MPP|txt|csv|jv))|(.+\.nk))$',
    mainfile_mime_re='(application|text|image)/.*',
)


tfsc_general_experiment_experiment_parser = TFSCGeneralExperimentParserEntryPoint(
    name='TFSCGeneralBatchParser',
    description='Parser for TFSC General Batch xlsx files',
    mainfile_name_re="""^(.+\.xlsx)$""",
    # mainfile_contents_re='Experiment Info',
    mainfile_mime_re='(application|text|image)/.*',
)
