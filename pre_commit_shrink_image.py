import argparse
from os import remove
from pathlib import Path
from subprocess import run
from sys import platform

from wcmatch import glob

parser = argparse.ArgumentParser()
parser.add_argument(
    "--image-glob",
    help="Glob pattern for images to replace",
    default="**/*.[jpg][jpeg,png,gif,webp,bmp,tiff}",
)
parser.add_argument(
    "--text-glob", help="Glob pattern for text files to replace", default="**/*.md"
)
parser.add_argument(
    "--imagemagick-args",
    help="Arguments for ImageMagick's convert command",
    default="-resize 2000000@> -define webp:method=5 "
    "-define webp:use-sharp-yuv=1 -define webp:thread-level=1",
)
parser.add_argument("--suffix", default=".webp", help="Suffix of the new image files")
parser.add_argument("--filelist", default=".pre-commit-shrink-image", help="File list")
parser.add_argument("--dry-run", action="store_true", help="Dry run", default=False)
parser.add_argument("files", nargs="*")

MAGICK_PATH = (
    Path(__file__).parent / ("magick.exe " if platform == "win32" else "magick")
).absolute()

if not MAGICK_PATH.exists():
    if platform == "win32":
        run(
            [
                "wget",
                "-N",
                "https://imagemagick.org/archive/binaries/ImageMagick-7.1.1-39-Q16-HDRI-x64-dll.exe",
                "-O",
                MAGICK_PATH,
            ]
        )
    elif platform == "linux":
        run(
            [
                "wget",
                "-N",
                "https://imagemagick.org/archive/binaries/magick",
                "-O",
                MAGICK_PATH,
            ]
        )
        run(
            ["chmod", "+x", MAGICK_PATH],
        )

args = parser.parse_args()

filelist = Path(args.filelist)
files = [Path(file) for file in args.files]

image_paths_processed = (
    set(filelist.read_text(encoding="utf-8").splitlines())
    if filelist.exists()
    else set()
)

# replace images
image_path_replace = {}
for image_path in glob.glob(
    args.image_glob, flags=glob.SPLIT | glob.GLOBTILDE | glob.NODIR | glob.BRACE
):
    image_path = Path(image_path)
    if image_path.as_posix() in image_paths_processed:
        continue
    if image_path not in files:
        continue
    size_prev, bytes_prev = (
        run(
            [
                MAGICK_PATH,
                "identify",
                "-precision",
                "3",
                "-format",
                "%wx%h|%b",
                image_path,
            ],
            capture_output=True,
        )
        .stdout.decode("utf-8")
        .split("|")
    )

    suffix = args.suffix
    if not suffix.startswith("."):
        suffix = "." + suffix
    image_path_new = image_path.with_suffix(suffix) if suffix else image_path
    magick_args = [
        MAGICK_PATH,
        "mogrify",
        *(args.imagemagick_args or "").split(),
        "-write",
        image_path_new,
        image_path,
    ]
    if args.dry_run:
        print(" ".join(magick_args))
        continue
    run(magick_args)

    stat_new = image_path_new.stat()
    size_new, bytes_new = (
        run(
            [
                MAGICK_PATH,
                "identify",
                "-precision",
                "3",
                "-format",
                "%wx%h|%b",
                image_path_new,
            ],
            capture_output=True,
        )
        .stdout.decode("utf-8")
        .split("|")
    )

    print_txt = f"{image_path} -> {image_path_new} ({bytes_prev} -> {bytes_new})"
    if size_prev != size_new:
        print_txt += f" ({size_prev} -> {size_new})"
    print(print_txt)

    if image_path != image_path_new:
        remove(image_path)
    image_path_replace[image_path] = image_path_new

    with filelist.open("a", encoding="utf-8") as f:
        f.write(image_path_new.as_posix() + "\n")

if args.dry_run:
    exit()

# replace text files
for text_path in Path.cwd().glob(args.text_glob):
    text = text_path.read_text(encoding="utf-8")
    for image_path, image_path_new in image_path_replace.items():
        text = text.replace(image_path.name, image_path_new.name)
    text_path.write_text(text, encoding="utf-8")
