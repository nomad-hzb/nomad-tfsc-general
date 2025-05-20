from datetime import datetime

def get_datetime(data):
    # this takes only the first element of the list, have to adapt for assigning to each sample and batch
    if isinstance(data, list) and data:
        data = data[0]
    
    # Now parse the string
    datetime_object = datetime.strptime(data, '%d-%m-%Y')
    datetime_nomad = datetime_object.strftime('%Y-%m-%d %H:%M:%S.%f')
    return datetime_nomad