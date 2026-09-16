from __future__ import annotations

import copy
import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
import xml.etree.ElementTree as ET
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

from . import __version__
from .platforms import adobe_standard_roots, find_dcptool, find_exiftool, find_style_root
from .platforms import install_root as default_install_root


StatusCallback = Callable[[str], None]


def normalized(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", value.casefold())

SUPPORTED_EXTENSIONS = {
    ".3fr", ".arw", ".cr2", ".cr3", ".dng", ".erf", ".fff", ".iiq",
    ".kdc", ".mef", ".mos", ".mrw", ".nef", ".nrw", ".orf", ".pef",
    ".raf", ".raw", ".rw2", ".rwl", ".sr2", ".srf", ".srw", ".x3f",
}

STYLES = (
    ("PROVIA / Standard", "provia.txt"),
    ("Velvia / Vivid", "velvia.txt"),
    ("ASTIA / Soft", "astia.txt"),
    ("Classic Chrome", "classic chrome.txt"),
    ("REALA ACE", "reala ace.txt"),
    ("PRO Neg. Hi", "pro neg hi.txt"),
    ("PRO Neg. Std", "pro neg std.txt"),
    ("ETERNA / Cinema", "eterna.txt"),
)


# Adobe uses the name of the regional model, or the model's international
# equivalent, in its camera-profile restriction.  Keep this table deliberately
# explicit: a camera profile is colour calibration data, so a broad fuzzy match
# can silently select the wrong sensor.  Keys and values are human-readable on
# purpose; ``normalized`` is applied by the lookup helpers below.
MODEL_ALIASES: dict[str, tuple[str, ...]] = {
    # Canon regional names and compact spelling used by a few raw.pixls.us
    # samples.  These are the same camera sold under a different market name.
    "Canon EOS 2000D": ("Canon EOS 1500D",),
    "Canon EOS 200D II": ("Canon EOS 250D",),
    "Canon EOS 4000D": ("Canon EOS 3000D",),
    "Canon EOS 350D DIGITAL": ("Canon EOS 350D",),
    "Canon EOS 400D DIGITAL": ("Canon EOS 400D",),
    "Canon EOS DIGITAL REBEL XSi": ("Canon EOS 450D",),
    "Canon EOS DIGITAL REBEL XT": ("Canon EOS 350D",),
    "Canon EOS DIGITAL REBEL XTi": ("Canon EOS 400D",),
    "Canon EOS Kiss Digital N": ("Canon EOS 350D",),
    "Canon EOS Kiss F": ("Canon EOS 1000D",),
    "Canon EOS KISS M": ("Canon EOS M50",),
    "Canon EOS Kiss X3": ("Canon EOS 500D",),
    "Canon EOS Kiss X4": ("Canon EOS 550D",),
    "Canon EOS Kiss X80": ("Canon EOS 1300D",),
    "Canon EOS Kiss X9": ("Canon EOS 200D",),
    "Canon EOS M50m2": ("Canon EOS M50 Mark II",),
    "Canon EOS R5m2": ("Canon EOS R5 Mark II",),
    "Canon EOS R6m2": ("Canon EOS R6 Mark II",),
    "Canon EOS REBEL SL1": ("Canon EOS 100D",),
    "Canon EOS Rebel SL2": ("Canon EOS 200D",),
    "Canon EOS Rebel SL3": ("Canon EOS 250D",),
    "Canon EOS Rebel T100": ("Canon EOS 3000D",),
    "Canon EOS REBEL T1i": ("Canon EOS 500D",),
    "Canon EOS REBEL T2i": ("Canon EOS 550D",),
    "Canon EOS Rebel T3": ("Canon EOS 1100D",),
    "Canon EOS Rebel T3i": ("Canon EOS 600D",),
    "Canon EOS Rebel T4i": ("Canon EOS 650D",),
    "Canon EOS Rebel T5": ("Canon EOS 1200D",),
    "Canon EOS Rebel T5i": ("Canon EOS 700D",),
    "Canon EOS Rebel T6": ("Canon EOS 1300D",),
    "Canon EOS Rebel T6i": ("Canon EOS 750D",),
    "Canon EOS Rebel T6s": ("Canon EOS 760D",),
    "Canon EOS Rebel T7": ("Canon EOS 1500D",),
    "Canon EOS REBEL T7i": ("Canon EOS 800D",),

    # Panasonic's TZ/ZS, FZ and G-series names vary by market.  Only aliases
    # for which this machine has an Adobe Standard calibration are included.
    "DC-FZ10002": ("Panasonic DC-FZ1000M2",),
    "DC-FZ45": ("Panasonic DC-FZ80",),
    "DC-FZ82": ("Panasonic DC-FZ80",),
    "DC-G100D": ("Panasonic DC-G100",),
    "DC-G110": ("Panasonic DC-G100",),
    "DC-G90": ("Panasonic DC-G99",),
    "DC-G91": ("Panasonic DC-G99",),
    "DC-G95": ("Panasonic DC-G99",),
    "DC-G95D": ("Panasonic DC-G99",),
    "DC-GX7MK3": ("Panasonic DC-GX9",),
    "DC-GX800": ("Panasonic DC-GF9",),
    "DC-GX850": ("Panasonic DC-GF9",),
    "DC-GX880": ("Panasonic DC-GF9",),
    "DMC-FZ2000": ("Panasonic DMC-FZ2500",),
    "DMC-FZ330": ("Panasonic DMC-FZ300",),
    "DMC-FZ38": ("Panasonic DMC-FZ35",),
    "DMC-FZ45": ("Panasonic DMC-FZ40",),
    "DMC-G70": ("Panasonic DMC-G7",),
    "DMC-G80": ("Panasonic DMC-G8",),
    "DMC-G81": ("Panasonic DMC-G8",),
    "DMC-G85": ("Panasonic DMC-G8",),
    "DMC-GM1S": ("Panasonic DMC-GM1",),
    "DMC-GX7MK2": ("Panasonic DMC-GX85",),
    "DMC-GX80": ("Panasonic DMC-GX85",),
    "DC-TZ200D": ("Panasonic DC-ZS200",),
    "DC-TZ202": ("Panasonic DC-ZS200",),
    "DC-TZ90": ("Panasonic DC-ZS70",),
    "DC-TZ91": ("Panasonic DC-ZS70",),
    "DC-TZ95": ("Panasonic DC-ZS80",),
    "DC-TZ95D": ("Panasonic DC-ZS80",),
    "DC-TZ96": ("Panasonic DC-ZS80",),
    "DC-ZS200D": ("Panasonic DC-ZS200",),
    "DMC-TZ60": ("Panasonic DMC-ZS40",),
    "DMC-TZ61": ("Panasonic DMC-ZS40",),
    "DMC-TZ70": ("Panasonic DMC-ZS50",),
    "DMC-TZ80": ("Panasonic DMC-ZS60",),
    "DMC-TZ81": ("Panasonic DMC-ZS60",),

    # Konica Minolta's Alpha/Dynax/Maxxum names identify the same bodies in
    # different markets.
    "ALPHA SWEET DIGITAL": ("Konica Minolta Maxxum 5D",),
    "ALPHA-7 DIGITAL": ("Konica Minolta Maxxum 7D",),
    "DYNAX 5D": ("Konica Minolta Maxxum 5D",),
    "DYNAX 7D": ("Konica Minolta Maxxum 7D",),

    # Olympus model strings in older files omit spaces or join the regional
    # suffix to the body name.
    "E-M10MarkIIIS": ("Olympus E-M10 Mark III",),
    "STYLUS1,1s": ("Olympus STYLUS 1s",),

    # Sony regional suffixes identify the same camera body as the base model.
    "ILCE-3500": ("Sony ILCE-3000",),
    "ILCE-6001": ("Sony ILCE-6000",),
    "SLT-A65V": ("Sony SLT-A65",),
    "SLT-A77V": ("Sony SLT-A77",),
    "ZV-1": ("Sony ZV-1A",),

    # Kodak's EXIF model is verbose while Adobe uses the short camera name.
    "KODAK EasyShare Z981 Digital Camera": ("Kodak Z981",),
    "KODAK EasyShare Z990 Digital Camera": ("Kodak Z990",),

    # The Leaf sample contains the back and host body in one EXIF string; the
    # Aptus back is the calibrated camera identity Adobe exposes.
    "Leaf Aptus 22(LF10043    )/Mamiya 645 AFD": ("Leaf Aptus 22",),
}


_MODEL_ALIAS_LOOKUP: dict[str, tuple[str, ...]] = {
    normalized(key): tuple(value) for key, value in MODEL_ALIASES.items()
}

# A restriction may include the vendor name while the RAW's model tag does
# not.  These are the only prefixes ignored by the strict matcher.  In
# particular, this prevents ``Olympus E-1`` from accidentally selecting
# ``Fujifilm X-E1`` merely because both normalized strings end in ``e1``.
_PROFILE_VENDOR_PREFIXES = {
    "apple", "asus", "canon", "dji", "fujifilm", "google", "hasselblad",
    "kodak", "konica", "konica minolta", "konicaminolta", "leaf", "leica",
    "lg", "minolta", "nikon", "olympus", "om", "panasonic", "pentax",
    "phase one", "phaseone", "ricoh", "samsung", "seiko epson corp",
    "sigma", "sony", "yuneec",
}


def _model_tokens(value: str) -> tuple[str, ...]:
    return tuple(re.findall(r"[a-z]+|\d+", value.casefold()))


def _strip_vendor_prefix(tokens: tuple[str, ...]) -> tuple[str, ...]:
    # Use the original token stream to recognize multi-word vendor prefixes.
    # The matcher is intentionally conservative: at most the leading vendor
    # words are removed, never arbitrary leading model characters.
    for prefix in sorted(_PROFILE_VENDOR_PREFIXES, key=lambda item: len(_model_tokens(item)), reverse=True):
        prefix_tokens = _model_tokens(prefix)
        if tokens[: len(prefix_tokens)] == prefix_tokens:
            return tokens[len(prefix_tokens) :]
    return tokens


def _strict_model_match(first: str, second: str) -> bool:
    first_tokens = _model_tokens(first)
    second_tokens = _model_tokens(second)
    if not first_tokens or not second_tokens:
        return False
    if first_tokens == second_tokens:
        return True
    return _strip_vendor_prefix(first_tokens) == _strip_vendor_prefix(second_tokens)


def profile_model_aliases(model: str) -> tuple[str, ...]:
    """Return the explicitly approved Adobe model names for a RAW model."""
    aliases = _MODEL_ALIAS_LOOKUP.get(normalized(model), ())
    return tuple(dict.fromkeys((model, *aliases)))


@dataclass(frozen=True)
class RawIdentity:
    make: str
    model: str
    file_type: str


@dataclass(frozen=True)
class GenerationResult:
    identity: RawIdentity
    base_profile: str
    install_directory: str
    profiles: tuple[str, ...]
    reused_cache: bool


def compatible_model(first: str, second: str) -> bool:
    """Compare camera identities without accepting arbitrary suffix matches."""
    if _strict_model_match(first, second):
        return True

    # An explicitly approved regional alias is allowed in either direction so
    # generated-profile verification and cache checks use the same rule as
    # Adobe Standard lookup.
    for source, target in ((first, second), (second, first)):
        if any(_strict_model_match(alias, target) for alias in profile_model_aliases(source)[1:]):
            return True
    return False


def is_fujifilm(make: str) -> bool:
    return "fujifilm" in normalized(make) or normalized(make) == "fuji"


def safe_name(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9._ -]+", "_", value).strip()


def camera_install_directory(root: Path, identity: RawIdentity) -> Path:
    """Keep identically named styles for different cameras from overwriting each other."""
    return root / safe_name(identity.model)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def run(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, check=True, capture_output=True, text=True)


def read_raw_identity(raw_path: Path) -> RawIdentity:
    if not raw_path.is_file():
        raise FileNotFoundError(f"找不到 RAW 文件：{raw_path}")
    if raw_path.suffix.casefold() not in SUPPORTED_EXTENSIONS:
        raise ValueError("请选择相机 RAW 文件，而不是 JPEG、TIFF 或导出图片。")
    completed = run(
        [
            str(find_exiftool()), "-json", "-Make", "-Model", "-UniqueCameraModel",
            "-FileType", str(raw_path),
        ]
    )
    metadata = json.loads(completed.stdout)[0]
    model = metadata.get("UniqueCameraModel") or metadata.get("Model") or ""
    make = metadata.get("Make") or ""
    if not model:
        raise ValueError("无法从这张 RAW 中识别相机型号。")
    if is_fujifilm(make):
        raise ValueError("这款工具用于非富士 RAW；富士相机请直接使用 Lightroom 的 Camera Matching。")
    return RawIdentity(make=make, model=model, file_type=metadata.get("FileType", ""))


def decompile(dcptool: Path, source: Path, destination: Path) -> None:
    run([str(dcptool), "-d", str(source), str(destination)])


def compile_profile(dcptool: Path, source: Path, destination: Path) -> None:
    run([str(dcptool), "-c", str(source), str(destination)])


def _profile_restriction(dcptool: Path, profile: Path, work: Path) -> str:
    xml_path = work / f"inspect-{hashlib.sha1(str(profile).encode()).hexdigest()}.xml"
    decompile(dcptool, profile, xml_path)
    return ET.parse(xml_path).getroot().findtext("UniqueCameraModelRestriction", default="")


def _profile_model_from_filename(candidate: Path) -> str:
    """Remove Adobe's naming suffix, including the underscore spelling."""
    return re.sub(
        r"\s+Adobe[ _]Standard(?:[ _]+v\d+)?$", "", candidate.stem, flags=re.IGNORECASE
    ).strip()


def find_base_profile(model: str, dcptool: Path, work: Path) -> Path:
    candidates: list[Path] = []
    model_names = profile_model_aliases(model)
    for root in adobe_standard_roots():
        if not root.is_dir():
            continue
        for candidate in root.glob("*.dcp"):
            profile_model = _profile_model_from_filename(candidate)
            if any(_strict_model_match(name, profile_model) for name in model_names):
                candidates.append(candidate)
    candidates.sort(key=lambda item: ("v2" not in item.stem.casefold(), item.name))
    for candidate in candidates:
        try:
            restriction = _profile_restriction(dcptool, candidate, work)
            if any(compatible_model(name, restriction) for name in model_names):
                return candidate
        except (OSError, subprocess.CalledProcessError, ET.ParseError):
            continue
    raise FileNotFoundError(
        f"当前 Lightroom/Camera Raw 中找不到 {model} 的 Adobe Standard 配置。请先升级 Adobe 软件。"
    )


def _style_fragment(path: Path) -> list[ET.Element]:
    root = ET.fromstring(f"<fragment>{path.read_text(encoding='utf-8')}</fragment>")
    children = list(root)
    if [child.tag for child in children] != ["LookTable", "ToneCurve"]:
        raise ValueError(f"风格数据结构不完整：{path.name}")
    return children


def _set_text(root: ET.Element, name: str, value: str) -> None:
    element = root.find(name)
    if element is None:
        element = ET.SubElement(root, name)
    element.text = value


def _replace_rendering(root: ET.Element, elements: list[ET.Element]) -> None:
    for tag in ("LookTable", "ToneCurve"):
        current = root.find(tag)
        if current is not None:
            root.remove(current)
    insertion_point = len(root)
    trailing = {
        "ProfileCalibrationSignature", "UniqueCameraModelRestriction",
        "ProfileLookTableEncoding", "BaselineExposureOffset", "DefaultBlackRender",
    }
    for index, child in enumerate(root):
        if child.tag in trailing:
            insertion_point = index
            break
    for offset, element in enumerate(elements):
        root.insert(insertion_point + offset, copy.deepcopy(element))


def _verify_profile(
    dcptool: Path, profile: Path, expected_name: str, expected_model: str, output_xml: Path
) -> None:
    decompile(dcptool, profile, output_xml)
    root = ET.parse(output_xml).getroot()
    actual_name = root.findtext("ProfileName", default="")
    restriction = root.findtext("UniqueCameraModelRestriction", default="")
    if actual_name != expected_name or not compatible_model(expected_model, restriction):
        raise ValueError(f"生成后的配置文件身份校验失败：{profile.name}")
    if root.find("LookTable") is None or root.find("ToneCurve") is None:
        raise ValueError(f"生成后的配置文件缺少风格数据：{profile.name}")


def _cached_result(destination: Path, model: str, base_hash: str) -> GenerationResult | None:
    manifest_path = destination / "manifest.json"
    if not manifest_path.is_file():
        return None
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        files = tuple(manifest["profiles"])
        if (
            compatible_model(model, manifest["identity"]["model"])
            and manifest["base_profile_sha256"] == base_hash
            and manifest.get("style_set") == "eight-color-v1"
            and all((destination / name).is_file() for name in files)
        ):
            return GenerationResult(
                identity=RawIdentity(**manifest["identity"]),
                base_profile=manifest["base_profile"],
                install_directory=str(destination),
                profiles=files,
                reused_cache=True,
            )
    except (KeyError, TypeError, ValueError, json.JSONDecodeError):
        return None
    return None


def generate_and_install(
    raw_path: Path,
    destination: Path | None = None,
    status: StatusCallback = lambda _message: None,
) -> GenerationResult:
    status("正在识别相机……")
    identity = read_raw_identity(raw_path)
    dcptool = find_dcptool()
    style_root = find_style_root()
    destination_root = destination or default_install_root()
    destination = camera_install_directory(destination_root, identity)

    with tempfile.TemporaryDirectory(prefix="fuprofile-unlocker-") as temporary:
        work = Path(temporary)
        status(f"正在查找 {identity.model} 的 Adobe Standard……")
        base_profile = find_base_profile(identity.model, dcptool, work)
        base_hash = sha256(base_profile)
        cached = _cached_result(destination, identity.model, base_hash)
        if cached:
            status("这台相机的八个配置已经安装。")
            return cached

        base_xml = work / "base.xml"
        decompile(dcptool, base_profile, base_xml)
        generated: list[tuple[str, Path]] = []
        for index, (style_name, filename) in enumerate(STYLES, start=1):
            status(f"正在生成 {index}/8：{style_name}")
            tree = ET.parse(base_xml)
            root = tree.getroot()
            profile_name = f"Camera FUJIFILM {style_name}"
            _replace_rendering(root, _style_fragment(style_root / filename))
            _set_text(root, "ProfileName", profile_name)
            _set_text(root, "ProfileLookTableEncoding", "1")
            _set_text(root, "DefaultBlackRender", "1")
            output_name = safe_name(profile_name) + ".dcp"
            source_xml = work / f"style-{index}.xml"
            output_dcp = work / output_name
            tree.write(source_xml, encoding="utf-8", xml_declaration=True)
            compile_profile(dcptool, source_xml, output_dcp)
            _verify_profile(dcptool, output_dcp, profile_name, identity.model, work / f"verify-{index}.xml")
            generated.append((output_name, output_dcp))

        status("正在安装配置文件……")
        destination.mkdir(parents=True, exist_ok=True)
        installed: list[str] = []
        try:
            for name, source in generated:
                temporary_target = destination / f".{name}.tmp"
                shutil.copy2(source, temporary_target)
                os.replace(temporary_target, destination / name)
                installed.append(name)
            manifest = {
                "app_version": __version__,
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "identity": asdict(identity),
                "base_profile": str(base_profile),
                "base_profile_sha256": base_hash,
                "style_set": "eight-color-v1",
                "profiles": installed,
            }
            manifest_temp = destination / ".manifest.json.tmp"
            manifest_temp.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            os.replace(manifest_temp, destination / "manifest.json")
        except Exception:
            for name in installed:
                (destination / name).unlink(missing_ok=True)
            raise

    status("安装完成，请重启 Lightroom。")
    return GenerationResult(
        identity=identity,
        base_profile=str(base_profile),
        install_directory=str(destination),
        profiles=tuple(name for name, _source in generated),
        reused_cache=False,
    )
