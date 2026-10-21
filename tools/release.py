#!/usr/bin/env python3
"""Protected release: verify history/packages, sign exact bytes, prepare Pages output.

No credentials are used on PRs. This runs only from reviewed main in the owner's
protected environment. An empty key pin or missing secret fails closed.
"""
import argparse
import base64
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import urllib.error
import urllib.request
from urllib.parse import urlsplit

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
import catalogue
from package_check import unpack_archive

ROOT = Path(__file__).resolve().parents[1]
INDEX = 'https://vyanhursky.github.io/DefJamFFNY-mods/index.json'
MAX_INDEX = 8 * 1024**2


class Redirects(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, message, headers, url):
        catalogue.https(url)
        return super().redirect_request(request,fp,code,message,headers,url)


def get(url, limit):
    catalogue.https(url)
    with urllib.request.build_opener(Redirects()).open(
            urllib.request.Request(url,headers={'User-Agent':'DefJamModCatalogue/1','Cache-Control':'no-cache','Accept-Encoding':'identity'}),timeout=30) as response:
        data=response.read(limit+1)
        catalogue.require(len(data)<=limit,'Response exceeds size limit')
        return data


def previous_index(keys, bootstrap=False):
    try:
        raw=get(INDEX,MAX_INDEX)
    except urllib.error.HTTPError as error:
        if error.code==404 and bootstrap:return {'revision':0,'mods':[]}
        if error.code==404:raise ValueError('Published history missing; refuse automatic bootstrap/reset') from error
        raise
    signature=get(INDEX+'.sig',64)
    trusted=False
    for key in keys:
        try:
            Ed25519PublicKey.from_public_bytes(bytes.fromhex(key)).verify(signature,raw)
            trusted=True;break
        except Exception:
            pass
    catalogue.require(trusted,'Prior published index signature is untrusted')
    previous=json.loads(raw,object_pairs_hook=catalogue.unique_object)
    catalogue.require(previous['schema']==1 and previous['game']=='defjam-ffny-recomp','Wrong prior catalogue')
    catalogue.build(previous['mods'],previous['revision'],previous['issued'],previous['expires'])
    return previous


def verify_downloads(rows, scan=True):
    with tempfile.TemporaryDirectory(prefix='defjam-catalogue-check-') as scratch:
        root=Path(scratch)
        for mod in rows:
            for version in mod['versions']:
                if version['version'] in mod['revoked_versions']:continue
                descriptor=version['archive']
                catalogue.require(descriptor['size']<=8*1024**3,'Archive too large')
                # Every mirror must contain exactly the reviewed bytes, including Content-Length.
                for mirror,url in enumerate(descriptor['urls']):
                    destination=root/'package.zip'
                    catalogue.https(url)
                    with urllib.request.build_opener(Redirects()).open(urllib.request.Request(url,headers={'Accept-Encoding':'identity'}),timeout=30) as response,destination.open('wb') as output:
                        catalogue.require(response.status==200 and int(response.headers.get('Content-Length','-1'))==descriptor['size'],'Download length/status mismatch')
                        count=0
                        while chunk:=response.read(1024*1024):
                            count+=len(chunk);catalogue.require(count<=descriptor['size'],'Oversized response');output.write(chunk)
                    target=root/'pack'
                    if target.exists():shutil.rmtree(target)
                    pack=unpack_archive(destination,descriptor,target)
                    catalogue.require(set(pack['capabilities'])<=set(version['capabilities']),'Required pack capability omitted')
                    if scan:subprocess.run(['clamscan','--recursive','--infected','--no-summary',str(target)],check=True)
                    shutil.rmtree(target);destination.unlink()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=('prepare','sign'))
    parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--bootstrap',action='store_true',help='Explicit first publication only; catalogue must be empty')
    args=parser.parse_args()
    keys=json.loads((ROOT/'catalogue-keys.json').read_text())['keys']
    catalogue.require(bool(keys),'Provision and review a public signing-key pin first')
    rows=catalogue.load_mods(ROOT/'mods')
    previous=previous_index(keys,bootstrap=args.bootstrap)
    catalogue.require(not args.bootstrap or (previous['revision']==0 and not rows),
                      'Bootstrap is only allowed for the first empty catalogue publication')
    catalogue.validate_history(rows,previous)
    now=dt.datetime.now(dt.timezone.utc)
    if args.command=='prepare':
        # This job has no signing/upload credentials. Untrusted image parsers and
        # malware scanners never share a process/environment with the private key.
        verify_downloads(rows)
        raw=catalogue.build(rows,previous['revision']+1,now.strftime('%Y-%m-%dT%H:%M:%SZ'),
                            (now+dt.timedelta(days=30)).strftime('%Y-%m-%dT%H:%M:%SZ'))
        args.out.mkdir(parents=True,exist_ok=False)
        (args.out/'index.json').write_bytes(raw)
        print('Verified unsigned catalogue revision',previous['revision']+1)
        return
    raw=(args.out/'index.json').read_bytes()
    catalogue.require(len(raw)<=MAX_INDEX,'Oversized prepared index')
    prepared=json.loads(raw,object_pairs_hook=catalogue.unique_object)
    catalogue.fields(prepared,'schema game revision issued expires mods')
    expected=catalogue.build(rows,previous['revision']+1,prepared['issued'],prepared['expires'])
    catalogue.require(raw==expected,'Prepared catalogue differs from approved source/revision')
    catalogue.require(catalogue.timestamp(prepared['expires'])>now.replace(tzinfo=None),'Prepared catalogue expired')
    catalogue.require(catalogue.timestamp(prepared['issued'])<=now.replace(tzinfo=None)+dt.timedelta(minutes=5),'Future catalogue')
    secret=os.environ.get('CATALOGUE_ED25519_KEY','')
    catalogue.require(bool(secret),'Protected signing secret is missing')
    private=Ed25519PrivateKey.from_private_bytes(base64.b64decode(secret,validate=True))
    catalogue.require(private.public_key().public_bytes_raw().hex() in keys,'Signing secret does not match a reviewed key pin')
    (args.out/'index.json.sig').write_bytes(private.sign(raw))
    # Public keys for inspection, never a substitute for the helper's built-in trust pin.
    (args.out/'catalogue-keys.json').write_text(json.dumps({'schema':1,'keys':keys},indent=2)+'\n')
    print('Signed catalogue revision',previous['revision']+1)


if __name__=='__main__':main()
