"""Validate Episode 05's isolated role-aware sprite performance plan."""

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pipeline.episode_plan import episode_directory, load_episode_plan, pacing_flags
from pipeline.sprite_manifest import frame_available, load_manifest


EPISODE_DIR = episode_directory(5, ROOT)
SEED, SHOTS = load_episode_plan(5, ROOT)
CONTRACT = json.loads(
    (EPISODE_DIR / SEED["performance_contract"]).read_text(encoding="utf-8")
)
MANIFEST = load_manifest(SEED["sprite_manifest"], ROOT)
CHARACTER_COLUMNS = {"Dage": "dage", "Dixon": "dixon", "Cila": "cila"}


def validate():
    errors = []
    checks = {
        "runtime_is_short": 60 <= int(SEED["runtime_seconds"]) <= 120,
        "no_pacing_flags": not pacing_flags(SHOTS),
        "current_sprite_manifest": SEED["sprite_manifest"]
        == "references/mascot_sprites/current_sprite_manifest.json",
        "lead_is_dixon": SEED["lead_character"] == "Dixon",
    }

    for shot in SHOTS:
        energies = {}
        roles = {}
        for character, column in CHARACTER_COLUMNS.items():
            action_name = shot[f"{column}_action"]
            role = shot[f"{column}_role"]
            roles[character] = role
            library = CONTRACT["characters"][character]
            if action_name not in library:
                errors.append(f"{shot['shot']} {character}: unknown action {action_name}")
                continue
            action = library[action_name]
            energies[character] = int(action["energy"])
            if role not in action["roles"]:
                errors.append(
                    f"{shot['shot']} {character}: {action_name} not allowed for {role}"
                )
            if len(action["frames"]) < 2:
                errors.append(f"{shot['shot']} {character}: action is not multi-frame")
            info = MANIFEST["characters"][character]
            invalid = [frame for frame in action["frames"] if not frame_available(info, frame)]
            if invalid:
                errors.append(
                    f"{shot['shot']} {character}: unavailable frames {invalid}"
                )

        lead_roles = [name for name, role in roles.items() if role.startswith("LEAD_")]
        if shot["beat"] not in ("TITLE", "QUIET_BUTTON"):
            if lead_roles != ["Dixon"]:
                errors.append(
                    f"{shot['shot']}: expected Dixon as sole lead, got {lead_roles}"
                )
        elif shot["beat"] == "TITLE" and any(role != "BACKGROUND" for role in roles.values()):
            errors.append(f"{shot['shot']}: title characters must remain background")
        elif shot["beat"] == "QUIET_BUTTON" and any(role != "SHARED" for role in roles.values()):
            errors.append(f"{shot['shot']}: quiet button must be shared")

        if CONTRACT["rules"]["support_energy_must_not_exceed_lead"] and "Dixon" in energies:
            lead_energy = energies["Dixon"]
            for supporting in ("Dage", "Cila"):
                if roles.get(supporting, "").startswith("SUPPORT"):
                    if energies.get(supporting, 0) > lead_energy and roles["Dixon"] == "LEAD_ACTION":
                        errors.append(
                            f"{shot['shot']} {supporting}: support energy exceeds lead"
                        )

    checks["role_action_pairs_valid"] = not errors
    report = {
        "episode": 5,
        "title": SEED["episode_title"],
        "runtime_seconds": int(SEED["runtime_seconds"]),
        "shot_count": len(SHOTS),
        "contract_version": CONTRACT["version"],
        "checks": checks,
        "errors": errors,
    }
    output = EPISODE_DIR / "EP05_PERFORMANCE_PREFLIGHT.json"
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if errors or not all(checks.values()):
        raise SystemExit(1)
    print("EP05_PERFORMANCE_PREFLIGHT_OK", output)


if __name__ == "__main__":
    validate()
