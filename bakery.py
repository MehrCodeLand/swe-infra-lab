import time
import random
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource

# --- setup ---
provider = TracerProvider(resource=Resource.create({"service.name": "bakery"}))
provider.add_span_processor(
    BatchSpanProcessor(OTLPSpanExporter(endpoint="localhost:4317", insecure=True))
)
trace.set_tracer_provider(provider)
tracer = trace.get_tracer("bakery")

def gather_ingredients():
    with tracer.start_as_current_span("gather_ingredients") as span:
        span.set_attribute("ingredients.count", 6)
        time.sleep(random.uniform(0.2, 0.5))

def mix_batter():
    with tracer.start_as_current_span("mix_batter") as span:
        span.set_attribute("mixer.speed", "medium")
        time.sleep(random.uniform(0.3, 0.7))

def bake_cake():
    with tracer.start_as_current_span("bake_cake") as span:
        temp = 180
        span.set_attribute("oven.temp_celsius", temp)
        time.sleep(random.uniform(2.0, 3.5))  # the long one, like the LLM step

def decorate_cake():
    with tracer.start_as_current_span("decorate_cake") as span:
        span.set_attribute("frosting.type", "chocolate")
        time.sleep(random.uniform(0.4, 0.8))

def make_cake():
    with tracer.start_as_current_span("make_cake") as span:  # parent, wraps everything
        span.set_attribute("cake.flavor", "vanilla")
        gather_ingredients()
        mix_batter()
        bake_cake()
        decorate_cake()

if __name__ == "__main__":
    make_cake()
    time.sleep(2)  # give exporter time to flush before process exits
    print("Cake done! Check Jaeger.")