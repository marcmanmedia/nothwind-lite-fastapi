from pydantic import BaseModel
from decimal import Decimal

class EmployeeSales(BaseModel):
    employee_id: int
    employee_name: str
    total_sales: Decimal

class EmployeeSalesResponse(BaseModel):
    data: list[EmployeeSales]