from pydantic import BaseModel

class CreateDoctor(BaseModel):
    fio: str
    specialization: str

class Doctor:
    def __init__(self, id: int, fio: str, specialization: str) -> None:
        self.id = id
        self.fio = fio
        self.specialization = specialization