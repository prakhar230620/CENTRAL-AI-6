from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any, List
from ai_manager import AIManager
from input_analyzer import InputAnalyzer
from junction import Junction
from output_processor import OutputProcessor
import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor
from config import Settings
from dependency_injector import containers, providers
from dependency_injector.wiring import inject, Provide

logging.config.fileConfig('logging.conf', disable_existing_loggers=False)
logger = logging.getLogger(__name__)


class Container(containers.DeclarativeContainer):
    config = providers.Configuration()
    ai_manager = providers.Singleton(AIManager, config=config.ai_manager)
    input_analyzer = providers.Singleton(InputAnalyzer, config=config.input_analyzer)
    junction = providers.Singleton(Junction, config=config.junction)
    output_processor = providers.Singleton(OutputProcessor, config=config.output_processor)


container = Container()
container.config.from_yaml('config.yaml')

app = FastAPI()


class InputData(BaseModel):
    input: str
    type: str


class AIData(BaseModel):
    name: str
    type: str
    config: Dict[str, Any]


@app.post("/process_input")
@inject
async def process_input(
        data: InputData,
        ai_manager: AIManager = Depends(Provide[Container.ai_manager]),
        input_analyzer: InputAnalyzer = Depends(Provide[Container.input_analyzer]),
        junction: Junction = Depends(Provide[Container.junction]),
        output_processor: OutputProcessor = Depends(Provide[Container.output_processor])
):
    try:
        analyzed_input = await input_analyzer.analyze(data.input)
        selected_ai = await ai_manager.select_ai(analyzed_input)

        if not selected_ai:
            raise HTTPException(status_code=400, detail="No suitable AI found")

        raw_output = await junction.process(selected_ai, analyzed_input)
        processed_output = await output_processor.process(raw_output, data.type)

        return processed_output
    except Exception as e:
        logger.exception("Error processing input")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/add_ai")
@inject
async def add_ai(
        ai_data: AIData,
        ai_manager: AIManager = Depends(Provide[Container.ai_manager])
):
    try:
        result = await ai_manager.add_ai(ai_data.dict())
        return result
    except Exception as e:
        logger.exception("Error adding AI")
        raise HTTPException(status_code=500, detail="Failed to add AI")


@app.get("/ai_manager")
@inject
async def list_ais(
        ai_manager: AIManager = Depends(Provide[Container.ai_manager])
):
    return await ai_manager.list_ais()


@app.put("/ai_manager/{ai_id}")
@inject
async def update_ai(
        ai_id: str,
        ai_data: AIData,
        ai_manager: AIManager = Depends(Provide[Container.ai_manager])
):
    result = await ai_manager.update_ai(ai_id, ai_data.dict())
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


@app.delete("/ai_manager/{ai_id}")
@inject
async def remove_ai(
        ai_id: str,
        ai_manager: AIManager = Depends(Provide[Container.ai_manager])
):
    result = await ai_manager.remove_ai(ai_id)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)