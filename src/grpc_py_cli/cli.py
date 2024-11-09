import os

import click_extra as click

from .utils import (
    create_dir_if_not_exists,
    generate_grpc_files,
    get_default_root_dir,
    ruff_format,
    ruff_lint,
    version_info,
)

ROOT_DIR = get_default_root_dir()
BASE_DIR = ROOT_DIR
PROTO_DIR = os.path.join(BASE_DIR, "protos")
OUT_DIR = os.path.join(BASE_DIR, "grpc_generated")


@click.extra_group(params=None, help="CLI tool for gRPC Python code generation")
@click.version_option(
    None,
    "-v",
    "--version",
    message=version_info(),
)
def grpc_cli():
    pass


@grpc_cli.command(help="Create Python files from proto file")
@click.argument(
    "proto_file",
    type=click.Path(exists=True, file_okay=True, dir_okay=False, resolve_path=True),
)
@click.option(
    "--python_out",
    default=OUT_DIR,
    help="Output directory for serialization/deserialization Python files. e.g. xxx_pb2.py",
    type=click.Path(exists=False, file_okay=False, dir_okay=True, resolve_path=True),
)
@click.option(
    "--grpc_python_out",
    default=OUT_DIR,
    help="Output directory for generate grpc stub and server Python code. e.g. xxx_pb2_grpc.py",
    type=click.Path(exists=False, file_okay=False, dir_okay=True, resolve_path=True),
)
@click.option(
    "--pyi_out",
    default=OUT_DIR,
    help="Output directory for generate Python type hint stubs. e.g. xxx_pb2.pyi",
    type=click.Path(exists=False, file_okay=False, dir_okay=True, resolve_path=True),
)
def create(
    proto_file: str,
    python_out: str,
    grpc_python_out: str,
    pyi_out: str,
):
    if not os.path.exists(proto_file):
        click.secho("Error: ", fg="red", nl=False)
        click.echo(f"File {click.style(proto_file, fg='yellow')} does not exist")
        return

    create_dir_if_not_exists(python_out)
    create_dir_if_not_exists(grpc_python_out)
    create_dir_if_not_exists(pyi_out)

    proto_dir = os.path.dirname(proto_file)
    proto_filename = os.path.basename(proto_file)

    click.echo(
        f"Generating Python files from {click.style(proto_filename, fg='yellow')}...",
        nl=False,
    )

    if (
        generate_grpc_files(
            proto_dir, proto_filename, python_out, grpc_python_out, pyi_out
        )
        != 0
    ):
        click.secho("Failed", fg="red")
        return

    click.secho("Done", fg="green")

    for dir, filename in [
        (python_out, proto_filename.replace(".proto", "_pb2.py")),
        (grpc_python_out, proto_filename.replace(".proto", "_pb2_grpc.py")),
        (pyi_out, proto_filename.replace(".proto", "_pb2.pyi")),
    ]:
        click.echo(
            f"Generated {click.style(filename, fg='yellow')} under {click.style(dir, fg='yellow')}."
        )
    click.echo("")

    click.echo(
        "Linting generated files...",
    )
    if ruff_lint(python_out, grpc_python_out, pyi_out) != 0:
        click.secho("Failed", fg="red")
        return
    click.secho("Done\n", fg="green")

    click.echo("Formatting generate files...")
    if ruff_format(python_out, grpc_python_out, pyi_out) != 0:
        click.secho("Failed", fg="red")
        return
    click.secho("Done\n", fg="green")


@grpc_cli.command(help="Clean generated grpc Python files")
@click.argument(
    "proto_file",
    type=click.Path(exists=True, file_okay=True, dir_okay=False),
    help="Proto file to clean",
)
@click.option(
    "--python_out",
    default=OUT_DIR,
    help="Output directory for serialization/deserialization Python files. e.g. xxx_pb2.py",
    type=click.Path(exists=False, file_okay=False, dir_okay=True, resolve_path=True),
)
@click.option(
    "--grpc_python_out",
    default=OUT_DIR,
    help="Output directory for generate grpc stub and server Python code. e.g. xxx_pb2_grpc.py",
    type=click.Path(exists=False, file_okay=False, dir_okay=True, resolve_path=True),
)
@click.option(
    "--pyi_out",
    default=OUT_DIR,
    help="Output directory for generate Python type hint stubs. e.g. xxx_pb2.pyi",
    type=click.Path(exists=False, file_okay=False, dir_okay=True, resolve_path=True),
)
def clean(
    proto_file: str,
    python_out: str,
    grpc_python_out: str,
    pyi_out: str,
):
    proto_filename = os.path.basename(proto_file)

    python_files = [
        (python_out, proto_filename.replace(".proto", "_pb2.py")),
        (grpc_python_out, proto_filename.replace(".proto", "_pb2_grpc.py")),
        (pyi_out, proto_filename.replace(".proto", "_pb2.pyi")),
    ]

    click.echo(
        f"Cleaning generated Python files from {click.style(proto_file, fg='yellow')}...",
    )

    for dir, file in python_files:
        file_path = os.path.join(dir, file)
        if os.path.exists(file_path):
            click.echo(f"Removing {click.style(file, fg='yellow')}...", nl=False)

            os.remove(os.path.join(OUT_DIR, file))

            click.secho("Done", fg="green")
        else:
            click.echo(
                f"File {click.style(file, fg='yellow')} not found. {click.style('Skipped.', fg='yellow')}"
            )

    click.secho("Done", fg="green")


def main():
    grpc_cli()
