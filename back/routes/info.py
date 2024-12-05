from fastapi import APIRouter
from controller.info import BasicInfoController
from utils.task_queue import task_queue, connected_workers

router = APIRouter(prefix="", tags=["Info"])
BasicInfoService = None

@router.get("/health")
async def health_check():
    return await BasicInfoService.health_check(task_queue, connected_workers)

@router.get("/status")
async def service_status():
    return await BasicInfoService.service_status(task_queue, connected_workers)

@router.get("/status/{task_id}")
async def get_status(task_id: str):
    return await BasicInfoService.get_task_status(task_queue, task_id)
