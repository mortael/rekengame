"""3D world generation using Ursina entities."""
import math
import random
from ursina import Entity, color, Vec3, load_texture, destroy
from src.config import LEVEL_CONFIGS


# Tile types
TILE_FLOOR = 0
TILE_WALL = 1
TILE_BOSS_ROOM = 2


def _rgba(r, g, b, a=1.0):
    return color.rgba(int(r * 255), int(g * 255), int(b * 255), int(a * 255))


class WorldTile(Entity):
    """A single floor or wall tile in the 3D world."""

    def __init__(self, tile_type: int, position: Vec3, cfg: dict, **kwargs):
        if tile_type == TILE_FLOOR:
            super().__init__(
                model="cube",
                position=position,
                scale=(1, 0.1, 1),
                texture=cfg.get("floor_texture", "white_cube"),
                collider=None,
                **kwargs,
            )
        else:  # TILE_WALL
            r, g, b = cfg.get("wall_color", (0.5, 0.5, 0.5))
            super().__init__(
                model="cube",
                position=position + Vec3(0, 0.5, 0),
                scale=(1, 1.5, 1),
                color=_rgba(r, g, b),
                texture="brick",
                collider="box",
                **kwargs,
            )
        self.tile_type = tile_type


class EnemyMarker(Entity):
    """Visual 3D representation of an enemy in the world."""

    def __init__(self, enemy, cfg: dict, **kwargs):
        r, g, b = cfg.get("enemy_color", (0.8, 0.2, 0.2))
        super().__init__(
            model="cube",
            position=Vec3(enemy.position[0], 0.6, enemy.position[1]),
            scale=(0.8, 0.8, 0.8),
            color=_rgba(r, g, b),
            collider="box",
            **kwargs,
        )
        self.enemy_data = enemy
        # Name tag above enemy
        self._label = Entity(
            parent=self,
            model="quad",
            scale=(2, 0.4),
            position=(0, 1.2, 0),
            color=color.rgba(0, 0, 0, 180),
        )

    def update_visibility(self):
        self.visible = self.enemy_data.is_alive()
        self._label.visible = self.enemy_data.is_alive()


class BossMarker(Entity):
    """Visual 3D representation of a boss enemy."""

    def __init__(self, boss, cfg: dict, **kwargs):
        r, g, b = cfg.get("boss_color", (0.6, 0.0, 0.0))
        super().__init__(
            model="cube",
            position=Vec3(boss.position[0], 0.9, boss.position[1]),
            scale=(1.4, 1.4, 1.4),
            color=_rgba(r, g, b),
            collider="box",
            **kwargs,
        )
        self.boss_data = boss
        self._pulse_t = 0.0

    def update(self):
        self._pulse_t += 0.02
        scale_mod = 1.0 + 0.05 * abs(math.sin(self._pulse_t * 3))
        self.scale = (1.4 * scale_mod, 1.4 * scale_mod, 1.4 * scale_mod)

    def update_visibility(self):
        self.visible = self.boss_data.is_alive()


class CraftingStationMarker(Entity):
    """Visual marker for a crafting station."""

    def __init__(self, position: Vec3, **kwargs):
        super().__init__(
            model="cube",
            position=position,
            scale=(0.7, 0.7, 0.7),
            color=color.rgba(50, 200, 100, 255),
            collider="box",
            **kwargs,
        )


