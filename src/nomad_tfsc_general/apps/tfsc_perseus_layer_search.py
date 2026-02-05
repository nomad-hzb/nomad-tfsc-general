from nomad.config.models.ui import (
    App,
    Axis,
    Column,
    Columns,
    Filters,
    Menu,
    MenuItemHistogram,
    MenuItemTerms,
    Pagination,
)

perseus_layer_search_app = App(
    # Label of the App
    label='Find PERSEUS Sample Layers',
    # Path used in the URL, must be unique
    path='perseus-find-layer',
    # Used to categorize apps in the explore menu
    category='Solar Cell Data',
    # Brief description used in the app menu
    description='Advanced search for layer fabrication processes with comprehensive filters.',
    # Longer description that can also use markdown
    readme="""
    ## PERSEUS Layer Search
    
    This application provides advanced search capabilities for thin-film solar cell 
    layer fabrication processes. Use the dashboard to explore:
    
    - **Layer Materials**: Different materials used in each fabrication process
    - **Sample Processing**: Distribution of samples across techniques
    - **Performance Metrics**: Solar cell efficiency and other key parameters
    - **Process Parameters**: Detailed fabrication conditions and settings
    
    The search includes multiple deposition techniques: SpinCoating, AtomicLayerDeposition, 
    BladeCoating, Evaporation, GravurePrinting, InkjetPrinting, ScreenPrinting, 
    SlotDieCoating, and Sputtering.
    """,
    # Controls the available search filters. If you want to filter by
    # quantities in a schema package, you need to load the schema package
    # explicitly here. Note that you can use a glob syntax to load the
    # entire package, or just a single schema from a package.
    filters=Filters(
        include=[
            '*#nomad_tfsc_general.schema_packages.tfsc_general_package.*',
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
            'results.properties.optoelectronic.solar_cell.open_circuit_voltage',
            'results.properties.optoelectronic.solar_cell.short_circuit_current_density',
            'results.properties.optoelectronic.solar_cell.fill_factor',
        ],
        options={
            'entry_type': Column(label='Process Type', align='left'),
            'entry_name': Column(label='Process Name', align='left'),
            'entry_create_time': Column(label='Entry Date', align='left'),
            'authors': Column(label='Authors', align='left'),
            'upload_name': Column(label='Upload', align='left'),
            'results.properties.optoelectronic.solar_cell.efficiency': Column(
                label='Efficiency (%)', align='left', format={'decimals': 2, 'mode': 'standard'}
            ),
            'results.properties.optoelectronic.solar_cell.open_circuit_voltage': Column(
                label='Voc (V)', align='left', format={'decimals': 3, 'mode': 'standard'}
            ),
            'results.properties.optoelectronic.solar_cell.short_circuit_current_density': Column(
                label='Jsc (mA/cm²)', align='left', format={'decimals': 2, 'mode': 'standard'}
            ),
            'results.properties.optoelectronic.solar_cell.fill_factor': Column(
                label='Fill Factor', align='left', format={'decimals': 3, 'mode': 'standard'}
            ),
        },
    ),
    # Enhanced menu with histogram examples for TFSC processes
    menu=Menu(
        title='TFSC Layer Search Filters',
        items=[
            # Solar Cell Performance Histograms
            MenuItemHistogram(
                x=Axis(
                    quantity='results.properties.optoelectronic.solar_cell.open_circuit_voltage',
                    title='Open Circuit Voltage (V)',
                ),
                title='Voc Distribution',
                nbins=25,
            ),
            MenuItemHistogram(
                x=Axis(
                    quantity='results.properties.optoelectronic.solar_cell.short_circuit_current_density',
                    title='Short Circuit Current Density (mA/cm²)',
                ),
                title='Jsc Distribution',
                nbins=25,
            ),
            # Material Terms Filters
            MenuItemTerms(
                quantity='data.layer.layer_material_name#nomad_tfsc_general.schema_packages.tfsc_general_package.TFSC_General_SpinCoating',
                title='Spin Coating Materials',
                show_input=True,
            ),
            MenuItemTerms(
                quantity='data.layer.layer_material_name#nomad_tfsc_general.schema_packages.tfsc_general_package.TFSC_General_GravurePrinting',
                title='Gravure Printing Materials',
                show_input=True,
            ),
            MenuItemTerms(
                quantity='data.layer.layer_material_name#nomad_tfsc_general.schema_packages.tfsc_general_package.TFSC_General_SlotDieCoating',
                title='Slot Die Coating Materials',
                show_input=True,
            ),
            MenuItemTerms(
                quantity='data.layer.layer_material_name#nomad_tfsc_general.schema_packages.tfsc_general_package.TFSC_General_BladeCoating',
                title='Blade Coating Materials',
                show_input=True,
            ),
            MenuItemTerms(
                quantity='data.layer.layer_material_name#nomad_tfsc_general.schema_packages.tfsc_general_package.TFSC_General_ScreenPrinting',
                title='Screen Printing Materials',
                show_input=True,
            ),
            MenuItemTerms(
                quantity='data.layer.layer_material_name#nomad_tfsc_general.schema_packages.tfsc_general_package.TFSC_General_AtomicLayerDeposition',
                title='ALD Materials',
                show_input=True,
            ),
            MenuItemTerms(
                quantity='data.layer.layer_material_name#nomad_tfsc_general.schema_packages.tfsc_general_package.TFSC_General_Evaporation',
                title='Evaporation Materials',
                show_input=True,
            ),
            MenuItemTerms(
                quantity='data.layer.layer_material_name#nomad_tfsc_general.schema_packages.tfsc_general_package.TFSC_General_Sputtering',
                title='Sputtering Materials',
                show_input=True,
            ),
        ],
    ),
    dashboard={
        'widgets': [
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
                    'xxl': {'minH': 6, 'minW': 6, 'h': 8, 'w': 12, 'y': 0, 'x': 0},
                    'xl': {'minH': 6, 'minW': 6, 'h': 8, 'w': 12, 'y': 0, 'x': 0},
                    'lg': {'minH': 6, 'minW': 6, 'h': 8, 'w': 12, 'y': 0, 'x': 0},
                    'md': {'minH': 6, 'minW': 6, 'h': 8, 'w': 12, 'y': 0, 'x': 0},
                    'sm': {'minH': 6, 'minW': 6, 'h': 8, 'w': 12, 'y': 0, 'x': 0},
                },
                'markers': {
                    'color': {
                        'quantity': 'results.properties.optoelectronic.solar_cell.absorber_fabrication',
                    },
                },
            },
            # Row 1: Efficiency histogram
            {
                'type': 'histogram',
                'autorange': True,
                'nbins': 30,
                'x': {
                    'quantity': 'results.properties.optoelectronic.solar_cell.efficiency',
                    'title': 'Efficiency (%)',
                },
                'layout': {
                    'xxl': {'minH': 3, 'minW': 3, 'h': 4, 'w': 6, 'y': 0, 'x': 12},
                    'xl': {'minH': 3, 'minW': 3, 'h': 4, 'w': 6, 'y': 0, 'x': 12},
                    'lg': {'minH': 3, 'minW': 3, 'h': 4, 'w': 6, 'y': 8, 'x': 0},
                    'md': {'minH': 3, 'minW': 3, 'h': 4, 'w': 6, 'y': 8, 'x': 0},
                    'sm': {'minH': 3, 'minW': 3, 'h': 4, 'w': 12, 'y': 8, 'x': 0},
                },
            },
            # Row 1: Fill factor histogram
            {
                'type': 'histogram',
                'autorange': True,
                'nbins': 30,
                'x': {
                    'quantity': 'results.properties.optoelectronic.solar_cell.fill_factor',
                    'title': 'Fill Factor',
                },
                'layout': {
                    'xxl': {'minH': 3, 'minW': 3, 'h': 4, 'w': 6, 'y': 4, 'x': 12},
                    'xl': {'minH': 3, 'minW': 3, 'h': 4, 'w': 6, 'y': 4, 'x': 12},
                    'lg': {'minH': 3, 'minW': 3, 'h': 4, 'w': 6, 'y': 8, 'x': 6},
                    'md': {'minH': 3, 'minW': 3, 'h': 4, 'w': 6, 'y': 8, 'x': 6},
                    'sm': {'minH': 3, 'minW': 3, 'h': 4, 'w': 12, 'y': 12, 'x': 0},
                },
            },
            # Row 2: Process overview
            {
                'type': 'terms',
                'scale': 'linear',
                'search_quantity': 'entry_type',
                'title': 'Fabrication Processes',
                'showinput': True,
                'layout': {
                    'xxl': {'minH': 3, 'minW': 3, 'h': 6, 'w': 9, 'y': 8, 'x': 0},
                    'xl': {'minH': 3, 'minW': 3, 'h': 6, 'w': 9, 'y': 8, 'x': 0},
                    'lg': {'minH': 3, 'minW': 3, 'h': 6, 'w': 6, 'y': 12, 'x': 0},
                    'md': {'minH': 3, 'minW': 3, 'h': 6, 'w': 6, 'y': 12, 'x': 0},
                    'sm': {'minH': 3, 'minW': 3, 'h': 6, 'w': 12, 'y': 16, 'x': 0},
                },
            },
            # Row 2: Author statistics
            {
                'type': 'terms',
                'scale': 'linear',
                'search_quantity': 'authors.name',
                'title': 'Research Groups',
                'showinput': True,
                'layout': {
                    'xxl': {'minH': 3, 'minW': 3, 'h': 6, 'w': 9, 'y': 8, 'x': 9},
                    'xl': {'minH': 3, 'minW': 3, 'h': 6, 'w': 9, 'y': 8, 'x': 9},
                    'lg': {'minH': 3, 'minW': 3, 'h': 6, 'w': 6, 'y': 12, 'x': 6},
                    'md': {'minH': 3, 'minW': 3, 'h': 6, 'w': 6, 'y': 12, 'x': 6},
                    'sm': {'minH': 3, 'minW': 3, 'h': 6, 'w': 12, 'y': 22, 'x': 0},
                },
            },
        ]
    },
)
