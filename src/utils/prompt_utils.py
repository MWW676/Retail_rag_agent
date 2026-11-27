from jinja2 import Environment, StrictUndefined
from pathlib import Path


def render_prompt(template_name:str, **kwargs) -> str:
    template_path = Path(__file__).parent.parent / "prompts" / template_name

    env = Environment(undefined=StrictUndefined, trim_blocks=True, lstrip_blocks=True)
    with open(template_path, "r", encoding="utf-8") as f:
        template = env.from_string(f.read())

    return template.render(**kwargs)