from baseclasses.helper.solar_cell_batch_mapping import get_value, get_datetime

def get_product_values(df_sheet_two, product_id):
    for i, row in df_sheet_two.iterrows():
        if row["Product ID"] == product_id:
            return row

def map_product(i,j,lab_ids,data,upload_id, product_class):
    archive =product_class(
        name='Product/Material'
        + get_value(data, 'Product Name', None, False),
        product_id = get_value(data, 'Product ID', None, False),
        product_number = get_value(data, 'Product Number', None, False),
        lot_number = get_value(data, 'Lot Number', None, False),
        product_volume = get_value(data, 'Product Volume [ml]', None, unit= 'ml' ),
        product_weight = get_value(data, 'Product Weight [g]', None, unit = 'g'),
        shipping_date = get_datetime(data, 'Shipping Date'),
        opening_date = get_datetime(data, 'Opening Date'),
        supplier = get_value(data, 'Supplier', None, False),
        product_description = get_value(data, 'Product Description', None, False),
    )
    product_name = get_value(data, 'Product Name', None, False)
    return (f'{i}_{j}_supplier_product_{product_name}', archive)