class World:
    """Builds and manages the 3D dungeon world."""

    INTERACTION_RANGE = 2.5  # units

    def __init__(self, level_config: dict):
        self.cfg = level_config
        self.size = level_config["world_size"]
        self.tiles: list[WorldTile] = []
        self.enemy_markers: list[EnemyMarker] = []
        self.boss_markers: list[BossMarker] = []
        self.crafting_markers: list[CraftingStationMarker] = []
        self._grid: list[list[int]] = []
        self._entities: list[Entity] = []

    def build(self, enemies, bosses) -> None:
        """Generate the world and populate with enemies and bosses."""
        self._generate_grid()
        self._build_tiles()
        self._place_enemies(enemies)
        self._place_bosses(bosses)
        self._place_crafting_stations()
        self._add_sky_and_light()

    def _generate_grid(self) -> None:
        """Simple room-corridor dungeon grid."""
        size = self.size
        grid = [[TILE_WALL] * size for _ in range(size)]

        # Carve a main cross corridor
        mid = size // 2
        for x in range(1, size - 1):
            grid[mid][x] = TILE_FLOOR
        for z in range(1, size - 1):
            grid[z][mid] = TILE_FLOOR

        # Carve extra rooms randomly
        rooms = [
            (4, 4, 5, 5),
            (4, size - 9, 5, 5),
            (size - 9, 4, 5, 5),
            (size - 9, size - 9, 5, 5),
            (mid - 3, mid - 3, 7, 7),   # central room
        ]
        for rx, rz, rw, rh in rooms:
            for x in range(rx, rx + rw):
                for z in range(rz, rz + rh):
                    if 0 < x < size - 1 and 0 < z < size - 1:
                        grid[z][x] = TILE_FLOOR

        # Connect rooms to corridors with extra passages
        for _ in range(size):
            x = random.randint(1, size - 2)
            z = random.randint(1, size - 2)
            grid[z][x] = TILE_FLOOR

        self._grid = grid

    def _build_tiles(self) -> None:
        size = self.size
        for z in range(size):
            for x in range(size):
                tile_type = self._grid[z][x]
                pos = Vec3(x, 0, z)
                tile = WorldTile(tile_type, pos, self.cfg)
                self.tiles.append(tile)
                self._entities.append(tile)

    def _place_enemies(self, enemies) -> None:
        for enemy in enemies:
            if self._is_walkable(enemy.position[0], enemy.position[1]):
                marker = EnemyMarker(enemy, self.cfg)
                self.enemy_markers.append(marker)
                self._entities.append(marker)

    def _place_bosses(self, bosses) -> None:
        for boss in bosses:
            if self._is_walkable(boss.position[0], boss.position[1]):
                marker = BossMarker(boss, self.cfg)
                self.boss_markers.append(marker)
                self._entities.append(marker)

    def _place_crafting_stations(self) -> None:
        size = self.size
        mid = size // 2
        station_positions = [
            Vec3(mid - 4, 0.4, mid),
            Vec3(mid + 4, 0.4, mid),
            Vec3(mid, 0.4, mid - 4),
        ]
        for pos in station_positions:
            x, z = int(pos.x), int(pos.z)
            if self._is_walkable(x, z):
                marker = CraftingStationMarker(pos)
                self.crafting_markers.append(marker)
                self._entities.append(marker)

    def _add_sky_and_light(self) -> None:
        from ursina import Sky, DirectionalLight, AmbientLight
        sky = Sky()
        self._entities.append(sky)

        sun = DirectionalLight()
        sun.look_at(Vec3(1, -1, 1))
        self._entities.append(sun)

        ambient = AmbientLight(color=color.rgba(100, 100, 130, 255))
        self._entities.append(ambient)

    def _is_walkable(self, x: int, z: int) -> bool:
        x, z = int(x), int(z)
        if 0 <= z < len(self._grid) and 0 <= x < len(self._grid[0]):
            return self._grid[z][x] == TILE_FLOOR
        return False

    def get_player_spawn(self) -> Vec3:
        """Return a safe spawn position for the player."""
        mid = self.size // 2
        return Vec3(mid, 1, mid)

    def get_nearby_enemy(self, player_pos: Vec3):
        """Return the nearest alive enemy within interaction range, or None."""
        for marker in self.enemy_markers:
            if not marker.enemy_data.is_alive():
                continue
            dist = (marker.position - player_pos).length()
            if dist <= self.INTERACTION_RANGE:
                return marker
        return None

    def get_nearby_boss(self, player_pos: Vec3):
        """Return the nearest alive boss within interaction range, or None."""
        for marker in self.boss_markers:
            if not marker.boss_data.is_alive():
                continue
            dist = (marker.position - player_pos).length()
            if dist <= self.INTERACTION_RANGE:
                return marker
        return None

    def get_nearby_crafting_station(self, player_pos: Vec3):
        """Return nearest crafting station within interaction range, or None."""
        for marker in self.crafting_markers:
            dist = (marker.position - player_pos).length()
            if dist <= self.INTERACTION_RANGE:
                return marker
        return None

    def refresh_markers(self) -> None:
        """Hide markers for defeated enemies/bosses."""
        for m in self.enemy_markers:
            m.update_visibility()
        for m in self.boss_markers:
            m.update_visibility()

    def destroy_all(self) -> None:
        """Remove all world entities (for level transition)."""
        for e in self._entities:
            destroy(e)
        self._entities.clear()
        self.tiles.clear()
        self.enemy_markers.clear()
        self.boss_markers.clear()
        self.crafting_markers.clear()
