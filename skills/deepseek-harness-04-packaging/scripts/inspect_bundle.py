#!/usr/bin/env python3
"""Read-only structural checks for a local DSH bundle and optional npm tarball.

Uses only the Python standard library. Does not execute package scripts, parse
Cordis YAML, evaluate semver, resolve dependencies, or install the package.
"""

import argparse
import json
from pathlib import Path, PurePosixPath, PureWindowsPath
import sys
import tarfile


def inspect_bundle(directory, tarball=None):
    root = Path(directory).resolve()
    errors, warnings, required = [], [], set()

    def require_file(raw, label):
        if not isinstance(raw, str) or not raw:
            errors.append(f'{label}: expected a non-empty relative path')
            return
        normal = raw.replace('\\', '/')
        pure = PurePosixPath(normal)
        if pure.is_absolute() or PureWindowsPath(raw).drive or '..' in pure.parts:
            errors.append(f'{label}: path must stay within the package')
            return
        candidate = (root / normal).resolve()
        if not candidate.is_relative_to(root) or not candidate.is_file():
            errors.append(f'{label}: file is absent or outside package: {raw}')
            return
        required.add(candidate.relative_to(root).as_posix())

    try:
        manifest = json.loads((root / 'package.json').read_text(encoding='utf-8-sig'))
    except (OSError, ValueError) as exc:
        return {'ok': False, 'errors': [f'package.json: {exc}'], 'warnings': []}
    if not isinstance(manifest, dict):
        return {'ok': False, 'errors': ['package.json must be an object'], 'warnings': []}
    for key in ('name', 'version'):
        if not isinstance(manifest.get(key), str) or not manifest[key]:
            errors.append(f'{key}: expected a non-empty string')
    required.add('package.json')
    dsh = manifest.get('dsh', {})
    bundle = dsh.get('bundle') if isinstance(dsh, dict) else None
    if not isinstance(bundle, dict):
        errors.append('dsh.bundle is missing; a plain dependency is not an activated bundle')
    else:
        patches = bundle.get('patch')
        patches = [patches] if isinstance(patches, str) else patches
        if not isinstance(patches, list) or not patches:
            errors.append('dsh.bundle.patch must be a path or a non-empty path list')
        else:
            for value in patches:
                require_file(value, 'dsh.bundle.patch')
    if isinstance(dsh, dict) and 'profile' in dsh:
        errors.append('this bundle should not also declare dsh.profile')
    if 'main' in manifest:
        require_file(manifest['main'], 'main')

    def visit_exports(value):
        if isinstance(value, str):
            if '*' in value:
                warnings.append(f'exports wildcard not expanded: {value}')
            else:
                require_file(value, 'exports')
        elif isinstance(value, dict):
            for child in value.values():
                visit_exports(child)
        elif isinstance(value, list):
            for child in value:
                visit_exports(child)
        elif value is not None:
            errors.append('exports contains an unsupported value')

    if 'exports' in manifest:
        visit_exports(manifest['exports'])
    if 'main' not in manifest and 'exports' not in manifest:
        warnings.append('no explicit main/exports; inspect actual plugin module resolution')
    if not manifest.get('files'):
        warnings.append('no files allowlist; inspect the actual pack output')
    engines = manifest.get('engines', {})
    if not isinstance(engines, dict) or not engines.get('dsh'):
        warnings.append('no explicit engines.dsh compatibility range')
    if any(name.endswith(('.ts', '.tsx')) and not name.endswith('.d.ts') for name in required):
        warnings.append('TypeScript entry detected; verify the distributed runtime can load it')
    tarball_files = None
    if tarball:
        try:
            with tarfile.open(tarball, mode='r:gz') as archive:
                members = archive.getmembers()
                tarball_files = sorted(m.name for m in members if m.isfile())
                for member in members:
                    path = PurePosixPath(member.name)
                    if path.is_absolute() or '..' in path.parts or member.issym() or member.islnk():
                        errors.append(f'tarball contains an unsafe or linked entry: {member.name}')
                for filename in required:
                    if f'package/{filename}' not in tarball_files:
                        errors.append(f'tarball is missing package/{filename}')
                packed = archive.extractfile('package/package.json')
                if packed is None:
                    raise ValueError('missing packed manifest')
                packed_manifest = json.load(packed)
                for key in ('name', 'version', 'dsh'):
                    if packed_manifest.get(key) != manifest.get(key):
                        errors.append(f'packed manifest differs in {key}')
        except (OSError, tarfile.TarError, KeyError, ValueError, AttributeError) as exc:
            errors.append(f'tarball: {exc}')
    return {
        'ok': not errors,
        'package': manifest.get('name'),
        'version': manifest.get('version'),
        'required_files': sorted(required),
        'tarball_files': tarball_files,
        'errors': errors,
        'warnings': sorted(set(warnings)),
        'limits': 'Structure only; no YAML semantics, dependency resolution or DSH runtime validation.',
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', type=Path)
    parser.add_argument('--tarball', type=Path)
    args = parser.parse_args()
    report = inspect_bundle(args.directory, args.tarball)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report['ok'] else 1


if __name__ == '__main__':
    sys.exit(main())
