from jinja2 import Template, Environment, StrictUndefined
from pathlib import Path
from src.core.models import Chunk

def render_prompt(template_name:str, **kwargs) -> str:
    template_path = Path(__file__).parent.parent / "prompts" / template_name

    env = Environment(undefined=StrictUndefined)
    with open(template_path, "r", encoding="utf-8") as f:
        template = env.from_string(f.read())

    return template.render(**kwargs)