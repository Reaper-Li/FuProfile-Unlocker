# Third-party notices

The root `LICENSE` covers original FuProfile Unlocker code and documentation only.
Third-party components and data retain the licenses listed below. Free distribution
does not remove attribution, share-alike, source-distribution, or trademark obligations.
Copies of the applicable license texts and attribution records are kept in `licenses/`.

## FujifilmCameraProfiles style data

- Source: `abpy/FujifilmCameraProfiles`
- License: Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International
- Use in this project: eight `LookTable` and `ToneCurve` data files
- Required treatment: attribution, non-commercial distribution, and share-alike for adaptations

Only the eight files under the upstream `xml tables/` directory are redistributed.
The upstream `dcp examples/` directory is deliberately excluded because it contains
Adobe Standard profiles.

The upstream project describes these tables as being based on Fujifilm Camera Matching
profiles available through Adobe Camera Raw / Lightroom. The CC notice applies only to
rights the upstream licensor can grant; it does not grant trademark rights or imply that
Adobe or Fujifilm endorses this project.

The profile names contain third-party trademarks solely to identify the intended photographic rendering style. The project is not affiliated with or endorsed by Fujifilm or Adobe.

## dcpTool

- Copyright: Sandy McGuffog and contributors
- License: GNU General Public License, version 2 or later
- Use in this project: separate executable invoked to convert between DCP and XML

Distributions that include dcpTool must also provide its applicable license notice and corresponding source-code offer/source as required by the GPL.
The GitHub repository and complete source release retain the dcpTool source tree and
`licenses/DCPTOOL-GPL-2.0.txt`.

## Adobe camera profiles

Adobe Standard DCP files are discovered and read from the user's existing Lightroom or Camera Raw installation. They are not included in this project and must not be redistributed by this project.

## ExifTool

- Copyright: Phil Harvey
- License: Perl Artistic License or GNU General Public License
- Use in this project: read-only extraction of RAW camera make, model, and file type

The source archive does not bundle ExifTool. A platform build may include the
official executable and its support directory; retain the ExifTool license and
notices when redistributing that build. FuProfile Unlocker release bundles include
the license copy stored as `licenses/EXIFTOOL-GPL-3.0.txt`.

## tkinterdnd2 and tkDnD

- Project: `Eliav2/tkinterdnd2`, wrapping George Petasis' tkDnD extension
- License: MIT
- Use in this project: native file drag-and-drop support for the Tk interface

Distributions include the platform-specific tkDnD extension files collected
from the `tkinterdnd2` Python package.

The bundled license copy is stored as `licenses/TKINTERDND2-MIT.txt`.

## FuProfile Unlocker license boundary

Original application code is available under the MIT License. The style tables are
not MIT-licensed and carry a non-commercial restriction. Do not describe the entire
binary or source bundle as being licensed solely under MIT; refer users to this file
and `licenses/README.md`.
