import gzip
import json
import math
import os
import random
import re
from collections import defaultdict
from datetime import date, timedelta
from itertools import combinations
from .diplomacy import Diplomacy
from .time_system import TimeSystem
from .ai import AISystem
from .events import EventSystem
from .ideology import (
    adopt, develop as develop_ideology, validate_development,
)
from .ideology import ideology_bonuses
from .technology import research, validate_research
from .country import Country
from .war import War
from .political_courses import (
    COURSES_BY_ID, course_available, political_courses_for,
)
from .emergency_measures import (
    EMERGENCY_MEASURE_TREE, EMERGENCY_MEASURES_BY_ID,
    emergency_measure_available, emergency_measure_bonuses,
)
from .decision_events import DECISION_EVENTS_BY_ID
from .zombie_mode import ideology_options, ideology_tree, technology_tree
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from config import DATA_DIR


class Region:
    def __init__(self, data):
        self.id = data["id"]
        self.unit_id = data.get("unit_id", self.id)
        self.name = data["name"]
        self.owner = data["owner"]
        self.initial_owner = data.get("initial_owner", self.owner)
        self.occupied = data.get("occupied", False)
        source_polygons = data.get("polygons", [data["points"]])
        self.polygons = [[tuple(point) for point in polygon] for polygon in source_polygons]
        self.points = [tuple(point) for point in data.get("points", self.polygons[0])]
        self.render_points = [tuple(point) for point in data.get("render_points", self.points)]
        self.fine_points = [tuple(point) for point in data.get("fine_points", self.render_points)]
        self.render_polygons = [
            [tuple(point) for point in polygon]
            for polygon in data.get("render_polygons", self.polygons)
        ]
        self.development = 50
        self.label_point = tuple(data["label_point"]) if data.get("label_point") else None
        all_points = [point for polygon in self.polygons for point in polygon]
        self.bounds = (
            min(point[0] for point in all_points),
            min(point[1] for point in all_points),
            max(point[0] for point in all_points),
            max(point[1] for point in all_points),
        )

    def to_dict(self):
        return {"id": self.id, "name": self.name, "owner": self.owner,
                "initial_owner": self.initial_owner,
                "points": [list(point) for point in self.points],
                "development": self.development,
                "occupied": self.occupied,
                "label_point": list(self.label_point) if self.label_point else None}


ISO_ALIASES = {
    "USA": "usa", "CAN": "canada", "MEX": "mexico", "BRA": "brazil",
    "ARG": "argentina", "GBR": "uk", "FRA": "france", "DEU": "germany",
    "ESP": "spain", "ITA": "italy", "RUS": "russia", "TUR": "turkey",
    "EGY": "egypt", "DZA": "algeria", "NGA": "nigeria", "ZAF": "southafrica",
    "SAU": "saudi", "IRN": "iran", "IND": "india", "CHN": "china",
    "JPN": "japan", "KOR": "korea", "IDN": "indonesia", "AUS": "australia",
    "SWE": "sweden", "POL": "poland", "NLD": "netherlands",
    "BEL": "belgium", "PRT": "portugal", "AUT": "austria",
    "CZE": "czechia", "SVK": "slovakia", "SRB": "serbia",
}

CAPITAL_COORDINATES = {
    "usa": (-77.0365, 38.8977), "canada": (-75.6972, 45.4215),
    "mexico": (-99.1332, 19.4326), "brazil": (-47.8825, -15.7942),
    "argentina": (-58.3816, -34.6037), "uk": (-0.1276, 51.5072),
    "france": (2.3522, 48.8566), "germany": (13.4050, 52.5200),
    "spain": (-3.7038, 40.4168), "italy": (12.4964, 41.9028),
    "russia": (37.6173, 55.7558), "ussr": (37.6173, 55.7558),
    "turkey": (32.8597, 39.9334), "egypt": (31.2357, 30.0444),
    "algeria": (3.0588, 36.7538), "nigeria": (7.3986, 9.0765),
    "southafrica": (28.2293, -25.7479), "saudi": (46.6753, 24.7136),
    "iran": (51.3890, 35.6892), "india": (77.2090, 28.6139),
    "china": (116.4074, 39.9042), "japan": (139.6917, 35.6895),
    "korea": (126.9780, 37.5665), "indonesia": (106.8456, -6.2088),
    "australia": (149.1300, -35.2809), "sweden": (18.0686, 59.3293),
    "poland": (21.0122, 52.2297), "netherlands": (4.9041, 52.3676),
    "belgium": (4.3517, 50.8503), "portugal": (-9.1393, 38.7223),
    "austria": (16.3738, 48.2082), "czechia": (14.4378, 50.0755),
    "czechoslovakia": (14.4378, 50.0755), "slovakia": (17.1077, 48.1486),
    "serbia": (20.4489, 44.7866), "yugoslavia": (20.4489, 44.7866),
    "ukraine": (30.5234, 50.4501), "ukr": (30.5234, 50.4501),
    "belarus": (27.5615, 53.9006),
    "norway": (10.7522, 59.9139), "finland": (24.9384, 60.1699),
    "greece": (23.7275, 37.9838), "romania": (26.1025, 44.4268),
    "bulgaria": (23.3219, 42.6977), "georgia": (44.7833, 41.7151),
    "iraq": (44.3661, 33.3152), "syria": (36.2765, 33.5138),
    "afghanistan": (69.2075, 34.5553), "pakistan": (73.0479, 33.6844),
    "bangladesh": (90.4125, 23.8103), "thailand": (100.5018, 13.7563),
    "vietnam": (105.8342, 21.0278), "mongolia": (106.9057, 47.8864),
    "new-zealand": (174.7633, -41.2865),
    "eu": (2.3522, 48.8566), "zombies": (114.3050, 30.5930),
}

MAP_PALETTE = (
    (187, 111, 106), (116, 154, 174), (197, 164, 103), (132, 163, 121),
    (165, 134, 168), (196, 137, 112), (116, 159, 151), (177, 150, 111),
    (131, 147, 184), (194, 150, 158), (153, 165, 115), (177, 132, 105),
    (121, 158, 188), (190, 169, 119), (152, 137, 178), (123, 164, 132),
    (204, 157, 111), (146, 162, 174), (184, 128, 138), (156, 169, 133),
)

ZOMBIE_OUTBREAK_COUNTRIES_BY_CONTINENT = {
    "north_america": ("canada", "mexico"),
    "south_america": ("brazil", "argentina"),
    "europe": ("eu",),
    "africa": ("algeria", "egypt", "nigeria", "southafrica"),
    "asia": (
        "india", "japan", "korea", "iran", "saudi", "indonesia",
        "pakistan", "vietnam", "thailand", "turkey",
    ),
    "oceania": ("australia",),
}

