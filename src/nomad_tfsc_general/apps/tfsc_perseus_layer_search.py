from nomad.config.models.ui import (
    App,
    Column,
    Columns,
    FilterMenu,
    FilterMenus,
    Filters,
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
    readme='''
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
    ''',
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

    # Enhanced filter menus for better navigation
    filter_menus=FilterMenus(
        options={
            'material': FilterMenu(label='Layer Materials', level=0, size='xl'),
            'solarcell': FilterMenu(label='Solar Cell Performance', level=0, size='l'),
            'fabrication': FilterMenu(label='Fabrication Process', level=0, size='l'),
            'eln': FilterMenu(label='Electronic Lab Notebook', level=0),
            'custom_quantities': FilterMenu(label='User Defined Quantities', level=0, size='l'),
            'author': FilterMenu(label='Author / Origin / Dataset', level=0, size='m'),
            'metadata': FilterMenu(label='Visibility / IDs / Schema', level=0),
        }
    ),

    dashboard= {
        'widgets': [
            # Row 1: Performance overview - Solar cell key metrics
            {
                'type': 'scatterplot',
                'autorange': True,
                'size': 1000,
                'markers': {
                    'color': {
                        'quantity': 'entry_type',
                    }
                },
                'x': {
                    'quantity': 'results.properties.optoelectronic.solar_cell.open_circuit_voltage',
                    'title': 'Open Circuit Voltage (V)'
                },
                'y': {
                    'quantity': 'results.properties.optoelectronic.solar_cell.efficiency',
                    'title': 'Efficiency (%)'
                },
                'layout': {
                    'xxl': {'minH': 6, 'minW': 6, 'h': 8, 'w': 12, 'y': 0, 'x': 0},
                    'xl': {'minH': 6, 'minW': 6, 'h': 8, 'w': 12, 'y': 0, 'x': 0},
                    'lg': {'minH': 6, 'minW': 6, 'h': 8, 'w': 12, 'y': 0, 'x': 0},
                    'md': {'minH': 6, 'minW': 6, 'h': 8, 'w': 12, 'y': 0, 'x': 0},
                    'sm': {'minH': 6, 'minW': 6, 'h': 8, 'w': 12, 'y': 0, 'x': 0},
                },
            },

            # Row 1: Efficiency histogram
            {
                'type': 'histogram',
                'autorange': True,
                'nbins': 30,
                'x': {
                    'quantity': 'results.properties.optoelectronic.solar_cell.efficiency',
                    'title': 'Efficiency (%)'
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
                    'title': 'Fill Factor'
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

            # Row 3: Layer material comparison for spin coating
            {
                'type': 'terms',
                'scale': 'linear',
                'search_quantity': (
                    'data.layer.layer_material_name#nomad_tfsc_general.schema_packages.tfsc_general_package.TFSC_General_SpinCoating'
                ),
                'title': 'Spin Coating Materials',
                'showinput': True,
                'layout': {
                    'xxl': {'minH': 3, 'minW': 3, 'h': 5, 'w': 6, 'y': 14, 'x': 0},
                    'xl': {'minH': 3, 'minW': 3, 'h': 5, 'w': 6, 'y': 14, 'x': 0},
                    'lg': {'minH': 3, 'minW': 3, 'h': 5, 'w': 6, 'y': 18, 'x': 0},
                    'md': {'minH': 3, 'minW': 3, 'h': 5, 'w': 6, 'y': 18, 'x': 0},
                    'sm': {'minH': 3, 'minW': 3, 'h': 5, 'w': 12, 'y': 28, 'x': 0},
                },
            },

            # Row 3: Evaporation materials
            {
                'type': 'terms',
                'scale': 'linear',
                'search_quantity': (
                    'data.layer.layer_material_name#nomad_tfsc_general.schema_packages.tfsc_general_package.TFSC_General_Evaporation'
                ),
                'title': 'Evaporation Materials',
                'showinput': True,
                'layout': {
                    'xxl': {'minH': 3, 'minW': 3, 'h': 5, 'w': 6, 'y': 14, 'x': 6},
                    'xl': {'minH': 3, 'minW': 3, 'h': 5, 'w': 6, 'y': 14, 'x': 6},
                    'lg': {'minH': 3, 'minW': 3, 'h': 5, 'w': 6, 'y': 18, 'x': 6},
                    'md': {'minH': 3, 'minW': 3, 'h': 5, 'w': 6, 'y': 18, 'x': 6},
                    'sm': {'minH': 3, 'minW': 3, 'h': 5, 'w': 12, 'y': 33, 'x': 0},
                },
            },

            # Row 3: Sputtering materials
            {
                'type': 'terms',
                'scale': 'linear',
                'search_quantity': (
                    'data.layer.layer_material_name#nomad_tfsc_general.schema_packages.tfsc_general_package.TFSC_General_Sputtering'
                ),
                'title': 'Sputtering Materials',
                'showinput': True,
                'layout': {
                    'xxl': {'minH': 3, 'minW': 3, 'h': 5, 'w': 6, 'y': 14, 'x': 12},
                    'xl': {'minH': 3, 'minW': 3, 'h': 5, 'w': 6, 'y': 14, 'x': 12},
                    'lg': {'minH': 3, 'minW': 3, 'h': 5, 'w': 6, 'y': 23, 'x': 0},
                    'md': {'minH': 3, 'minW': 3, 'h': 5, 'w': 6, 'y': 23, 'x': 0},
                    'sm': {'minH': 3, 'minW': 3, 'h': 5, 'w': 12, 'y': 38, 'x': 0},
                },
            },

            # Row 4: Sample correlation analysis
            {
                'type': 'scatterplot',
                'autorange': True,
                'size': 800,
                'markers': {
                    'color': {
                        'search_quantity': (
                            'data.layer.layer_material_name#nomad_tfsc_general.schema_packages.tfsc_general_package.TFSC_General_SpinCoating'
                        ),
                    }
                },
                'x': {
                    'quantity': 'results.properties.optoelectronic.solar_cell.short_circuit_current_density',
                    'title': 'Short Circuit Current Density (mA/cm²)'
                },
                'y': {
                    'quantity': 'results.properties.optoelectronic.solar_cell.efficiency',
                    'title': 'Efficiency (%)'
                },
                'layout': {
                    'xxl': {'minH': 6, 'minW': 6, 'h': 6, 'w': 9, 'y': 19, 'x': 0},
                    'xl': {'minH': 6, 'minW': 6, 'h': 6, 'w': 9, 'y': 19, 'x': 0},
                    'lg': {'minH': 6, 'minW': 6, 'h': 6, 'w': 6, 'y': 23, 'x': 6},
                    'md': {'minH': 6, 'minW': 6, 'h': 6, 'w': 6, 'y': 23, 'x': 6},
                    'sm': {'minH': 6, 'minW': 6, 'h': 6, 'w': 12, 'y': 43, 'x': 0},
                },
            },

            # Row 4: Process statistics - Gravure and Slot Die materials
            {
                'type': 'terms',
                'scale': 'linear',
                'search_quantity': (
                    'data.layer.layer_material_name#nomad_tfsc_general.schema_packages.tfsc_general_package.TFSC_General_GravurePrinting'
                ),
                'title': 'Gravure Printing Materials',
                'showinput': True,
                'layout': {
                    'xxl': {'minH': 3, 'minW': 3, 'h': 6, 'w': 9, 'y': 19, 'x': 9},
                    'xl': {'minH': 3, 'minW': 3, 'h': 6, 'w': 9, 'y': 19, 'x': 9},
                    'lg': {'minH': 3, 'minW': 3, 'h': 6, 'w': 6, 'y': 28, 'x': 0},
                    'md': {'minH': 3, 'minW': 3, 'h': 6, 'w': 6, 'y': 28, 'x': 0},
                    'sm': {'minH': 3, 'minW': 3, 'h': 6, 'w': 12, 'y': 49, 'x': 0},
                },
            },

            # Row 5: Additional process techniques overview
            {
                'type': 'terms',
                'scale': 'linear',
                'search_quantity': (
                    'data.layer.layer_material_name#nomad_tfsc_general.schema_packages.tfsc_general_package.TFSC_General_SlotDieCoating'
                ),
                'title': 'Slot Die Coating Materials',
                'showinput': True,
                'layout': {
                    'xxl': {'minH': 3, 'minW': 3, 'h': 4, 'w': 6, 'y': 25, 'x': 0},
                    'xl': {'minH': 3, 'minW': 3, 'h': 4, 'w': 6, 'y': 25, 'x': 0},
                    'lg': {'minH': 3, 'minW': 3, 'h': 4, 'w': 6, 'y': 29, 'x': 0},
                    'md': {'minH': 3, 'minW': 3, 'h': 4, 'w': 6, 'y': 29, 'x': 0},
                    'sm': {'minH': 3, 'minW': 3, 'h': 4, 'w': 6, 'y': 55, 'x': 0},
                },
            },

            {
                'type': 'terms',
                'scale': 'linear',
                'search_quantity': (
                    'data.layer.layer_material_name#nomad_tfsc_general.schema_packages.tfsc_general_package.TFSC_General_AtomicLayerDeposition'
                ),
                'title': 'ALD Materials',
                'showinput': True,
                'layout': {
                    'xxl': {'minH': 3, 'minW': 3, 'h': 4, 'w': 6, 'y': 25, 'x': 6},
                    'xl': {'minH': 3, 'minW': 3, 'h': 4, 'w': 6, 'y': 25, 'x': 6},
                    'lg': {'minH': 3, 'minW': 3, 'h': 4, 'w': 6, 'y': 29, 'x': 6},
                    'md': {'minH': 3, 'minW': 3, 'h': 4, 'w': 6, 'y': 29, 'x': 6},
                    'sm': {'minH': 3, 'minW': 3, 'h': 4, 'w': 6, 'y': 55, 'x': 6},
                },
            },

            {
                'type': 'terms',
                'scale': 'linear',
                'search_quantity': (
                    'data.layer.layer_material_name#nomad_tfsc_general.schema_packages.tfsc_general_package.TFSC_General_BladeCoating'
                ),
                'title': 'Blade Coating Materials',
                'showinput': True,
                'layout': {
                    'xxl': {'minH': 3, 'minW': 3, 'h': 4, 'w': 6, 'y': 25, 'x': 6},
                    'xl': {'minH': 3, 'minW': 3, 'h': 4, 'w': 6, 'y': 25, 'x': 6},
                    'lg': {'minH': 3, 'minW': 3, 'h': 4, 'w': 6, 'y': 33, 'x': 0},
                    'md': {'minH': 3, 'minW': 3, 'h': 4, 'w': 6, 'y': 33, 'x': 0},
                    'sm': {'minH': 3, 'minW': 3, 'h': 4, 'w': 6, 'y': 55, 'x': 6},
                },
            },

            {
                'type': 'terms',
                'scale': 'linear',
                'search_quantity': (
                    'data.layer.layer_material_name#nomad_tfsc_general.schema_packages.tfsc_general_package.TFSC_General_ScreenPrinting'
                ),
                'title': 'Screen Printing Materials',
                'showinput': True,
                'layout': {
                    'xxl': {'minH': 3, 'minW': 3, 'h': 4, 'w': 6, 'y': 25, 'x': 12},
                    'xl': {'minH': 3, 'minW': 3, 'h': 4, 'w': 6, 'y': 25, 'x': 12},
                    'lg': {'minH': 3, 'minW': 3, 'h': 4, 'w': 6, 'y': 33, 'x': 6},
                    'md': {'minH': 3, 'minW': 3, 'h': 4, 'w': 6, 'y': 33, 'x': 6},
                    'sm': {'minH': 3, 'minW': 3, 'h': 4, 'w': 6, 'y': 59, 'x': 0},
                },
            },
        ]
    }
            
)