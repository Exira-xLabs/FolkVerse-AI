"""Database-free integrity audit; this does not verify PostgreSQL restoration."""
import hashlib
import json
from collections import Counter
from datetime import datetime
from pathlib import Path

root = Path(__file__).resolve().parents[3]
snapshot = json.loads((root / 'data/manifests/corpus.json').read_text())
reviews = {r['id']: r for r in snapshot['review']}
results = {'record_counts': {}, 'approved_hash_checks': [], 'errors': []}
for kind in ['region', 'source', 'passage', 'exhibit', 'claim', 'artifact', 'media']:
    actual = Counter(r['status'] for r in snapshot[kind])
    results['record_counts'][kind] = dict(actual)
    for status, expected in snapshot['counts'][kind].items():
        if actual[status] != expected:
            results['errors'].append(f'{kind} {status} count mismatch')
    for row in snapshot[kind]:
        if row['status'] != 'approved':
            continue
        values = {k: v for k, v in row.items() if k not in {'status', 'review_id', 'embedding_version'}}
        if kind == 'source':
            values['fetched_at'] = datetime.fromisoformat(values['fetched_at'])
        if kind == 'exhibit':
            values['regions'] = sorted((r['region_id'], r['geographic_role']) for r in snapshot['exhibit_region'] if r['exhibit_id'] == row['id'])
            values['claims'] = sorted(r['id'] for r in snapshot['claim'] if r['exhibit_id'] == row['id'])
        if kind == 'claim':
            values['passages'] = sorted(r['passage_id'] for r in snapshot['claim_evidence'] if r['claim_id'] == row['id'])
        digest = hashlib.sha256(json.dumps(values, sort_keys=True, ensure_ascii=False, default=str).encode()).hexdigest()
        review = reviews.get(row['review_id'])
        passed = bool(review and review['entity_type'] == kind and review['entity_id'] == row['id'] and review['status'] == 'approved' and review['content_hash'] == digest)
        results['approved_hash_checks'].append({'kind': kind, 'id': row['id'], 'passed': passed})
        if not passed:
            results['errors'].append(f'{kind} {row["id"]} review mismatch')
for row in snapshot['source']:
    if hashlib.sha256(row['raw_payload'].encode()).hexdigest() != row['raw_hash']:
        results['errors'].append(f'{row["id"]} raw payload mismatch')
results['verified_source_payloads'] = len(snapshot['source'])
results['review_count'] = len(reviews)
results['approved_passages'] = [{k: r[k] for k in ['id', 'language', 'text', 'source_id', 'rights_status']} for r in snapshot['passage'] if r['status'] == 'approved']
results['present_image_files'] = sum(bool(r['storage_key']) and (root / r['storage_key']).is_file() for r in snapshot['media'])
results['manifest_downloaded_count'] = snapshot['counts']['downloaded_cc0_candidates']
results['fresh_snapshot_check_would_match_counts'] = results['present_image_files'] == results['manifest_downloaded_count']
(Path(__file__).parent / 'snapshot-probe.json').write_text(json.dumps(results, indent=2, ensure_ascii=False) + '\n')
print(json.dumps(results, indent=2, ensure_ascii=False))
raise SystemExit(bool(results['errors']))
