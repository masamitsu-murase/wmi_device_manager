import argparse
import subprocess


def find_all_keys(dll_path):
    result = subprocess.run(
        ["strings", "-u", "-nobanner", "-n", "8", dll_path],
        universal_newlines=True,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL)
    return [
        x.rstrip() for x in result.stdout.split("\n")
        if x.startswith("DEVPKEY")
    ]


def parse_keys(keys):
    key_tree = {}
    for key in keys:
        splitted_key = key.split("_", 2)
        if len(splitted_key) < 3:
            continue
        group = splitted_key[1]
        name = splitted_key[2]

        if group not in key_tree:
            key_tree[group] = []
        key_tree[group].append(name)
    return key_tree


def output_const(key_tree):
    special_groups = [
        "Device",
        "DeviceContainer",
        "FirmwareResource",
        "PciDevice",
        "PciRootBus",
    ]

    output = ""
    for key in sorted(key_tree.keys()):
        output += f"{key} = {{\n"
        for name in sorted(key_tree[key]):
            output += f"  \"{name}\",\n"
        output += "}\n\n"

    output += "DEVPKEY_LIST = (\n"
    for key in special_groups:
        output += f"  (\"{key}\", {key}),\n"
    output += "\n"
    for key in sorted(key_tree.keys()):
        line = f"(\"{key}\", {key}),"
        if key in special_groups:
            output += f"  # {line}\n"
        else:
            output += f"  {line}\n"
    output += ")\n"

    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("cimwin32_dll")
    parser.add_argument("output_const_py")
    args = parser.parse_args()
    output = output_const(parse_keys(find_all_keys(args.cimwin32_dll)))
    with open(args.output_const_py, "w") as file:
        file.write(output)
