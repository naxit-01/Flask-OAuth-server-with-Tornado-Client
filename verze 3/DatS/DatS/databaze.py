database=[]
my_request_token="NoN"
database.append(my_request_token)


def write_my_request_token(data):   
    database[0]=data

def read_my_request_token():
    return database[0]