class World:
    def __init__(self):
        self.countries = {}
        self.regions = []
        self.detailed_regions = []
        self.regions_by_id = {}
        self.provinces = []
        self.provinces_by_id = {}
        self.province_index = {}
        self.province_bucket_size = 32
        self.province_neighbors = {}
        self.province_country_ids = set()
        self.capital_provinces = {}
        self.region_border_segments = {}
        self.province_border_segments = {}
        self.region_neighbors = {}
        self.country_neighbors = {}
        self.region_counts = {}
        self.province_counts = {}
        self.wars = {}
        self.war_counter = 0
        self._front_cache = {}
        self.map_revision = 0
        self.map_labels = {}
        self.capital_provinces = {}
        self.player_id = None
        self.day = 0
        self.year = 2026
        self.scenario_id = "modern"
        self.scenario_name = "Современный мир"
        self.scenario_outcome = None
        self.zombie_breach_ready_day = 0
        self.zombie_readiness_penalty_until = 0
        self.international_evacuation_result = None
        self.auto_skip_news = False
        self.decision_events_seen = set()
        self.events = []
        self.notifications = []
        self.pending_modal_events = []
        self.modal_resume_after = False
        self.time = TimeSystem()
        self.rng = random.Random()
        self.diplomacy = Diplomacy(self)
        self.ai = AISystem(self)
        self.event_system = EventSystem(self)

    def load_data(self, scenario_id="modern", build_provinces=True):
        with open(os.path.join(DATA_DIR, "scenarios.json"), "r", encoding="utf-8") as file:
            scenarios = json.load(file)
        if scenario_id not in scenarios:
            raise ValueError(f"Unknown scenario: {scenario_id}")
        scenario = scenarios[scenario_id]
        self.scenario_id = scenario_id
        self.scenario_name = scenario["name"]
        self.year = scenario["year"]
        self.scenario_outcome = None
        self.zombie_breach_ready_day = 0
        self.zombie_readiness_penalty_until = 0
        self.international_evacuation_result = None
        self.auto_skip_news = False
        self.decision_events_seen = set()
        self.map_revision += 1

        with open(os.path.join(DATA_DIR, "countries.json"), "r", encoding="utf-8") as file:
            country_definitions = json.load(file)
        custom_countries = {item["id"]: item for item in country_definitions}
        custom_names = {
            item["id"]: item["name"] for item in country_definitions
        }
        custom_by_iso = {iso: custom_countries[country_id]
                         for iso, country_id in ISO_ALIASES.items()
                         if country_id in custom_countries}
        map_path = os.path.join(DATA_DIR, "world_countries.geojson")
        with open(map_path, "r", encoding="utf-8") as file:
            features = json.load(file)["features"]
        native_country_names = {}
        for feature in features:
            properties = feature["properties"]
            iso = properties.get("ISO_A3")
            if not iso or iso == "-99":
                iso = properties.get("ADM0_A3")
            if not iso or iso == "-99":
                iso = re.sub(
                    r"[^a-z0-9]+", "-",
                    properties.get("ADMIN", "territory").lower(),
                ).strip("-")
            native_country_names.setdefault(
                ISO_ALIASES.get(iso, iso.lower()),
                properties.get("NAME_RU") or properties["ADMIN"],
            )

        self.countries = {}
        self.regions = []
        self.detailed_regions = []
        self.provinces = []
        self.provinces_by_id = {}
        self.province_index = {}
        self.map_labels = {}
        label_candidates = {}
        self.capital_provinces = {}
        self.province_neighbors = {}
        self.province_country_ids = set()
        self.capital_provinces = {}
        self.region_border_segments = {}
        self.province_border_segments = {}
        self.region_neighbors = {}
        self.country_neighbors = {}
        self.region_counts = {}
        self.province_counts = {}
        self.wars = {}
        self.war_counter = 0
        self._front_cache = {}
        for feature in features:
            properties = feature["properties"]
            iso = properties.get("ISO_A3")
            if not iso or iso == "-99":
                iso = properties.get("ADM0_A3")
            if not iso or iso == "-99":
                iso = re.sub(r"[^a-z0-9]+", "-", properties.get("ADMIN", "territory").lower()).strip("-")
            country_id = scenario.get("owner_overrides", {}).get(iso, ISO_ALIASES.get(iso, iso.lower()))
            custom = (
                custom_by_iso.get(iso)
                if scenario_id == "modern" or scenario.get("base_data") == "modern"
                else None
            )
            if country_id not in self.countries:
                data = dict(custom) if custom else self._country_defaults(country_id, properties)
                data["id"] = country_id
                data["name"] = scenario.get("country_names", {}).get(
                    country_id,
                    custom_names.get(country_id)
                    or native_country_names.get(country_id)
                    or data.get("name")
                    or properties.get("NAME_RU")
                    or properties["ADMIN"],
                )
                data["color"] = list(map_color(country_id))
                if scenario_id != "modern" and country_id in scenario.get("country_stats", {}):
                    data.update(scenario["country_stats"][country_id])
                self.countries[country_id] = Country(data)
            elif scenario_id != "modern":
                if country_id not in scenario.get("country_stats", {}):
                    self.countries[country_id].population += int(properties.get("POP_EST") or 0)

            geometry = feature.get("geometry")
            if not geometry:
                continue
            polygons = geometry["coordinates"] if geometry["type"] == "MultiPolygon" else [geometry["coordinates"]]
            label = properties.get("LABEL_X"), properties.get("LABEL_Y")
            label_point = geo_to_map(label) if all(value is not None for value in label) else None
            if label_point:
                iso_owner = ISO_ALIASES.get(iso, iso.lower())
                area = sum(
                    abs(sum(
                        polygon[0][index][0] * polygon[0][(index + 1) % len(polygon[0])][1]
                        - polygon[0][(index + 1) % len(polygon[0])][0] * polygon[0][index][1]
                        for index in range(len(polygon[0]))
                    )) / 2
                    for polygon in polygons
                    if polygon and len(polygon[0]) > 2
                )
                candidate = (0 if iso_owner == country_id else 1, -area, label_point)
                previous = label_candidates.get(country_id)
                if previous is None or candidate[:2] < previous[:2]:
                    label_candidates[country_id] = candidate
            for index, polygon in enumerate(polygons):
                ring = polygon[0]
                points = [geo_to_map(point) for point in ring]
                if len(points) < 3:
                    continue
                region = Region({
                    "id": f"{country_id}_{index}",
                    "name": properties.get("NAME_RU") or properties["ADMIN"],
                    "owner": country_id,
                    "points": points,
                    "label_point": label_point if index == 0 else None,
                })
                self.regions.append(region)

        for country_id, country_data in scenario.get("special_countries", {}).items():
            if country_id in self.countries:
                raise ValueError(f"Special country ID already exists: {country_id}")
            data = dict(country_data)
            data["id"] = country_id
            self.countries[country_id] = Country(data)

        detailed_path = os.path.join(DATA_DIR, "world_countries_50m.geojson")
        with open(detailed_path, "r", encoding="utf-8") as file:
            detailed_features = json.load(file)["features"]
        for feature in detailed_features:
            properties = feature["properties"]
            iso = properties.get("ISO_A3")
            if not iso or iso == "-99":
                iso = properties.get("ADM0_A3")
            if not iso or iso == "-99":
                iso = re.sub(r"[^a-z0-9]+", "-", properties.get("ADMIN", "territory").lower()).strip("-")
            country_id = scenario.get("owner_overrides", {}).get(iso, ISO_ALIASES.get(iso, iso.lower()))
            if country_id not in self.countries:
                continue
            geometry = feature.get("geometry")
            if not geometry:
                continue
            polygons = geometry["coordinates"] if geometry["type"] == "MultiPolygon" else [geometry["coordinates"]]
            for index, polygon in enumerate(polygons):
                points = [geo_to_map(point) for point in polygon[0]]
                if len(points) >= 3:
                    render_points = simplify_polygon(points, 0.45)
                    fine_points = simplify_polygon(points, 0.12)
                    self.detailed_regions.append(Region({
                        "id": f"{country_id}_detail_{index}",
                        "name": self.countries[country_id].name,
                        "owner": country_id,
                        "points": points,
                        "render_points": render_points,
                        "fine_points": fine_points,
                    }))

        ids = list(self.countries)
        for country_id, name in scenario.get("country_names", {}).items():
            if country_id in self.countries:
                self.countries[country_id].name = name
        self.map_labels = {
            country_id: {
                "name": self.countries[country_id].name,
                "point": candidate[2],
            }
            for country_id, candidate in label_candidates.items()
            if country_id in self.countries
        }
        (
            self.region_neighbors,
            self.region_border_segments,
        ) = self._build_boundary_adjacency(self.regions, with_segments=True)
        self.regions_by_id = {region.id: region for region in self.regions}
        self.country_neighbors = {country_id: set() for country_id in self.countries}
        for region_id, neighbors in self.region_neighbors.items():
            region = self.regions_by_id[region_id]
            for neighbor_id in neighbors:
                neighbor = self.regions_by_id[neighbor_id]
                if region.owner != neighbor.owner:
                    self.country_neighbors[region.owner].add(neighbor.owner)

        if build_provinces:
            self._build_provinces(scenario)
            self._index_provinces()
            self._index_capitals()
        for a in ids:
            for b in ids:
                if a != b:
                    self.countries[a].relations[b] = self.rng.randint(-20, 35)
        self._rebuild_territory_counts()
        self._refresh_country_neighbors()
        max_tax_rate = int(scenario.get("max_tax_rate", 30))
        for country in self.countries.values():
            country.tax_rate_cap = max_tax_rate
            country.tax_rate = min(country.tax_rate, max_tax_rate)

    def _build_provinces(self, scenario):
        map_path = os.path.join(DATA_DIR, "world_admin1_regions.json.gz")
        with gzip.open(map_path, "rt", encoding="utf-8") as file:
            features = json.load(file)["features"]
        used_ids = set()
        for feature in features:
            iso = feature.get("country_iso")
            if not iso:
                continue
            country_id = scenario.get(
                "owner_overrides", {}
            ).get(iso, ISO_ALIASES.get(iso, iso.lower()))
            province_owner_overrides = scenario.get(
                "province_owner_overrides", {}
            )
            country_id = province_owner_overrides.get(
                f"{iso}:{feature.get('id') or feature['name']}",
                province_owner_overrides.get(
                    str(feature.get("id") or feature["name"]), country_id
                ),
            )
            if country_id not in self.countries:
                continue
            region_id = str(feature.get("id") or feature["name"]).strip()
            province_id = f"{country_id}_admin1_{region_id}"
            if province_id in used_ids:
                province_id = f"{province_id}_{len(used_ids)}"
            used_ids.add(province_id)
            polygons = feature.get("polygons", [])
            if not polygons:
                continue
            points = polygons[0]
            name = feature.get("name") or feature.get("local_name") or region_id
            province = Region({
                "id": province_id,
                "unit_id": province_id,
                "name": name,
                "owner": country_id,
                "initial_owner": country_id,
                "points": points,
                "polygons": polygons,
                "label_point": (
                    sum(point[0] for point in points) / len(points),
                    sum(point[1] for point in points) / len(points),
                ),
            })
            self.provinces.append(province)
            self.provinces_by_id[province.id] = province

    def _index_provinces(self):
        self.province_index = {}
        bucket_size = self.province_bucket_size
        for province in self.provinces:
            left, top, right, bottom = province.bounds
            for bucket_x in range(math.floor(left / bucket_size), math.floor(right / bucket_size) + 1):
                for bucket_y in range(math.floor(top / bucket_size), math.floor(bottom / bucket_size) + 1):
                    self.province_index.setdefault((bucket_x, bucket_y), []).append(province)
        (
            self.province_neighbors,
            self.province_border_segments,
        ) = self._build_boundary_adjacency(self.provinces, with_segments=True)
        self._connect_isolated_provinces()
        self.province_country_ids = {
            province.initial_owner for province in self.provinces
        }

    def _connect_isolated_provinces(self):
        isolated = [
            province for province in self.provinces
            if not self.province_neighbors.get(province.id)
        ]
        if not isolated:
            return

        for province in isolated:
            candidates = []
            left, top, right, bottom = province.bounds
            bucket_size = self.province_bucket_size
            possible = {}
            for bucket_x in range(
                math.floor((left - 0.15) / bucket_size),
                math.floor((right + 0.15) / bucket_size) + 1,
            ):
                for bucket_y in range(
                    math.floor((top - 0.15) / bucket_size),
                    math.floor((bottom + 0.15) / bucket_size) + 1,
                ):
                    for other in self.province_index.get(
                        (bucket_x, bucket_y), ()
                    ):
                        possible[other.id] = other
            for other in possible.values():
                if (
                    other.id == province.id
                    or other.initial_owner != province.initial_owner
                ):
                    continue
                other_left, other_top, other_right, other_bottom = other.bounds
                gap_x = max(left - other_right, other_left - right, 0)
                gap_y = max(top - other_bottom, other_top - bottom, 0)
                if gap_x > 0.15 or gap_y > 0.15:
                    continue
                distance, first_point, second_point = min(
                    (
                        math.hypot(first_x - second_x, first_y - second_y),
                        (first_x, first_y),
                        (second_x, second_y),
                    )
                    for polygon in province.polygons
                    for first_x, first_y in polygon
                    for other_polygon in other.polygons
                    for second_x, second_y in other_polygon
                )
                if distance <= 1.0:
                    candidates.append(
                        (distance, other, first_point, second_point)
                    )

            if not candidates:
                continue
            center = ((left + right) / 2, (top + bottom) / 2)
            containing = [
                candidate for candidate in candidates
                if any(
                    point_in_polygon(*center, polygon)
                    for polygon in candidate[1].polygons
                )
            ]
            if containing:
                candidates = containing
            nearest = min(item[0] for item in candidates)
            for distance, other, first_point, second_point in candidates:
                if distance <= nearest + 0.25:
                    self.province_neighbors[province.id].add(other.id)
                    self.province_neighbors[other.id].add(province.id)
                    border_key = tuple(sorted((province.id, other.id)))
                    self.province_border_segments.setdefault(
                        border_key, []
                    ).append((first_point, second_point))

    def _index_capitals(self):
        self.capital_provinces = {}
        for country_id, coordinates in CAPITAL_COORDINATES.items():
            if country_id not in self.countries:
                continue
            province = self.get_province(geo_to_map(coordinates))
            if province and province.owner == country_id:
                self.capital_provinces[country_id] = province.id

    @staticmethod
    def _build_boundary_adjacency(regions, with_segments=False):
        edges = defaultdict(set)
        edge_segments = {}
        for region in regions:
            for polygon in region.polygons:
                for first, second in zip(polygon, polygon[1:] + polygon[:1]):
                    start = (round(first[0], 1), round(first[1], 1))
                    end = (round(second[0], 1), round(second[1], 1))
                    if start != end:
                        edge_key = tuple(sorted((start, end)))
                        region_ids = edges[edge_key]
                        if (
                            with_segments and region.id not in region_ids and region_ids
                        ):
                            edge_segments.setdefault(
                                edge_key, (tuple(first), tuple(second))
                            )
                        region_ids.add(region.id)

        adjacency = {region.id: set() for region in regions}
        shared_segments = defaultdict(list)
        for edge_key, region_ids in edges.items():
            if len(region_ids) < 2:
                continue
            for region_id in region_ids:
                adjacency[region_id].update(region_ids - {region_id})
            for first_id, second_id in combinations(sorted(region_ids), 2):
                shared_segments[(first_id, second_id)].append(edge_segments[edge_key])
        return (adjacency, dict(shared_segments)) if with_segments else adjacency

    def _rebuild_territory_counts(self):
        self.region_counts = {country_id: 0 for country_id in self.countries}
        self.province_counts = {country_id: 0 for country_id in self.countries}
        for region in self.regions:
            if region.owner in self.region_counts:
                self.region_counts[region.owner] += 1
        for province in self.provinces:
            if province.owner in self.province_counts:
                self.province_counts[province.owner] += 1

    def _refresh_country_neighbors(self):
        self.country_neighbors = {country_id: set() for country_id in self.countries}
        for regions, adjacency in (
            (self.regions_by_id, self.region_neighbors),
            (self.provinces_by_id, self.province_neighbors),
        ):
            for region_id, neighbors in adjacency.items():
                region = regions.get(region_id)
                if not region:
                    continue
                for neighbor_id in neighbors:
                    neighbor = regions[neighbor_id]
                    if region.owner != neighbor.owner and region.owner in self.country_neighbors:
                        self.country_neighbors[region.owner].add(neighbor.owner)

    def visible_provinces(self, bounds):
        left, top, right, bottom = bounds
        bucket_size = self.province_bucket_size
        visible = {}
        for bucket_x in range(math.floor(left / bucket_size), math.floor(right / bucket_size) + 1):
            for bucket_y in range(math.floor(top / bucket_size), math.floor(bottom / bucket_size) + 1):
                for province in self.province_index.get((bucket_x, bucket_y), ()):
                    if province.id in visible:
                        continue
                    p_left, p_top, p_right, p_bottom = province.bounds
                    if (p_right >= left and p_left <= right
                            and p_bottom >= top and p_top <= bottom):
                        visible[province.id] = province
        return visible.values()

    @staticmethod
    def _country_defaults(country_id, properties):
        population = max(100000, int(properties.get("POP_EST") or 1000000))
        gdp = max(0, float(properties.get("GDP_MD") or 0))
        per_capita = gdp * 1000000 / population
        economy = max(1, min(10, int(per_capita / 6500) + 1))
        return {
            "id": country_id,
            "name": properties.get("NAME_RU") or properties.get("ADMIN", country_id),
            "color": list(map_color(country_id)),
            "population": population,
            "money": 1800 + economy * 470,
            "economy_level": economy,
            "stability": 62,
            "development": min(90, 25 + economy * 7),
            "difficulty": "Сложная" if economy < 4 else "Средняя",
            "strategy": "resource" if properties.get("CONTINENT") == "Africa" else (
                "industrial" if economy >= 7 else "balanced"
            ),
            "food": 58,
            "industry": min(100, 25 + economy * 7),
            "energy": 58,
            "military": min(90, 30 + economy * 5),
            "tax_rate": 12,
        }

    def new_game(self, player_id, scenario_id="modern"):
        self.load_data(scenario_id)
        selectable = self._scenario_settings().get("selectable_countries")
        if selectable and player_id not in selectable:
            raise ValueError(
                f"Country {player_id!r} cannot be selected in scenario {scenario_id!r}"
            )
        if player_id not in self.countries:
            raise ValueError(f"Unknown player country: {player_id}")
        self.player_id = player_id
        self.day = 0
        self.scenario_outcome = None
        self.zombie_breach_ready_day = 0
        self.zombie_readiness_penalty_until = 0
        self.international_evacuation_result = None
        self.auto_skip_news = False
        self.decision_events_seen = set()
        self.events = []
        self.notifications = []
        self.pending_modal_events = []
        self.modal_resume_after = False
        self.time.paused = False
        self.time.speed = 1
        if scenario_id == "zombie":
            for country in self.countries.values():
                country.ideology = "z_horde" if country.id == "zombies" else "z_emergency"
                country.ideology_upgrades.clear()
                country.techs.clear()
                country.political_policies.clear()
                country.emergency_measures.clear()
                country.active_upgrade = None
                country.active_political_course = None
                country.research_points = max(40, country.research_points)
                country.political_power = max(130, country.political_power)
                if country.id == "zombies":
                    country.political_power = max(200, country.political_power)
                title = (
                    "Коллективный разум" if country.id == "zombies"
                    else "Чрезвычайное правительство"
                )
                country.leadership_term = 1
                country.leader = f"{title} №1"
        self.countries[player_id].is_player = True
        if scenario_id == "zombie":
            self._seed_zombie_outbreaks()
        self.add_event(f"{self.countries[player_id].name} начинает кампанию: {self.scenario_name}.")
        if scenario_id == "zombie":
            defenders = [
                country_id for country_id in self.countries
                if country_id != "zombies"
            ]
            self._add_war(
                ["zombies"], defenders,
                {"type": "zombie_outbreak", "target": "zombies"},
            )
            self.add_event(
                "2031 год: всем странам объявлена чрезвычайная угроза заражения.",
                notify=True,
                consequences="Все государства объединились против заражённых орд.",
            )

    def _scenario_settings(self):
        with open(os.path.join(DATA_DIR, "scenarios.json"), "r", encoding="utf-8") as file:
            return json.load(file).get(self.scenario_id, {})

    def _seed_zombie_outbreaks(self):
        for country_ids in ZOMBIE_OUTBREAK_COUNTRIES_BY_CONTINENT.values():
            available_provinces = {
                country_id: [
                    province for province in self.provinces
                    if province.owner == country_id
                ]
                for country_id in country_ids
                if country_id != self.player_id
                and country_id in self.countries
                and not self.countries[country_id].is_defeated
            }
            outbreak_count = self.rng.randint(2, 3)
            for _ in range(outbreak_count):
                eligible_countries = [
                    country_id for country_id, provinces
                    in available_provinces.items() if provinces
                ]
                if not eligible_countries:
                    break
                country_id = self.rng.choice(eligible_countries)
                province = self.rng.choice(available_provinces[country_id])
                available_provinces[country_id].remove(province)
                self._set_region_owner(
                    province, "zombies", kind="province", occupied=False
                )

    def ideology_options_for(self, country_id):
        return ideology_options(self.scenario_id, country_id)

    def ideology_name_for(self, country_id):
        country = self.countries[country_id]
        options = self.ideology_options_for(country_id)
        ideology = options.get(country.ideology)
        if ideology:
            return ideology["name"]
        fallback_id = (
            "z_horde" if country_id == "zombies"
            else "z_emergency" if self.scenario_id == "zombie"
            else "democracy"
        )
        return options[fallback_id]["name"]

    def ideology_tree_for(self, country_id, ideology_id=None):
        country = self.countries[country_id]
        ideology_id = ideology_id or country.ideology
        if self.scenario_id == "zombie":
            return ideology_tree(ideology_id) or ()
        from .ideology import IDEOLOGY_TREES
        return IDEOLOGY_TREES[ideology_id]

    def emergency_measure_global_bonuses(self):
        bonuses = {}
        for country in self.countries.values():
            if country.id == "zombies" or country.is_defeated:
                continue
            for key, value in emergency_measure_bonuses(
                country.emergency_measures
            ).items():
                bonuses[key] = bonuses.get(key, 0) + value
        return bonuses

    def zombie_breach_interval(self):
        reduction = min(
            0.75,
            self.emergency_measure_global_bonuses().get(
                "sea_breach_reduction", 0
            ),
        )
        return math.ceil(30 / (1 - reduction))

    def technology_tree_for(self, country_id):
        return technology_tree(self.scenario_id, country_id)

    def political_courses_for(self, country_id=None):
        return political_courses_for(self.scenario_id, country_id)

    def _update_zombie_scenario_outcome(self):
        if self.scenario_id != "zombie" or self.scenario_outcome:
            return self.scenario_outcome
        player = self.countries.get(self.player_id)
        zombies_remaining = self.province_count("zombies")
        total_provinces = max(1, len(self.provinces))
        if player and player.is_defeated:
            self.scenario_outcome = "player_defeat"
            message = f"Кампания завершена: {player.name} полностью захвачено."
        elif zombies_remaining == 0:
            self.scenario_outcome = "humans_win"
            message = "Человечество отбило заражённые территории и победило."
        elif zombies_remaining >= math.ceil(total_provinces * 0.75):
            self.scenario_outcome = "zombies_win"
            message = "Заражённые захватили 75% мира. Человечество проиграло."
        else:
            return None
        self.time.paused = True
        self.add_event(
            message, notify=True, consequences="Кампания остановлена."
        )
        return self.scenario_outcome

    def date_text(self):
        current = date(self.year, 1, 1) + timedelta(days=self.day)
        return current.strftime("%d.%m.%Y")

    def add_event(self, text, notify=True, modal=False, consequences=None):
        record = {"day": self.day, "year": self.year, "text": text}
        if consequences:
            record["consequences"] = consequences
        self.events.insert(0, record)
        self.events = self.events[:100]
        if notify:
            self.notifications.insert(0, {"text": text, "ttl": 8.0})
            self.notifications = self.notifications[:3]
        if notify and modal and not self.auto_skip_news:
            if not self.pending_modal_events:
                self.modal_resume_after = not self.time.paused
            self.pending_modal_events.append(dict(record))
            self.time.paused = True

    def acknowledge_modal_event(self):
        if not self.pending_modal_events:
            return False
        if self.pending_modal_events[0].get("decision_id"):
            return False
        self.pending_modal_events.pop(0)
        if not self.pending_modal_events:
            if self.modal_resume_after and not self.scenario_outcome:
                self.time.paused = False
            self.modal_resume_after = False
        return True

    def present_decision_event(self, event_id, country_id):
        if self.scenario_id != "zombie":
            return False
        event = DECISION_EVENTS_BY_ID.get(event_id)
        country = self.countries.get(country_id)
        if (
            not event or not country or country.is_defeated
            or event_id in self.decision_events_seen
            or self.pending_modal_events
        ):
            return False
        record = {
            "day": self.day,
            "year": self.year,
            "text": event["title"],
            "description": event["description"],
            "decision_id": event_id,
            "country_id": country_id,
            "choices": event["choices"],
        }
        self.events.insert(0, dict(record))
        self.events = self.events[:100]
        self.notifications.insert(
            0, {"text": event["title"], "ttl": 8.0}
        )
        self.notifications = self.notifications[:3]
        if not self.pending_modal_events:
            self.modal_resume_after = not self.time.paused
        self.pending_modal_events.append(record)
        self.decision_events_seen.add(event_id)
        self.time.paused = True
        return True

    def resolve_decision_event(self, choice_index):
        if not self.pending_modal_events:
            return False, "Нет события, ожидающего решения"
        event = self.pending_modal_events[0]
        event_id = event.get("decision_id")
        if not event_id:
            return False, "Текущее событие не содержит выбора"
        choices = event.get("choices", ())
        if (
            not isinstance(choice_index, int)
            or isinstance(choice_index, bool)
            or not 0 <= choice_index < len(choices)
        ):
            return False, "Неизвестный вариант решения"
        choice = choices[choice_index]
        country_id = event["country_id"]
        details = self._apply_decision_effects(
            country_id, choice.get("effects", {})
        )
        risk = choice.get("risk")
        risk_text = ""
        if risk and self.rng.random() < risk["chance"]:
            details.extend(
                self._apply_decision_effects(
                    country_id, risk.get("effects", {})
                )
            )
            risk_text = f" Риск реализовался: {risk['consequence']}"
        elif risk:
            risk_text = " Риск не реализовался."
        country = self.countries[country_id]
        detail_text = " ".join(details)
        result = (
            f"Мировое решение — {event['text']}: {choice['name']}. "
            f"{country.name}: {choice['consequence']} "
            f"{detail_text}{risk_text}"
        ).strip()
        self.add_event(result, notify=True)
        self.pending_modal_events.pop(0)
        if not self.pending_modal_events:
            if self.modal_resume_after and not self.scenario_outcome:
                self.time.paused = False
            self.modal_resume_after = False
        self._update_zombie_scenario_outcome()
        return True, result

    def _apply_decision_effects(self, country_id, effects):
        country = self.countries[country_id]
        details = []
        bounds = {
            "population": (100_000, None),
            "stability": (0, 100),
            "unrest": (0, 100),
            "political_power": (0, None),
            "research_points": (0, None),
            "army_size": (1000, None),
            "army_readiness": (0, 100),
            "food": (0, 100),
            "energy": (0, 100),
            "industry": (0, 100),
            "development": (0, 100),
        }
        supported_effects = set(bounds) | {
            "money", "army_growth", "military_strength", "unrest_growth",
            "global_military_strength", "lose_regions", "infect_regions",
        }
        unknown_effects = set(effects) - supported_effects
        if unknown_effects:
            raise ValueError(
                "Unknown decision effects: "
                + ", ".join(sorted(unknown_effects))
            )
        for attribute, amount in effects.items():
            if attribute in bounds:
                minimum, maximum = bounds[attribute]
                value = max(minimum, getattr(country, attribute) + amount)
                if maximum is not None:
                    value = min(maximum, value)
                setattr(country, attribute, value)
            elif attribute == "money":
                country.money = max(0, country.money + amount)
            elif attribute == "army_growth":
                country.army_size = max(
                    1000, round(country.army_size * (1 + amount))
                )
            elif attribute in ("military_strength", "unrest_growth"):
                low = -0.75 if attribute == "military_strength" else -1.0
                country.decision_modifiers[attribute] = max(
                    low,
                    min(
                        2.0,
                        country.decision_modifiers.get(attribute, 0) + amount,
                    ),
                )
            elif attribute == "global_military_strength":
                for survivor in self.countries.values():
                    if survivor.id != "zombies" and not survivor.is_defeated:
                        survivor.decision_modifiers["military_strength"] = min(
                            2.0,
                            survivor.decision_modifiers.get(
                                "military_strength", 0
                            ) + amount,
                        )
            elif attribute == "lose_regions":
                details.extend(self._lose_decision_regions(country_id, amount))
            elif attribute == "infect_regions":
                details.extend(self._infect_decision_regions(amount))
        return details

    def _lose_decision_regions(self, country_id, amount):
        provinces = [
            province for province in self.provinces
            if province.owner == country_id
        ]
        if len(provinces) <= 1:
            return [f"{self.countries[country_id].name} не потеряло регионы."]
        exposed = [
            province for province in provinces
            if any(
                self.provinces_by_id[neighbor_id].owner == "zombies"
                for neighbor_id in self.province_neighbors.get(province.id, ())
            )
        ]
        choices = exposed or provinces
        count = min(max(0, int(amount)), len(provinces) - 1)
        lost = self.rng.sample(choices, min(count, len(choices)))
        if len(lost) < count:
            remaining = [province for province in provinces if province not in lost]
            lost.extend(self.rng.sample(remaining, count - len(lost)))
        for province in lost:
            self._set_region_owner(
                province, "zombies", kind="province", occupied=False
            )
        if lost:
            self._update_zombie_scenario_outcome()
            return [
                f"Заражённым досталось {len(lost)} регионов государства "
                f"{self.countries[country_id].name}."
            ]
        return []

    def _infect_decision_regions(self, amount):
        countries = [
            country for country in self.countries.values()
            if country.id != "zombies" and not country.is_defeated
            and self.province_count(country.id) > 1
        ]
        infected = []
        for country in self.rng.sample(
            countries, min(max(0, int(amount)), len(countries))
        ):
            provinces = [
                province for province in self.provinces
                if province.owner == country.id
            ]
            province = self.rng.choice(provinces)
            self._set_region_owner(
                province, "zombies", kind="province", occupied=False
            )
            country.unrest = min(100, country.unrest + 4)
            country.stability = max(0, country.stability - 2)
            infected.append(f"{province.name} ({country.name})")
        if infected:
            self._update_zombie_scenario_outcome()
            return ["Заражение в регионах: " + ", ".join(infected) + "."]
        return []

    def update(self, dt):
        for notification in self.notifications:
            notification["ttl"] -= dt
        self.notifications = [n for n in self.notifications if n["ttl"] > 0]

    def advance_day(self):
        player = self.countries.get(self.player_id)
        if self.scenario_outcome or (player and player.is_defeated):
            self.time.paused = True
            return
        self.day += 1
        days_in_year = (date(self.year, 12, 31) - date(self.year, 1, 1)).days + 1
        if self.day >= days_in_year:
            self.day -= days_in_year
            self.year += 1
        for country in self.countries.values():
            if country.is_defeated:
                continue
            for partner_id, until in list(country.pacts.items()):
                if self.absolute_day() >= until:
                    del country.pacts[partner_id]
            for partner_id, treaty in list(country.treaties.items()):
                expires = treaty.get("expires")
                if expires is not None and self.absolute_day() >= expires:
                    del country.treaties[partner_id]
            country.advance_day(
                self.rng, self.province_count(country.id),
                len(self.wars_for(country.id)),
                zombie_scenario=self.scenario_id == "zombie",
            )
            self._advance_upgrade(country)
            self._advance_political_course(country)
        self._process_rebellions()
        if self.pending_modal_events:
            return
        self.event_system.try_random_event()
        if self.pending_modal_events:
            return
        self.ai.update()
        self._update_zombie_scenario_outcome()
        if self.pending_modal_events:
            return
        absolute_day = self.absolute_day()
        for country in self.countries.values():
            for target, until in list(country.truce_until.items()):
                if absolute_day >= until:
                    del country.truce_until[target]

    def _process_rebellions(self):
        absolute_day = self.absolute_day()
        for country in list(self.countries.values()):
            if (
                (self.scenario_id == "zombie" and country.id == "zombies")
                or country.is_defeated
                or (country.wars and self.scenario_id != "zombie")
                or absolute_day < country.rebellion_cooldown_until
                or country.unrest < 72
                or country.stability > 48
                or country.government_support > 42
                or self.territory_count(country.id) < 2
            ):
                continue
            chance = min(0.012, 0.001 + (country.unrest - 72) * 0.00045)
            if self.rng.random() >= chance:
                continue

            provinces = [
                province for province in self.provinces
                if province.owner == country.id
            ]
            if not provinces:
                provinces = [region for region in self.regions if region.owner == country.id]
                kind = "region"
            else:
                kind = "province"
            if len(provinces) < 2:
                continue

            province = self.rng.choice(provinces)
            rebel_population = max(150_000, int(country.population * 0.06))
            rebel_funds = max(700, country.money * 0.08)
            rebel_army = max(
                5000,
                int(country.army_size * 0.45 + country.population * 0.001),
            )
            if self.scenario_id == "zombie":
                rebel_army = max(2500, int(rebel_army * 0.5))
            rebel_id = f"rebels_{country.id}_{self.day}"
            suffix = 2
            while rebel_id in self.countries:
                rebel_id = f"rebels_{country.id}_{self.day}_{suffix}"
                suffix += 1
            rebel = Country({
                "id": rebel_id,
                "name": f"Повстанцы — {country.name}",
                "color": [184, 67, 59],
                "population": rebel_population,
                "money": rebel_funds,
                "economy_level": 1,
                "stability": 35,
                "development": 25,
                "difficulty": "Сложная",
                "strategy": "expansion",
                "food": 45,
                "industry": 25,
                "energy": 35,
                "military": 48,
                "army_size": rebel_army,
                "army_readiness": 88,
                "government_support": 35,
                "war_support": 85,
                "unrest": 10,
                "ideology": (
                    "z_emergency" if self.scenario_id == "zombie"
                    else "democracy"
                ),
            })
            country.population = max(100_000, country.population - rebel_population)
            country.money = max(0, country.money - rebel_funds)
            country.stability = max(0, country.stability - 8)
            country.government_support = max(0, country.government_support - 10)
            country.rebellion_cooldown_until = absolute_day + 240
            self.countries[rebel_id] = rebel
            self.region_counts[rebel_id] = 0
            self.province_counts[rebel_id] = 0
            for other_id, other in self.countries.items():
                if other_id == rebel_id:
                    continue
                relation = -100 if other_id == country.id else 0
                rebel.relations[other_id] = relation
                other.relations[rebel_id] = relation

            self._set_region_owner(province, rebel_id, kind, occupied=False)
            war = self._add_war(
                [country.id], [rebel_id],
                {"type": "rebellion", "target": rebel_id},
            )
            if self.scenario_id == "zombie":
                self._join_zombie_outbreak(rebel)
            self.capital_provinces[rebel_id] = province.id
            self.add_event(
                f"Восстание в государстве {country.name}: "
                f"повстанцы захватили регион «{province.name}».",
                notify=self.player_id in war.attackers,
            )
            self._update_zombie_scenario_outcome()
            break

    def _join_zombie_outbreak(self, country):
        outbreak = next(
            (
                war for war in self.active_wars()
                if war.objective.get("type") == "zombie_outbreak"
            ),
            None,
        )
        if not outbreak or country.id in outbreak.attackers + outbreak.defenders:
            return
        outbreak.defenders.append(country.id)
        outbreak.started_territories[country.id] = max(
            1, self.territory_count(country.id)
        )
        country.wars.add("zombies")
        zombies = self.countries["zombies"]
        zombies.wars.add(country.id)
        country.relations["zombies"] = -100
        zombies.relations[country.id] = -100
        outbreak.last_progress_day = self.absolute_day()
        self.map_revision += 1

    def absolute_day(self):
        return date(self.year, 1, 1).toordinal() + self.day

    def get_region(self, point, detailed=False):
        x, y = point
        regions = self.detailed_regions if detailed and self.detailed_regions else self.regions
        for region in reversed(regions):
            if point_in_polygon(x, y, region.points):
                return region
        return None

    def get_province(self, point):
        x, y = point
        bucket = (
            math.floor(x / self.province_bucket_size),
            math.floor(y / self.province_bucket_size),
        )
        for province in reversed(self.province_index.get(bucket, ())):
            left, top, right, bottom = province.bounds
            if left <= x <= right and top <= y <= bottom:
                if any(point_in_polygon(x, y, polygon) for polygon in province.polygons):
                    return province
        return None

    def province_count(self, country_id):
        if self.province_counts:
            return self.province_counts.get(country_id, 0)
        return sum(province.owner == country_id for province in self.provinces)

    def territory_count(self, country_id):
        count = self.province_count(country_id)
        if country_id in self.province_country_ids or count:
            return count
        if self.region_counts:
            return self.region_counts.get(country_id, 0)
        return sum(region.owner == country_id for region in self.regions)

    def alliance_partner(self, country_id):
        country = self.countries.get(country_id)
        if not country or not country.alliance or country.is_defeated:
            return None
        partner = self.countries.get(country.alliance)
        if (
            not partner or partner.id == country.id or partner.is_defeated
            or partner.alliance != country.id
        ):
            return None
        return partner

    def _normalize_alliances(self):
        for country in self.countries.values():
            if country.alliance:
                partner = self.countries.get(country.alliance)
                if (
                    not partner or partner.id == country.id or partner.is_defeated
                    or country.is_defeated or partner.alliance != country.id
                ):
                    country.alliance = None
            for partner_id, treaty in list(country.treaties.items()):
                partner = self.countries.get(partner_id)
                if (
                    treaty.get("type") == "alliance"
                    and (
                        not partner or country.alliance != partner_id
                        or partner.alliance != country.id
                    )
                ):
                    del country.treaties[partner_id]

    def _set_region_owner(
        self, region, owner_id, kind=None, occupied=None, update_neighbors=True
    ):
        previous = region.owner
        if previous != owner_id:
            counts = self.province_counts if kind == "province" else self.region_counts
            if kind in ("province", "region") and counts:
                counts[previous] = max(0, counts.get(previous, 0) - 1)
                counts[owner_id] = counts.get(owner_id, 0) + 1
            if kind == "province":
                self.province_country_ids.update((previous, owner_id))
            region.owner = owner_id
            self.map_revision += 1
            self._front_cache.clear()
            if update_neighbors:
                self._refresh_country_neighbors()
        if occupied is not None and region.occupied != occupied:
            region.occupied = occupied
            self.map_revision += 1

    def active_wars(self):
        return [war for war in self.wars.values() if war.status == "active"]

    def wars_for(self, country_id):
        return [war for war in self.active_wars() if war.side(country_id)]

    def war_between(self, first_id, second_id):
        for war in self.active_wars():
            if first_id in war.attackers and second_id in war.defenders:
                return war
            if second_id in war.attackers and first_id in war.defenders:
                return war
        return None

    def offer_peace(self, proposer_id, recipient_id, terms="status_quo"):
        war = self.war_between(proposer_id, recipient_id)
        if not war:
            return False, "Активная война между государствами не найдена"
        if war.objective.get("type") == "zombie_outbreak":
            return False, "Перемирие с заражёнными в этом сценарии невозможно"
        if terms not in {"status_quo", "transfer", "reparations", "capitulation"}:
            return False, "Неизвестные условия мирного предложения"
        if war.peace_offer:
            return False, "Сначала ответьте на действующее предложение мира"
        if war.last_peace_offer_day is not None:
            days_since_offer = self.absolute_day() - war.last_peace_offer_day
            if days_since_offer < 30:
                return False, (
                    "Новое предложение мира можно отправить через "
                    f"{30 - days_since_offer} игровых дней"
                )
        if terms == "capitulation" and not self.can_capitulate(war, proposer_id):
            return False, "Требовать капитуляцию может только побеждающая сторона"

        war.last_peace_offer_day = self.absolute_day()
        war.peace_offer = {
            "proposer": proposer_id,
            "recipient": recipient_id,
            "terms": terms,
            "proposed_day": self.absolute_day(),
        }
        term_names = {
            "status_quo": "перемирие без изменения границ",
            "transfer": "сохранение занятых территорий",
            "reparations": "выплата компенсации",
            "capitulation": "капитуляция",
        }
        proposer = self.countries[proposer_id]
        recipient = self.countries[recipient_id]
        message = (
            f"{proposer.name} предлагает государству {recipient.name}: "
            f"{term_names[terms]}."
        )
        self.add_event(
            message,
            notify=self.player_id in (proposer_id, recipient_id),
            modal=self.player_id in (proposer_id, recipient_id),
        )
        return True, "Предложение мира отправлено; война продолжается до ответа"

    def respond_peace_offer(self, war_id, responder_id, accept):
        war = self.wars.get(war_id)
        offer = war.peace_offer if war and war.status == "active" else None
        if not offer:
            return False, "Действующего предложения мира нет"
        if offer["recipient"] != responder_id:
            return False, "Ответить на это предложение может только его адресат"
        if accept:
            return self.settle_war(
                offer["proposer"], offer["recipient"], offer["terms"]
            )

        war.peace_offer = None
        proposer = self.countries[offer["proposer"]]
        responder = self.countries[responder_id]
        self.add_event(
            f"{responder.name} отклоняет предложение мира от {proposer.name}.",
            notify=self.player_id in (offer["proposer"], responder_id),
            modal=self.player_id in (offer["proposer"], responder_id),
        )
        return True, "Предложение отклонено; война продолжается"

    def withdraw_peace_offer(self, war_id, proposer_id):
        war = self.wars.get(war_id)
        offer = war.peace_offer if war and war.status == "active" else None
        if not offer or offer["proposer"] != proposer_id:
            return False, "Нет вашего действующего предложения мира"
        war.peace_offer = None
        self.add_event(
            f"{self.countries[proposer_id].name} отзывает предложение о мире.",
            notify=self.player_id == proposer_id,
        )
        return True, "Предложение отозвано"

    def respond_ai_peace_offer(self, war):
        if not war or war.status != "active" or not war.peace_offer:
            return False, "Действующего предложения мира нет"
        if war.objective.get("type") == "zombie_outbreak":
            return False, "Перемирие с заражёнными в этом сценарии невозможно"
        offer = war.peace_offer
        responder_id = offer["recipient"]
        if responder_id == self.player_id:
            return False, "На предложение игрока должен ответить игрок"

        winners, losers = self._winning_sides(war)
        recipient = self.countries[responder_id]
        terms = offer["terms"]
        if terms == "capitulation":
            accept = (
                responder_id in losers
                and self.can_capitulate(war, offer["proposer"])
            )
        elif responder_id in winners:
            accept = (
                terms in {"transfer", "reparations"}
                or recipient.war_exhaustion >= 75
                or (
                    recipient.war_exhaustion >= 55
                    and recipient.war_support <= 25
                )
            )
        else:
            accept = (
                self.territory_count(responder_id) == 0
                or recipient.war_exhaustion >= 80
                or (
                    terms == "status_quo"
                    and recipient.war_exhaustion >= 55
                    and recipient.war_support <= 25
                )
            )
        return self.respond_peace_offer(war.id, responder_id, accept)

    def propose_ai_peace(self, war):
        if not war or war.status != "active" or war.peace_offer:
            return False, "Предложение мира уже существует"
        if war.objective.get("type") == "zombie_outbreak":
            return False, "Заражённым нельзя предложить мир в этом сценарии"
        winners, losers = self._winning_sides(war)
        if self.player_id not in winners:
            return False, "ИИ пока не предлагает мир игроку"
        losing_ai = [
            country_id for country_id in losers
            if country_id != self.player_id
        ]
        if not losing_ai:
            return False, "На проигрывающей стороне нет государства ИИ"
        proposer_id = max(
            losing_ai,
            key=lambda item: (
                self.countries[item].war_exhaustion
                + max(0, 100 - self.countries[item].war_support) * 0.6
            ),
        )
        if (
            self.countries[proposer_id].war_exhaustion < 65
            and self.countries[proposer_id].war_support > 20
        ):
            return False, "ИИ пока готов продолжать войну"
        return self.offer_peace(proposer_id, self.player_id, "status_quo")

    def _eligible_ally(self, country_id, enemy_ids):
        country = self.countries[country_id]
        if country.is_defeated:
            return None
        ally = self.alliance_partner(country_id)
        if not ally or ally.id in enemy_ids:
            return None
        if ally.is_defeated or ally.wars:
            return None
        if any(enemy in ally.truce_until for enemy in enemy_ids):
            return None
        return ally.id

    def _add_war(self, attackers, defenders, objective):
        self.war_counter += 1
        war_id = f"war-{self.absolute_day()}-{self.war_counter}"
        war = War(war_id, attackers, defenders, objective, self.absolute_day())
        war.started_territories = {
            country_id: max(
                1, self.territory_count(country_id)
            )
            for country_id in attackers + defenders
        }
        self.wars[war_id] = war
        for attacker_id in war.attackers:
            attacker = self.countries[attacker_id]
            attacker.wars.update(war.defenders)
        for defender_id in war.defenders:
            defender = self.countries[defender_id]
            defender.wars.update(war.attackers)
        for attacker_id in war.attackers:
            for defender_id in war.defenders:
                self.countries[attacker_id].relations[defender_id] = -100
                self.countries[defender_id].relations[attacker_id] = -100
        self.map_revision += 1
        return war

    def declare_war(self, attacker_id, defender_id):
        attacker = self.countries.get(attacker_id)
        defender = self.countries.get(defender_id)
        if not attacker or not defender:
            return False, "Неизвестное государство"
        if attacker_id == defender_id:
            return False, "Нельзя объявить войну самому себе"
        if attacker.is_defeated or defender.is_defeated:
            return False, "Поверженное государство больше не участвует в конфликтах"
        if self.war_between(attacker_id, defender_id):
            return False, "Война уже объявлена"
        if attacker.wars or defender.wars:
            return False, "Одно из государств уже участвует в конфликте"
        if (
            self.alliance_partner(attacker_id) == defender
            or self.alliance_partner(defender_id) == attacker
        ):
            return False, "Нельзя атаковать союзника: сначала расторгните союз"
        if defender_id in attacker.truce_until:
            until = attacker.truce_until[defender_id] - self.absolute_day()
            return False, f"Действует перемирие до дня {until}"
        if (
            attacker.pacts.get(defender_id, 0) > self.absolute_day()
            or defender.pacts.get(attacker_id, 0) > self.absolute_day()
        ):
            return False, "Действует политический пакт о ненападении"

        attackers = [attacker_id]
        attacker_ally = self._eligible_ally(attacker_id, {defender_id})
        if attacker_ally:
            attackers.append(attacker_ally)
        defenders = [defender_id]
        defender_ally = self._eligible_ally(defender_id, set(attackers))
        if defender_ally:
            defenders.append(defender_ally)

        war = self._add_war(attackers, defenders, {"type": "conquest", "target": defender_id})
        participants = ", ".join(self.countries[item].name for item in attackers + defenders)
        if defender_id == self.player_id:
            message = (
                f"Внимание: {attacker.name} объявляет войну вашему государству."
            )
        elif attacker_id == self.player_id:
            message = f"Ваше государство объявляет войну государству {defender.name}."
        elif self.player_id in war.attackers + war.defenders:
            message = (
                f"Ваше государство вступает в войну: {attacker.name} "
                f"против {defender.name}."
            )
        else:
            message = (
                f"{attacker.name} объявляет войну государству {defender.name}."
            )
        self.add_event(
            f"{message} В конфликт вступают: {participants}.",
            notify=self.player_id in war.attackers + war.defenders,
            modal=self.player_id in war.attackers + war.defenders,
        )
        return True, "Конфликт начат с участием доступных союзников"

    def _front_regions(self, attacker_ids, defender_ids):
        cache_key = (
            self.map_revision,
            tuple(sorted(attacker_ids)),
            tuple(sorted(defender_ids)),
        )
        cached = self._front_cache.get(cache_key)
        if cached is not None:
            return cached
        if self.provinces:
            fronts = [
                province for province in self.provinces
                if province.owner in defender_ids
                and any(
                    self.provinces_by_id[neighbor_id].owner in attacker_ids
                    for neighbor_id in self.province_neighbors.get(province.id, ())
                )
            ]
            if "zombies" in attacker_ids:
                exposed = {
                    neighbor_id
                    for province in self.provinces
                    if province.owner in attacker_ids
                    for neighbor_id in self.province_neighbors.get(province.id, ())
                }
                breach = {
                    next_id
                    for exposed_id in exposed
                    for next_id in self.province_neighbors.get(exposed_id, ())
                    if self.provinces_by_id[next_id].owner in defender_ids
                }
                water_gap = 14
                bucket_size = self.province_bucket_size
                defender_set = set(defender_ids)
                for infected in self.provinces:
                    if infected.owner not in attacker_ids:
                        continue
                    left, top, right, bottom = infected.bounds
                    nearby = {}
                    for bucket_x in range(
                        math.floor((left - water_gap) / bucket_size),
                        math.floor((right + water_gap) / bucket_size) + 1,
                    ):
                        for bucket_y in range(
                            math.floor((top - water_gap) / bucket_size),
                            math.floor((bottom + water_gap) / bucket_size) + 1,
                        ):
                            for province in self.province_index.get(
                                (bucket_x, bucket_y), ()
                            ):
                                if province.owner in defender_set:
                                    nearby[province.id] = province
                    for province in nearby.values():
                        p_left, p_top, p_right, p_bottom = province.bounds
                        dx = max(0, left - p_right, p_left - right)
                        dy = max(0, top - p_bottom, p_top - bottom)
                        if dx * dx + dy * dy <= water_gap * water_gap:
                            breach.add(province.id)
                front_ids = {province.id for province in fronts}
                fronts.extend(
                    self.provinces_by_id[province_id]
                    for province_id in breach - front_ids
                )
            if fronts:
                result = (tuple(fronts), "province")
                self._front_cache[cache_key] = result
                return result

        if any(self.province_count(country_id) for country_id in defender_ids):
            result = ((), "province")
            self._front_cache[cache_key] = result
            return result

        fronts = [
            region for region in self.regions
            if region.owner in defender_ids
            and any(
                self.regions_by_id[neighbor_id].owner in attacker_ids
                for neighbor_id in self.region_neighbors.get(region.id, ())
            )
        ]
        result = (tuple(fronts), "region")
        self._front_cache[cache_key] = result
        return result

    def can_attack(self, attacker_id, defender_id):
        war = self.war_between(attacker_id, defender_id)
        if not war:
            return False
        defending_side = war.enemies(attacker_id)
        fronts, _ = self._front_regions([attacker_id], defending_side)
        return any(region.owner == defender_id for region in fronts)

    def resolve_conflict(
        self, attacker_id, defender_id, target_region_id=None,
        cooldown_days=7,
    ):
        attacker = self.countries.get(attacker_id)
        defender = self.countries.get(defender_id)
        war = self.war_between(attacker_id, defender_id)
        if not attacker or not defender or not war:
            return False, "Конфликта нет"
        attacking_side = war.side(attacker_id)
        defending_side = war.enemies(attacker_id)
        if defender_id not in defending_side:
            return False, "Государства находятся на одной стороне конфликта"
        if attacker.money < 120:
            return False, "Нужно 120 денег на подготовку операции"
        ready_day = attacker.battle_cooldowns.get(defender_id, 0)
        if self.absolute_day() < ready_day:
            return False, f"Следующая операция будет доступна через {ready_day - self.absolute_day()} дней"
        fronts, kind = self._front_regions([attacker_id], defending_side)
        fronts = [region for region in fronts if region.owner == defender_id]
        if target_region_id:
            region_index = self.provinces_by_id if kind == "province" else self.regions_by_id
            target = region_index.get(target_region_id)
            if target not in fronts:
                return False, "Эта территория не соединена с фронтом"
            fronts = [target]
        if not fronts:
            return False, "Нет сухопутного доступа к территориям противника"

        target = self._prioritize_front_target(
            fronts, kind, war, [defender_id], target_country_id=defender_id
        )
        defending_country = self.countries[target.owner]
        zombie_water_breach = (
            war.objective.get("type") == "zombie_outbreak"
            and attacker_id == "zombies"
            and not any(
                self.provinces_by_id[neighbor_id].owner == "zombies"
                for neighbor_id in self.province_neighbors.get(target.id, ())
            )
        )
        if (
            zombie_water_breach
            and self.absolute_day() < self.zombie_breach_ready_day
        ):
            return False, (
                "Следующий морской прорыв заражённых будет доступен через "
                f"{self.zombie_breach_ready_day - self.absolute_day()} дней"
            )
        attacker.money -= 120
        if war.objective.get("type") == "zombie_outbreak":
            attack_score = attacker.military_strength(self)
            defend_score = defending_country.military_strength(self)
            if attacker_id == "zombies":
                attack_score *= 0.9 if zombie_water_breach else 1.25
        else:
            attack_score = sum(
                self.countries[item].military_strength(self)
                for item in attacking_side
            )
            defend_score = sum(
                self.countries[item].military_strength(self)
                for item in defending_side
            )
        attack_score *= self.rng.uniform(0.85, 1.15)
        defend_score *= self.rng.uniform(0.85, 1.15)
        attacker.battle_cooldowns[defender_id] = (
            self.absolute_day() + max(
                14 if zombie_water_breach else 1,
                cooldown_days,
            )
        )
        if zombie_water_breach:
            self.zombie_breach_ready_day = (
                self.absolute_day() + self.zombie_breach_interval()
            )
        war.battles += 1
        attackers_won = attack_score >= defend_score
        if attack_score >= defend_score:
            previous_owner = target.owner
            self._set_region_owner(
                target, attacker_id,
                kind="province" if kind == "province" else "region",
                occupied=True,
            )
            occupied = next(
                (item for item in war.occupied_regions if item["id"] == target.id),
                None,
            )
            if occupied is None:
                war.occupied_regions.append({
                    "id": target.id,
                    "kind": kind,
                    "original_owner": previous_owner,
                    "controller": attacker_id,
                })
            else:
                occupied["controller"] = attacker_id
            captured_capital = (
                self.capital_provinces.get(defending_country.id) == target.id
            )
            score_gain = 32 if captured_capital else 12
            result = (
                f"Победа в операции: {attacker.name} занимает регион "
                f"«{target.name}» у {defending_country.name}."
            )
            if captured_capital:
                defending_country.stability = max(0, defending_country.stability - 15)
                defending_country.government_support = max(
                    0, defending_country.government_support - 18
                )
                defending_country.war_exhaustion = min(
                    100, defending_country.war_exhaustion + 20
                )
                result += f" Захвачена столица государства {defending_country.name}!"
            if attacker_id in war.attackers:
                war.attacker_score += score_gain
            else:
                war.defender_score += score_gain
            war.last_progress_day = self.absolute_day()
        else:
            if attacker_id in war.attackers:
                war.defender_score += 10
            else:
                war.attacker_score += 10
            result = f"Операция не удалась: {defending_country.name} удерживает регион «{target.name}»."
        self._apply_conflict_losses(war, attacker, defending_country, attackers_won)
        for participant_id in war.attackers + war.defenders:
            participant = self.countries[participant_id]
            for enemy_id in war.enemies(participant_id):
                participant.relations[enemy_id] = max(
                    -100, participant.relations.get(enemy_id, 0) - 2
                )
        if attacker.war_exhaustion >= 90:
            result += " Усталость армии критическая."
        self.add_event(
            result,
            notify=self.player_id in (attacker_id, defending_country.id),
            modal=False,
        )
        if self.territory_count(defending_country.id) == 0:
            self._handle_country_elimination(
                defending_country.id, attacking_side, source_war=war
            )
        self._update_zombie_scenario_outcome()
        return True, result

    def _prioritize_front_target(
        self, fronts, kind, war, defender_ids, target_country_id=None
    ):
        if not fronts:
            return None
        region_index = self.provinces_by_id if kind == "province" else self.regions_by_id
        adjacency = self.province_neighbors if kind == "province" else self.region_neighbors
        target_country_id = target_country_id or war.objective.get("target")
        capital_id = self.capital_provinces.get(target_country_id)
        if not capital_id or capital_id not in region_index:
            capital_id = next(
                (
                    self.capital_provinces.get(country_id)
                    for country_id in defender_ids
                    if self.capital_provinces.get(country_id) in region_index
                ),
                None,
            )
        capital = region_index.get(capital_id)
        if not capital or capital.owner not in defender_ids:
            return self.rng.choice(fronts)

        distances = {capital.id: 0}
        queue = [capital.id]
        for region_id in queue:
            for neighbor_id in adjacency.get(region_id, ()):
                neighbor = region_index[neighbor_id]
                if neighbor.owner in defender_ids and neighbor_id not in distances:
                    distances[neighbor_id] = distances[region_id] + 1
                    queue.append(neighbor_id)

        reachable_fronts = [
            region for region in fronts if region.id in distances
        ]
        if not reachable_fronts:
            return self.rng.choice(fronts)
        best_distance = min(distances[region.id] for region in reachable_fronts)
        best_fronts = [
            region for region in reachable_fronts
            if distances[region.id] == best_distance
        ]
        return self.rng.choice(best_fronts)

    def _transfer_remaining_territory(self, defender_id, attacker_id):
        for province in self.provinces:
            if province.owner == defender_id:
                self._set_region_owner(
                    province, attacker_id, "province", occupied=False,
                    update_neighbors=False,
                )
        for region in self.regions:
            if region.owner == defender_id:
                self._set_region_owner(
                    region, attacker_id, "region", occupied=False,
                    update_neighbors=False,
                )
        for region in self.detailed_regions:
            if region.owner == defender_id:
                self._set_region_owner(
                    region, attacker_id, occupied=False, update_neighbors=False
                )

    def _apply_conflict_losses(self, war, attacker, defender, attackers_won):
        attacker_fraction = self.rng.uniform(0.004, 0.014) if attackers_won else self.rng.uniform(0.012, 0.032)
        defender_fraction = self.rng.uniform(0.012, 0.032) if attackers_won else self.rng.uniform(0.004, 0.014)
        for country, fraction in ((attacker, attacker_fraction), (defender, defender_fraction)):
            losses = min(country.army_size, max(1, int(country.army_size * fraction)))
            country.army_size -= losses
            war.casualties[country.id] = war.casualties.get(country.id, 0) + losses
        attacker.war_support = max(0, attacker.war_support - (4 if attackers_won else 10))
        defender.war_support = max(0, defender.war_support - (10 if attackers_won else 4))
        attacker_fatigue = 1 + ideology_bonuses(
            attacker.ideology, attacker.ideology_upgrades
        ).get("war_exhaustion", 0)
        defender_fatigue = 1 + ideology_bonuses(
            defender.ideology, defender.ideology_upgrades
        ).get("war_exhaustion", 0)
        attacker.war_exhaustion = min(
            100, attacker.war_exhaustion
            + (4 if attackers_won else 8) * attacker_fatigue
        )
        defender.war_exhaustion = min(
            100, defender.war_exhaustion
            + (8 if attackers_won else 4) * defender_fatigue
        )
        attacker.army_readiness = max(10, attacker.army_readiness - (3 if attackers_won else 8))
        defender.army_readiness = max(10, defender.army_readiness - (8 if attackers_won else 3))
        attacker.military = max(0, attacker.military - (1 if attackers_won else 3))
        defender.military = max(0, defender.military - (3 if attackers_won else 1))
        losing_country = defender if attackers_won else attacker
        losing_country.stability = max(0, losing_country.stability - (4 if attackers_won else 3))

    def can_capitulate(self, war, requester_id=None):
        if isinstance(war, str):
            war = self.wars.get(war)
        if not war or war.status != "active":
            return False
        if war.objective.get("type") == "zombie_outbreak":
            return False
        winners, losers = self._winning_sides(war)
        if requester_id is not None and requester_id not in winners:
            return False
        target_id = war.objective.get("target")
        if target_id not in losers:
            target_id = max(
                losers,
                key=lambda item: (
                    self.countries[item].war_exhaustion,
                    100 - self.countries[item].war_support,
                ),
                default=None,
            )
        target = self.countries.get(target_id)
        if not target or not winners:
            return False
        winning_score = war.attacker_score if winners == war.attackers else war.defender_score
        losing_score = war.defender_score if winners == war.attackers else war.attacker_score
        score_margin = winning_score - losing_score
        started = war.started_territories.get(target_id, 0)
        remaining = self.territory_count(target_id)
        capital_id = self.capital_provinces.get(target_id)
        capital = self.provinces_by_id.get(capital_id)
        capital_lost = capital is not None and capital.owner != target_id
        lost_share = 1 - remaining / max(1, started)
        decisive_defeat = not target.is_player and (
            capital_lost and lost_share >= 0.65
            or lost_share >= 0.55 and target.war_exhaustion >= 85
            and target.war_support <= 15
        )
        exhausted_defeat = (
            lost_share >= 0.35
            and target.war_exhaustion >= 85
            and target.war_support <= 15
            and score_margin >= 35
        )
        return (
            remaining == 0
            or decisive_defeat
            or exhausted_defeat
            or (
                score_margin >= 60
                and lost_share >= 0.45
                and target.war_exhaustion >= 70
                and target.war_support <= 20
            )
        )

    def settle_war(self, first_id, second_id, terms="status_quo"):
        war = self.war_between(first_id, second_id)
        if not war:
            return False, "Активная война не найдена"
        if war.objective.get("type") == "zombie_outbreak":
            return False, "Заражённым нельзя предложить мир в этом сценарии"
        if terms not in {"status_quo", "transfer", "reparations", "capitulation"}:
            return False, "Неизвестный вариант мирного договора"
        if terms == "capitulation" and not self.can_capitulate(war, first_id):
            return False, "Требовать капитуляцию может только побеждающая сторона после тяжёлых потерь противника"

        winners, losers = self._winning_sides(war)
        victor_id = max(winners, key=lambda item: self.countries[item].military_strength(self))
        loser_id = war.objective.get("target")
        if loser_id not in losers:
            loser_id = max(
                losers,
                key=lambda item: (
                    self.countries[item].war_exhaustion,
                    100 - self.countries[item].war_support,
                ),
            )

        if terms == "status_quo":
            self._restore_war_territories(war)
        elif terms == "transfer":
            self._finalize_war_territories(war, winners)
        elif terms == "reparations":
            loser = self.countries[loser_id]
            victor = self.countries[victor_id]
            available_funds = max(0, loser.money)
            payment = min(available_funds, 2000, max(100, available_funds * 0.18))
            loser.money -= payment
            victor.money += payment
            self._finalize_war_territories(war, winners)
        else:
            territory_victor_id = victor_id
            if loser_id == war.objective.get("target"):
                territory_victor_id = next(
                    (
                        country_id for country_id in war.enemies(loser_id)
                        if country_id in winners
                    ),
                    victor_id,
                )
            self._transfer_remaining_territory(
                loser_id, territory_victor_id
            )
            self._finalize_war_territories(war, winners)

        self._refresh_country_neighbors()
        participants = list(war.attackers + war.defenders)
        self._end_war(war, terms)
        for participant_id in participants:
            if self.territory_count(participant_id) == 0:
                self._handle_country_elimination(participant_id, winners)
        descriptions = {
            "status_quo": "перемирие восстановило довоенные границы",
            "transfer": "стороны закрепили занятые территории",
            "reparations": "мирный договор предусматривает компенсацию",
            "capitulation": f"{self.countries[loser_id].name} капитулирует",
        }
        message = f"Война завершена: {descriptions[terms]}."
        player_in_war = self.player_id in war.attackers + war.defenders
        self.add_event(message, notify=player_in_war, modal=player_in_war)
        return True, message

    def _winning_sides(self, war):
        if war.attacker_score == war.defender_score:
            attacker_strength = sum(
                self.countries[country_id].military_strength(self) for country_id in war.attackers
            )
            defender_strength = sum(
                self.countries[country_id].military_strength(self) for country_id in war.defenders
            )
            attackers_won = attacker_strength >= defender_strength
        else:
            attackers_won = war.attacker_score > war.defender_score
        return (
            (war.attackers, war.defenders)
            if attackers_won else (war.defenders, war.attackers)
        )

    def _restore_war_territories(self, war):
        for item in reversed(war.occupied_regions):
            region = (
                self.provinces_by_id.get(item["id"])
                if item["kind"] == "province"
                else self.regions_by_id.get(item["id"])
            )
            if region:
                kind = "province" if item["kind"] == "province" else "region"
                self._set_region_owner(
                    region, item["original_owner"], kind, occupied=False,
                    update_neighbors=False,
                )

    def _finalize_war_territories(self, war, winning_side):
        winners = set(winning_side)
        for item in war.occupied_regions:
            region = (
                self.provinces_by_id.get(item["id"])
                if item["kind"] == "province"
                else self.regions_by_id.get(item["id"])
            )
            if not region:
                continue
            if region.owner not in winners and item["original_owner"] in winners:
                kind = "province" if item["kind"] == "province" else "region"
                self._set_region_owner(
                    region, item["original_owner"], kind, occupied=False,
                    update_neighbors=False,
                )
            else:
                self._set_region_owner(
                    region, region.owner, occupied=False, update_neighbors=False
                )

    def _end_war(self, war, settlement):
        absolute_day = self.absolute_day()
        for attacker_id in war.attackers:
            attacker = self.countries[attacker_id]
            attacker.recovery_ready_day = max(
                attacker.recovery_ready_day, absolute_day + 30
            )
            attacker.wars.difference_update(war.defenders)
            for defender_id in war.defenders:
                attacker.battle_cooldowns.pop(defender_id, None)
                attacker.truce_until[defender_id] = absolute_day + 120
                attacker.relations[defender_id] = min(
                    100, attacker.relations.get(defender_id, -100) + 15
                )
        for defender_id in war.defenders:
            defender = self.countries[defender_id]
            defender.recovery_ready_day = max(
                defender.recovery_ready_day, absolute_day + 30
            )
            defender.wars.difference_update(war.attackers)
            for attacker_id in war.attackers:
                defender.battle_cooldowns.pop(attacker_id, None)
                defender.truce_until[attacker_id] = absolute_day + 120
                defender.relations[attacker_id] = min(
                    100, defender.relations.get(attacker_id, -100) + 15
                )
        war.status = "ended"
        war.settlement = settlement
        war.ended_day = absolute_day
        war.peace_offer = None
        self.map_revision += 1

    def _handle_country_elimination(self, country_id, winning_side=None, source_war=None):
        country = self.countries.get(country_id)
        if not country or self.territory_count(country_id) > 0:
            return False
        active_wars = list(self.wars_for(country_id))
        if country.is_defeated and not active_wars:
            return False

        country.is_defeated = True
        for war in active_wars:
            enemies = list(war.enemies(country_id))
            winners = (
                list(winning_side)
                if war is source_war and winning_side
                else enemies
            )
            country.wars.difference_update(enemies)
            for participant_id in war.attackers + war.defenders:
                if participant_id != country_id:
                    self.countries[participant_id].wars.discard(country_id)

            remaining_occupied = []
            for item in war.occupied_regions:
                if item["original_owner"] != country_id:
                    remaining_occupied.append(item)
                    continue
                region_index = (
                    self.provinces_by_id
                    if item["kind"] == "province" else self.regions_by_id
                )
                region = region_index.get(item["id"])
                if region:
                    self._set_region_owner(
                        region, region.owner, item["kind"],
                        occupied=False, update_neighbors=False,
                    )
            war.occupied_regions = remaining_occupied
            war.attackers = [
                item for item in war.attackers if item != country_id
            ]
            war.defenders = [
                item for item in war.defenders if item != country_id
            ]
            self.map_revision += 1
            if war.peace_offer and country_id in (
                war.peace_offer["proposer"], war.peace_offer["recipient"]
            ):
                war.peace_offer = None

            if not war.attackers or not war.defenders:
                self._finalize_war_territories(war, winners)
                self._end_war(
                    war,
                    "capitulation" if war is source_war else "elimination",
                )
                self.add_event(
                    f"Война завершена после разгрома государства {country.name}.",
                    notify=self.player_id in winners,
                    modal=self.player_id in winners,
                )
            elif war.objective.get("target") == country_id:
                reference_id = war.attackers[0]
                replacement = next(iter(war.enemies(reference_id)), None)
                war.objective = dict(war.objective, target=replacement)

        if country.alliance:
            ally = self.countries.get(country.alliance)
            if ally and ally.alliance == country_id:
                ally.alliance = None
                if ally.treaties.get(country_id, {}).get("type") == "alliance":
                    del ally.treaties[country_id]
                self.add_event(
                    f"Союз с государством {country.name} распущен после его поражения.",
                    notify=country_id == self.player_id or ally.id == self.player_id,
                    modal=country_id == self.player_id or ally.id == self.player_id,
                )
            country.alliance = None
        for partner_id in set(country.treaties) | set(country.pacts):
            partner = self.countries.get(partner_id)
            if not partner:
                continue
            partner.treaties.pop(country_id, None)
            partner.pacts.pop(country_id, None)
        country.treaties.clear()
        country.pacts.clear()
        country.wars.clear()
        self._refresh_country_neighbors()
        if country_id == self.player_id:
            self.time.paused = True
        self.add_event(
            f"{country.name} потеряло последнюю территорию и считается поверженным.",
            notify=country_id == self.player_id,
            modal=country_id == self.player_id,
        )
        self._update_zombie_scenario_outcome()
        return True

    def change_ideology(self, country_id, ideology_id):
        country = self.countries.get(country_id)
        if not country or ideology_id not in self.ideology_options_for(country_id):
            return False, "Эта идеология недоступна в выбранном сценарии"
        result = adopt(country, ideology_id)
        if result[0]:
            self.add_event(result[1], notify=country_id == self.player_id)
        return result

    def start_political_course(self, country_id, course_id):
        country = self.countries.get(country_id)
        if not country or country.is_defeated:
            return False, "Государство недоступно"
        course = COURSES_BY_ID.get(course_id)
        if not course:
            return False, "Политический курс не найден"
        if not course_available(self, country, course_id):
            return False, "Этот политический курс сейчас недоступен"
        if country.money < course["cost"]:
            return False, f"Нужно денег: {course['cost']}"
        if country.political_power < course["political_power"]:
            return False, f"Нужно политической силы: {course['political_power']}"
        country.money -= course["cost"]
        country.political_power -= course["political_power"]
        country.active_political_course = {
            "id": course_id,
            "remaining_days": course["days"],
        }
        message = (
            f"Начат политический курс «{course['name']}»: "
            f"{course['days']} дней"
        )
        self.add_event(message, notify=country_id == self.player_id)
        return True, message

    def _advance_political_course(self, country):
        active = country.active_political_course
        if not active:
            return
        active["remaining_days"] -= 1
        if active["remaining_days"] > 0:
            return
        course = COURSES_BY_ID[active["id"]]
        country.active_political_course = None
        country.political_policies.add(course["id"])
        if course.get("change_leader"):
            country.leadership_term += 1
            title = {
                "communism": "Председатель правительства",
                "fascism": "Национальный лидер",
                "monarchy": "Монарх",
                "democracy": "Президент",
                "z_emergency": "Чрезвычайный совет",
                "z_science": "Научный совет",
                "z_defense": "Командование обороны",
                "z_horde": "Коллективный разум",
            }.get(country.ideology, "Глава государства")
            country.leader = f"{title} №{country.leadership_term}"
        self._apply_course_immediate(country, course["immediate"])

        partner_id = course.get("partner")
        consequences = [
            f"{key}: {value:+g}" for key, value in course["immediate"].items()
        ]
        if partner_id:
            partner = self.countries[partner_id]
            pact_type = course.get("pact_type", "non_aggression")
            expires = None
            if pact_type == "non_aggression":
                expires = self.absolute_day() + course["pact_days"]
                country.pacts[partner_id] = expires
                partner.pacts[country.id] = expires
            elif pact_type == "trade":
                expires = self.absolute_day() + course["treaty_days"]
            elif pact_type == "alliance":
                country.alliance = partner.id
                partner.alliance = country.id
                country.relations[partner.id] = max(
                    60, country.relations.get(partner.id, 0)
                )
                partner.relations[country.id] = max(
                    60, partner.relations.get(country.id, 0)
                )

            country.treaties[partner_id] = {
                "id": course["id"],
                "name": course["name"],
                "type": pact_type,
                "expires": expires,
                "bonuses": course["bonuses"],
            }
            partner.treaties[country.id] = {
                "id": course["id"],
                "name": course["name"],
                "type": pact_type,
                "expires": expires,
                "bonuses": course.get("partner_bonuses", {}),
            }
            self._apply_course_immediate(
                partner, course.get("partner_immediate", {})
            )
            relation_change = course["relation_change"]
            country.relations[partner_id] = min(
                100, country.relations.get(partner_id, 0) + relation_change
            )
            partner.relations[country.id] = min(
                100, partner.relations.get(country.id, 0) + relation_change
            )
            consequences.append(
                f"{course['name']} с государством {partner.name}"
            )
            if expires is not None:
                consequences.append(
                    f"Договор действует до дня {expires}"
                )
            for key, value in course.get("partner_immediate", {}).items():
                consequences.append(
                    f"{partner.name}: {key} {value:+g}"
                )

        effects = "; ".join(consequences) or "договор вступил в силу"
        self.add_event(
            f"Завершён политический курс «{course['name']}».",
            notify=country.id == self.player_id,
            consequences=effects,
        )

    @staticmethod
    def _apply_course_immediate(country, effects):
        bounds = {
            "stability": (0, 100),
            "government_support": (0, 100),
            "army_readiness": (0, 100),
            "unrest": (0, 100),
            "industry": (0, 100),
            "development": (0, 100),
            "economy_level": (1, 10),
            "military": (0, 100),
            "food": (0, 100),
            "energy": (0, 100),
        }
        for field, amount in effects.items():
            if field == "money":
                country.money = max(0, country.money + amount)
            elif field in bounds:
                minimum, maximum = bounds[field]
                setattr(
                    country, field,
                    max(minimum, min(maximum, getattr(country, field) + amount)),
                )
            elif field in ("army_size", "research_points", "political_power"):
                setattr(country, field, max(0, getattr(country, field) + amount))

    def develop_ideology(self, country_id, doctrine_id):
        country = self.countries[country_id]
        if self.scenario_id != "zombie":
            result = develop_ideology(country, doctrine_id)
            if result[0]:
                self.add_event(result[1], notify=country_id == self.player_id)
            return result
        if country.active_upgrade:
            return False, "Сначала дождитесь завершения текущей прокачки"
        valid, result = validate_development(country, doctrine_id)
        if not valid:
            return False, result
        node = result
        country.political_power -= node["cost"]
        days = max(5, min(30, math.ceil(node["cost"] / 8)))
        return self._start_upgrade(country, "ideology", doctrine_id, days)

    def research_technology(self, country_id, technology_id):
        country = self.countries[country_id]
        tree = self.technology_tree_for(country_id)
        if self.scenario_id != "zombie":
            result = research(country, technology_id, tree)
            if result[0]:
                self.add_event(result[1], notify=country_id == self.player_id)
            return result
        if country.active_upgrade:
            return False, "Сначала дождитесь завершения текущей прокачки"
        valid, result = validate_research(country, technology_id, tree)
        if not valid:
            return False, result
        node = result
        country.money -= node["cost"]
        country.research_points -= node["points"]
        days = max(5, min(35, math.ceil(node["points"] / 2)))
        return self._start_upgrade(country, "technology", technology_id, days)

    def start_emergency_measure(self, country_id, measure_id):
        if self.scenario_id != "zombie":
            return False, "Экстренные меры доступны только в сценарии 2031 года"
        country = self.countries.get(country_id)
        if not country or country.is_defeated or country_id == "zombies":
            return False, "Это государство не может вводить меры защиты"
        available, result = emergency_measure_available(
            country, measure_id, self
        )
        if not available:
            return False, result
        measure = result
        country.money -= measure["cost"]
        country.research_points -= measure["points"]
        return self._start_upgrade(
            country, "emergency_measure", measure_id, measure["days"]
        )

    def _start_upgrade(self, country, kind, upgrade_id, days):
        if country.active_upgrade:
            return False, "Сначала дождитесь завершения текущей прокачки"
        country.active_upgrade = {
            "kind": kind,
            "id": upgrade_id,
            "remaining_days": days,
        }
        name = self._upgrade_name(kind, upgrade_id)
        message = f"Начата прокачка «{name}»: завершение через {days} дней."
        self.add_event(message, notify=country.id == self.player_id)
        return True, message

    def _upgrade_name(self, kind, upgrade_id):
        if kind == "technology":
            for country_id in self.countries:
                node = next(
                    (
                        node for node in self.technology_tree_for(country_id)
                        if node["id"] == upgrade_id
                    ),
                    None,
                )
                if node:
                    return node["name"]
        if kind == "ideology":
            for country_id in self.countries:
                node = next(
                    (
                        node for node in self.ideology_tree_for(country_id)
                        if node["id"] == upgrade_id
                    ),
                    None,
                )
                if node:
                    return node["name"]
        if kind == "emergency_measure":
            return EMERGENCY_MEASURES_BY_ID[upgrade_id]["name"]
        return upgrade_id

    def _advance_upgrade(self, country):
        active = country.active_upgrade
        if not active:
            return
        active["remaining_days"] -= 1
        if active["remaining_days"] > 0:
            return
        country.active_upgrade = None
        kind, upgrade_id = active["kind"], active["id"]
        if kind == "technology":
            result = research(
                country, upgrade_id,
                self.technology_tree_for(country.id), paid=True,
            )
        elif kind == "ideology":
            result = develop_ideology(country, upgrade_id, paid=True)
        elif kind == "emergency_measure":
            if upgrade_id not in EMERGENCY_MEASURES_BY_ID:
                result = (False, "Экстренная мера не найдена")
            elif upgrade_id == "emergency_import_labor_force":
                result = self._resolve_import_labor_force(country)
            elif upgrade_id == "emergency_international_evacuation":
                result = self._resolve_international_evacuation(country)
            else:
                country.emergency_measures.add(upgrade_id)
                result = (
                    True,
                    f"Введена экстренная мера: "
                    f"{EMERGENCY_MEASURES_BY_ID[upgrade_id]['name']}",
                )
        else:
            result = (False, f"Неизвестный тип прокачки: {kind}")
        if result[0]:
            self.add_event(result[1], notify=country.id == self.player_id)
        else:
            self.add_event(
                f"Прокачка «{self._upgrade_name(kind, upgrade_id)}» не завершена: "
                f"{result[1]}.",
                notify=country.id == self.player_id,
            )

    def _resolve_import_labor_force(self, country):
        california = self.provinces_by_id.get("usa_admin1_USA-3521")
        if not california or california.owner != "usa":
            return (
                False,
                "Операция отменена: Калифорния больше не находится под контролем США",
            )

        country.emergency_measures.add("emergency_import_labor_force")
        if self.rng.random() < 0.60:
            usa = self.countries["usa"]
            usa.unrest = min(100, usa.unrest + 8)
            usa.stability = max(0, usa.stability - 4)
            self._set_region_owner(
                california, "zombies", kind="province", occupied=False
            )
            self._handle_country_elimination("usa")
            self._update_zombie_scenario_outcome()
            return (
                True,
                "Авария при исследовании заражённых: вспышка в Калифорнии! "
                "Регион перешёл под контроль заражённых; недовольство США +8%, "
                "стабильность −4.",
            )

        self.zombie_readiness_penalty_until = self.absolute_day() + 183
        return (
            True,
            "Исследование завершилось успешно: боеготовность заражённых "
            "снижена на 10% на 183 дня.",
        )

    def _resolve_international_evacuation(self, country):
        country.emergency_measures.add("emergency_international_evacuation")
        if self.rng.random() < 0.5:
            self.international_evacuation_result = "success"
            return (
                True,
                "Международная эвакуация прошла успешно: военная сила всех "
                "стран людей увеличена на 10%.",
            )

        self.international_evacuation_result = "failure"
        survivors = [
            item for item in self.countries.values()
            if item.id != "zombies"
            and not item.is_defeated
            and self.province_count(item.id) > 0
        ]
        affected = []
        for owner in self.rng.sample(survivors, min(7, len(survivors))):
            provinces = [
                province for province in self.provinces
                if province.owner == owner.id
            ]
            if not provinces:
                continue
            province = self.rng.choice(provinces)
            owner.unrest = min(100, owner.unrest + 4)
            owner.stability = max(0, owner.stability - 2)
            self._set_region_owner(
                province, "zombies", kind="province", occupied=False
            )
            if self.province_count(owner.id) == 0:
                self._handle_country_elimination(owner.id)
            affected.append(f"{province.name} ({owner.name})")
        self._update_zombie_scenario_outcome()
        return (
            True,
            "Международная эвакуация сорвалась: заражённые появились в "
            f"{len(affected)} регионах — {', '.join(affected)}.",
        )

    def can_recruit(self, country_id):
        country = self.countries[country_id]
        target_size = self._recruitment_target(country)
        return (
            not country.is_defeated
            and self.absolute_day() >= country.recruitment_ready_day
            and country.army_size < target_size * 0.9
            and country.money >= (400 if country.wars else 550)
        )

    def recruit(self, country_id):
        country = self.countries[country_id]
        if country.is_defeated:
            return False, "Поверженное государство не может пополнять армию"
        if self.absolute_day() < country.recruitment_ready_day:
            return False, "Армия уже пополняется"
        target_size = self._recruitment_target(country)
        if country.army_size >= target_size * 0.9:
            return False, "Потери армии пока невелики"
        cost = 400 if country.wars else 550
        if country.money < cost:
            return False, f"Для пополнения армии нужно {cost} денег"

        reinforcements = min(
            target_size - country.army_size,
            max(1000, int(target_size * (0.12 if country.wars else 0.10))),
        )
        country.money -= cost
        country.army_size += reinforcements
        country.army_readiness = min(100, country.army_readiness + 8)
        country.recruitment_ready_day = self.absolute_day() + (
            30 if country.wars else 60
        )
        message = (
            f"{country.name} пополняет армию на {reinforcements:,} человек "
            f"за ${cost}."
            .replace(",", " ")
        )
        self.add_event(message, notify=country_id == self.player_id)
        return True, message

    def _recruitment_target(self, country):
        if self.scenario_id == "zombie" and country.id == "zombies":
            return max(1000, int(country.population * 0.12))
        return max(
            1000,
            int(country.population * (0.0015 + country.military / 100000)),
        )

    def unrest_relief_cost(self, country_id):
        country = self.countries[country_id]
        return 250 + country.unrest_relief_count * 250

    def reduce_unrest(self, country_id):
        country = self.countries.get(country_id)
        if not country or country.is_defeated:
            return False, "Государство не может проводить внутренние реформы"
        if country.unrest < 2:
            return False, "Недовольство уже ниже 2%"
        cost = self.unrest_relief_cost(country_id)
        if country.money < cost:
            return False, f"Для программы умиротворения нужно ${cost}"
        country.money -= cost
        country.unrest = max(0, country.unrest - 2)
        country.unrest_relief_count += 1
        message = (
            f"{country.name} направляет ${cost} на общественные программы: "
            "недовольство −2%."
        )
        self.add_event(message, notify=country_id == self.player_id)
        return True, message

    def mobilize(self, country_id):
        country = self.countries[country_id]
        if not country.wars:
            return False, "Мобилизация возможна только во время войны"
        if country.money < 300:
            return False, "Для мобилизации нужно 300 денег"
        if country.war_support >= 90:
            return False, "Поддержка войны уже высока"
        country.money -= 300
        country.war_support = min(100, country.war_support + 12)
        country.military = min(100, country.military + 3)
        country.army_size += max(1000, int(country.population * 0.00015))
        country.army_readiness = min(100, country.army_readiness + 12)
        country.stability = max(0, country.stability - 2)
        message = (
            f"{country.name} проводит мобилизацию: поддержка +12%, "
            "армия и боеготовность увеличены"
        )
        self.add_event(message, notify=country_id == self.player_id)
        return True, message

    def to_dict(self):
        return {
            "player_id": self.player_id, "day": self.day, "year": self.year,
            "scenario_id": self.scenario_id, "scenario_name": self.scenario_name,
            "scenario_outcome": self.scenario_outcome,
            "zombie_breach_ready_day": self.zombie_breach_ready_day,
            "zombie_readiness_penalty_until": self.zombie_readiness_penalty_until,
            "international_evacuation_result": (
                self.international_evacuation_result
            ),
            "auto_skip_news": self.auto_skip_news,
            "decision_events_seen": sorted(self.decision_events_seen),
            "events": self.events,
            "pending_modal_events": self.pending_modal_events,
            "modal_resume_after": self.modal_resume_after,
            "wars": {key: war.to_dict() for key, war in self.wars.items()},
            "war_counter": self.war_counter,
            "capital_provinces": self.capital_provinces,
            "countries": {key: value.to_dict() for key, value in self.countries.items()},
            "regions": [region.to_dict() for region in self.regions],
            "detailed_owners": {region.id: region.owner for region in self.detailed_regions},
            "province_owners": {province.id: province.owner for province in self.provinces},
            "occupied_provinces": [
                province.id for province in self.provinces if province.occupied
            ],
        }

    def from_dict(self, data):
        self.load_data(data.get("scenario_id", "modern"))
        self.capital_provinces.update(data.get("capital_provinces", {}))
        self.player_id = data["player_id"]
        self.day = data["day"]
        self.year = data["year"]
        self.scenario_outcome = data.get("scenario_outcome")
        self.zombie_breach_ready_day = data.get("zombie_breach_ready_day", 0)
        self.zombie_readiness_penalty_until = data.get(
            "zombie_readiness_penalty_until", 0
        )
        self.international_evacuation_result = data.get(
            "international_evacuation_result"
        )
        self.auto_skip_news = data.get("auto_skip_news", False)
        self.decision_events_seen = set(
            data.get("decision_events_seen", ())
        )
        self.scenario_name = data.get("scenario_name", self.scenario_name)
        self.events = data.get("events", [])
        self.pending_modal_events = list(data.get("pending_modal_events", ()))
        self.modal_resume_after = bool(data.get("modal_resume_after", False))
        if self.pending_modal_events:
            self.time.paused = True
        self.countries = {}
        for key, country_data in data["countries"].items():
            self.countries[key] = Country.from_dict(country_data)
        if self.scenario_id == "zombie":
            for country_id, country in self.countries.items():
                options = self.ideology_options_for(country_id)
                if country.ideology not in options:
                    country.ideology = (
                        "z_horde" if country_id == "zombies" else "z_emergency"
                    )
                    country.ideology_upgrades.clear()
                valid_ideology_upgrades = {
                    node["id"] for node in self.ideology_tree_for(country_id)
                }
                country.ideology_upgrades.intersection_update(
                    valid_ideology_upgrades
                )
                valid_techs = {
                    node["id"] for node in self.technology_tree_for(country_id)
                }
                country.techs.intersection_update(valid_techs)
                valid_courses = {
                    course["id"]
                    for course in self.political_courses_for(country_id)
                }
                country.political_policies.intersection_update(valid_courses)
                country.emergency_measures.intersection_update(
                    EMERGENCY_MEASURES_BY_ID
                )
                if (
                    country.active_political_course
                    and country.active_political_course.get("id") not in valid_courses
                ):
                    country.active_political_course = None
                active_upgrade = country.active_upgrade
                if active_upgrade:
                    upgrade_id = active_upgrade.get("id")
                    valid_active_ids = (
                        {node["id"] for node in self.technology_tree_for(country_id)}
                        if active_upgrade.get("kind") == "technology"
                        else {node["id"] for node in self.ideology_tree_for(country_id)}
                        if active_upgrade.get("kind") == "ideology"
                        else set(EMERGENCY_MEASURES_BY_ID)
                        if active_upgrade.get("kind") == "emergency_measure"
                        else set()
                    )
                    if (
                        upgrade_id not in valid_active_ids
                        or active_upgrade.get("remaining_days", 0) <= 0
                    ):
                        country.active_upgrade = None
        self._normalize_alliances()
        self.regions = [Region(region) for region in data["regions"]]
        self.regions_by_id = {region.id: region for region in self.regions}
        detailed_owners = data.get("detailed_owners", {})
        for region in self.detailed_regions:
            if region.id in detailed_owners:
                region.owner = detailed_owners[region.id]
        province_owners = data.get("province_owners", {})
        occupied_provinces = set(data.get("occupied_provinces", ()))
        for province in self.provinces:
            if province.id in province_owners:
                province.owner = province_owners[province.id]
            province.occupied = (
                province.id in occupied_provinces
                if "occupied_provinces" in data
                else province.owner != province.initial_owner
            )
        self._restore_legacy_provinces(province_owners)
        self.wars = {}
        self.war_counter = data.get("war_counter", 0)
        for war_id, war_data in data.get("wars", {}).items():
            self.wars[war_id] = War(war_id, [], [], {}, self.absolute_day(), war_data)
        if not self.wars:
            seen = set()
            for country_id, country in self.countries.items():
                for enemy_id in country.wars:
                    pair = tuple(sorted((country_id, enemy_id)))
                    if pair in seen or enemy_id not in self.countries:
                        continue
                    seen.add(pair)
                    self.war_counter += 1
                    war_id = f"war-{self.absolute_day()}-{self.war_counter}"
                    self.wars[war_id] = War(
                        war_id, [country_id], [enemy_id],
                        {"type": "conquest", "target": enemy_id},
                        self.absolute_day(),
                    )
        self.map_labels = {
            country_id: label for country_id, label in self.map_labels.items()
            if country_id in self.countries
        }
        self._rebuild_territory_counts()
        self._refresh_country_neighbors()
        self.diplomacy = Diplomacy(self)
        self.ai = AISystem(self)
        self.event_system = EventSystem(self)
        for country_id, country in list(self.countries.items()):
            if not country.is_defeated and self.territory_count(country_id) == 0:
                self._handle_country_elimination(country_id)

    def _restore_legacy_provinces(self, province_owners):
        assigned = set()
        for legacy_id, owner in province_owners.items():
            if legacy_id in self.provinces_by_id or owner not in self.countries:
                continue
            match = re.search(r"_province_(-?\d+)_(-?\d+)$", legacy_id)
            if not match:
                continue
            row, column = (int(value) for value in match.groups())
            column_step = math.sqrt(3) * 2.2
            row_step = 1.5 * 2.2
            center = (
                column * column_step + (row % 2) * column_step / 2,
                row * row_step,
            )
            province = self.get_province(center)
            if province and province.id not in assigned:
                self._set_region_owner(
                    province, owner, "province",
                    occupied=owner != province.initial_owner,
                )
                assigned.add(province.id)


