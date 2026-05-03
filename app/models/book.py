from odmantic import  Model
from pydantic import ConfigDict

class BookModel(Model):
    
    keyword: str
    publisher: str
    price:int
    image:str

    model_config = ConfigDict(collection="books")
