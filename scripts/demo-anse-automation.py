import marimo

__generated_with = "0.23.6"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _():
    import marimo as mo
    import platform
    import subprocess
    import os
    import sqlite3
    import sqlalchemy
    import pandas as pd
    import matplotlib.pyplot as plt
    from pathlib import Path
    import faostat

    return Path, faostat, mo, os, pd, platform, sqlalchemy, subprocess


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # ANSE Engine Setup
    """)
    return


@app.cell
def _(platform):
    ANSE_EXEC: str = "./anse.exe" if platform.system() == "Windows" else "./anse"
    ANSE_DIR: str = "/Users/shxie/projects/anse-core-engine/dist/osx-arm64/"
    return ANSE_DIR, ANSE_EXEC


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Helper functions
    """)
    return


@app.cell(hide_code=True)
def _(os):
    def process_logs(logs: str) -> None:
        log_lines = logs.split("\n")
        # Find and print lines that include "warning", "error", or other similar keywords
        keywords = [" warn ", " error ", "error:"]
        important_logs = filter(lambda line : any(keyword in line.lower() for keyword in keywords), log_lines)
        print("\n".join(list(important_logs)))
        # Find and print log paths
        log_paths = filter(lambda line : "log file path" in line, log_lines)
        print(f"Detailed logs can be found by following the paths below:")
        print("\n".join(list(log_paths)))

    def check_db_exists(db_file_name: str) -> None:
        # Check if db file in workspace exists, before attempting to simulate
        if os.path.exists(db_file_name):
            print(f"\033[1mDatabase successfully created: {db_file_name}\033[0m")
        else:
            print("\033[1mError: No .db file found!\033[0m")

    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Converter
    """)
    return


@app.cell
def _(ANSE_DIR: str, ANSE_EXEC: str, Path, os, subprocess):
    def anse_converter(xlsx_path: str, config_path: str | None = None) -> bool:
        if config_path is None:
            config_path = os.path.join(os.path.dirname(xlsx_path), "config.json")

        output_path = str(Path(xlsx_path).with_suffix('.anse'))

        converter = subprocess.run([ANSE_EXEC, 
                                    "convert",
                                    "-i",           xlsx_path,
                                    "-o",           output_path,
                                    "--config-in",  config_path,
                                    "--config-out", config_path,
                                   ], cwd=ANSE_DIR, capture_output=True, text=True)

        if "CONVERSION COMPLETED" in converter.stdout:
            print("✅ Conversion successful!")
            return True
        print("❌ Conversion failed")

        # if converter.returncode == 0:
        #     print("✅ Conversion successful!")
        #     return True
        # print("❌ Conversion failed")
        # print(converter.stderr)

        print(converter.stdout)
        return False

    return (anse_converter,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Importer
    """)
    return


@app.cell
def _(ANSE_DIR: str, ANSE_EXEC: str, os, subprocess):
    def anse_importer(workspace: str, model_name: str | None = None) -> None:
        if model_name is None:
            model_name = os.path.basename(workspace.rstrip(os.sep))
        importer = subprocess.run([ANSE_EXEC, 
                                    "import",
                                    "-w", workspace,
                                    "-m", model_name,
                                   ], cwd=ANSE_DIR, capture_output=True, text=True)

        if f"[Importer] Model '{model_name}' has been created" in importer.stderr:
            print("✅ Import successful!")
            return True
        print("❌ Importer Error")

        # # if importer.returncode == 0:
        # #     print("✅ Import successful!")
        # #     return True
        # # print("❌ Importer Error")
        print(importer.stderr)

        print(importer.stdout)
        return False

    return (anse_importer,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Simulator
    """)
    return


@app.cell
def _(ANSE_DIR: str, ANSE_EXEC: str, os, subprocess):
    def anse_simulator(workspace: str, duration: int, model_name: str | None = None, **kwargs) -> bool:
        if model_name is None:
            model_name = os.path.basename(workspace.rstrip(os.sep))

        cmd = [ANSE_EXEC, 
               "simulate", 
                "-w", workspace, 
                "-m", model_name, 
                "--duration", str(duration), 
                "-o", "true"
              ]

        for key, value in kwargs.items():
            flag = f"--{key.replace('_', '-')}"
            cmd.extend([flag, str(value)])

        simulator = subprocess.run(cmd, cwd=ANSE_DIR, capture_output=True, text=True)

        if simulator.returncode == 0:
            print("✅ Simulation successful!")
            return True
        print("❌ Simulation failed!")
        print(simulator.stderr)

        print(simulator.stdout)
        return False

    return (anse_simulator,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # One Model
    """)
    return


