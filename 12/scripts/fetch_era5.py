"""Fetch one real ERA5 hour from CDS; never contains credentials or renders maps."""
import argparse
import hashlib
from importlib.metadata import version
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="Print selection only; no imports or network requests")
    parser.add_argument("--resume-only", action="store_true", help="Only resume a saved job; never submit a new CDS request")
    parser.add_argument("--config", default="config/era5_request.json", help="Day 12 request configuration; default remains January")
    args = parser.parse_args()
    config_path=(ROOT / args.config).resolve()
    if not config_path.is_relative_to(ROOT.resolve()):
        sys.exit('Request configuration must stay in Day 12.')
    config = json.loads(config_path.read_text(encoding="utf-8"))
    dataset = config['dataset']
    target = ROOT / 'data/cache' / config['cache_filename']
    if target.resolve().parent != (ROOT / 'data/cache').resolve():
        sys.exit('Cache filename must stay in Day 12 data/cache.')
    request = config['request']
    if args.dry_run:
        print(json.dumps({"dataset": dataset, "request": request, "target": str(target)}, indent=2))
        return
    if target.exists():
        if target.stat().st_size == 0:
            sys.exit("Empty cache file: inspect/remove it before retrying.")
        print("Cache exists; no request submitted. Validate its metadata before rendering.")
        return
    handle_path = target.with_suffix('.job.json')
    if args.resume_only and not handle_path.is_file():
        sys.exit('Resume-only requested but no saved job exists; no CDS request submitted.')
    rc = Path(os.environ.get("CDSAPI_RC", str(Path.home() / ".cdsapirc")))
    env_ready = bool(os.environ.get("CDSAPI_URL") and os.environ.get("CDSAPI_KEY"))
    if not rc.is_file() and not env_ready:
        sys.exit("CDS credentials missing. Configure ~/.cdsapirc outside the repository; never paste a token into this script.")
    try:
        import cdsapi
    except ImportError:
        sys.exit('Install cdsapi>=0.7.7 in a local environment first.')
    client_version = version("cdsapi")
    if tuple(int(x) for x in client_version.split(".")[:3]) < (0, 7, 7):
        sys.exit("Upgrade cdsapi to >=0.7.7; legacy CDS settings are not supported here.")
    target.parent.mkdir(parents=True, exist_ok=True)
    partial = target.with_suffix(".nc.part")
    client = cdsapi.Client(wait_until_complete=False, retry_max=3, sleep_max=10, timeout=120)
    if client.url.rstrip("/") != "https://cds.climate.copernicus.eu/api":
        sys.exit("Configure the current official CDS endpoint: https://cds.climate.copernicus.eu/api")
    request_hash = hashlib.sha256(json.dumps({'dataset': dataset, 'request': request}, sort_keys=True).encode()).hexdigest()
    if handle_path.exists():
        handle = json.loads(handle_path.read_text(encoding='utf-8'))
        if handle['request_sha256'] != request_hash:
            sys.exit('Cached job describes a different request. Use a distinct cache filename.')
        print('Resuming the existing CDS request; no duplicate job submitted.')
        remote = client.client.get_remote(handle['request_id'])
    else:
        if args.resume_only:
            sys.exit('Resume-only forbids submitting a new CDS request.')
        remote = client.retrieve(dataset, request)
        handle = {'request_id': remote.request_id, 'request_sha256': request_hash,
                  'dataset': dataset, 'request': request}
        handle_path.write_text(json.dumps(handle, indent=2) + '\n', encoding='utf-8')
    remote.download(str(partial))
    if partial.stat().st_size == 0:
        sys.exit("Download was empty; cache not finalized.")
    partial.replace(target)
    manifest = {"dataset": dataset, "request": request, "request_id": handle['request_id'], "cdsapi_version": client_version,
                "validation_status": "downloaded_not_yet_scientifically_validated"}
    target.with_suffix(".request.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print("Downloaded and cached. Validate time, units, coordinates and finite values before rendering.")


if __name__ == "__main__":
    main()
