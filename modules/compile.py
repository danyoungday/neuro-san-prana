import pyhocon

BASE_PATH = "modules/base.hocon"


def compile_hocon(tool_names: list[str], save_path: str):
    """
    Compiles HOCON tool files into a base configuration file then saves it as a JSON file.
    """
    factory = pyhocon.ConfigFactory.parse_file(BASE_PATH)
    tools = []
    for tool_name in tool_names:
        tool = pyhocon.ConfigFactory.parse_file(f"modules/{tool_name}.hocon")
        tools.extend(tool)
    factory.put("tools", tools)
    with open(save_path, "w", encoding="utf-8") as f:
        f.write(pyhocon.HOCONConverter.to_json(factory))


if __name__ == "__main__":
    compile_hocon(["analyst", "historian", "tools"], "modules/prana-compiled.hocon")
