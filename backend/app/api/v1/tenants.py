from typing import List
from fastapi import APIRouter, HTTPException
from ...models.tenant import (
    Department,
    DepartmentTransferRequest,
    DepartmentTransferResult,
    TenantSummary,
)
from ...services.tenant_service import tenant_service

router = APIRouter(prefix="/tenants", tags=["Multi-Tenant Department Hierarchy"])


@router.get("/departments", response_model=List[Department])
async def list_departments():
    return tenant_service.list_departments()


@router.get("/departments/{dept_id}", response_model=Department)
async def get_department(dept_id: str):
    dept = tenant_service.get_department(dept_id)
    if not dept:
        raise HTTPException(status_code=404, detail="Department not found")
    return dept


@router.get("/summary", response_model=TenantSummary)
async def get_tenant_summary():
    return tenant_service.get_summary()


@router.post("/transfer", response_model=DepartmentTransferResult)
async def transfer_budget(request: DepartmentTransferRequest):
    try:
        return tenant_service.transfer_budget(request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
