# smet

A package for creatint MET icons

## Installation

```bash
$ pip install smet
```

## Usage

```bash
    s = SearchMET("sun")
    imgs = s.cropped_images()
    for i in imgs:
        print(i.size)
    print(type(imgs))
    print(len(imgs))
    print(s.artists())
    print(s.titles())
    print(s.regions())
    print(s.objects())
    s.export_image_icons()
```

## Contributing

Interested in contributing? Check out the contributing guidelines. Please note that this project is released with a Code of Conduct. By contributing to this project, you agree to abide by its terms.

## License

`smet` was created by CP. It is licensed under the terms of the MIT license.

## Credits

`smet` was created with [`cookiecutter`](https://cookiecutter.readthedocs.io/en/latest/) and the `py-pkgs-cookiecutter` [template](https://github.com/py-pkgs/py-pkgs-cookiecutter).
