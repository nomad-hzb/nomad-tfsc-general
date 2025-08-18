from nomad.config.models.ui import (  
    App,
    Column, 
    Dashboard,
    WidgetScatterPlot,
    WidgetTerms,
    Axis,
    Filters,
    FilterMenu,
    FilterMenus,
    Layout,
    Format,
    ModeEnum
)

schema = 'nomad_tfsc_general.schema_packages.tfsc_general_package.TFSC_General_Sample'

perseus_dashboard_app = App(
    label='PERSEUS Solar Cells Dashboard',
    path='PSC',
    category='Analytics Tools',
    description='Summary analytics of the Solar Cells uploaded for the PERSEUS project',
    readme='Summary analytics of the Solar Cells uploaded for the PERSEUS project',
    filters=Filters(
        include=[
            f'*#{schema}',
        ]
    ),
    filters_locked={'section_defs.definition_qualified_name': [schema]},
    filter_menus=FilterMenus(
        options={
            'material': FilterMenu(label='Material', level=0),
            'elements': FilterMenu(label='Elements / Formula', level=1, size='xl'),
            'eln': FilterMenu(label='Electronic Lab Notebook', level=0),
            'custom_quantities': FilterMenu(label='User Defined Quantities', level=0, size='l'),
            'author': FilterMenu(label='Author / Origin / Dataset', level=0, size='m'),
            'metadata': FilterMenu(label='Visibility / IDs / Schema', level=0),
        }
    ),
    columns=[
        Column(
            quantity='entry_name', 
            label='Entry Name', 
            align='left', 
            selected=True),
        Column(
            quantity='upload_name',
            label='Upload Name',
            align='left',
            selected=True,
        ),
        Column(
            quantity='authors',
            label='Authors',
            align='left',
            selected=True,
        ),
        Column(
            quantity='entry_create_time',
            label='Creation Date',
            align='left',
            selected=True,
            format=Format(mode=ModeEnum.DATE),
        )
    ],
    dashboard=Dashboard(
        widgets=[
            WidgetTerms(
                title='Sample Names',
                layout={
                    'lg': Layout(minH=3, minW=3, h=7, w=6, y=0, x=0),
                    'sm': Layout(minH=3, minW=3, h=7, w=6, y=0, x=0),
                },
                search_quantity=f'data.name#{schema}',
                showinput=True,
                scale='linear',
            ),
            WidgetTerms(
                title='Upload Names',
                layout={
                    'lg': Layout(minH=3, minW=3, h=7, w=6, y=0, x=6),
                    'sm': Layout(minH=3, minW=3, h=7, w=6, y=0, x=6),
                },
                search_quantity='upload_name',
                showinput=True,
                scale='linear',
            ),
            WidgetTerms(
                title='Authors',
                layout={
                    'lg': Layout(minH=3, minW=3, h=7, w=6, y=7, x=0),
                    'sm': Layout(minH=3, minW=3, h=7, w=6, y=7, x=0),
                },
                search_quantity='authors.name',
                showinput=True,
                scale='linear',
            )
        ]
    )
)


