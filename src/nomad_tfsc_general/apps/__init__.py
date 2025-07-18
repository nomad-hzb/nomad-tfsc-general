from nomad.config.models.plugins import AppEntryPoint
from nomad.config.models.ui import (
    App,
    Column,
    FilterMenu,
    FilterMenus,
    FilterMenuSizeEnum,
    Filters,
    Format,
    ModeEnum,
    RowActions,
    RowActionURL,
    RowDetails,
    Rows,
    RowSelection,
)

schema_name = 'nomad_tfsc_general.schema_packages.tfsc_general_package.TFSC_General_VoilaNotebook'
tfsc_voila_documentation_app = AppEntryPoint(
    name='voila',
    description='Find and launch your Voila Tools.',
    app=App(
        # Label of the App
        label='Voila',
        # Path used in the URL, must be unique
        path='voila',
        # Used to categorize apps in the explore menu
        category='use cases',
        # Brief description used in the app menu
        description='Find and launch your Voila Tools.',
        # Longer description that can also use markdown
        readme='Find and launch your Voila Tools.',
        # Controls the available search filters. If you want to filter by
        # quantities in a schema package, you need to load the schema package
        # explicitly here. Note that you can use a glob syntax to load the
        # entire package, or just a single schema from a package.
        filters=Filters(
            include=[
                f'*#{schema_name}',
            ]
        ),
        # Dictionary of search filters that are always enabled for queries made
        # within this app. This is especially important to narrow down the
        # results to the wanted subset. Any available search filter can be
        # targeted here. This example makes sure that only entries that use
        # MySchema are included.
        filters_locked={'section_defs.definition_qualified_name': schema_name},
        filter_menus=FilterMenus(
            options={
                'custom_quantities': FilterMenu(label='Notebooks', size=FilterMenuSizeEnum.L),
                'author': FilterMenu(label='Author', size=FilterMenuSizeEnum.M),
                'metadata': FilterMenu(label='Visibility / IDs'),
            }
        ),
        columns=[
            Column(quantity=f'data.name#{schema_name}', selected=True),
            Column(quantity='entry_type', label='Entry type', align='left', selected=True),
            Column(
                quantity='entry_create_time',
                label='Entry time',
                align='left',
                selected=True,
                format=Format(mode=ModeEnum.DATE),
            ),
            Column(
                quantity='upload_name',
                label='Upload name',
                align='left',
                selected=True,
            ),
            Column(
                quantity='authors',
                label='Authors',
                align='left',
                selected=True,
            ),
            Column(quantity='entry_id'),
            Column(quantity='upload_id'),
            Column(quantity=f'data.notebook_file#{schema_name}'),
        ],
        rows=Rows(
            actions=RowActions(
                items=[
                    RowActionURL(
                        path=f'data.file_uri#{schema_name}',
                        description='View in file browser',
                        icon='search',
                    ),
                ]
            ),
            details=RowDetails(),
            selection=RowSelection(),
        ),
    ),
)
