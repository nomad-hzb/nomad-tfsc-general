from nomad.config.models.plugins import SchemaPackageEntryPoint


class TFSCGeneralPackageEntryPoint(SchemaPackageEntryPoint):
    def load(self):
        from nomad_tfsc_general.schema_packages.tfsc_general_package import m_package

        return m_package


tfsc_general_package = TFSCGeneralPackageEntryPoint(
    name='TFSC General',
    description='General Thin Film Solar Cell Package',
)
