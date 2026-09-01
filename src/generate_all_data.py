from pathlib import Path
import subprocess
import sys
import time


# ============================================================
# CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE_FOLDER = PROJECT_ROOT / "src"

PIPELINE_STEPS = [
    {
        "name": "Base customer and sales representative data",
        "script": "generate_base_data.py",
    },
    {
        "name": "Automotive product catalog",
        "script": "generate_products.py",
    },
    {
        "name": "Marketing campaigns",
        "script": "generate_campaigns.py",
    },
    {
        "name": "Campaign targeting funnel",
        "script": "generate_campaign_targets.py",
    },
    {
        "name": "Sales order headers",
        "script": "generate_sales_orders.py",
    },
    {
        "name": "Sales order lines",
        "script": "generate_sales_order_lines.py",
    },
    {
        "name": "Customer payments",
        "script": "generate_payments.py",
    },
    {
        "name": "Comprehensive data quality validation",
        "script": "validate_all_data.py",
    },
]


# ============================================================
# PIPELINE EXECUTION
# ============================================================

def validate_pipeline_scripts() -> None:
    """Confirm that every required script exists."""

    missing_scripts = []

    for step in PIPELINE_STEPS:
        script_path = SOURCE_FOLDER / step["script"]

        if not script_path.exists():
            missing_scripts.append(str(script_path))

    if missing_scripts:
        formatted_paths = "\n".join(missing_scripts)

        raise FileNotFoundError(
            "The following pipeline scripts are missing:\n"
            f"{formatted_paths}"
        )


def run_pipeline_step(
    step_number: int,
    step_name: str,
    script_name: str,
) -> float:
    """Run one pipeline script in a separate process."""

    script_path = SOURCE_FOLDER / script_name

    print("\n" + "=" * 70)
    print(
        f"STEP {step_number}/{len(PIPELINE_STEPS)}: "
        f"{step_name}"
    )
    print(f"SCRIPT: {script_name}")
    print("=" * 70)

    start_time = time.perf_counter()

    subprocess.run(
        [
            sys.executable,
            str(script_path),
        ],
        cwd=PROJECT_ROOT,
        check=True,
    )

    elapsed_time = time.perf_counter() - start_time

    print(
        f"\nStep completed in {elapsed_time:.2f} seconds."
    )

    return elapsed_time


def main() -> None:
    """Run the complete data-generation and validation pipeline."""

    print("AutoParts data pipeline started.")
    print(f"Python executable: {sys.executable}")
    print(f"Project root: {PROJECT_ROOT}")

    validate_pipeline_scripts()

    pipeline_start_time = time.perf_counter()
    step_results = []

    try:
        for step_number, step in enumerate(
            PIPELINE_STEPS,
            start=1,
        ):
            elapsed_time = run_pipeline_step(
                step_number=step_number,
                step_name=step["name"],
                script_name=step["script"],
            )

            step_results.append(
                {
                    "step": step_number,
                    "name": step["name"],
                    "status": "Success",
                    "seconds": elapsed_time,
                }
            )

    except subprocess.CalledProcessError as error:
        print("\n" + "!" * 70)
        print("PIPELINE FAILED")
        print(f"Failed script: {error.cmd[-1]}")
        print(f"Exit code: {error.returncode}")
        print("!" * 70)

        raise SystemExit(error.returncode) from error

    total_elapsed_time = (
        time.perf_counter() - pipeline_start_time
    )

    print("\n" + "=" * 70)
    print("PIPELINE COMPLETED SUCCESSFULLY")
    print("=" * 70)

    for result in step_results:
        print(
            f"{result['step']}. "
            f"{result['name']}: "
            f"{result['status']} "
            f"({result['seconds']:.2f} seconds)"
        )

    print(
        "\nTotal pipeline time: "
        f"{total_elapsed_time:.2f} seconds"
    )

    print(
        "Generated and validated files are available in: "
        f"{PROJECT_ROOT / 'data' / 'raw'}"
    )


if __name__ == "__main__":
    main()
