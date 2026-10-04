"""Corpus-wide, zero-execution BinDict container grammar probe.

Imports only the local static byte parser; never imports or executes game data.
The purpose is to test bounded byte grammars and address hypotheses over every
reachable 0x0B reference in the current all_equips_data member.
"""
from __future__ import annotations

from collections import Counter, defaultdict, deque
from pathlib import Path
import csv
import hashlib
import json
import math
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import analyze_pc_bindict_objects as base  # local static parser, main guarded

OUT = HERE
PRIMITIVE_TYPES = {0x01, 0x03, 0x05, 0x0B, 0x11, 0x12, 0x22}
OBJECT_TAGS = {0x06, 0x07, 0x27, 0x36, 0x86, 0x96, 0xC6, 0xD6}
ROOT_TAGS = {0x16, 0x96, 0xD6}


class StaticGrammar:
    def __init__(self, blob: bytes, data_end: int, slots: list[str]):
        self.blob = blob
        self.data_end = data_end
        self.slots = slots
        self.schema_cache: dict[int, tuple[list[dict], int, int]] = {}

    def schema(self, ref: int):
        """Parse a bounded schema without assuming identifier-like labels.

        Root all_equips schemas use identifiers, but a reachable nested schema
        has the literal CHS label ``biped bone23``. Identifier shape is thus a
        semantic convenience, not a framing invariant.
        """
        if ref not in self.schema_cache:
            if not 4 <= ref < self.data_end:
                raise ValueError(f"schema ref out of data region: {ref}")
            pos = ref
            count, pos, _ = base.uleb(self.blob, pos, self.data_end)
            bitmap_bits, pos, _ = base.uleb(self.blob, pos, self.data_end)
            if not (1 <= count <= 4096 and 0 <= bitmap_bits <= count):
                raise ValueError("schema count/bitmap bounds")
            fields = []
            for index in range(count):
                slot, pos, slot_raw = base.uleb(self.blob, pos, self.data_end)
                if pos >= self.data_end or not 0 <= slot < len(self.slots):
                    raise ValueError("schema slot/type bounds")
                type_byte = self.blob[pos]
                pos += 1
                if type_byte not in PRIMITIVE_TYPES:
                    raise ValueError(f"unknown schema type {type_byte:#x}")
                fields.append({
                    "field_index": index,
                    "field_slot": slot,
                    "field_name": self.slots[slot],
                    "type_byte": type_byte,
                    "slot_uleb_hex": slot_raw.hex(),
                })
            self.schema_cache[ref] = (fields, bitmap_bits, pos)
        return self.schema_cache[ref]

    def primitive(self, pos: int, type_byte: int, end: int, source: dict) -> tuple[dict, int, list[dict]]:
        start = pos
        edges = []
        if type_byte == 0x01:
            value, pos, raw = base.uleb(self.blob, pos, end)
            kind = "uleb_unsigned_candidate"
        elif type_byte == 0x03:
            if pos >= end:
                raise ValueError("truncated boolean byte")
            raw = self.blob[pos:pos + 1]
            value = bool(self.blob[pos])
            pos += 1
            kind = "nonzero_bool_candidate"
        elif type_byte == 0x05:
            value_u, pos, raw = base.uleb(self.blob, pos, end)
            if not 0 <= value_u < len(self.slots):
                raise ValueError(f"CHS reference out of bounds: {value_u}")
            value = {"slot": value_u, "text": self.slots[value_u]}
            kind = "CHS_string_ref"
        elif type_byte == 0x0B:
            value_u, pos, raw = base.uleb(self.blob, pos, end)
            value = {"operand_u": value_u}
            kind = "absolute_blob_ref_candidate"
            edges.append({
                **source,
                "operand_start": start,
                "operand_end": pos,
                "operand_uleb_hex": raw.hex(),
                "operand_u": value_u,
            })
        elif type_byte == 0x11:
            unsigned, pos, raw = base.uleb(self.blob, pos, end)
            value = (unsigned >> 1) ^ (-(unsigned & 1))
            kind = "zigzag_int_candidate"
        elif type_byte == 0x12:
            if pos + 4 > end:
                raise ValueError("truncated f32")
            raw = self.blob[pos:pos + 4]
            value = base.struct.unpack_from("<f", self.blob, pos)[0]
            pos += 4
            if not math.isfinite(value):
                raise ValueError("non-finite f32")
            kind = "f32_candidate"
        elif type_byte == 0x22:
            if pos + 8 > end:
                raise ValueError("truncated f64")
            raw = self.blob[pos:pos + 8]
            value = base.struct.unpack_from("<d", self.blob, pos)[0]
            pos += 8
            if not math.isfinite(value):
                raise ValueError("non-finite f64")
            kind = "f64_candidate"
        else:
            raise ValueError(f"unsupported primitive type {type_byte:#x}")
        return {
            "type_byte": f"0x{type_byte:02x}",
            "kind": kind,
            "start": start,
            "end": pos,
            "raw_hex": raw.hex(),
            "value": value,
        }, pos, edges

    def schema_record(self, start: int, tag: int, source_context: dict) -> tuple[dict, list[dict]]:
        pos = start + 1
        schema_ref, pos, schema_raw = base.uleb(self.blob, pos, self.data_end)
        schema, bitmap_bits, schema_end = self.schema(schema_ref)
        bitmap_size = (bitmap_bits + 7) // 8
        if tag in (0xC6, 0xD6):
            bitmap_ref, pos, bitmap_ref_raw = base.uleb(self.blob, pos, self.data_end)
            if not (4 <= bitmap_ref and bitmap_ref + bitmap_size <= self.data_end):
                raise ValueError(f"shared bitmap out of bounds: {bitmap_ref}+{bitmap_size}")
            bitmap = self.blob[bitmap_ref:bitmap_ref + bitmap_size]
            bitmap_mode = "absolute_shared_bitmap_ref"
            bitmap_stream_start = None
            bitmap_stream_end = None
        elif tag in (0x86, 0x96):
            bitmap_ref = None
            bitmap_ref_raw = b""
            bitmap_stream_start = pos
            bitmap_stream_end = pos + bitmap_size
            if bitmap_stream_end > self.data_end:
                raise ValueError("inline bitmap out of data-region bounds")
            bitmap = self.blob[bitmap_stream_start:bitmap_stream_end]
            pos = bitmap_stream_end
            bitmap_mode = "inline_bitmap"
        else:
            raise ValueError(f"not a schema-record tag: {tag:#x}")
        fields = base.selected_fields(schema, bitmap_bits, bitmap)
        values = []
        edges = []
        for field in fields:
            value, pos, new_edges = self.primitive(pos, field["type_byte"], self.data_end, {
                **source_context,
                "container_start": start,
                "field_index": field["field_index"],
                "field_name": field["field_name"],
                "field_slot": field["field_slot"],
                "source_type": "schema_field",
            })
            values.append({
                "field_index": field["field_index"],
                "field_name": field["field_name"],
                "field_slot": field["field_slot"],
                **value,
            })
            edges.extend(new_edges)
        return {
            "start": start,
            "end": pos,
            "length": pos - start,
            "tag": f"0x{tag:02x}",
            "kind": "schema_record",
            "schema_ref": schema_ref,
            "schema_ref_uleb_hex": schema_raw.hex(),
            "schema_end": schema_end,
            "schema_field_count": len(schema),
            "bitmap_bits": bitmap_bits,
            "bitmap_mode": bitmap_mode,
            "bitmap_ref": bitmap_ref,
            "bitmap_ref_uleb_hex": bitmap_ref_raw.hex() if bitmap_ref is not None else None,
            "bitmap_stream_start": bitmap_stream_start,
            "bitmap_stream_end": bitmap_stream_end,
            "bitmap_hex": bitmap.hex(),
            "selected_field_count": len(fields),
            "values": values,
        }, edges

    def object(self, start: int, source_context: dict | None = None) -> tuple[dict, list[dict]]:
        if not 4 <= start < self.data_end:
            raise ValueError(f"object start out of data region: {start}")
        source_context = dict(source_context or {})
        tag = self.blob[start]
        if tag in (0x86, 0x96, 0xC6, 0xD6):
            return self.schema_record(start, tag, source_context)
        if tag == 0x27:
            pos = start + 1
            if pos >= self.data_end:
                raise ValueError("truncated 0x27 element type")
            element_type = self.blob[pos]
            pos += 1
            if element_type not in PRIMITIVE_TYPES:
                raise ValueError(f"unsupported 0x27 element type {element_type:#x}")
            count, pos, count_raw = base.uleb(self.blob, pos, self.data_end)
            if count > 100000:
                raise ValueError("implausible 0x27 count")
            values = []
            edges = []
            for index in range(count):
                value, pos, new_edges = self.primitive(pos, element_type, self.data_end, {
                    **source_context,
                    "container_start": start,
                    "element_index": index,
                    "source_type": "homogeneous_sequence_element",
                })
                values.append(value)
                edges.extend(new_edges)
            return {
                "start": start,
                "end": pos,
                "length": pos - start,
                "tag": "0x27",
                "kind": "homogeneous_sequence_candidate",
                "element_type": f"0x{element_type:02x}",
                "count": count,
                "count_uleb_hex": count_raw.hex(),
                "values": values,
            }, edges
        if tag == 0x07:
            pos = start + 1
            count, pos, count_raw = base.uleb(self.blob, pos, self.data_end)
            if count > 100000:
                raise ValueError("implausible 0x07 count")
            values = []
            edges = []
            for index in range(count):
                if pos >= self.data_end:
                    raise ValueError("truncated 0x07 element type")
                element_type = self.blob[pos]
                pos += 1
                if element_type not in PRIMITIVE_TYPES:
                    raise ValueError(f"unsupported 0x07 element type {element_type:#x}")
                value, pos, new_edges = self.primitive(pos, element_type, self.data_end, {
                    **source_context,
                    "container_start": start,
                    "element_index": index,
                    "source_type": "heterogeneous_sequence_element",
                })
                values.append(value)
                edges.extend(new_edges)
            return {
                "start": start,
                "end": pos,
                "length": pos - start,
                "tag": "0x07",
                "kind": "typed_sequence_candidate",
                "count": count,
                "count_uleb_hex": count_raw.hex(),
                "values": values,
            }, edges
        if tag == 0x36:
            pos = start + 1
            if pos + 2 > self.data_end:
                raise ValueError("truncated 0x36 key/value types")
            key_type = self.blob[pos]
            value_type = self.blob[pos + 1]
            pos += 2
            if key_type not in PRIMITIVE_TYPES or value_type not in PRIMITIVE_TYPES:
                raise ValueError(f"unsupported 0x36 types {key_type:#x}/{value_type:#x}")
            count, pos, count_raw = base.uleb(self.blob, pos, self.data_end)
            if count > 100000:
                raise ValueError("implausible 0x36 count")
            pairs = []
            edges = []
            for index in range(count):
                key, pos, key_edges = self.primitive(pos, key_type, self.data_end, {
                    **source_context,
                    "container_start": start,
                    "pair_index": index,
                    "pair_side": "key",
                    "source_type": "homogeneous_mapping_pair",
                })
                value, pos, value_edges = self.primitive(pos, value_type, self.data_end, {
                    **source_context,
                    "container_start": start,
                    "pair_index": index,
                    "pair_side": "value",
                    "source_type": "homogeneous_mapping_pair",
                })
                pairs.append({"key": key, "value": value})
                edges.extend(key_edges)
                edges.extend(value_edges)
            return {
                "start": start,
                "end": pos,
                "length": pos - start,
                "tag": "0x36",
                "kind": "homogeneous_mapping_candidate",
                "key_type": f"0x{key_type:02x}",
                "value_type": f"0x{value_type:02x}",
                "count": count,
                "count_uleb_hex": count_raw.hex(),
                "pairs": pairs,
            }, edges
        if tag == 0x16:
            # The five root 0x16 rows expose a non-schema mapping form:
            # one homogeneous key type, a ULEB entry count, then each key
            # followed by its own primitive value type and payload.
            pos = start + 1
            if pos >= self.data_end:
                raise ValueError("truncated 0x16 key type")
            key_type = self.blob[pos]
            pos += 1
            if key_type not in PRIMITIVE_TYPES:
                raise ValueError(f"unsupported 0x16 key type {key_type:#x}")
            count, pos, count_raw = base.uleb(self.blob, pos, self.data_end)
            if count > 100000:
                raise ValueError("implausible 0x16 entry count")
            values = []
            edges = []
            for index in range(count):
                key, pos, key_edges = self.primitive(pos, key_type, self.data_end, {
                    **source_context,
                    "container_start": start,
                    "pair_index": index,
                    "pair_side": "key",
                    "source_type": "typed_mapping_pair",
                })
                if pos >= self.data_end:
                    raise ValueError("truncated 0x16 value type")
                value_type = self.blob[pos]
                pos += 1
                if value_type not in PRIMITIVE_TYPES:
                    raise ValueError(f"unsupported 0x16 value type {value_type:#x}")
                field_name = None
                field_slot = None
                if key_type == 0x05 and isinstance(key["value"], dict):
                    field_name = key["value"]["text"]
                    field_slot = key["value"]["slot"]
                value, pos, value_edges = self.primitive(pos, value_type, self.data_end, {
                    **source_context,
                    "container_start": start,
                    "pair_index": index,
                    "field_index": index,
                    "field_name": field_name,
                    "field_slot": field_slot,
                    "source_type": "typed_mapping_value",
                })
                values.append({
                    "field_index": index,
                    "field_name": field_name,
                    "field_slot": field_slot,
                    "key": key,
                    **value,
                })
                edges.extend(key_edges)
                edges.extend(value_edges)
            return {
                "start": start,
                "end": pos,
                "length": pos - start,
                "tag": "0x16",
                "kind": "typed_value_mapping_candidate",
                "key_type": f"0x{key_type:02x}",
                "count": count,
                "count_uleb_hex": count_raw.hex(),
                "values": values,
            }, edges
        if tag == 0x06:
            pos = start + 1
            count, pos, count_raw = base.uleb(self.blob, pos, self.data_end)
            if count != 0:
                raise ValueError("nonempty 0x06 grammar not yet established")
            return {
                "start": start,
                "end": pos,
                "length": pos - start,
                "tag": "0x06",
                "kind": "empty_generic_mapping_candidate",
                "count": count,
                "count_uleb_hex": count_raw.hex(),
                "values": [],
            }, []
        raise ValueError(f"unsupported object tag {tag:#x} at {start}")


