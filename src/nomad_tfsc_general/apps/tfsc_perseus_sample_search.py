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

schema = 'nomad_tfsc_general.schema_packages.tfsc_general_package.TFSC_General_Sample'

perseus_sample_search_app = App(
    # Label of the App
    label='Find PERSEUS Samples',
    # Path used in the URL, must be unique
    path='perseus-find',
    # Used to categorize apps in the explore menu
    category='Solar Cell Data',
    # Brief description used in the app menu
    description='Provides filters to quickly find experiment entries.',
    # Longer description that can also use markdown
    readme='Provides filters to quickly find experiment entries.',
    # Controls the available search filters. If you want to filter by
    # quantities in a schema package, you need to load the schema package
    # explicitly here. Note that you can use a glob syntax to load the
    # entire package, or just a single schema from a package.
    search_quantities=SearchQuantities(include=[f'*#{schema}']),
    filters=Filters(
        include=[
            f'*#{schema}',
        ]
    ),
    filters_locked={'section_defs.definition_qualified_name': schema},
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
    # Dictionary of search filters that are always enabled for queries made
    # within this app. This is especially important to narrow down the
    # results to the wanted subset. Any available search filter can be
    # targeted here. This example makes sure that only entries that use
    # MySchema are included.
    # Controls the filter menus shown on the left
    filter_menus=FilterMenus(
        options={
            'material': FilterMenu(label='Material', level=0),
            'elements': FilterMenu(label='Elements / Formula', level=1, size='xl'),
            #'eln': FilterMenu(label='Electronic Lab Notebook', level=0),
            'custom_quantities': FilterMenu(label='User Defined Quantities', level=0, size='l'),
            #'author': FilterMenu(label='Author / Origin / Dataset', level=0, size='m'),
            'metadata': FilterMenu(label='Visibility / IDs / Schema', level=0),
            'optimade': FilterMenu(label='Optimade', level=0, size='m'),
        }
    ),
    # Controls the default dashboard shown in the search interface
    dashboard={
        'widgets': [
            # Row 1: Author and Entry Upload Date histograms
            {
                'type': 'terms',
                'showinput': True,
                'scale': 'linear',
                'search_quantity': 'authors.name',
                'layout': {
                    'xxl': {'minH': 3, 'minW': 3, 'h': 4, 'w': 8, 'y': 0, 'x': 0},
                    'xl': {'minH': 3, 'minW': 3, 'h': 4, 'w': 8, 'y': 0, 'x': 0},
                    'lg': {'minH': 3, 'minW': 3, 'h': 4, 'w': 6, 'y': 0, 'x': 0},
                    'md': {'minH': 3, 'minW': 3, 'h': 4, 'w': 12, 'y': 0, 'x': 0},
                    'sm': {'minH': 3, 'minW': 3, 'h': 4, 'w': 12, 'y': 0, 'x': 0},
                },
            },
            {
                'type': 'histogram',
                'showinput': True,
                'autorange': False,
                'nbins': 30,
                'y': {'scale': '1/4'},
                'x': {'search_quantity': 'entry_create_time', 'scale': 'linear'},
                'title': 'Entry Upload Date',
                'layout': {
                    'xxl': {'minH': 3, 'minW': 3, 'h': 4, 'w': 8, 'y': 0, 'x': 8},
                    'xl': {'minH': 3, 'minW': 3, 'h': 4, 'w': 8, 'y': 0, 'x': 8},
                    'lg': {'minH': 3, 'minW': 3, 'h': 4, 'w': 6, 'y': 0, 'x': 6},
                    'md': {'minH': 3, 'minW': 3, 'h': 4, 'w': 12, 'y': 4, 'x': 0},
                    'sm': {'minH': 3, 'minW': 3, 'h': 4, 'w': 12, 'y': 4, 'x': 0},
                },
            },
            {
                'type': 'histogram',
                'autorange': False,
                'nbins': 30,
                'y': {'scale': 'linear'},
                'x': {
                    'search_quantity': (
                        'data.datetime#nomad_tfsc_general.schema_packages.tfsc_general_package.'
                        'TFSC_General_Sample'
                    ),
                },
                'title': 'Sample Fabrication Date',
                'layout': {
                    'xxl': {'minH': 3, 'minW': 3, 'h': 4, 'w': 8, 'y': 0, 'x': 16},
                    'xl': {'minH': 3, 'minW': 3, 'h': 4, 'w': 8, 'y': 0, 'x': 16},
                    'lg': {'minH': 3, 'minW': 3, 'h': 4, 'w': 12, 'y': 4, 'x': 0},
                    'md': {'minH': 3, 'minW': 3, 'h': 4, 'w': 12, 'y': 8, 'x': 0},
                    'sm': {'minH': 3, 'minW': 3, 'h': 4, 'w': 12, 'y': 8, 'x': 0},
                },
            },
            # Row 2: Material properties terms widgets
            {
                'type': 'terms',
                'scale': 'linear',
                'search_quantity': 'results.properties.optoelectronic.solar_cell.substrate',
                'layout': {
                    'xxl': {'minH': 3, 'minW': 3, 'h': 5, 'w': 6, 'y': 4, 'x': 0},
                    'xl': {'minH': 3, 'minW': 3, 'h': 5, 'w': 6, 'y': 4, 'x': 0},
                    'lg': {'minH': 3, 'minW': 3, 'h': 5, 'w': 6, 'y': 8, 'x': 0},
                    'md': {'minH': 3, 'minW': 3, 'h': 5, 'w': 6, 'y': 12, 'x': 0},
                    'sm': {'minH': 3, 'minW': 3, 'h': 5, 'w': 12, 'y': 12, 'x': 0},
                },
            },
            {
                'type': 'terms',
                'scale': 'linear',
                'search_quantity': 'results.properties.optoelectronic.solar_cell.device_stack',
                'layout': {
                    'xxl': {'minH': 3, 'minW': 3, 'h': 5, 'w': 6, 'y': 4, 'x': 6},
                    'xl': {'minH': 3, 'minW': 3, 'h': 5, 'w': 6, 'y': 4, 'x': 6},
                    'lg': {'minH': 3, 'minW': 3, 'h': 5, 'w': 6, 'y': 8, 'x': 6},
                    'md': {'minH': 3, 'minW': 3, 'h': 5, 'w': 6, 'y': 12, 'x': 6},
                    'sm': {'minH': 3, 'minW': 3, 'h': 5, 'w': 12, 'y': 17, 'x': 0},
                },
            },
            {
                'type': 'terms',
                'scale': 'linear',
                'search_quantity': 'results.properties.optoelectronic.solar_cell.electron_transport_layer',
                'layout': {
                    'xxl': {'minH': 3, 'minW': 3, 'h': 5, 'w': 6, 'y': 4, 'x': 12},
                    'xl': {'minH': 3, 'minW': 3, 'h': 5, 'w': 6, 'y': 4, 'x': 12},
                    'lg': {'minH': 3, 'minW': 3, 'h': 5, 'w': 6, 'y': 13, 'x': 0},
                    'md': {'minH': 3, 'minW': 3, 'h': 5, 'w': 6, 'y': 17, 'x': 0},
                    'sm': {'minH': 3, 'minW': 3, 'h': 5, 'w': 12, 'y': 22, 'x': 0},
                },
            },
            {
                'type': 'terms',
                'scale': 'linear',
                'search_quantity': 'results.properties.optoelectronic.solar_cell.hole_transport_layer',
                'layout': {
                    'xxl': {'minH': 3, 'minW': 3, 'h': 5, 'w': 6, 'y': 4, 'x': 18},
                    'xl': {'minH': 3, 'minW': 3, 'h': 5, 'w': 6, 'y': 4, 'x': 18},
                    'lg': {'minH': 3, 'minW': 3, 'h': 5, 'w': 6, 'y': 13, 'x': 6},
                    'md': {'minH': 3, 'minW': 3, 'h': 5, 'w': 6, 'y': 17, 'x': 6},
                    'sm': {'minH': 3, 'minW': 3, 'h': 5, 'w': 12, 'y': 27, 'x': 0},
                },
            },
            # Row 3: Absorber-related terms widgets
            {
                'type': 'terms',
                'scale': 'linear',
                'search_quantity': 'results.properties.optoelectronic.solar_cell.absorber',
                'layout': {
                    'xxl': {'minH': 3, 'minW': 3, 'h': 5, 'w': 12, 'y': 9, 'x': 0},
                    'xl': {'minH': 3, 'minW': 3, 'h': 5, 'w': 12, 'y': 9, 'x': 0},
                    'lg': {'minH': 3, 'minW': 3, 'h': 5, 'w': 12, 'y': 18, 'x': 0},
                    'md': {'minH': 3, 'minW': 3, 'h': 5, 'w': 12, 'y': 22, 'x': 0},
                    'sm': {'minH': 3, 'minW': 3, 'h': 5, 'w': 12, 'y': 32, 'x': 0},
                },
            },
            {
                'type': 'terms',
                'scale': 'linear',
                'search_quantity': 'results.properties.optoelectronic.solar_cell.absorber_fabrication',
                'layout': {
                    'xxl': {'minH': 3, 'minW': 3, 'h': 5, 'w': 12, 'y': 9, 'x': 12},
                    'xl': {'minH': 3, 'minW': 3, 'h': 5, 'w': 12, 'y': 9, 'x': 12},
                    'lg': {'minH': 3, 'minW': 3, 'h': 5, 'w': 12, 'y': 23, 'x': 0},
                    'md': {'minH': 3, 'minW': 3, 'h': 5, 'w': 12, 'y': 27, 'x': 0},
                    'sm': {'minH': 3, 'minW': 3, 'h': 5, 'w': 12, 'y': 37, 'x': 0},
                },
            },
            # Row 4: Performance scatter plots
            {
                'type': 'scatter_plot',
                'autorange': True,
                'size': 1000,
                'y': {
                    'search_quantity': 'results.properties.optoelectronic.solar_cell.efficiency',
                    'title': 'Efficiency (%)',
                },
                'x': {
                    'search_quantity': 'results.properties.optoelectronic.solar_cell.open_circuit_voltage',
                    'title': 'Open Circuit Voltage (Voc)',
                    'unit': 'volt',
                },
                'title': 'PCE vs Open Circuit Voltage',
                'layout': {
                    'xxl': {'minH': 4, 'minW': 4, 'h': 8, 'w': 12, 'y': 14, 'x': 0},
                    'xl': {'minH': 4, 'minW': 4, 'h': 8, 'w': 12, 'y': 14, 'x': 0},
                    'lg': {'minH': 4, 'minW': 4, 'h': 8, 'w': 12, 'y': 28, 'x': 0},
                    'md': {'minH': 4, 'minW': 4, 'h': 8, 'w': 12, 'y': 32, 'x': 0},
                    'sm': {'minH': 4, 'minW': 4, 'h': 8, 'w': 12, 'y': 42, 'x': 0},
                },
                'markers': {
                    'color': {
                        'quantity': (
                            'results.properties.optoelectronic.solar_cell.short_circuit_current_density'
                        ),
                        'unit': 'mA/cm^2',
                    },
                },
            },
            {
                'type': 'scatter_plot',
                'autorange': True,
                'size': 1000,
                'y': {
                    'search_quantity': 'results.properties.optoelectronic.solar_cell.efficiency',
                    'title': 'Efficiency (%)',
                },
                'x': {
                    'search_quantity': 'results.properties.optoelectronic.solar_cell.device_area',
                    'title': 'Device Area',
                    'unit': 'mm^2',
                },
                'title': 'PCE vs Device Area (by Fabrication)',
                'layout': {
                    'xxl': {'minH': 4, 'minW': 4, 'h': 8, 'w': 12, 'y': 14, 'x': 12},
                    'xl': {'minH': 4, 'minW': 4, 'h': 8, 'w': 12, 'y': 14, 'x': 12},
                    'lg': {'minH': 4, 'minW': 4, 'h': 8, 'w': 12, 'y': 36, 'x': 0},
                    'md': {'minH': 4, 'minW': 4, 'h': 8, 'w': 12, 'y': 40, 'x': 0},
                    'sm': {'minH': 4, 'minW': 4, 'h': 8, 'w': 12, 'y': 50, 'x': 0},
                },
                'markers': {
                    'color': {
                        'quantity': 'results.properties.optoelectronic.solar_cell.absorber_fabrication',
                    },
                },
            },
            {
                'type': 'scatter_plot',
                'autorange': True,
                'size': 1000,
                'y': {
                    'search_quantity': 'results.properties.optoelectronic.solar_cell.efficiency',
                    'title': 'Efficiency (%)',
                },
                'x': {
                    'search_quantity': 'results.properties.optoelectronic.solar_cell.device_area',
                    'title': 'Device Area',
                    'unit': 'mm^2',
                },
                'title': 'PCE vs Device Area (by Absorber)',
                'layout': {
                    'xxl': {'minH': 4, 'minW': 4, 'h': 8, 'w': 24, 'y': 22, 'x': 0},
                    'xl': {'minH': 4, 'minW': 4, 'h': 8, 'w': 24, 'y': 22, 'x': 0},
                    'lg': {'minH': 4, 'minW': 4, 'h': 8, 'w': 12, 'y': 44, 'x': 0},
                    'md': {'minH': 4, 'minW': 4, 'h': 8, 'w': 12, 'y': 48, 'x': 0},
                    'sm': {'minH': 4, 'minW': 4, 'h': 8, 'w': 12, 'y': 58, 'x': 0},
                },
                'markers': {
                    'color': {
                        'quantity': 'results.properties.optoelectronic.solar_cell.absorber',
                    },
                },
            },
        ]
    },
)
