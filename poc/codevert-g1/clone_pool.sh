#!/usr/bin/env bash
# G1 pool clone per DESIGN-PIN.md §2.1 (pinned order; backups on failure)
set -u
cd "$(dirname "$0")/corpus"
PRIMARY="psf/requests pallets/jinja pallets/markupsafe pallets/itsdangerous python-attrs/attrs GrahamDumpleton/wrapt dateutil/dateutil pytest-dev/pluggy pypa/packaging jawah/charset_normalizer kjd/idna pallets-eco/blinker hukkin/tomli python-humanize/humanize jd/tenacity tkem/cachetools micheles/decorator grantjenks/python-sortedcontainers mahmoud/boltons arrow-py/arrow"
BACKUP="marshmallow-code/marshmallow jmespath/jmespath.py jquast/wcwidth Suor/funcy keleshev/schema"
for r in $PRIMARY $BACKUP; do
  name="${r#*/}"
  [ -d "$name" ] && continue
  git clone --depth 1 --quiet "https://github.com/$r.git" "$name" 2>>clone.log && echo "OK $r" || echo "FAIL $r"
done