@app.cell
def _(anse_converter, anse_importer, anse_simulator, os):
    models_dir: str = "/Users/shxie/projects/anse-models/"

    m = "demo-cbm-hwp" # example model

    workspace = os.path.join(models_dir, m)
    xlsx_i = os.path.join(workspace, m + ".xlsx")

    if anse_converter(xlsx_i):
        if anse_importer(workspace):
            anse_simulator(workspace, duration=35, start_timestep=1990)
        else:
            print("❌ Aborting simulation.")
    else:
        print("❌ Aborting rest of process.")
    return m, workspace


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Query simulation results
    """)
    return


@app.cell
def _(m, os, pd, sqlalchemy, workspace):
    db_file: str = os.path.join(workspace, m + ".db")
    engine = sqlalchemy.create_engine(f'sqlite:///{db_file}')

    query = 'SELECT * FROM "VIEW-Stocks"'
    df_stock = pd.read_sql(query, engine)
    return (df_stock,)


@app.cell
def _(df_stock, mo):
    mo.ui.table(df_stock)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Parameter Controller
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Example: Retrieve data from FAOSTAT API and write to .anse
    """)
    return


@app.cell
def _(faostat):
    # Use the token already present in your notebook
    USERNAME = "anse-workshop"
    PASSWORD = "qekhyc-tafwi6-socHap"

    faostat.set_requests_args(username=USERNAME, password=PASSWORD)

    # faostat.set_requests_args(token=TOKEN)

    faostat.faostat.__BASE_URL__ = "https://faostatservices.fao.org/api/v1/en/"

    paramcode={'area': '33',      # Canada
               'item': '1861',    # Roundwood
               'element': '2510',  # Production
               'year': [str(y) for y in range(1990, 2025)]
              }
    roundwood_harvest = faostat.get_data_df(code='FO', pars=paramcode)
    return (roundwood_harvest,)


@app.cell
def _(mo, roundwood_harvest):
    mo.ui.table(roundwood_harvest)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Write to ANSE Flat File
    """)
    return


@app.cell
def _(os, roundwood_harvest, workspace):
    output_path = os.path.join(workspace, "harvest-data.anse")

    C_Factor = {"roundwood": 0.229}

    with open(output_path, "w") as f:
        for _, y in roundwood_harvest.iterrows():
            # Extract variables from the dataframe
            p = y["Item"]
            # Ensure the value is numeric before multiplying
            q = float(y["Value"]) * C_Factor["roundwood"]
            yr = int(y["Year"]) - 1989

            # Construct the <INITIAL_CMO> entry
            # Format: <INITIAL_CMO>Entry Pool;Species;Physical_State;Quantity;Entry timestep;Initial Age;Tag;Is Retained;Description 
            entry = f"<INITIAL_CMO>{p};;;{q};{yr};;;;;\n"
            f.write(entry)

    print(f"✅ Successfully wrote {len(roundwood_harvest)} rows to {output_path}")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Multi-Model
    """)
    return


@app.cell
def _(anse_converter, anse_importer, anse_simulator, os):
    models_dir_multi: str = "/Users/shxie/projects/anse-models/"
    model_list_multi: list[str] = [mm for mm in os.listdir(models_dir_multi) if os.path.isdir(os.path.join(models_dir_multi, mm))]
    # model_list_multi = ["demo-hwp101"]
    # # loop through the model_list
    for mm in model_list_multi:
        if mm not in ("demo-cbm-hwp", "ireland-hwp-updated"):
            print(mm)
            workspace_multi = os.path.join(models_dir_multi, mm)
            xlsx_i_multi = os.path.join(workspace_multi, mm + ".xlsx")

            if anse_converter(xlsx_i_multi):
                if anse_importer(workspace_multi):
                    anse_simulator(workspace_multi, duration=100)
                else:
                    print("❌ Aborting simulation.")
            else:
                print("❌ Aborting rest of process.")
    return


if __name__ == "__main__":
    app.run()
