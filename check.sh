#!/usr/bin/env bash
# Проверка консистентности репо. Запуск: ./check.sh
# Кода тут нет, поэтому «тесты» — это проверки того, что инструкции скилла
# не противоречат друг другу и не ссылаются в пустоту.
set -uo pipefail
cd "$(dirname "$0")" || { echo "cannot cd to repo root"; exit 2; }

fail=0
ok()   { printf '  ok   %s\n' "$1"; }
bad()  { printf '  FAIL %s\n' "$1"; fail=1; }
indent() { printf '%s\n' "${1//$'\n'/$'\n'       }" | sed '1s/^/       /'; }

echo "1. relative links resolve"
broken=$(git ls-files -z '*.md' | xargs -0 grep -noE '\]\(([^)h][^)]*)\)' | while IFS=: read -r f l t; do
  t=${t#\]\(}; t=${t%\)}; t=${t%%#*}
  [ -z "$t" ] && continue
  [ -e "$(dirname "$f")/$t" ] || echo "$f:$l -> $t"
done)
if [ -z "$broken" ]; then ok "all resolve"; else indent "$broken"; bad "broken links"; fi

echo "2. no secrets in tracked files"
# Exclude this file: it holds the pattern, so it always matches itself.
hits=$(git ls-files -z -- ':(exclude)check.sh' | xargs -0 grep -nEi 'api[_-]?key|secret|token|passwo?r?d|sk-[A-Za-z0-9]{16,}|ghp_|AKIA[0-9A-Z]{16}' || true)
if [ -z "$hits" ]; then ok "none"; else indent "$hits"; bad "possible secret"; fi

echo "3. SKILL.md frontmatter"
python3 - <<'PY' || fail=1
import io,re,sys
s=io.open('essayist/SKILL.md',encoding='utf-8').read()
m=re.match(r'^---\n(.*?)\n---\n',s,re.S)
if not m: print("  FAIL missing frontmatter"); sys.exit(1)
k=dict(re.findall(r'^([a-z]+):\s*(.+)$',m.group(1),re.M))
if k.get('name')!='essayist': print("  FAIL name=%r"%k.get('name')); sys.exit(1)
if not k.get('description'): print("  FAIL empty description"); sys.exit(1)
print("  ok   name=%s, description=%d chars"%(k['name'],len(k['description'])))
PY

echo "4. README structure block == tracked skill files"
if diff <(sed -n '/^essayist\//,/^```$/p' README.md | grep -oE '[A-Za-z-]+\.md' | sort -u) \
        <(git ls-files 'essayist/*' | xargs -n1 basename | sort -u) >/dev/null; then
  ok "matches"
else
  indent "$(diff <(sed -n '/^essayist\//,/^```$/p' README.md | grep -oE '[A-Za-z-]+\.md' | sort -u) \
                 <(git ls-files 'essayist/*' | xargs -n1 basename | sort -u))"
  bad "README tree out of sync"
fi

echo "5. session statuses used == template enum"
python3 - <<'PY' || fail=1
import io,re,sys
tpl=set(x.strip() for x in re.search(r'status: (.+)',
    io.open('essayist/assets/session-template.md',encoding='utf-8').read()).group(1).split('|'))
used=set(re.findall(r'status: ([a-z]+)',io.open('essayist/SKILL.md',encoding='utf-8').read()))
if used-tpl: print("  FAIL unknown status: %s"%sorted(used-tpl)); sys.exit(1)
print("  ok   %s"%", ".join(sorted(used)))
PY

echo "6. no bare relative essays/ path in skill (must use <base>)"
# SKILL.md defines the base with a real absolute path; that one line is the
# exception every other file must go through.
hits=$(git ls-files -z 'essayist/*' | xargs -0 grep -n 'essays/' | grep -v 'далее <base>' || true)
if [ -z "$hits" ]; then ok "all use <base>"; else indent "$hits"; bad "bare essays/ path"; fi

echo
if [ $fail -eq 0 ]; then echo "PASS"; else echo "FAIL"; fi
exit $fail
