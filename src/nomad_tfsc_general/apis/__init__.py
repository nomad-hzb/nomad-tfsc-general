from nomad.config.models.plugins import APIEntryPoint


class UploadQCEntryPoint(APIEntryPoint):

    def load(self):
        from nomad_tfsc_general.apis.upload_qc import app

        return app


upload_qc = UploadQCEntryPoint(
    prefix = 'uploadqc',
    name = 'Upload Quality Check',
    description = 'Allows overview of uploaded entities, measurements and potential errors.',
)