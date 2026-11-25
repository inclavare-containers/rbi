"""Reusable CLI helper powering the in-toto GitHub Actions in inclavare-containers/rbi.

Provides four subcommands:
  - keygen: Generate PEM private key + in-toto JSON public key.
  - layout: Build and sign an in-toto root.layout from a step specification.
  - run:    Execute a CI step under in-toto-run and emit a signed .link file.
  - verify: Verify root.layout and .link metadata against trusted owner key(s).
"""

from __future__ import annotations

import argparse
import datetime as dt
import glob
import json
import os
import shlex
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from cryptography.hazmat.primitives import serialization
from in_toto.models.layout import Layout
from in_toto.models.metadata import Metablock
from in_toto.runlib import in_toto_run
from in_toto.verifylib import in_toto_verify
from securesystemslib.signer import CryptoSigner, SSlibKey


def _pubkey_dict(pub_key: SSlibKey) -> Dict[str, Any]:
    return {"keyid": pub_key.keyid, **pub_key.to_dict()}


def generate_keypair(out_dir: Path, name: str, key_type: str = "ed25519") -> Tuple[Path, Path, str]:
    """Generate a signing keypair (PEM private key + in-toto JSON public key)."""
    out_dir.mkdir(parents=True, exist_ok=True)
    if key_type == "ed25519":
        signer = CryptoSigner.generate_ed25519()
    elif key_type == "rsa":
        signer = CryptoSigner.generate_rsa()
    elif key_type == "ecdsa":
        signer = CryptoSigner.generate_ecdsa()
    else:
        raise ValueError(f"Unsupported key_type: {key_type}")

    priv_path = out_dir / f"{name}.pem"
    pub_path = out_dir / f"{name}.pub"
    priv_path.write_bytes(signer.private_bytes)
    try:
        os.chmod(priv_path, 0o600)
    except OSError:
        pass
    pub_data = _pubkey_dict(signer.public_key)
    pub_path.write_text(json.dumps(pub_data, indent=2) + "\n", encoding="utf-8")
    return priv_path, pub_path, signer.public_key.keyid


def load_signer_from_pem(pem_bytes: bytes, password: Optional[bytes] = None) -> CryptoSigner:
    """Construct a CryptoSigner from PEM-encoded private key bytes."""
    priv_key = serialization.load_pem_private_key(pem_bytes, password=password)
    pub_key = SSlibKey.from_crypto(priv_key.public_key())
    return CryptoSigner(priv_key, pub_key)


def resolve_signer(
    key_path: Optional[str],
    key_env: Optional[str],
    ephemeral_dir: Optional[str],
    ephemeral_name: str,
    key_type: str = "ed25519",
) -> Tuple[CryptoSigner, Path]:
    """Resolve signing key from file, env var, or ephemeral generation."""
    if key_path:
        pem = Path(key_path).read_bytes()
        signer = load_signer_from_pem(pem)
        pub_path = Path(key_path).with_suffix(".pub")
        if not pub_path.exists():
            pub_path.write_text(json.dumps(_pubkey_dict(signer.public_key), indent=2) + "\n", encoding="utf-8")
        return signer, pub_path

    if key_env and os.environ.get(key_env, "").strip():
        pem_text = os.environ[key_env].strip() + "\n"
        signer = load_signer_from_pem(pem_text.encode("utf-8"))
        out_dir = Path(ephemeral_dir or ".in-toto/keys")
        out_dir.mkdir(parents=True, exist_ok=True)
        pub_path = out_dir / f"{ephemeral_name}.pub"
        pub_path.write_text(json.dumps(_pubkey_dict(signer.public_key), indent=2) + "\n", encoding="utf-8")
        return signer, pub_path

    out_dir = Path(ephemeral_dir or ".in-toto/keys")
    priv_path, pub_path, _ = generate_keypair(out_dir, ephemeral_name, key_type=key_type)
    return load_signer_from_pem(priv_path.read_bytes()), pub_path


def write_github_outputs(outputs: Dict[str, str]) -> None:
    """Append key=value pairs to GITHUB_OUTPUT when running inside GitHub Actions."""
    gh_out = os.environ.get("GITHUB_OUTPUT")
    if not gh_out:
        return
    with open(gh_out, "a", encoding="utf-8") as fh:
        for k, v in outputs.items():
            fh.write(f"{k}={v}\n")


