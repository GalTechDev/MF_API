from requests import Response

def csv_to_MClass(csv: str|list, sep=";"):
    if isinstance(csv, str):
        csv = csv.split("\n")
    keys =  csv[0].split(sep)
    return [MClass({keys[i]:line.split(sep)[i] for i in range(len(keys))}) for line in csv[1:] if line]

def response_to_MClass(response: Response):
    #response.headers.
    return 

class MClass(dict):
    """
    Universal wrapper for any kind of dict item
    if the data structure change I won't have to do
    massive change in the code
    """
    def __init__(self, dico: dict):

        for k, v in dico.items():
            self.__setitem__(k, v)

    def __setattr__(self, k, v):
        super().__setitem__(k, MObject(v))

    def __getattr__(self, k):
        return super().__getattr__(k)
        
    def __setitem__(self, k, v):
        super().__setitem__(k, MObject(v))

def MObject(data: dict|list|MClass|Response) -> MClass:
    if isinstance(data, list):
        return [MObject(v) for v in data]

    elif isinstance(data, dict):
        return MClass(data)

    
    elif isinstance(data, MClass):
        return data

    elif isinstance(data, Response):
        return response_to_MClass(data)
    
    return data
    