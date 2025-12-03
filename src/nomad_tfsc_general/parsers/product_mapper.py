# def get_product_values(df_sheet_two, chemical_id):
#     for i, row in df_sheet_two.iterrows():
#         if row["Chemical ID"] == chemical_id:
#             return row


def get_product_values(df_sheet_two, chemical_id):
    """
    Get product data from the second sheet based on chemical ID.

    Returns a pandas Series with column names as index if found, None otherwise.
    """
    matched_rows = df_sheet_two[df_sheet_two['Chemical ID'] == chemical_id]

    if not matched_rows.empty:
        return matched_rows.iloc[0]  # Return first match as Series
    return None
