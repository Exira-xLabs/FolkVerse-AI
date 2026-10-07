#!/usr/bin/env python3
"""Fail-closed staged/current-tree secret gate. Never prints secret values."""
import argparse, os, pathlib, re, shutil, subprocess, sys, tempfile

PATTERNS=[
    r'\bsk-(?:proj|svcacct)-[A-Za-z0-9_-]{16,}',r'\bsk_live_[A-Za-z0-9]{8,}',
    r'\bgithub_pat_[A-Za-z0-9_]{16,}',r'\bgh[pousr]_[A-Za-z0-9]{20,}',
    r'\bhf_[A-Za-z0-9]{20,}',r'\bAKIA[0-9A-Z]{16}\b',
    r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',r'\bxox[baprs]-[A-Za-z0-9-]{10,}',
]

def git(*args):
    return subprocess.check_output(['git',*args])

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--staged',action='store_true')
    parser.add_argument('--tracked',action='store_true')
    args=parser.parse_args()
    try:
        repo=pathlib.Path(git('rev-parse','--show-toplevel').decode().strip());os.chdir(repo)
        scanner=os.environ.get('GITLEAKS_BIN') or shutil.which('gitleaks')
        if not scanner: raise RuntimeError('gitleaks is required; install the reviewed version before committing')
        if args.staged:
            paths=git('diff','--cached','--name-only','--diff-filter=ACMR','-z').split(b'\0')
        else:
            paths=git('ls-files','-z').split(b'\0')
        errors=[];compiled=[re.compile(p.encode()) for p in PATTERNS]
        with tempfile.TemporaryDirectory(prefix='hermes-secret-gate-') as directory:
            export=pathlib.Path(directory)
            for raw in paths:
                if not raw: continue
                name=raw.decode('utf-8',errors='surrogateescape');relative=pathlib.PurePosixPath(name)
                if relative.is_absolute() or '..' in relative.parts: raise RuntimeError('Unsafe repository path')
                content=git('show',':'+name)
                if len(content)>100*1024*1024: raise RuntimeError('Blob exceeds gate limit: '+name)
                for pattern in compiled:
                    if pattern.search(content): errors.append(name+': hardcoded secret pattern')
                dest=export/name;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(content)
            result=subprocess.run([scanner,'dir',str(export),'--no-banner','--redact','--exit-code','1'],capture_output=True,timeout=120)
            if result.returncode: errors.append('gitleaks rejected the content or failed; run its redacted scan locally for details')
        if errors:
            print('SECRET GATE BLOCKED:',*sorted(set(errors)),sep='\n',file=sys.stderr);return 1
        print('Secret gate PASS ('+str(sum(bool(p) for p in paths))+' index blobs; gitleaks completed)');return 0
    except (subprocess.SubprocessError,OSError,RuntimeError) as e:
        print('SECRET GATE ERROR: '+str(e)+'; commit rejected',file=sys.stderr);return 2

if __name__=='__main__': raise SystemExit(main())
