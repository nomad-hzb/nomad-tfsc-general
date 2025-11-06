from baseclasses import PubChemPureSubstanceSectionCustom
from baseclasses.helper.solar_cell_batch_mapping import get_datetime, get_value


def get_product_values(df_sheet_two, product_id):
    for i, row in df_sheet_two.iterrows():
        if row["Product ID"] == product_id:
            return row

def map_product(i, j, lab_ids, data, upload_id, product_class):
    product_id_value = get_value(data, 'Product ID', None, False)
    product_name_value = get_value(data, 'Product Name', None, False)
    
    archive = product_class(
        name='Product/Material ' + (product_name_value if product_name_value else ''),
        product_name=PubChemPureSubstanceSectionCustom(
            name=product_name_value,
            load_data=False
        ) if product_name_value else None,
        product_id=product_id_value,
        product_number=get_value(data, 'Product Number', None, False),
        lot_number=get_value(data, 'Lot Number', None, False),
        product_volume=get_value(data, 'Product Volume [ml]', None, unit='ml'),
        product_weight=get_value(data, 'Product Weight [g]', None, unit='g'),
        shipping_date=get_datetime(data, 'Shipping Date'),
        opening_date=get_datetime(data, 'Opening Date'),
        supplier=get_value(data, 'Supplier', None, False),
        product_description=get_value(data, 'Product Description', None, False),
    )
    return (f'{i}_{j}_supplier_product_{product_name_value}', archive)