def parse_list_arg(raw_values: Optional[List[str]]) -> List[str]:
    """Split whitespace/newline-separated items and expand file globs where matched."""
    if not raw_values:
        return []
    tokens: List[str] = []
    for val in raw_values:
        for part in val.replace("\r", "\n").split():
            if part:
                tokens.append(part)
    expanded: List[str] = []
    for tok in tokens:
        matches = glob.glob(tok, recursive=True)
        expanded.extend(sorted(matches) if matches else [tok])
    return expanded


def cmd_keygen(args: argparse.Namespace) -> int:
    priv_path, pub_path, keyid = generate_keypair(Path(args.out_dir), args.name, key_type=args.key_type)
    write_github_outputs(
        {
            "private-key-path": str(priv_path),
            "public-key-path": str(pub_path),
            "keyid": keyid,
        }
    )
    print(json.dumps({"private_key": str(priv_path), "public_key": str(pub_path), "keyid": keyid}))
    return 0


def _parse_step_key_mappings(items: Optional[List[str]]) -> Dict[str, Dict[str, Any]]:
    mapping: Dict[str, Dict[str, Any]] = {}
    for item in items or []:
        for entry in item.replace("\r", "\n").splitlines():
            entry = entry.strip()
            if not entry:
                continue
            if "=" not in entry:
                raise ValueError(f"Invalid step-key mapping {entry!r}; expected step=path/to/pub.json")
            step, pub_file = entry.split("=", 1)
            pub_data = json.loads(Path(pub_file.strip()).read_text(encoding="utf-8"))
            if "keyid" not in pub_data:
                raise ValueError(f"Public key file {pub_file} missing 'keyid'")
            mapping[step.strip()] = pub_data
    return mapping


def cmd_layout(args: argparse.Namespace) -> int:
    spec = json.loads(Path(args.spec).read_text(encoding="utf-8"))
    step_keys = _parse_step_key_mappings(args.step_key)

    keys: Dict[str, Dict[str, Any]] = dict(spec.get("keys") or {})
    steps = spec.get("steps") or []
    for step in steps:
        name = step.get("name")
        if name in step_keys:
            pub = step_keys[name]
            keys[pub["keyid"]] = pub
            pubkeys = list(step.get("pubkeys") or [])
            if pub["keyid"] not in pubkeys:
                pubkeys.append(pub["keyid"])
            step["pubkeys"] = pubkeys

    expires_days = args.expires_days if args.expires_days is not None else spec.get("expires_days", 30)
    expires_dt = dt.datetime.now(dt.timezone.utc) + dt.timedelta(days=int(expires_days))
    expires_str = spec.get("expires") or expires_dt.strftime("%Y-%m-%dT%H:%M:%SZ")

    layout_dict: Dict[str, Any] = {
        "_type": "layout",
        "expires": expires_str,
        "keys": keys,
        "steps": steps,
        "inspect": spec.get("inspect") or [],
    }
    if spec.get("readme"):
        layout_dict["readme"] = spec["readme"]

    layout = Layout.read(layout_dict)
    signer, owner_pub_path = resolve_signer(
        args.key_path,
        args.key_env,
        args.ephemeral_dir,
        ephemeral_name="owner",
        key_type=args.key_type,
    )
    metablock = Metablock(signed=layout)
    metablock.create_signature(signer)

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    metablock.dump(str(out_path))

    write_github_outputs(
        {
            "layout-file": str(out_path),
            "owner-keyid": signer.public_key.keyid,
            "owner-public-key-path": str(owner_pub_path),
        }
    )
    print(f"Signed layout written to {out_path} (owner keyid: {signer.public_key.keyid})")
    return 0


def cmd_run(args: argparse.Namespace) -> int:
    metadata_dir = Path(args.metadata_dir).resolve()
    metadata_dir.mkdir(parents=True, exist_ok=True)

    signer, pub_path = resolve_signer(
        args.key_path,
        args.key_env,
        args.ephemeral_dir or str(metadata_dir / "keys"),
        ephemeral_name=args.step_name,
        key_type=args.key_type,
    )

    if args.command_str:
        cmd_args = shlex.split(args.command_str, posix=(os.name != "nt"))
    elif args.command:
        cmd_args = list(args.command)
        if cmd_args and cmd_args[0] == "--":
            cmd_args = cmd_args[1:]
    else:
        raise ValueError("A command must be provided via --command-str or positional arguments")

    cwd = os.getcwd()
    work_dir = Path(args.working_dir).resolve()
    os.chdir(work_dir)
    try:
        materials = parse_list_arg(args.materials)
        products = parse_list_arg(args.products)
        excludes = parse_list_arg(args.exclude_patterns) or None
        in_toto_run(
            name=args.step_name,
            material_list=materials,
            product_list=products,
            link_cmd_args=cmd_args,
            record_streams=args.record_streams,
            exclude_patterns=excludes,
            base_path=args.base_path or None,
            record_environment=args.record_environment,
            metadata_directory=str(metadata_dir),
            timeout=args.timeout,
            signer=signer,
        )
    finally:
        os.chdir(cwd)

    short_keyid = signer.public_key.keyid[:8]
    link_file = metadata_dir / f"{args.step_name}.{short_keyid}.link"
    if not link_file.exists():
        matches = sorted(metadata_dir.glob(f"{args.step_name}.*.link"))
        if matches:
            link_file = matches[-1]

    write_github_outputs(
        {
            "link-file": str(link_file),
            "keyid": signer.public_key.keyid,
            "public-key-path": str(pub_path.resolve()),
        }
    )
    print(f"Step '{args.step_name}' recorded and signed -> {link_file} (keyid: {signer.public_key.keyid})")
    return 0


