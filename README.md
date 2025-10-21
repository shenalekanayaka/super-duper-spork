# Worker Allocation System

This project helps you manage worker allocations efficiently.

## Creating the Executable

To generate the executable file, use the following command:

```bash
pyinstaller --noconfirm --clean --name "Worker Allocation System" --add-data "utils;utils" --add-data "allocations_json;allocations_json" --add-data "exports;exports" --add-data "excel;excel" --add-data "allocation_history.json;." --add-data "audit_trail.json;." --hidden-import tkcalendar main.py
```

After running this command, the executable will be located in the `dist/Worker Allocation System/` folder.

## Creating the Executable Without Console

To create an executable without the console window, add the `--windowed` option:

```bash
pyinstaller --noconfirm --clean --name "Worker Allocation System" --add-data "utils;utils" --add-data "allocations_json;allocations_json" --add-data "exports;exports" --add-data "excel;excel" --add-data "allocation_history.json;." --add-data "audit_trail.json;." --hidden-import tkcalendar --windowed main.py
```

The resulting executable will also be in the `dist/Worker Allocation System/` folder.
