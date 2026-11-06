#!/usr/bin/env python3
"""Persist and validate progress for agent-executed workflow skills."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import yaml  # type: ignore
except Exception as exc:
    print(json.dumps({"ok": False, "error": f"PyYAML unavailable: {exc}"}, ensure_ascii=False))
    sys.exit(2)


class RuntimeFailure(Exception):
    pass


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def emit(value: dict[str, Any]) -> None:
    print(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True))


def workflow_data(path: Path) -> tuple[dict[str, Any], str]:
    try:
        document = yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise RuntimeFailure(f"cannot load workflow: {exc}") from exc
    if not isinstance(document, dict) or not isinstance(document.get("workflow"), dict):
        raise RuntimeFailure("workflow file must contain a workflow mapping")
    workflow = document["workflow"]
    for field in ("id", "initial_state", "artifacts", "states"):
        if field not in workflow:
            raise RuntimeFailure(f"workflow.{field} is required")
    canonical = json.dumps(document, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return workflow, hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def run_id(args: argparse.Namespace) -> str:
    value = args.workflow_run_id or os.environ.get("AGENT_WORKFLOW_RUN_ID")
    if not value or not value.strip():
        raise RuntimeFailure("workflow run id is required via --workflow-run-id or AGENT_WORKFLOW_RUN_ID")
    return value.strip()


def state_root(args: argparse.Namespace) -> Path:
    if args.state_root:
        return Path(args.state_root).expanduser().resolve()
    configured = os.environ.get("AGENT_WORKFLOW_STATE_ROOT")
    if configured:
        return Path(configured).expanduser().resolve()
    xdg = os.environ.get("XDG_RUNTIME_DIR")
    if xdg:
        return (Path(xdg) / "agent-workflows").resolve()
    tmpdir = os.environ.get("TMPDIR")
    if tmpdir:
        return (Path(tmpdir) / "agent-workflows").resolve()
    return (Path(tempfile.gettempdir()) / "agent-workflows").resolve()


def run_paths(args: argparse.Namespace, workflow_id: str, workflow_run_id: str) -> tuple[Path, Path]:
    identity = f"{workflow_id}\0{workflow_run_id}".encode("utf-8")
    run_dir = state_root(args) / hashlib.sha256(identity).hexdigest()
    return run_dir, run_dir / "state.json"


def prepare_run_dir(run_dir: Path) -> None:
    run_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
    os.chmod(run_dir, 0o700)
    artifacts_dir = run_dir / "artifacts"
    artifacts_dir.mkdir(exist_ok=True, mode=0o700)
    os.chmod(artifacts_dir, 0o700)


def atomic_write(path: Path, value: dict[str, Any]) -> None:
    descriptor, temporary_name = tempfile.mkstemp(prefix=".state-", suffix=".json", dir=path.parent)
    temporary_path = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(value, handle, ensure_ascii=False, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(temporary_path, 0o600)
        os.replace(temporary_path, path)
        directory_descriptor = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory_descriptor)
        finally:
            os.close(directory_descriptor)
    finally:
        if temporary_path.exists():
            temporary_path.unlink()


def read_state(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise RuntimeFailure("workflow run does not exist; call open first")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise RuntimeFailure(f"cannot read runtime state: {exc}") from exc
    if not isinstance(value, dict):
        raise RuntimeFailure("runtime state must be a JSON object")
    return value


def verify_identity(
    state: dict[str, Any], workflow: dict[str, Any], workflow_run_id: str, digest: str
) -> None:
    if state.get("workflow_id") != workflow.get("id"):
        raise RuntimeFailure("runtime workflow_id does not match workflow.yaml")
    if state.get("workflow_run_id") != workflow_run_id:
        raise RuntimeFailure("runtime workflow_run_id does not match requested run")
    if state.get("workflow_digest") != digest:
        raise RuntimeFailure("workflow.yaml changed since this run started; migrate explicitly or use a new workflow_run_id")


def indexed(workflow: dict[str, Any]) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    states = {
        item["id"]: item
        for item in workflow.get("states", [])
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }
    artifacts = {
        item["id"]: item
        for item in workflow.get("artifacts", [])
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }
    return states, artifacts


def parse_pairs(values: list[str], option: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for value in values:
        key, separator, item_value = value.partition("=")
        if not separator or not key or not item_value:
            raise RuntimeFailure(f"{option} expects ID=VALUE: {value}")
        if key in result:
            raise RuntimeFailure(f"duplicate {option} id: {key}")
        result[key] = item_value
    return result


def file_digest(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def register_artifacts(
    args: argparse.Namespace,
    state: dict[str, Any],
    artifact_definitions: dict[str, dict[str, Any]],
    run_dir: Path,
    next_revision: int,
    producer_state: str,
    state_outputs: set[str],
) -> None:
    files = parse_pairs(args.artifact, "--artifact")
    references = parse_pairs(args.artifact_ref, "--artifact-ref")
    summaries = parse_pairs(args.artifact_summary, "--artifact-summary")
    overlap = set(files) & set(references)
    if overlap:
        raise RuntimeFailure(f"artifact cannot be both file and reference: {sorted(overlap)}")
    unknown = (set(files) | set(references) | set(summaries)) - set(artifact_definitions)
    if unknown:
        raise RuntimeFailure(f"unknown artifact ids: {sorted(unknown)}")
    unregistered_summaries = set(summaries) - (set(files) | set(references))
    if unregistered_summaries:
        raise RuntimeFailure(f"artifact summaries require a matching artifact registration: {sorted(unregistered_summaries)}")
    wrong_producers = {
        artifact_id: artifact_definitions[artifact_id].get("producer")
        for artifact_id in set(files) | set(references)
        if artifact_definitions[artifact_id].get("producer") != "external" and artifact_id not in state_outputs
    }
    if wrong_producers:
        raise RuntimeFailure(f"artifacts cannot be produced in state {producer_state}: {wrong_producers}")

    records = state.setdefault("artifacts", {})
    timestamp = now()
    for artifact_id, source_value in files.items():
        source = Path(source_value).expanduser().resolve()
        if not source.is_file():
            raise RuntimeFailure(f"artifact source is not a regular file: {source}")
    for artifact_id, source_value in files.items():
        source = Path(source_value).expanduser().resolve()
        previous = records.get(artifact_id, {})
        version = int(previous.get("version", 0)) + 1
        suffix = source.suffix if len(source.suffix) <= 16 else ""
        destination = run_dir / "artifacts" / f"{artifact_id}.v{version}.r{next_revision}{suffix}"
        temporary = destination.with_name(f".{destination.name}.tmp")
        shutil.copyfile(source, temporary)
        with temporary.open("rb") as handle:
            os.fsync(handle.fileno())
        os.replace(temporary, destination)
        records[artifact_id] = {
            "kind": "file",
            "path": str(destination.relative_to(run_dir)),
            "source_name": source.name,
            "status": "validated",
            "version": version,
            "revision": next_revision,
            "sha256": file_digest(destination),
            "bytes": destination.stat().st_size,
            "summary": summaries.get(artifact_id, artifact_definitions[artifact_id].get("description", "")),
            "updated_at": timestamp,
        }
    for artifact_id, uri in references.items():
        previous = records.get(artifact_id, {})
        version = int(previous.get("version", 0)) + 1
        records[artifact_id] = {
            "kind": "reference",
            "uri": uri,
            "status": "validated",
            "version": version,
            "revision": next_revision,
            "sha256": hashlib.sha256(uri.encode("utf-8")).hexdigest(),
            "summary": summaries.get(artifact_id, artifact_definitions[artifact_id].get("description", "")),
            "updated_at": timestamp,
        }


def require_state_artifacts(state_definition: dict[str, Any], state: dict[str, Any]) -> None:
    required = list(state_definition.get("inputs", [])) + list(state_definition.get("outputs", []))
    missing = [artifact_id for artifact_id in required if artifact_id not in state.get("artifacts", {})]
    if missing:
        raise RuntimeFailure(f"state inputs or outputs are not registered: {missing}")


def preflight_state_artifacts(args: argparse.Namespace, state_definition: dict[str, Any], state: dict[str, Any]) -> None:
    registered = set(state.get("artifacts", {}))
    registered.update(parse_pairs(args.artifact, "--artifact"))
    registered.update(parse_pairs(args.artifact_ref, "--artifact-ref"))
    required = list(state_definition.get("inputs", [])) + list(state_definition.get("outputs", []))
    missing = [artifact_id for artifact_id in required if artifact_id not in registered]
    if missing:
        raise RuntimeFailure(f"state inputs or outputs are not registered: {missing}")


def open_run(args: argparse.Namespace) -> dict[str, Any]:
    workflow, digest = workflow_data(Path(args.workflow).resolve())
    workflow_run_id = run_id(args)
    run_dir, state_path = run_paths(args, workflow["id"], workflow_run_id)
    prepare_run_dir(run_dir)
    if state_path.exists():
        state = read_state(state_path)
        verify_identity(state, workflow, workflow_run_id, digest)
        return {"ok": True, "created": False, "run_dir": str(run_dir), **state}
    timestamp = now()
    state = {
        "schema_version": 1,
        "workflow_id": workflow["id"],
        "workflow_run_id": workflow_run_id,
        "workflow_digest": digest,
        "status": "active",
        "current_state": workflow["initial_state"],
        "revision": 0,
        "completed_states": [],
        "artifacts": {},
        "blocked": None,
        "failure": None,
        "created_at": timestamp,
        "updated_at": timestamp,
        "completed_at": None,
    }
    atomic_write(state_path, state)
    return {"ok": True, "created": True, "run_dir": str(run_dir), **state}


def commit_run(args: argparse.Namespace) -> dict[str, Any]:
    workflow, digest = workflow_data(Path(args.workflow).resolve())
    workflow_run_id = run_id(args)
    run_dir, state_path = run_paths(args, workflow["id"], workflow_run_id)
    state = read_state(state_path)
    verify_identity(state, workflow, workflow_run_id, digest)
    if state.get("status") in {"completed", "failed"}:
        raise RuntimeFailure(f"workflow run is already {state.get('status')}")
    if state.get("current_state") != args.expect_state:
        raise RuntimeFailure(f"expected state {args.expect_state}, actual state {state.get('current_state')}")
    if state.get("revision") != args.expect_revision:
        raise RuntimeFailure(f"expected revision {args.expect_revision}, actual revision {state.get('revision')}")

    states, artifact_definitions = indexed(workflow)
    current = states.get(args.expect_state)
    if current is None:
        raise RuntimeFailure(f"current state is not defined: {args.expect_state}")
    local_conditions = {
        item["id"]: item
        for item in current.get("conditions", [])
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }
    satisfied = set(args.satisfy)
    unknown_conditions = satisfied - set(local_conditions)
    if unknown_conditions:
        raise RuntimeFailure(f"unknown conditions for state {args.expect_state}: {sorted(unknown_conditions)}")

    next_revision = args.expect_revision + 1
    timestamp = now()

    if args.fail:
        if not args.evidence:
            raise RuntimeFailure("--evidence is required with --fail")
        condition = local_conditions.get(args.fail)
        if condition is None:
            raise RuntimeFailure(f"failed condition is not defined in current state: {args.fail}")
        failure = condition.get("failure", {})
        failure_type = failure.get("type")
        if failure_type not in {"retry", "transition", "blocked", "failed"}:
            raise RuntimeFailure(f"condition {args.fail} has unsupported failure.type: {failure_type}")
        target_state = failure.get("to") if failure_type == "transition" else failure.get("resume_state", args.expect_state)
        if target_state not in states:
            raise RuntimeFailure(f"condition failure target state is not defined: {target_state}")
        register_artifacts(
            args,
            state,
            artifact_definitions,
            run_dir,
            next_revision,
            args.expect_state,
            set(current.get("outputs", [])),
        )
        failure_record = {
            "state": args.expect_state,
            "condition": args.fail,
            "type": failure_type,
            "message": failure.get("message", ""),
            "evidence": args.evidence,
            "recovery": failure.get("recovery", ""),
            "resume_state": target_state,
        }
        state["current_state"] = target_state
        state["failure"] = failure_record
        if failure_type == "blocked":
            state["status"] = "blocked"
            state["blocked"] = failure_record
        elif failure_type == "failed":
            state["status"] = "failed"
            state["blocked"] = None
        else:
            state["status"] = "active"
            state["blocked"] = None
    elif args.complete:
        if current.get("type") != "terminal":
            raise RuntimeFailure("--complete is only valid for a terminal state")
        missing_conditions = set(local_conditions) - satisfied
        if missing_conditions:
            raise RuntimeFailure(f"terminal conditions are not satisfied: {sorted(missing_conditions)}")
        preflight_state_artifacts(args, current, state)
        register_artifacts(
            args,
            state,
            artifact_definitions,
            run_dir,
            next_revision,
            args.expect_state,
            set(current.get("outputs", [])),
        )
        require_state_artifacts(current, state)
        state["status"] = "completed"
        state["blocked"] = None
        state["failure"] = None
        state["completed_at"] = timestamp
        if args.expect_state not in state["completed_states"]:
            state["completed_states"].append(args.expect_state)
    else:
        if current.get("type") == "terminal":
            raise RuntimeFailure("terminal state must use --complete")
        if args.to not in states:
            raise RuntimeFailure(f"target state is not defined: {args.to}")
        matching = []
        for transition in current.get("transitions", []):
            if isinstance(transition, dict) and transition.get("to") == args.to:
                required = set(transition.get("when", []))
                if required <= satisfied:
                    matching.append(transition)
        if not matching:
            raise RuntimeFailure(f"no transition to {args.to} is enabled by satisfied conditions {sorted(satisfied)}")
        preflight_state_artifacts(args, current, state)
        register_artifacts(
            args,
            state,
            artifact_definitions,
            run_dir,
            next_revision,
            args.expect_state,
            set(current.get("outputs", [])),
        )
        require_state_artifacts(current, state)
        state["status"] = "active"
        state["current_state"] = args.to
        state["blocked"] = None
        state["failure"] = None
        if args.expect_state not in state["completed_states"]:
            state["completed_states"].append(args.expect_state)

    state["revision"] = next_revision
    state["updated_at"] = timestamp
    atomic_write(state_path, state)
    return {"ok": True, "run_dir": str(run_dir), **state}


def inspect_run(args: argparse.Namespace) -> dict[str, Any]:
    workflow, digest = workflow_data(Path(args.workflow).resolve())
    workflow_run_id = run_id(args)
    run_dir, state_path = run_paths(args, workflow["id"], workflow_run_id)
    state = read_state(state_path)
    verify_identity(state, workflow, workflow_run_id, digest)
    return {"ok": True, "run_dir": str(run_dir), **state}


def add_common(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--workflow", required=True, help="path to workflow.yaml")
    parser.add_argument("--workflow-run-id", help="stable host-provided execution id")
    parser.add_argument("--state-root", help="override runtime state root")


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description="Persist workflow skill execution state")
    commands = root.add_subparsers(dest="command", required=True)
    open_parser = commands.add_parser("open", help="open or initialize a workflow run")
    add_common(open_parser)
    inspect_parser = commands.add_parser("inspect", help="inspect an existing workflow run")
    add_common(inspect_parser)
    commit_parser = commands.add_parser("commit", help="commit a transition, condition failure, or completion")
    add_common(commit_parser)
    commit_parser.add_argument("--expect-state", required=True)
    commit_parser.add_argument("--expect-revision", required=True, type=int)
    outcome = commit_parser.add_mutually_exclusive_group(required=True)
    outcome.add_argument("--to", help="target state for a normal transition")
    outcome.add_argument("--fail", metavar="CONDITION", help="failed condition id; outcome follows its failure definition")
    outcome.add_argument("--complete", action="store_true", help="complete the current terminal state")
    commit_parser.add_argument("--satisfy", action="append", default=[], metavar="CONDITION")
    commit_parser.add_argument("--artifact", action="append", default=[], metavar="ID=PATH")
    commit_parser.add_argument("--artifact-ref", action="append", default=[], metavar="ID=URI")
    commit_parser.add_argument("--artifact-summary", action="append", default=[], metavar="ID=TEXT")
    commit_parser.add_argument("--evidence", help="evidence for a failed condition")
    return root


def main() -> int:
    args = parser().parse_args()
    try:
        if args.command == "open":
            result = open_run(args)
        elif args.command == "commit":
            result = commit_run(args)
        else:
            result = inspect_run(args)
        emit(result)
        return 0
    except RuntimeFailure as exc:
        emit({"ok": False, "error": str(exc)})
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
