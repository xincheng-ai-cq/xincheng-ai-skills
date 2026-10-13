#!/usr/bin/env python3
"""Read-only OOXML inventory and declared editability checks (standard library)."""
import argparse
import json
import posixpath
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

NS = {
    "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "c": "http://schemas.openxmlformats.org/drawingml/2006/chart",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
}
RID = "{" + NS["r"] + "}id"
REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"


def compact(value):
    return "".join(char for char in value if not char.isspace())


def manifest(path):
    if path is None:
        return None
    def unique_keys(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("Duplicate manifest key: " + key)
            result[key] = value
        return result
    with open(path, encoding="utf-8-sig") as stream:
        data = json.load(stream, object_pairs_hook=unique_keys)
    if not isinstance(data, dict) or set(data) - {"slide_count", "slides"}:
        raise ValueError("Manifest must be an object with only slide_count and slides")
    if "slide_count" in data and (type(data["slide_count"]) is not int or data["slide_count"] < 1):
        raise ValueError("slide_count must be a positive integer")
    if "slides" in data and not isinstance(data["slides"], list):
        raise ValueError("slides must be an array")
    allowed = {"number", "min_textboxes", "min_native_shapes", "min_tables", "min_charts", "required_text", "require_chart_workbooks"}
    seen = set()
    for item in data.get("slides", []):
        if not isinstance(item, dict) or set(item) - allowed:
            raise ValueError("Slide expectation has unknown keys or is not an object")
        number = item.get("number")
        if type(number) is not int or number < 1 or number in seen:
            raise ValueError("Slide number must be a unique positive integer")
        seen.add(number)
        if "slide_count" in data and number > data["slide_count"]:
            raise ValueError("Slide number exceeds declared slide_count")
        for key in allowed - {"number", "required_text", "require_chart_workbooks"}:
            if key in item and (type(item[key]) is not int or item[key] < 0):
                raise ValueError(key + " must be a nonnegative integer")
        if "require_chart_workbooks" in item and type(item["require_chart_workbooks"]) is not bool:
            raise ValueError("require_chart_workbooks must be a boolean")
        if "required_text" in item:
            texts = item["required_text"]
            if not isinstance(texts, list) or any(not isinstance(t, str) or not compact(t) for t in texts):
                raise ValueError("required_text must be an array of nonblank strings")
    return data


class Package:
    def __init__(self, archive):
        self.archive = archive
        self.names = set(archive.namelist())

    def xml(self, name):
        return ET.fromstring(self.archive.read(name))

    def relationships(self, part):
        folder, name = posixpath.split(part)
        rels = posixpath.join(folder, "_rels", name + ".rels")
        if rels not in self.names:
            return {}
        result = {}
        for rel in self.xml(rels).findall("{" + REL_NS + "}Relationship"):
            identifier = rel.get("Id")
            if not identifier or identifier in result:
                raise ValueError("Missing or duplicate relationship Id in " + rels)
            result[identifier] = dict(rel.attrib)
        return result

    def target(self, part, rel):
        if rel.get("TargetMode") == "External" or not rel.get("Target"):
            return None
        target = rel["Target"]
        name = posixpath.normpath(target.lstrip("/") if target.startswith("/") else posixpath.join(posixpath.dirname(part), target))
        return name if not name.startswith("../") and name in self.names else None


def paragraphs(root):
    result = []
    for paragraph in root.findall(".//a:p", NS):
        text = "".join(node.text or "" for node in paragraph.findall(".//a:t", NS))
        if compact(text):
            result.append(text)
    return result


def chart_info(package, slide_part, rels, node, failures):
    rel = rels.get(node.get(RID), {})
    part = package.target(slide_part, rel)
    info = {"part": part, "workbook_parts": []}
    if not part or not rel.get("Type", "").endswith("/chart"):
        failures.append("Broken native chart relationship in " + slide_part)
        return info
    try:
        root = package.xml(part)
        if root.tag != "{" + NS["c"] + "}chartSpace":
            raise ValueError("Target is not a chartSpace")
        chart_rels = package.relationships(part)
        for external_data in root.findall(".//c:externalData", NS):
            data_rel = chart_rels.get(external_data.get(RID), {})
            workbook = package.target(part, data_rel)
            if workbook and data_rel.get("Type", "").endswith("/package") and posixpath.splitext(workbook)[1].lower() in {".xlsx", ".xls"}:
                info["workbook_parts"].append(workbook)
    except (ET.ParseError, KeyError, ValueError) as exc:
        failures.append("Invalid native chart " + part + ": " + str(exc))
    return info


def inventory(package, part, number, dimensions, failures):
    root = package.xml(part)
    if root.tag != "{" + NS["p"] + "}sld":
        raise ValueError("Slide relationship target is not a slide: " + part)
    tree = root.find("p:cSld/p:spTree", NS)
    if tree is None:
        raise ValueError("Slide has no shape tree: " + part)
    result = dict(number=number, part=part, textboxes=0, native_shapes=0, tables=0, charts=0, images=0, groups=0, text_segments=[], chart_details=[], warnings=[])
    for shape in tree.findall(".//p:sp", NS):
        body = shape.find("p:txBody", NS)
        texts = paragraphs(body) if body is not None else []
        result["text_segments"].extend(texts)
        if texts:
            result["textboxes"] += 1
        elif shape.find("p:spPr/a:prstGeom", NS) is not None or shape.find("p:spPr/a:custGeom", NS) is not None:
            result["native_shapes"] += 1
    result["native_shapes"] += len(tree.findall(".//p:cxnSp", NS))
    for table in tree.findall(".//a:tbl", NS):
        result["tables"] += 1
        result["text_segments"].extend(paragraphs(table))
    rels = package.relationships(part)
    for chart in tree.findall(".//c:chart", NS):
        result["charts"] += 1
        result["chart_details"].append(chart_info(package, part, rels, chart, failures))
    result["chart_workbooks"] = sum(bool(chart["workbook_parts"]) for chart in result["chart_details"])
    result["groups"] = len(tree.findall(".//p:grpSp", NS))
    for picture in tree.findall(".//p:pic", NS):
        result["images"] += 1
        transform = picture.find("p:spPr/a:xfrm", NS)
        if transform is None or not all(dimensions):
            continue
        offset, extent = transform.find("a:off", NS), transform.find("a:ext", NS)
        if offset is None or extent is None:
            continue
        x, y, width, height = (int(offset.get("x", 0)), int(offset.get("y", 0)), int(extent.get("cx", 0)), int(extent.get("cy", 0)))
        overlap_w = max(0, min(x + width, dimensions[0]) - max(x, 0))
        overlap_h = max(0, min(y + height, dimensions[1]) - max(y, 0))
        if overlap_w * overlap_h >= 0.85 * dimensions[0] * dimensions[1]:
            result["warnings"].append("Near-fullpage image; compare with source to distinguish background from flattened content (group transforms are not applied)")
    if not result["text_segments"]:
        result["warnings"].append("No native textbox or table text")
    if not any(result[key] for key in ("textboxes", "native_shapes", "tables", "charts", "images", "groups")):
        result["warnings"].append("No recognized objects")
    return result


def audit(path, expected):
    failures = []
    with zipfile.ZipFile(path) as archive:
        package = Package(archive)
        presentation = package.xml("ppt/presentation.xml")
        size = presentation.find("p:sldSz", NS)
        dimensions = (int(size.get("cx", 0)), int(size.get("cy", 0))) if size is not None else (0, 0)
        rels = package.relationships("ppt/presentation.xml")
        slides = []
        for node in presentation.findall("p:sldIdLst/p:sldId", NS):
            rel = rels.get(node.get(RID), {})
            part = package.target("ppt/presentation.xml", rel)
            if not part or not rel.get("Type", "").endswith("/slide"):
                raise ValueError("Broken presentation slide relationship")
            slides.append(inventory(package, part, len(slides) + 1, dimensions, failures))
    if expected is not None:
        if "slide_count" in expected and expected["slide_count"] != len(slides):
            failures.append("slide_count: expected " + str(expected["slide_count"]) + ", found " + str(len(slides)))
        for item in expected.get("slides", []):
            number = item["number"]
            if number > len(slides):
                failures.append("Slide " + str(number) + " is missing")
                continue
            slide = slides[number - 1]
            for key in ("textboxes", "native_shapes", "tables", "charts"):
                if slide[key] < item.get("min_" + key, 0):
                    failures.append("Slide " + str(number) + " " + key + ": expected at least " + str(item["min_" + key]) + ", found " + str(slide[key]))
            for text in item.get("required_text", []):
                if not any(compact(text) in compact(segment) for segment in slide["text_segments"]):
                    failures.append("Slide " + str(number) + " missing required_text: " + text)
            if item.get("require_chart_workbooks") and (not slide["charts"] or slide["chart_workbooks"] != slide["charts"]):
                failures.append("Slide " + str(number) + " needs an internal workbook for each native chart")
    return {"slide_count": len(slides), "slides": slides, "expectations_provided": expected is not None, "passed": not failures, "failures": failures, "limitations": ["Structural counts do not certify visual fidelity or full editability", "Workbook relationships do not validate workbook contents, chart data, or compatibility with an editor", "Near-fullpage image geometry does not apply group transforms"]}


def main():
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pptx")
    parser.add_argument("--expect")
    parser.add_argument("--output")
    args = parser.parse_args()
    output_safe = True
    try:
        if args.output:
            destination = Path(args.output)
            for path in (args.pptx, args.expect):
                if path and (destination.resolve() == Path(path).resolve() or (destination.exists() and Path(path).exists() and destination.samefile(path))):
                    output_safe = False
                    raise ValueError("--output must not overwrite the input PPTX or expectation manifest")
        report = audit(args.pptx, manifest(args.expect))
        code = 0 if report["passed"] else 1
    except (OSError, KeyError, ValueError, ET.ParseError, zipfile.BadZipFile, zipfile.LargeZipFile, RuntimeError) as exc:
        report, code = {"error": str(exc), "passed": False}, 2
    serialized = json.dumps(report, ensure_ascii=False, indent=2)
    try:
        if args.output and output_safe:
            Path(args.output).write_text(serialized + "\n", encoding="utf-8")
        print(serialized)
    except OSError as exc:
        print("Report output error: " + str(exc), file=sys.stderr)
        return 2
    return code


if __name__ == "__main__":
    sys.exit(main())
