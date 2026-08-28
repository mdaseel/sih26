"""TopologyService — the network graph the 2D twin draws.

Nodes and edges come from feeder_network.json, the same network the power flow
solves. The frontend never invents a bus, a line, or a connection.

Layout
------
The IEEE feeder ships no coordinates (feeder_network.json has no bus_geodata),
so x/y are computed here from the electrical structure itself: x is the graph
distance from the source, y separates branches. That makes the drawing a real
single-line diagram — position carries meaning — while remaining honest that
this is a schematic layout, not surveyed geography. Every node is tagged
layout_source = "ELECTRICAL_SCHEMATIC".

The layout is deterministic: the same feeder always produces the same picture.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from functools import lru_cache
from typing import Any

import networkx as nx
import pandapower as pp

from app.core import paths

SOURCE_BUS = "700"


@dataclass
class TwinNode:
    id: str
    type: str  # SUBSTATION | BUS | TRANSFORMER | HOUSE
    label: str
    x: float
    y: float
    vn_kv: float | None = None
    sn_kva: float | None = None
    hops_from_source: int = 0
    pv_eligible: bool = False
    existing_load_kw: float | None = None
    attributes: dict[str, Any] = field(default_factory=dict)


@dataclass
class TwinEdge:
    id: str
    source: str
    target: str
    type: str  # LINE | TRANSFORMER | SWITCH | SERVICE
    label: str
    length_km: float | None = None


class TopologyService:
    def __init__(self) -> None:
        self._net = pp.from_json(str(paths.FEEDER_NETWORK))
        # respect_switches=True is REQUIRED, not a preference. With it False the
        # graph traverses OPEN tie switches, inventing connections that do not
        # exist electrically: paths to the 752-772 branch came out ~8.8 km short
        # and routed through a switch that is open in the model. This also
        # matches compute_electrical_features.py, so distances here agree with
        # the feeder_distance_km feature the model was trained on.
        self._graph = pp.topology.create_nxgraph(self._net, respect_switches=True)
        self._name_by_idx = {
            int(i): str(self._net.bus.name.iloc[int(i)]) for i in range(len(self._net.bus))
        }
        self._idx_by_name = {v: k for k, v in self._name_by_idx.items()}
        self._src_idx = self._idx_by_name[SOURCE_BUS]

        # Hop count from the source drives the horizontal axis.
        self._hops: dict[int, int] = nx.single_source_shortest_path_length(
            self._graph, self._src_idx
        )

    # ---------------- helpers ----------------

    def bus_name(self, idx: int) -> str:
        return self._name_by_idx[int(idx)]

    def path_to(self, bus_id: str) -> list[str]:
        """Bus names along the electrical path source → bus_id.

        Uses the same shortest-path traversal that compute_electrical_features.py
        used to derive upstream impedance, so the diagram matches the features
        the model was trained on.
        """
        target = self._idx_by_name.get(str(bus_id))
        if target is None:
            return []
        try:
            return [self.bus_name(i) for i in nx.shortest_path(self._graph, self._src_idx, target)]
        except nx.NetworkXNoPath:
            return []

    def transformer_for_path(self, path: list[str]) -> dict[str, Any] | None:
        """The last transformer crossed on the way to the bus — the one whose
        loading a rooftop system at that bus actually affects."""
        found = None
        for a, b in zip(path, path[1:]):
            ia, ib = self._idx_by_name[a], self._idx_by_name[b]
            hit = self._net.trafo[
                ((self._net.trafo.hv_bus == ia) & (self._net.trafo.lv_bus == ib))
                | ((self._net.trafo.hv_bus == ib) & (self._net.trafo.lv_bus == ia))
            ]
            if len(hit):
                row = hit.iloc[0]
                found = {
                    "index": int(hit.index[0]),
                    "name": str(row["name"]),
                    "sn_kva": float(row["sn_mva"]) * 1000.0,
                    "hv_bus": self.bus_name(int(row["hv_bus"])),
                    "lv_bus": self.bus_name(int(row["lv_bus"])),
                }
        return found

    def lines_on_path(self, path: list[str]) -> list[dict[str, Any]]:
        out = []
        for a, b in zip(path, path[1:]):
            ia, ib = self._idx_by_name[a], self._idx_by_name[b]
            hit = self._net.line[
                ((self._net.line.from_bus == ia) & (self._net.line.to_bus == ib))
                | ((self._net.line.from_bus == ib) & (self._net.line.to_bus == ia))
            ]
            if len(hit):
                row = hit.iloc[0]
                out.append(
                    {
                        "index": int(hit.index[0]),
                        "name": str(row["name"]),
                        "from_bus": self.bus_name(int(row["from_bus"])),
                        "to_bus": self.bus_name(int(row["to_bus"])),
                        "length_km": float(row["length_km"]),
                    }
                )
        return out

    # ---------------- geography ----------------

    @lru_cache(maxsize=1)
    def distances_km(self) -> dict[str, float]:
        """Route distance from the source to every bus, in km.

        Sums the real length_km of each line along the path, the same way
        compute_electrical_features.py derived feeder_distance_km — so the
        numbers here agree with the model's own features. Transformers and
        closed switches contribute no length, because they have none.
        """
        lengths: dict[tuple[int, int], float] = {}
        for _, row in self._net.line.iterrows():
            a, b = int(row["from_bus"]), int(row["to_bus"])
            lengths[(a, b)] = lengths[(b, a)] = float(row["length_km"])

        out: dict[str, float] = {}
        for idx in range(len(self._net.bus)):
            try:
                path = nx.shortest_path(self._graph, self._src_idx, idx)
            except (nx.NetworkXNoPath, nx.NodeNotFound):
                continue
            out[self.bus_name(idx)] = round(
                sum(lengths.get((a, b), 0.0) for a, b in zip(path, path[1:])), 4
            )
        return out

    @lru_cache(maxsize=8)
    def geo_positions(self, anchor_lat: float, anchor_lon: float) -> dict[str, dict[str, float]]:
        """Illustrative map coordinates for every bus.

        HONESTY NOTE. The IEEE feeder ships no geographic data, so absolute
        position here is invented and must never be presented as surveyed.
        What IS real is the geometry: a bus is placed east of the substation by
        its true route distance in km, and branches are fanned north/south to
        keep them legible. Measure along the feeder on this map and you get the
        real distance; look up where it sits on Earth and you get nothing.

        Deterministic: same feeder and anchor always give the same map.
        """
        distances = self.distances_km()

        # Fan branches out by their vertical slot in the schematic layout, so
        # two buses at the same distance do not land on top of each other.
        by_hop: dict[int, list[int]] = {}
        for idx, hop in sorted(self._hops.items(), key=lambda kv: (kv[1], kv[0])):
            by_hop.setdefault(hop, []).append(idx)

        slot: dict[str, float] = {}
        for members in by_hop.values():
            span = (len(members) - 1) / 2.0
            for n, idx in enumerate(members):
                slot[self.bus_name(idx)] = (n - span) * 0.55  # km of lateral offset

        # Degrees per km. Longitude compresses with latitude.
        import math

        lat_per_km = 1.0 / 110.574
        lon_per_km = 1.0 / (111.320 * max(math.cos(math.radians(anchor_lat)), 1e-6))

        out: dict[str, dict[str, float]] = {}
        for name, dist in distances.items():
            out[name] = {
                "latitude": round(anchor_lat + slot.get(name, 0.0) * lat_per_km, 7),
                "longitude": round(anchor_lon + dist * lon_per_km, 7),
                "distance_km": dist,
            }
        return out

    # ---------------- full graph ----------------

    @lru_cache(maxsize=1)
    def full_graph(self) -> dict[str, Any]:
        """Every bus and every connection, with a schematic layout."""
        from app.services.grid_assets import get_grid_asset_service

        grid = get_grid_asset_service()
        eligible = set(grid.eligible_bus_ids())

        # Group buses by hop distance, then spread each group vertically.
        by_hop: dict[int, list[int]] = {}
        for idx, hop in sorted(self._hops.items(), key=lambda kv: (kv[1], kv[0])):
            by_hop.setdefault(hop, []).append(idx)

        X_STEP, Y_STEP = 180.0, 86.0
        nodes: list[TwinNode] = []
        for hop, members in by_hop.items():
            span = (len(members) - 1) * Y_STEP
            for n, idx in enumerate(members):
                name = self.bus_name(idx)
                is_source = name == SOURCE_BUS
                attrs: dict[str, Any] = {"layout_source": "ELECTRICAL_SCHEMATIC"}
                load_kw = None
                if name in eligible:
                    bus = grid.get(name)
                    load_kw = bus.existing_load_kw
                    attrs |= {
                        "transformer_association": bus.transformer_association,
                        "feeder_section": bus.feeder_section,
                        "base_voltage_pu": bus.base_voltage_pu,
                    }
                nodes.append(
                    TwinNode(
                        id=name,
                        type="SUBSTATION" if is_source else "BUS",
                        label=name,
                        x=hop * X_STEP,
                        y=(n * Y_STEP) - span / 2.0,
                        vn_kv=float(self._net.bus.vn_kv.iloc[idx]),
                        hops_from_source=hop,
                        pv_eligible=name in eligible,
                        existing_load_kw=load_kw,
                        attributes=attrs,
                    )
                )

        edges: list[TwinEdge] = []
        for i, row in self._net.line.iterrows():
            edges.append(
                TwinEdge(
                    id=f"line:{int(i)}",
                    source=self.bus_name(int(row["from_bus"])),
                    target=self.bus_name(int(row["to_bus"])),
                    type="LINE",
                    label=str(row["name"]),
                    length_km=float(row["length_km"]),
                )
            )
        for i, row in self._net.trafo.iterrows():
            edges.append(
                TwinEdge(
                    id=f"trafo:{int(i)}",
                    source=self.bus_name(int(row["hv_bus"])),
                    target=self.bus_name(int(row["lv_bus"])),
                    type="TRANSFORMER",
                    label=str(row["name"]),
                )
            )
        for i, row in self._net.switch.iterrows():
            if row["et"] == "b" and bool(row["closed"]):
                edges.append(
                    TwinEdge(
                        id=f"switch:{int(i)}",
                        source=self.bus_name(int(row["bus"])),
                        target=self.bus_name(int(row["element"])),
                        type="SWITCH",
                        label=str(row.get("name") or f"SW{int(i)}"),
                    )
                )

        return {
            "nodes": [n.__dict__ for n in nodes],
            "edges": [e.__dict__ for e in edges],
            "source_bus": SOURCE_BUS,
            "layout_source": "ELECTRICAL_SCHEMATIC",
            "note": (
                "Positions are derived from electrical distance from the source. "
                "The feeder model carries no geographic coordinates."
            ),
        }

    # ---------------- the affected sub-graph ----------------

    def local_view(self, bus_id: str) -> dict[str, Any]:
        """Source → PV bus, plus the customer premises at the end.

        This is the slice a rooftop system actually influences, and it is what
        the twin animates: the chain the power travels along.
        """
        path = self.path_to(bus_id)
        if not path:
            return {"nodes": [], "edges": [], "path": []}

        from app.services.grid_assets import get_grid_asset_service

        grid = get_grid_asset_service()
        eligible = set(grid.eligible_bus_ids())

        trafo = self.transformer_for_path(path)
        lines = {(l["from_bus"], l["to_bus"]): l for l in self.lines_on_path(path)}

        X_STEP = 150.0
        nodes: list[dict[str, Any]] = []
        for i, name in enumerate(path):
            idx = self._idx_by_name[name]
            node = TwinNode(
                id=name,
                type="SUBSTATION" if name == SOURCE_BUS else "BUS",
                label=name,
                x=i * X_STEP,
                y=0.0,
                vn_kv=float(self._net.bus.vn_kv.iloc[idx]),
                hops_from_source=i,
                pv_eligible=name in eligible,
                existing_load_kw=grid.get(name).existing_load_kw if name in eligible else None,
                attributes={"layout_source": "ELECTRICAL_SCHEMATIC"},
            )
            nodes.append(node.__dict__)

        # The customer premises hang off the connection point.
        nodes.append(
            TwinNode(
                id=f"house:{bus_id}",
                type="HOUSE",
                label="Customer premises",
                x=len(path) * X_STEP,
                y=0.0,
                pv_eligible=False,
                existing_load_kw=grid.get(str(bus_id)).existing_load_kw
                if str(bus_id) in eligible
                else None,
                attributes={"layout_source": "ELECTRICAL_SCHEMATIC", "connected_bus": str(bus_id)},
            ).__dict__
        )

        edges: list[dict[str, Any]] = []
        for a, b in zip(path, path[1:]):
            line = lines.get((a, b)) or lines.get((b, a))
            if line:
                edges.append(
                    TwinEdge(
                        id=f"line:{line['index']}",
                        source=a,
                        target=b,
                        type="LINE",
                        label=line["name"],
                        length_km=line["length_km"],
                    ).__dict__
                )
                continue

            ia, ib = self._idx_by_name[a], self._idx_by_name[b]
            hit = self._net.trafo[
                ((self._net.trafo.hv_bus == ia) & (self._net.trafo.lv_bus == ib))
                | ((self._net.trafo.hv_bus == ib) & (self._net.trafo.lv_bus == ia))
            ]
            if len(hit):
                edges.append(
                    TwinEdge(
                        id=f"trafo:{int(hit.index[0])}",
                        source=a,
                        target=b,
                        type="TRANSFORMER",
                        label=str(hit.iloc[0]["name"]),
                    ).__dict__
                )
            else:
                # A closed bus-bus switch: an ideal, zero-impedance link.
                edges.append(
                    TwinEdge(id=f"link:{a}-{b}", source=a, target=b, type="SWITCH", label="busbar").__dict__
                )

        edges.append(
            TwinEdge(
                id=f"service:{bus_id}",
                source=str(bus_id),
                target=f"house:{bus_id}",
                type="SERVICE",
                label="service connection",
            ).__dict__
        )

        return {
            "nodes": nodes,
            "edges": edges,
            "path": path,
            "serving_transformer": trafo,
            "source_bus": SOURCE_BUS,
            "layout_source": "ELECTRICAL_SCHEMATIC",
        }


@lru_cache
def get_topology_service() -> TopologyService:
    return TopologyService()
