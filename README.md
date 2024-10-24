# pre-commit-shrink-image

## Installation

```yaml
- repo: https://github.com/34j/pre-commit-shrink-image
  rev: "8341bd6" # Use the sha / tag you want to point at
  hooks:
    - id: shrink-image
      args:
        [
          --image-glob,
          "images/*.{png,jpg}",
          --text-glob,
          "docs/*.md",
          --suffix,
          webp,
          --imagemagick-args,
          "-quality 92 -resize 2000000@> -define webp:method=5 -define webp:use-sharp-yuv=1 -define webp:thread-level=1",
        ]
```

## Usage

Only staged images are processed.
If image extension is changed, the paths in the text files are also updated and the original images are deleted.

```shell
> python3 -m pre_commit_shrink_image --help
usage: pre_commit_shrink_image.py [-h] [--image-glob IMAGE_GLOB] [--text-glob TEXT_GLOB] [--imagemagick-args IMAGEMAGICK_ARGS] [--suffix SUFFIX] [--filelist FILELIST] [--dry-run] [files ...]

positional arguments:
  files

options:
  -h, --help            show this help message and exit
  --image-glob IMAGE_GLOB
                        Glob pattern for images to replace
  --text-glob TEXT_GLOB
                        Glob pattern for text files to replace
  --imagemagick-args IMAGEMAGICK_ARGS
                        Arguments for ImageMagick's convert command
  --suffix SUFFIX       Suffix of the new image files
  --filelist FILELIST   File list
  --dry-run             Dry run
```

## See Also

- [ImageMagick – WebP Encoding Options](https://imagemagick.org/script/webp.php)
- [ImageMagick と WebP #ImageMagick - Qiita](https://qiita.com/yoya/items/0848a6b0b39db4cd57c2)
