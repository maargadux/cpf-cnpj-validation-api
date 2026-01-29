from pydantic import BaseModel, Field

class ValidationResponse(BaseModel):
    type: str = Field(examples=["CPF", "CNPJ", "UNKNOWN"])
    input: str = Field(examples=["12345678909"])
    formatted: str = Field(examples=["123.456.789-09"])
    valid: bool = Field(examples=[True])
    message: str = Field(examples=["CPF válido"])

