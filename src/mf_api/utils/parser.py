from requests import Response

def csv_to_MClass(csv: str|list, sep=";"):
    if isinstance(csv, str):
        csv = csv.split("\n")
    keys =  csv[0].split(sep)
    return [MClass({keys[i].strip("\r"):line.split(sep)[i].strip("\r") for i in range(len(keys))}) for line in csv[1:] if line]

def response_to_MClass(response: Response):
    content_type = response.headers.get("Content-Type")
    if "text/csv" in content_type:
        return csv_to_MClass(response.text)
    elif "application/json" in content_type:
        return MObject(response.json())
     
class APIResponse(Response):
    def __init__(self, response: Response):
        super().__init__()
        self.__dict__.update(response.__dict__)

    def to_MClass(self):
        return response_to_MClass(self)

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
        if k in super():
            return super().__getitem__(k)
        else:
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
    