from typing import Dict
from fastapi import APIRouter, WebSocket
from controller.info import BasicInfoController
from utils.task_queue import TaskQueue

router = APIRouter(prefix="", tags=["Info"])
BasicInfoService = None

design_history: list = []

# Connected workers
connected_workers: Dict[str, WebSocket] = {}
task_queue = TaskQueue()

BasicInfoService = BasicInfoController()

@router.get("/health")
async def health_check():
    return await BasicInfoService.health_check_controller(task_queue, connected_workers)

@router.get("/status")
async def service_status():
    return await BasicInfoService.service_status_controller(task_queue, connected_workers)

@router.get("/status/{task_id}")
async def get_status(task_id: str):
    return await BasicInfoService.get_task_status_controller(task_queue, task_id)


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await BasicInfoService.websocket_endpoint(websocket, task_queue, connected_workers)