def cmd_verify(args: argparse.Namespace) -> int:
    layout_mb = Metablock.load(args.layout)
    layout_keys: Dict[str, Dict[str, Any]] = {}
    for key_file in args.layout_key:
        pub = json.loads(Path(key_file).read_text(encoding="utf-8"))
        if "keyid" not in pub:
            raise ValueError(f"Layout public key {key_file} missing 'keyid'")
        layout_keys[pub["keyid"]] = pub

    in_toto_verify(
        metadata=layout_mb,
        layout_key_dict=layout_keys,
        link_dir_path=args.link_dir,
        step_name=args.step_name or "",
    )
    print(f"in-toto verification PASSED for {args.layout} (links in {args.link_dir})")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="in-toto GitHub Actions CI/CD CLI helper")
    sub = parser.add_subparsers(dest="subcommand", required=True)

    p_kg = sub.add_parser("keygen", help="Generate signing keypair")
    p_kg.add_argument("--out-dir", default=".in-toto/keys")
    p_kg.add_argument("--name", required=True)
    p_kg.add_argument("--key-type", default="ed25519", choices=["ed25519", "rsa", "ecdsa"])
    p_kg.set_defaults(func=cmd_keygen)

    p_lay = sub.add_parser("layout", help="Generate and sign root.layout")
    p_lay.add_argument("--spec", required=True, help="Path to layout JSON specification")
    p_lay.add_argument("--output", default=".in-toto/root.layout")
    p_lay.add_argument("--step-key", action="append", help="step=pub_key_json mapping")
    p_lay.add_argument("--expires-days", type=int, default=None)
    p_lay.add_argument("--key-path", default="")
    p_lay.add_argument("--key-env", default="")
    p_lay.add_argument("--ephemeral-dir", default=".in-toto/keys")
    p_lay.add_argument("--key-type", default="ed25519", choices=["ed25519", "rsa", "ecdsa"])
    p_lay.set_defaults(func=cmd_layout)

    p_run = sub.add_parser("run", help="Execute step via in-toto-run and sign linkfile")
    p_run.add_argument("--step-name", required=True)
    p_run.add_argument("--command-str", default="", help="Command string to execute")
    p_run.add_argument("--materials", action="append", default=[])
    p_run.add_argument("--products", action="append", default=[])
    p_run.add_argument("--exclude-patterns", action="append", default=[])
    p_run.add_argument("--base-path", default="")
    p_run.add_argument("--working-dir", default=".")
    p_run.add_argument("--metadata-dir", default=".in-toto")
    p_run.add_argument("--key-path", default="")
    p_run.add_argument("--key-env", default="")
    p_run.add_argument("--ephemeral-dir", default="")
    p_run.add_argument("--key-type", default="ed25519", choices=["ed25519", "rsa", "ecdsa"])
    p_run.add_argument("--record-streams", action=argparse.BooleanOptionalAction, default=True)
    p_run.add_argument("--record-environment", action=argparse.BooleanOptionalAction, default=False)
    p_run.add_argument("--timeout", type=int, default=600)
    p_run.add_argument("command", nargs=argparse.REMAINDER)
    p_run.set_defaults(func=cmd_run)

    p_ver = sub.add_parser("verify", help="Verify root.layout and .link files")
    p_ver.add_argument("--layout", default=".in-toto/root.layout")
    p_ver.add_argument("--layout-key", action="append", required=True)
    p_ver.add_argument("--link-dir", default=".in-toto")
    p_ver.add_argument("--step-name", default="")
    p_ver.set_defaults(func=cmd_verify)

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
