from nomad.config.models.ui import (
    App,
    Column,
    Columns,
    FilterMenu,
    FilterMenus,
    Filters,
    Pagination,
    SearchQuantities,
)

perseus_layer_search_app = App(
    # Label of the App
    label='Find PERSEUS Sample Layers',
    # Path used in the URL, must be unique
    path='perseus-find-layer',
    # Used to categorize apps in the explore menu
    category='Solar Cell Data',
    # Brief description used in the app menu
    description='Provides filters to quickly find experiment entries based on layer fabrication.',
    # Longer description that can also use markdown
    readme='Provides filters to quickly find experiment entries.',
    # Controls the available search filters. If you want to filter by
    # quantities in a schema package, you need to load the schema package
    # explicitly here. Note that you can use a glob syntax to load the
    # entire package, or just a single schema from a package.
    filters=Filters(
        include=[
            '*#nomad_tfsc_general.schema_packages.tfsc_general_package',
        ]
    ),

    # Controls which columns are shown in the results table
    pagination=Pagination(order_by='results.properties.optoelectronic.solar_cell.efficiency'),
    # Controls which columns are shown in the results table
    columns=Columns(
        selected=[
            'entry_type',
            'entry_name',
            'entry_create_time',
            'authors',
            'upload_name',
            'results.properties.optoelectronic.solar_cell.efficiency',
        ],
        options={
            'entry_type': Column(label='Entry type', align='left'),
            'entry_name': Column(label='Name', align='left'),
            'entry_create_time': Column(label='Entry time', align='left'),
            'authors': Column(label='Authors', align='left'),
            'upload_name': Column(label='Upload name', align='left'),
            'results.properties.optoelectronic.solar_cell.efficiency': Column(label='PCE', align='left'),
            # 'data.lab_id#nomad_tfsc_general.schema_packages.tfsc_general_package': Column(
            #     label='Experiment ID', align='left'
            # ),
        },
    ),

    dashboard= {
        'widgets': [
            {
                'type': 'terms',
                'scale': 'linear',
                'search_quantity': 'entry_name',
                'title': 'Entry Names',
                'layout': {
                    'xxl': {'minH': 3, 'minW': 3, 'h': 5, 'w': 8, 'y': 0, 'x': 0},
                    'xl': {'minH': 3, 'minW': 3, 'h': 5, 'w': 8, 'y': 0, 'x': 0},
                    'lg': {'minH': 3, 'minW': 3, 'h': 5, 'w': 6, 'y': 0, 'x': 0},
                    'md': {'minH': 3, 'minW': 3, 'h': 5, 'w': 6, 'y': 0, 'x': 0},
                    'sm': {'minH': 3, 'minW': 3, 'h': 5, 'w': 12, 'y': 0, 'x': 0},
                },
            },
            {
                'type': 'terms',
                'scale': 'linear',
                'search_quantity': 'entry_type',
                'title': 'Entry Types',
                'layout': {
                    'xxl': {'minH': 3, 'minW': 3, 'h': 5, 'w': 8, 'y': 0, 'x': 8},
                    'xl': {'minH': 3, 'minW': 3, 'h': 5, 'w': 8, 'y': 0, 'x': 8},
                    'lg': {'minH': 3, 'minW': 3, 'h': 5, 'w': 6, 'y': 0, 'x': 6},
                    'md': {'minH': 3, 'minW': 3, 'h': 5, 'w': 6, 'y': 0, 'x': 6},
                    'sm': {'minH': 3, 'minW': 3, 'h': 5, 'w': 12, 'y': 5, 'x': 0},
                },
            },
            {
                'type': 'terms',
                'scale': 'linear',
                'search_quantity': (
                    'data.layer.layer_material_name#nomad_tfsc_general.schema_packages.tfsc_general_package.TFSC_General_SpinCoating'
                ),
                'title': 'SpinCoating',
                'layout': {
                    'xxl': {'minH': 3, 'minW': 3, 'h': 5, 'w': 8, 'y': 0, 'x': 16},
                    'xl': {'minH': 3, 'minW': 3, 'h': 5, 'w': 8, 'y': 0, 'x': 16},
                    'lg': {'minH': 3, 'minW': 3, 'h': 5, 'w': 12, 'y': 5, 'x': 0},
                    'md': {'minH': 3, 'minW': 3, 'h': 5, 'w': 12, 'y': 5, 'x': 0},
                    'sm': {'minH': 3, 'minW': 3, 'h': 5, 'w': 12, 'y': 10, 'x': 0},
                },
            },
        ]
    }
            
)