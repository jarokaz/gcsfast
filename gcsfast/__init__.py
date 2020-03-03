#!/usr/bin/env python3
# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
gcsfast main entry point.
"""
import logging
import warnings
import click

from multiprocessing import cpu_count

from gcsfast.cli.download import download_command
from gcsfast.cli.download2 import download2_command
from gcsfast.cli.stream_upload import stream_upload_command
from gcsfast.utils import set_program_log_level

warnings.filterwarnings(
    "ignore", "Your application has authenticated using end user credentials")

logging.basicConfig()
LOG = logging.getLogger(__name__)


@click.group()
@click.option("-l",
              "--log_level",
              required=False,
              help="Set log level.",
              default=None)
@click.pass_context
def main(context: object = object(), **kwargs) -> None:
    """
    GCS fast file transfer tool.
    """
    context.obj = kwargs


def init(log_level: str = None) -> None:
    """
    Top-level initialization.

    Keyword Arguments:
        log_level {str} -- Desired log level. (default: {None})
    """
    set_program_log_level(log_level)


@main.command()
@click.pass_context
@click.option(
    "-p",
    "--processes",
    required=False,
    help=
    "Set number of processes for simultaneous downloads. Default is multiprocessing.cpu_count().",
    default=None,
    type=int)
@click.option(
    "-t",
    "--threads",
    required=False,
    help=
    "Set number of threads (per process) for simultaneous downloads. Default is 1."
    " Default slice limits will be multiplied by this value (as slices are subdivided into threads).",
    default=None,
    type=int)
@click.option(
    "-i",
    "--io_buffer",
    required=False,
    help=
    "Set io.DEFAULT_BUFFER_SIZE, which determines the size of writes to disk, in bytes. Default is 128KB.",
    default=None,
    type=int)
@click.option(
    "-n",
    "--min_slice",
    required=False,
    help="Set the minimum slice size to use, in bytes. Default is 64MiB.",
    default=None,
    type=int)
@click.option(
    "-m",
    "--max_slice",
    required=False,
    help="Set the maximum slice size to use, in bytes. Default is 1GiB.",
    default=None,
    type=int)
@click.option(
    "-s",
    "--slice_size",
    required=False,
    help=
    "Set the slice size to use, in bytes. Use this to override the slice calculation with your own value.",
    default=None,
    type=int)
@click.option(
    "-c",
    "--transfer_chunk",
    required=False,
    help=
    "Set the GCS transfer chunk size to use, in bytes. Must be a multiple of 262144. Default is 262144 * 4 * 16 (16MiB),"
    " which covers most cases quite well. Recommend setting this using shell evaluation, e.g. $((262144 * 4 * DESIRED_MB)).",
    default=None,
    type=int)
@click.argument('object_path')
@click.argument('file_path', type=click.Path(), required=False)
def download(context: object, processes: int, threads: int, io_buffer: int,
             min_slice: int, max_slice: int, slice_size: int,
             transfer_chunk: int, object_path: str, file_path: str) -> None:
    """
    Download a GCS object as fast as possible.

    OBJECT_PATH is the path to the object (use gs:// protocol).\n
    FILE_PATH is the filesystem path for the downloaded object.
    """
    init(**context.obj)
    return download_command(processes, threads, io_buffer, min_slice,
                            max_slice, slice_size, transfer_chunk, object_path,
                            file_path)


if __name__ == "__main__":
    main()

@main.command()
@click.pass_context
@click.option(
    "-p",
    "--processes",
    required=False,
    help=
    "Set number of processes for simultaneous downloads. Default is multiprocessing.cpu_count().",
    default=cpu_count(),
    type=int)
@click.option(
    "-t",
    "--threads",
    required=False,
    help=
    "Set number of threads (per process) for simultaneous downloads. Default is 1."
    " Default slice limits will be multiplied by this value (as slices are subdivided into threads).",
    default=None,
    type=int)
@click.option(
    "-i",
    "--io_buffer",
    required=False,
    help=
    "Set io.DEFAULT_BUFFER_SIZE, which determines the size of writes to disk, in bytes. Default is 128KB.",
    default=None,
    type=int)
@click.option(
    "-c",
    "--transfer_chunk",
    required=False,
    help=
    "Set the GCS transfer chunk size to use, in bytes. Must be a multiple of 262144. Default is 262144 * 4 * 16 (16MiB),"
    " which covers most cases quite well. Recommend setting this using shell evaluation, e.g. $((262144 * 4 * DESIRED_MB)).",
    default=None,
    type=int)
@click.argument('input_lines')
def download2(context: object, processes: int, threads: int, io_buffer: int,
             transfer_chunk: int, input_lines: str) -> None:
    """
    Download a stream of GCS objects as fast as possible.

    OBJECT_PATH is a file or stdin (-) from which to read full GCS object URLs, line delimited.
    """
    init(**context.obj)
    return download2_command(processes, threads, io_buffer, transfer_chunk, input_lines)


@main.command()
@click.pass_context
@click.option(
    "-t",
    "--threads",
    required=False,
    help=
    "Set number of threads for simultaneous slice uploads. Default is multiprocessing.cpu_count() * 4.",
    default=cpu_count() * 4,
    type=int)
@click.option(
    "-s",
    "--slice-size",
    required=False,
    help=
    "Set the size of an upload slice. When this many bytes are read from stdin (before EOF), a new composite slice object upload will begin."
    "Default is 16MB.",
    default=16 * 2**20,
    type=int)
@click.argument('object_path')
@click.argument('file_path', type=click.Path(), required=False)
def stream_upload(context: object, threads: int, slice_size: int, object_path: str, file_path: str) -> None:
    """
    Stream data of an arbitrary length into an object in GCS. 
    
    By default this command will read from stdin, but if a FILE_PATH is provided any file-like object (such as a FIFO) can be used.

    The stream will be read until slice-size or EOF is reached, at which point an upload will begin. 
    Subsequent bytes read will be sent in similar slices until EOF. Finally, the slices will be composed into
    the target object.

    OBJECT_PATH is the path to the object (use gs:// protocol).\n
    FILE_PATH is the optional path for a file-like object.
    """
    init(**context.obj)
    return stream_upload_command(threads, slice_size, object_path, file_path)


if __name__ == "__main__":
    main()


