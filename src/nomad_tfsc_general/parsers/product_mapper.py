def get_product_values(df_sheet_two, chemical_id):
    for i, row in df_sheet_two.iterrows():
        if row["Chemical ID"] == chemical_id:
            return row