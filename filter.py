import os
from multiprocessing import Pool
from multiprocessing import cpu_count
import subprocess
import yaml
from pathlib import Path
import shutil


def start_subprocess(command) -> tuple:
    try:
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            shell=True,
        )

        output = process.communicate(timeout=10)[0].decode("utf-8")
        error = process.stderr
        return_code = process.wait(10)
        return (output, error, return_code)
    except Exception:
        pass


def do_stuff(file):
    if not file.endswith(".yaml"):
        return
    output, error, return_code = start_subprocess(
        f"nuclei -t {file} -validate 2>/dev/null"
    )
    print(f"{file} => {return_code}")
    if return_code == 0 or return_code == 2:
        try:
            data = yaml.safe_load(Path(file).read_text())
            severity = (
                data.get(
                    "info",
                    {},
                )
                .get(
                    "severity",
                    "unknown",
                )
                .lower()
            )
            if not os.path.exists(f"./filtered/{severity}"):
                os.mkdir(f"./filtered/{severity}")
            shutil.copyfile(file, f"./filtered/{severity}/{file.split('/')[-1]}")
        except Exception as e:
            print(e)


def main():
    templates = set()
    for path, subdir, files in os.walk("."):
        for name in files:
            templates.add(os.path.join(path, name))

    with Pool(cpu_count()) as pool:
        try:
            pool.map(do_stuff, templates)
        except Exception as e:
            print(e)


if __name__ == "__main__":
    main()