def get_value(record: dict, name: str):
    hits = [item["value"] for item in record.get("values", []) if item.get("field_name") == name]
    return hits[0] if len(hits) == 1 else {"match_count": len(hits), "values": hits}


def compact_object(obj: dict) -> dict:
    result = {key: value for key, value in obj.items() if key not in ("values", "pairs")}
    if "values" in obj:
        result["value_count"] = len(obj["values"])
    if "pairs" in obj:
        result["pair_count"] = len(obj["pairs"])
    return result


def main():
    package, members = base.unpack_members()
    slots, chs_meta = base.parse_chs(members[base.CHS_ID]["body"])
    blob, data_end, key_to_start, base_meta = base.parse_base_blob(members[base.BASE_ID]["body"])
    grammar = StaticGrammar(blob, data_end, slots)

    root_tag_counts = Counter(blob[start] for start in key_to_start.values())
    decoded_roots: dict[int, dict] = {}
    root_failures = []
    all_edges = []
    id_checks = []
    for key, start in key_to_start.items():
        tag = blob[start]
        if tag not in (0x16, 0x96, 0xD6):
            root_failures.append({
                "key_u": key,
                "start": start,
                "tag": f"0x{tag:02x}",
                "status": "unexpected_root_tag",
            })
            continue
        try:
            obj, edges = grammar.object(start, {"root_key_u": key, "root_start": start})
            decoded_roots[key] = obj
            all_edges.extend(edges)
            id_value = get_value(obj, "id")
            id_checks.append({"key_u": key, "id_value": id_value, "equal": id_value == key})
        except Exception as exc:
            root_failures.append({
                "key_u": key,
                "start": start,
                "tag": f"0x{tag:02x}",
                "status": "decode_failure",
                "error": repr(exc),
            })

    root_name_by_key = {}
    for key, obj in decoded_roots.items():
        name_value = get_value(obj, "name")
        if isinstance(name_value, dict) and "text" in name_value:
            root_name_by_key[key] = name_value["text"]
        else:
            root_name_by_key[key] = None

    reachable: dict[int, dict] = {}
    reachable_failures = []
    queue = deque()
    queued = set()
    for edge in all_edges:
        target = edge["operand_u"]
        if target not in queued:
            queue.append(target)
            queued.add(target)
    while queue:
        target = queue.popleft()
        try:
            obj, edges = grammar.object(target, {"referenced_target": target})
            reachable[target] = obj
            all_edges.extend(edges)
            for edge in edges:
                child = edge["operand_u"]
                if child not in queued:
                    queue.append(child)
                    queued.add(child)
        except Exception as exc:
            reachable_failures.append({
                "target": target,
                "in_data_region": 4 <= target < data_end,
                "target_byte": f"0x{blob[target]:02x}" if 0 <= target < len(blob) else None,
                "error": repr(exc),
                "context_hex": blob[max(0, target):min(len(blob), target + 64)].hex(" ") if 0 <= target < len(blob) else None,
            })

    unique_edges = []
    edge_identity = set()
    for edge in all_edges:
        identity = (edge.get("operand_start"), edge.get("operand_end"), edge.get("operand_u"))
        if identity in edge_identity:
            continue
        edge_identity.add(identity)
        unique_edges.append(edge)
    all_edges = unique_edges

    all_known_starts = set(key_to_start.values()) | set(reachable)
    for obj in list(decoded_roots.values()) + list(reachable.values()):
        if obj.get("schema_ref") is not None:
            all_known_starts.add(obj["schema_ref"])
        if obj.get("bitmap_ref") is not None:
            all_known_starts.add(obj["bitmap_ref"])
    all_known_starts.add(data_end)

    tag_object_counts = Counter(obj["tag"] for obj in reachable.values())
    tag_edge_counts = Counter(f"0x{blob[e['operand_u']]:02x}" for e in all_edges if 0 <= e["operand_u"] < len(blob))
    object_end_hits_known_start = sum(obj["end"] in all_known_starts for obj in reachable.values())
    object_end_hits_root_start = sum(obj["end"] in set(key_to_start.values()) for obj in reachable.values())
    object_end_hits_ref_start = sum(obj["end"] in set(reachable) for obj in reachable.values())
    boundary_by_tag = {}
    for tag in sorted(tag_object_counts):
        objects = [obj for obj in reachable.values() if obj["tag"] == tag]
        boundary_by_tag[tag] = {
            "unique_object_count": len(objects),
            "end_hits_any_known_start_count": sum(obj["end"] in all_known_starts for obj in objects),
            "end_hits_root_start_count": sum(obj["end"] in set(key_to_start.values()) for obj in objects),
            "end_hits_referenced_start_count": sum(obj["end"] in set(reachable) for obj in objects),
            "min_length": min(obj["length"] for obj in objects),
            "max_length": max(obj["length"] for obj in objects),
        }

    # Falsifiable address-mode discriminators over every decoded 0x0B edge.
    mode_stats = {}
    modes = {
        "blob_absolute": lambda e: e["operand_u"],
        "blob_absolute_plus_4": lambda e: e["operand_u"] + 4,
        "operand_start_plus": lambda e: e["operand_start"] + e["operand_u"],
        "operand_end_plus": lambda e: e["operand_end"] + e["operand_u"],
        "root_start_plus": lambda e: e.get("root_start", e.get("container_start", 0)) + e["operand_u"],
        "operand_start_minus": lambda e: e["operand_start"] - e["operand_u"],
        "operand_end_minus": lambda e: e["operand_end"] - e["operand_u"],
    }
    for mode, fn in modes.items():
        in_bounds = 0
        recognized_tag = 0
        known_start = 0
        tags = Counter()
        for edge in all_edges:
            target = fn(edge)
            if 4 <= target < data_end:
                in_bounds += 1
                tag = blob[target]
                tags[f"0x{tag:02x}"] += 1
                if tag in OBJECT_TAGS:
                    recognized_tag += 1
                if target in reachable:
                    known_start += 1
        mode_stats[mode] = {
            "edge_count": len(all_edges),
            "in_data_region_count": in_bounds,
            "recognized_object_tag_count": recognized_tag,
            "recognized_object_tag_rate_all_edges": recognized_tag / len(all_edges) if all_edges else 0,
            "exact_reachable_object_start_count": known_start,
            "exact_reachable_object_start_rate_all_edges": known_start / len(all_edges) if all_edges else 0,
            "top_target_bytes": dict(tags.most_common(20)),
        }

    incoming = defaultdict(list)
    for edge in all_edges:
        incoming[edge["operand_u"]].append(edge)
    sharing_histogram = Counter(len(edges) for edges in incoming.values())

    target_offsets = (188212, 187449)
    target_details = {}
    reverse_roots = defaultdict(list)
    for key, start in key_to_start.items():
        reverse_roots[start].append(key)
    for target in target_offsets:
        obj = reachable.get(target)
        if obj is None:
            target_details[str(target)] = {"status": "not_reachable_or_failed"}
            continue
        in_edges = incoming[target]
        incoming_roots = []
        for edge in in_edges:
            root_key = edge.get("root_key_u")
            incoming_roots.append({
                "root_key_u": root_key,
                "root_name": root_name_by_key.get(root_key),
                "root_start": edge.get("root_start"),
                "field_name": edge.get("field_name"),
                "field_index": edge.get("field_index"),
                "operand_start": edge.get("operand_start"),
                "operand_end": edge.get("operand_end"),
                "operand_uleb_hex": edge.get("operand_uleb_hex"),
            })
        body_offset = base_meta["header_size"] + target
        decoded_member_offset = members[base.BASE_ID]["body_offset_in_member"] + body_offset
        target_details[str(target)] = {
            "status": "decoded_reachable_object",
            "coordinate_systems": {
                "blob_offset": target,
                "base_body_offset": body_offset,
                "decoded_base_member_offset": decoded_member_offset,
                "packed_NPK_physical_offset": None,
                "packed_offset_note": "No direct physical offset exists through deflate/AES; do not add the decoded offset to the packed member offset.",
            },
            "object": obj,
            "raw_hex": blob[target:obj["end"]].hex(" "),
            "sha256": hashlib.sha256(blob[target:obj["end"]]).hexdigest(),
            "end_is_known_start": obj["end"] in all_known_starts,
            "end_is_root_start": obj["end"] in reverse_roots,
            "root_keys_starting_at_end": reverse_roots.get(obj["end"], []),
            "incoming_edge_count": len(in_edges),
            "incoming_edges": in_edges,
            "incoming_roots": incoming_roots,
        }

    # 0x96 root validation and compact exemplars.
    roots_96 = {key: obj for key, obj in decoded_roots.items() if obj["tag"] == "0x96"}
    roots_d6 = {key: obj for key, obj in decoded_roots.items() if obj["tag"] == "0xd6"}
    roots_16 = {key: obj for key, obj in decoded_roots.items() if obj["tag"] == "0x16"}
    exemplars_96 = {}
    for key in (10003, 10004):
        if key in roots_96:
            obj = roots_96[key]
            exemplars_96[str(key)] = {
                "object": obj,
                "raw_prefix_hex": blob[obj["start"]:min(obj["end"], obj["start"] + 96)].hex(" "),
                "id_value": get_value(obj, "id"),
            }

    # 0x27 exact parse census and compact examples.
    objects_27 = [obj for obj in reachable.values() if obj["tag"] == "0x27"]
    seq_types = Counter(obj["element_type"] for obj in objects_27)
    seq_counts = Counter(obj["count"] for obj in objects_27)
    examples_27 = {}
    for target in (1258, 4569, 5941, 6007, 6287, 6755, 6801):
        if target in reachable and reachable[target]["tag"] == "0x27":
            obj = reachable[target]
            examples_27[str(target)] = {
                "object": obj,
                "raw_hex": blob[target:obj["end"]].hex(" "),
                "end_is_known_start": obj["end"] in all_known_starts,
            }

    attrs_schema_ref = target_details["188212"]["object"]["schema_ref"]
    attrs_schema, attrs_bitmap_bits, attrs_schema_end = grammar.schema(attrs_schema_ref)
    attrs_bitmap_ref = target_details["188212"]["object"]["bitmap_ref"]
    attrs_bitmap_size = (attrs_bitmap_bits + 7) // 8
    attrs_schema_evidence = {
        "schema_ref": attrs_schema_ref,
        "schema_start": attrs_schema_ref,
        "schema_end": attrs_schema_end,
        "schema_length": attrs_schema_end - attrs_schema_ref,
        "schema_raw_hex": blob[attrs_schema_ref:attrs_schema_end].hex(" "),
        "schema_sha256": hashlib.sha256(blob[attrs_schema_ref:attrs_schema_end]).hexdigest(),
        "schema_field_count": len(attrs_schema),
        "bitmap_bits": attrs_bitmap_bits,
        "fields": [{
            "field_index": field["field_index"],
            "field_slot": field["field_slot"],
            "field_name": field["field_name"],
            "type_byte": f"0x{field['type_byte']:02x}",
            "slot_uleb_hex": field["slot_uleb_hex"],
        } for field in attrs_schema],
        "shared_bitmap_ref": attrs_bitmap_ref,
        "shared_bitmap_end": attrs_bitmap_ref + attrs_bitmap_size,
        "shared_bitmap_raw_hex": blob[attrs_bitmap_ref:attrs_bitmap_ref + attrs_bitmap_size].hex(" "),
        "shared_bitmap_sha256": hashlib.sha256(blob[attrs_bitmap_ref:attrs_bitmap_ref + attrs_bitmap_size]).hexdigest(),
        "selected_field_indices": [field["field_index"] for field in attrs_schema if (
            blob[attrs_bitmap_ref + field["field_index"] // 8] & (1 << (field["field_index"] % 8))
        )] if attrs_bitmap_bits else list(range(len(attrs_schema))),
    }

    source_members = {}
    for file_id, member in members.items():
        source_members[f"{file_id:016X}"] = {key: value for key, value in member.items() if key != "body"}

    result = {
        "analysis": "corpus_wide_zero_execution_BinDict_container_grammar_probe",
        "safety": {
            "source_root": "E:/mrzh",
            "source_read_only": True,
            "payload_imported": False,
            "marshal_used": False,
            "exec_eval_compile_used": False,
            "output_root": OUT.as_posix(),
        },
        "package": package,
        "source_members": source_members,
        "base": base_meta,
        "chs": chs_meta,
        "grammar_hypotheses": {
            "schema_shared_bitmap": "tag 0xC6/0xD6 + ULEB absolute schema ref + ULEB absolute bitmap ref + selected scalar payloads",
            "schema_inline_bitmap": "tag 0x86/0x96 + ULEB absolute schema ref + inline ceil(bitmap_bits/8) bitmap + selected scalar payloads",
            "homogeneous_sequence": "0x27 + one-byte primitive element type + ULEB count + count untagged primitive payloads",
            "typed_sequence": "0x07 + ULEB count + repeated one-byte primitive type and payload",
            "homogeneous_mapping": "0x36 + key type + value type + ULEB pair count + untagged primitive key/value payloads",
            "empty_generic_mapping": "0x06 + ULEB zero (only reachable sample; nonempty grammar unresolved)",
            "typed_value_mapping": "0x16 + primitive key type + ULEB entry count + repeated untagged key, one-byte value type, primitive value",
            "root_tag_bit_candidate": "Observed root/reference pairs differ by 0x10 for D6/C6 and 96/86. The 16/06 pair is structurally suggestive, but only nonempty root 16 and empty referenced 06 occur, so the bit's semantic name remains unresolved.",
        },
        "root_coverage": {
            "indexed_row_count": len(key_to_start),
            "root_tag_counts": {f"0x{tag:02x}": count for tag, count in root_tag_counts.items()},
            "decoded_D6_count": len(roots_d6),
            "decoded_96_count": len(roots_96),
            "decoded_16_count": len(roots_16),
            "decode_or_unsupported_count": len(root_failures),
            "root_failures": root_failures,
            "id_field_check_count": len(id_checks),
            "id_equals_outer_key_count": sum(x["equal"] for x in id_checks),
            "id_mismatch_samples": [x for x in id_checks if not x["equal"]][:30],
        },
        "reachable_graph": {
            "decoded_unique_object_count": len(reachable),
            "failed_unique_target_count": len(reachable_failures),
            "failures": reachable_failures,
            "decoded_edge_count": len(all_edges),
            "unique_operand_count": len(incoming),
            "object_tag_unique_counts": dict(tag_object_counts),
            "edge_target_tag_counts": dict(tag_edge_counts),
            "object_end_hits_any_known_start_count": object_end_hits_known_start,
            "object_end_hits_root_start_count": object_end_hits_root_start,
            "object_end_hits_referenced_start_count": object_end_hits_ref_start,
            "boundary_counts_by_tag": boundary_by_tag,
            "sharing_in_degree_histogram": {str(k): v for k, v in sorted(sharing_histogram.items())},
            "max_in_degree": max((len(x) for x in incoming.values()), default=0),
        },
        "address_mode_tests": mode_stats,
        "addressing_verdict": {
            "rule": "0x0B ULEB operand is an unsigned absolute byte offset from blob[0]",
            "blob_definition": "base_body[8 + 4*slot_count:]",
            "status": "verified_on_all_decoded_edges_in_this_hash_locked_table",
            "decoded_edge_count": len(all_edges),
            "absolute_exact_object_start_count": mode_stats["blob_absolute"]["exact_reachable_object_start_count"],
            "counterexample_count": len(all_edges) - mode_stats["blob_absolute"]["exact_reachable_object_start_count"],
            "scope_limit": "This is a table/snapshot-local byte grammar; no universal cross-package claim is made.",
        },
        "target_attrs_objects": target_details,
        "attrs_shared_schema_and_bitmap": attrs_schema_evidence,
        "tag_0x96": {
            "decoded_root_count": len(roots_96),
            "id_equals_outer_key_count": sum(get_value(obj, "id") == key for key, obj in roots_96.items()),
            "exemplars": exemplars_96,
        },
        "tag_0x27": {
            "decoded_unique_object_count": len(objects_27),
            "element_type_counts": dict(seq_types),
            "sequence_count_histogram": {str(k): v for k, v in sorted(seq_counts.items())},
            "examples": examples_27,
        },
        "reachable_objects_compact": {str(start): compact_object(obj) for start, obj in sorted(reachable.items())},
    }
    object_manifest_path = OUT / "02_reachable_object_manifest.csv"
    object_columns = [
        "object_start", "object_end", "length", "tag", "kind", "schema_ref",
        "bitmap_mode", "bitmap_ref", "element_type", "key_type", "value_type",
        "count", "selected_field_count", "value_or_pair_count", "incoming_edge_count",
        "raw_sha256", "end_is_any_known_start", "end_is_root_start", "end_is_referenced_start",
    ]
    with object_manifest_path.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=object_columns)
        writer.writeheader()
        for start, obj in sorted(reachable.items()):
            writer.writerow({
                "object_start": start,
                "object_end": obj["end"],
                "length": obj["length"],
                "tag": obj["tag"],
                "kind": obj["kind"],
                "schema_ref": obj.get("schema_ref"),
                "bitmap_mode": obj.get("bitmap_mode"),
                "bitmap_ref": obj.get("bitmap_ref"),
                "element_type": obj.get("element_type"),
                "key_type": obj.get("key_type"),
                "value_type": obj.get("value_type"),
                "count": obj.get("count"),
                "selected_field_count": obj.get("selected_field_count"),
                "value_or_pair_count": len(obj.get("values", obj.get("pairs", []))),
                "incoming_edge_count": len(incoming[start]),
                "raw_sha256": hashlib.sha256(blob[start:obj["end"]]).hexdigest(),
                "end_is_any_known_start": obj["end"] in all_known_starts,
                "end_is_root_start": obj["end"] in set(key_to_start.values()),
                "end_is_referenced_start": obj["end"] in set(reachable),
            })

    edge_manifest_path = OUT / "03_0x0B_edge_manifest.csv"
    edge_columns = [
        "edge_index", "root_key_u", "root_name", "root_start", "container_start",
        "source_type", "field_index", "field_name", "field_slot", "element_index",
        "pair_index", "pair_side", "operand_start", "operand_end", "operand_uleb_hex",
        "operand_u", "target_tag", "target_kind", "target_end", "target_length",
    ]
    with edge_manifest_path.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=edge_columns)
        writer.writeheader()
        for index, edge in enumerate(all_edges):
            target = edge["operand_u"]
            target_obj = reachable[target]
            root_key = edge.get("root_key_u")
            writer.writerow({
                "edge_index": index,
                "root_key_u": root_key,
                "root_name": root_name_by_key.get(root_key),
                "root_start": edge.get("root_start"),
                "container_start": edge.get("container_start"),
                "source_type": edge.get("source_type"),
                "field_index": edge.get("field_index"),
                "field_name": edge.get("field_name"),
                "field_slot": edge.get("field_slot"),
                "element_index": edge.get("element_index"),
                "pair_index": edge.get("pair_index"),
                "pair_side": edge.get("pair_side"),
                "operand_start": edge["operand_start"],
                "operand_end": edge["operand_end"],
                "operand_uleb_hex": edge["operand_uleb_hex"],
                "operand_u": target,
                "target_tag": target_obj["tag"],
                "target_kind": target_obj["kind"],
                "target_end": target_obj["end"],
                "target_length": target_obj["length"],
            })

    hypothesis_path = OUT / "04_address_hypothesis_tests.csv"
    hypothesis_columns = [
        "mode", "edge_count", "in_data_region_count", "recognized_object_tag_count",
        "recognized_object_tag_rate_all_edges", "exact_reachable_object_start_count",
        "exact_reachable_object_start_rate_all_edges",
    ]
    with hypothesis_path.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=hypothesis_columns)
        writer.writeheader()
        for mode, stats in mode_stats.items():
            writer.writerow({key: stats.get(key, mode if key == "mode" else None) for key in hypothesis_columns})

    attrs_edges_path = OUT / "05_AUG_SCAR_attrs_edges.csv"
    attrs_columns = [
        "target", "target_tag", "target_end", "target_length", "target_raw_hex",
        "schema_ref", "bitmap_ref", "bitmap_hex", "decoded_values_json",
        "root_key_u", "root_name", "root_start", "field_name", "field_index",
        "operand_start", "operand_end", "operand_uleb_hex",
    ]
    attrs_row_count = 0
    with attrs_edges_path.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=attrs_columns)
        writer.writeheader()
        for target_text, detail in target_details.items():
            obj = detail["object"]
            decoded_values = [{
                "field_index": value["field_index"],
                "field_name": value["field_name"],
                "type_byte": value["type_byte"],
                "raw_hex": value["raw_hex"],
                "value": value["value"],
            } for value in obj["values"]]
            for incoming_root in detail["incoming_roots"]:
                writer.writerow({
                    "target": target_text,
                    "target_tag": obj["tag"],
                    "target_end": obj["end"],
                    "target_length": obj["length"],
                    "target_raw_hex": detail["raw_hex"],
                    "schema_ref": obj["schema_ref"],
                    "bitmap_ref": obj["bitmap_ref"],
                    "bitmap_hex": obj["bitmap_hex"],
                    "decoded_values_json": json.dumps(decoded_values, ensure_ascii=False, separators=(",", ":")),
                    **incoming_root,
                })
                attrs_row_count += 1

    result["artifacts"] = {
        "object_manifest_csv": {"path": object_manifest_path.as_posix(), "data_rows": len(reachable)},
        "edge_manifest_csv": {"path": edge_manifest_path.as_posix(), "data_rows": len(all_edges)},
        "address_hypothesis_csv": {"path": hypothesis_path.as_posix(), "data_rows": len(mode_stats)},
        "attrs_edges_csv": {"path": attrs_edges_path.as_posix(), "data_rows": attrs_row_count},
    }
    path = OUT / "01_container_grammar_corpus_probe.json"
    result["artifacts"]["corpus_probe_json"] = {"path": path.as_posix()}
    path.write_text(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    check = json.loads(path.read_text(encoding="utf-8"))
    assert check["package"]["sha256"] == package["sha256"]
    assert check["root_coverage"]["id_equals_outer_key_count"] == len(key_to_start)
    assert check["addressing_verdict"]["counterexample_count"] == 0
    print(json.dumps({
        "output": path.as_posix(),
        "root_coverage": result["root_coverage"],
        "reachable_graph": result["reachable_graph"],
        "absolute_mode": mode_stats["blob_absolute"],
        "other_modes": {k: {kk: vv for kk, vv in v.items() if kk not in ("top_target_bytes",)} for k, v in mode_stats.items() if k != "blob_absolute"},
        "target_summary": {k: {
            "status": v["status"],
            "tag": v.get("object", {}).get("tag"),
            "length": v.get("object", {}).get("length"),
            "end": v.get("object", {}).get("end"),
            "incoming": v.get("incoming_edge_count"),
            "root_keys_at_end": v.get("root_keys_starting_at_end"),
        } for k, v in target_details.items()},
        "tag_0x27_summary": {k: v for k, v in result["tag_0x27"].items() if k != "examples"},
    }, ensure_ascii=False, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
