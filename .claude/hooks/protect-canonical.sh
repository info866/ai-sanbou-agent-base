#!/bin/bash
# 正本文書保護フック
# PreToolUse (Edit|Write) で呼び出される
# 正本文書への直接編集をブロックする
#
# 入力: stdin に JSON (tool_name, tool_input)
# 出力: exit 0 = 許可, exit 2 = ブロック（stdoutがエラーメッセージ）

input=$(cat)

# file_path を抽出（python3で安全にJSON解析）
file_path=$(echo "$input" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    print(d.get('tool_input', {}).get('file_path', ''))
except:
    print('')
" 2>/dev/null)

# file_path が空なら許可（解析失敗時は安全側で通す）
if [ -z "$file_path" ]; then
    exit 0
fi

# 保護対象パターン（正本文書）
protected_patterns=(
    "大分類要件提起書"
    "大分類作業指示書"
    "フェーズ1 要件定義書"
    "フェーズ1作業指示書"
    "フェーズ２ 要件定義書"
    "フェーズ２作業指示書"
    "フェーズ3 要件定義書"
    "フェーズ3作業指示書"
)

for pattern in "${protected_patterns[@]}"; do
    if echo "$file_path" | grep -q "$pattern"; then
        echo "正本文書の直接編集をブロックしました: $(basename "$file_path")"
        echo "正本文書は変更禁止です。内容を参照し、成果物ファイルに反映してください。"
        exit 2
    fi
done

# 保護対象外 → 許可
exit 0
