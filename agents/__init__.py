from .athena import Athena


def agent_factory(class_name):
    if class_name == "Athena":
        return Athena()
    else:
        raise ValueError(f"Invalid class name {class_name}")
