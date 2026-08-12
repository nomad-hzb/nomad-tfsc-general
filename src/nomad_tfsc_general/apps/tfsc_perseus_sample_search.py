from nomad.config.models.ui import (
    App,
    Column,
    Columns,
    Filters,
    Menu,
    MenuItemCustomQuantities,
    MenuItemDefinitions,
    MenuItemHistogram,
    MenuItemOptimade,
    MenuItemPeriodicTable,
    MenuItemTerms,
    MenuItemVisibility,
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
            f'data.batch_id#{schema}',
            f'data.subbatch_id#{schema}',
            f'data.suppliers#{schema}',
            'results.properties.optoelectronic.solar_cell.efficiency',
        ],
        options={
            'entry_type': Column(label='Entry type', align='left'),
            'entry_name': Column(label='Name', align='left'),
            'entry_create_time': Column(label='Entry time', align='left'),
            'authors': Column(label='Authors', align='left'),
            'upload_name': Column(label='Upload name', align='left'),
            f'data.batch_id#{schema}': Column(label='Batch', align='left'),
            f'data.subbatch_id#{schema}': Column(label='Subbatch', align='left'),
            f'data.suppliers#{schema}': Column(label='Suppliers', align='left'),
            f'data.supplier_materials#{schema}': Column(label='Supplier / material', align='left'),
            'results.properties.optoelectronic.solar_cell.efficiency': Column(label='PCE', align='left'),
            # 'data.lab_id#nomad_tfsc_general.schema_packages.tfsc_general_package': Column(
            #     label='Experiment ID', align='left'
            # ),
        },
    ),
    # Left-hand sidebar menu. Controls which filters are shown on the left.
    # Note: this replaces the older, now-deprecated `filter_menus` config -
    # the two cannot be combined, since NOMAD auto-converts any `filter_menus`
    # into `menu` and would otherwise silently discard our custom "Batch" item
    # below. The Material/Elements/User Defined Quantities/Visibility/Optimade
    # menus reproduce exactly what the old `filter_menus` config produced.
    menu=Menu(
        title='Filters',
        size='sm',
        items=[
            # Searchable/scrollable lists of batch and subbatch names
            # (data.batch_id / data.subbatch_id), so users can filter samples
            # down to a single batch or subbatch.
            Menu(
                title='Batch',
                items=[
                    MenuItemTerms(
                        search_quantity=f'data.batch_id#{schema}',
                        title='Batch',
                        show_input=True,
                        # Fetch many options up front so the list doesn't
                        # require repeated "show more" clicks. There's no
                        # "unlimited" setting, so this is a generously high
                        # cap rather than a true "all" - raise further if you
                        # have more distinct batches than this.
                        options=200,
                    ),
                    MenuItemTerms(
                        search_quantity=f'data.subbatch_id#{schema}',
                        title='Subbatch',
                        show_input=True,
                        options=200,
                    ),
                ],
            ),
            # Searchable/scrollable lists of material suppliers (data.suppliers)
            # and supplier/material pairs (data.supplier_materials), aggregated
            # from product_info.supplier across every process entry (layers,
            # solutions, solvents, additives, encapsulation, ...) that produced
            # this sample - so users can pick a supplier (optionally narrowed to
            # a specific material) and see which samples used it, together with
            # their PCE (see the results table). Note: the two filters are not
            # correlated - NOMAD doesn't yet support nested search for custom
            # schema quantities - so use "Supplier / material" for a specific
            # pairing (e.g. "Sigma-Aldrich — MAPbI3 (layer)").
            Menu(
                title='Suppliers',
                items=[
                    MenuItemTerms(
                        search_quantity=f'data.suppliers#{schema}',
                        show_input=True,
                        options=200,
                    ),
                    MenuItemTerms(
                        search_quantity=f'data.supplier_materials#{schema}',
                        title='Supplier / material',
                        show_input=True,
                        options=200,
                    ),
                ],
            ),
            Menu(title='Material', indentation=0, size='md'),
            Menu(
                title='Elements / Formula',
                indentation=1,
                size='xxl',
                items=[
                    MenuItemPeriodicTable(search_quantity='results.material.elements'),
                    MenuItemTerms(
                        search_quantity='results.material.chemical_formula_hill',
                        width=6,
                        options=0,
                    ),
                    MenuItemTerms(
                        search_quantity='results.material.chemical_formula_iupac',
                        width=6,
                        options=0,
                    ),
                    MenuItemTerms(
                        search_quantity='results.material.chemical_formula_reduced',
                        width=6,
                        options=0,
                    ),
                    MenuItemTerms(
                        search_quantity='results.material.chemical_formula_anonymous',
                        width=6,
                        options=0,
                    ),
                    MenuItemHistogram(x='results.material.n_elements'),
                ],
            ),
            Menu(
                title='User Defined Quantities',
                indentation=0,
                size='xl',
                items=[MenuItemCustomQuantities()],
            ),
            Menu(
                title='Visibility / IDs / Schema',
                indentation=0,
                size='md',
                items=[
                    MenuItemVisibility(),
                    MenuItemTerms(search_quantity='entry_id', options=0),
                    MenuItemTerms(search_quantity='upload_id', options=0),
                    MenuItemTerms(search_quantity='upload_name', options=0),
                    MenuItemTerms(search_quantity='results.material.material_id', options=0),
                    MenuItemTerms(search_quantity='datasets.dataset_id', options=0),
                    MenuItemDefinitions(),
                ],
            ),
            Menu(
                title='Optimade',
                indentation=0,
                size='lg',
                items=[MenuItemOptimade()],
            ),
        ],
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