def geo_to_map(point):
    longitude, latitude = point
    x = (longitude + 180) * (1280 / 360)
    y = 40 + (90 - latitude) * (640 / 180)
    return x, y


def map_color(country_id):
    index = sum(country_id.encode("utf-8")) % len(MAP_PALETTE)
    return MAP_PALETTE[index]


def simplify_polygon(points, tolerance):
    if len(points) <= 4:
        return points
    tolerance_squared = tolerance * tolerance
    keep = {0, len(points) - 1}
    segments = [(0, len(points) - 1)]
    while segments:
        start, end = segments.pop()
        ax, ay = points[start]
        bx, by = points[end]
        dx, dy = bx - ax, by - ay
        length_squared = dx * dx + dy * dy
        largest_distance = tolerance_squared
        largest_index = None
        for index in range(start + 1, end):
            px, py = points[index]
            if length_squared:
                ratio = max(0, min(1, ((px - ax) * dx + (py - ay) * dy) / length_squared))
                closest_x, closest_y = ax + ratio * dx, ay + ratio * dy
                distance = (px - closest_x) ** 2 + (py - closest_y) ** 2
            else:
                distance = (px - ax) ** 2 + (py - ay) ** 2
            if distance > largest_distance:
                largest_distance = distance
                largest_index = index
        if largest_index is not None:
            keep.add(largest_index)
            segments.append((start, largest_index))
            segments.append((largest_index, end))
    result = [points[index] for index in sorted(keep)]
    return result if len(result) >= 4 else points


def point_in_polygon(x, y, points):
    inside = False
    j = len(points) - 1
    for i in range(len(points)):
        xi, yi = points[i]
        xj, yj = points[j]
        if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi + 1e-9) + xi):
            inside = not inside
        j = i
    return inside
