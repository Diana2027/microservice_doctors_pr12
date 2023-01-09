from fastapi import FastAPI, HTTPException
from app.doctor import Doctor, CreateDoctor

doctors: list[Doctor] = [
    # Doctor(0, 'Голубев Роман Даниилович', 'Хирург'),
    # Doctor(1, 'Михайлов Андрей Матвеевич', 'Лор'),
    # Doctor(2, 'Зеленин Матвей Тимофеевич', 'Ортопед'),
    # Doctor(3, 'Васильева Ева Тихоновна', 'Терапевт'),
    # Doctor(4, 'Бабушкина Лиана Степановна', 'Онколог')
]

def add_doctor(content: CreateDoctor):
    id = len(doctors)
    doctors.append(Doctor(id, content.fio, content.specialization))
    return id

app = FastAPI()

########
# Jaeger

from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

resource = Resource(attributes={
    SERVICE_NAME: 'drs-service'
})

jaeger_exporter = JaegerExporter(
    agent_host_name="jaeger",
    agent_port=6831,
)

provider = TracerProvider(resource=resource)
processor = BatchSpanProcessor(jaeger_exporter)
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)

FastAPIInstrumentor.instrument_app(app)

#
########

########
# Prometheus

from prometheus_fastapi_instrumentator import Instrumentator

@app.on_event("startup")
async def startup():
    Instrumentator().instrument(app).expose(app)

#
########

@app.get("/v1/drs")
async def get_drs():
    return doctors

@app.post("/v1/drs")
async def add_dr(content: CreateDoctor):
    add_doctor(content)
    return doctors[-1]

@app.get("/v1/drs/{id}")
async def get_drs_by_id(id: int):
    result = [item for item in doctors if item.id == id]
    if len(result) > 0:
        return result[0]
    raise HTTPException(status_code = 404, detail="Документ не найден")

@app.get("/__health")
async def check_service():
    return