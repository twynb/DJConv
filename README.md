# DJConv

DJConv eases the process of using different DJ software in different places by letting you convert your music library between different programs.

## Supported Programs

The following programs' databases can be used as of now:

- DJUCED

If you want to add support for a program not listed here, simply create a pull request linked to their respective issues, or create an issue if there is none yet. Please comment on an issue first if you do want to work on it in order to avoid having multiple people work on an issue separately.

## Usage

As of current, DJConv only exists as the python script itself. Simply run ``__main__.py`` with the relevant command line arguments.

The following arguments are recognised and required:

- ``-if [fname]``: The input file format, see [Accepted formats](#accepted-formats)
- ``-of [fname]``: The output file format, see [Accepted formats](#accepted-formats)
- ``-o [fname]``: The output file location.

The last argument must always be the input file location.

### Accepted Formats

The following format names can be passed as ``if`` and ``of`` and correspond to their respective database formats:

- ``djuced``

## Documentation

Proper Documentation will be added later.

Documentation for the different database formats can be found here:

- [DJUCED](docs/djuced-db.md)
- [rekordbox](https://pyrekordbox.readthedocs.io/en/latest/formats/db6.html)

Note that DJUCED was reverse engineered for this project as no other documentation of its file format seems to exist. If you find an issue with it or can explain a field that hasn't been figured out yet, feel free to add the corresponding information to the documentation via a pull request!

## License

This software is licensed under the GNU GPLv3 license, as found in the LICENSE.txt file or [on the GNU website](https://www.gnu.org/licenses/gpl-3.0.en.html).
