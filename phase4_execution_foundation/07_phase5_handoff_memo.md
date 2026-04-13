# フェーズ5接続メモ（Phase 5 Handoff Memo）

> **ステップ対応**: フェーズ4完了時の引き継ぎ資料  
> **最終更新**: 2026-04-13

---

## このメモの役割

フェーズ4で整備した実行基盤が、フェーズ5（AI参謀による統合）でどのように使われるかを明示し、両フェーズのハンドオフを確保する。
本ハンドオフメモは、フェーズ4からフェーズ5への引き継ぎを完全にするための基盤である。

---

## フェーズ4で整備したもの

### 全体像

フェーズ4では、以下の7つの実行基盤を整備した。

#### 1. 実行フロー定義 (01_execution_flow.md)
- 調査→比較→実装→修正→検証→記録→GitHub反映の7ステップ
- 各ステップの開始条件・終了条件・チェックポイント
- 判定ポイント（続行 vs 検討→修正 vs ロールバック）
- **フェーズ5での使い方**: AI参謀が各ステップの進行状況を判定し、次ステップ実行判定を自動化

#### 2. ツール最大活用方針 (02_tool_maximization_policy.md)
- D1採用候補（MCP、Subagents、Hooks、Skills等）の使用役割・深掘りポイント
- P1優先（6項目）と P2優先（6項目）の判定基準
- D2試験採用（12項目）の段階的実装方法
- 複合ツール活用シナリオ（Agent実装、自動化パイプライン、評価パイプライン）
- **フェーズ5での使い方**: AI参謀が新しい課題に直面したとき、最初にこのポリシーを参照して使用ツールを選定

#### 3. 新規ツール即時投入ルール (03_new_tool_intake_rules.md)
- 「あとで検討」を排除
- 4段階判定フロー（直接影響→既存比較→セットアップ時間→判定）
- 15分タイムボックス判定プロセス
- 即時採用（<30分）と試験採用（30-120分）の区分
- **フェーズ5での使い方**: AI参謀が新しいツールを発見したとき、即座にこのルールで採用/不採用を判定

#### 4. 作業単位定義 (04_work_unit_definitions.md)
- 5つの作業単位（調査・比較・実装・修正・記録）の標準化
- 各単位の開始条件・終了条件・チェックポイント
- 単位ごとの記録フォーマット
- 並列実行可能性の判定方法
- **フェーズ5での使い方**: AI参謀が作業を分割・並列化・優先順位付けするときの基準

#### 5. 品質保証ルール (05_quality_assurance_rules.md)
- 4階層自己検証（構文→インポート→機能→パフォーマンス/セキュリティ）
- Git差分確認の必須化
- 完了条件チェックリスト
- 影響範囲確認フロー
- 未完了報告・問題隠蔽禁止
- **フェーズ5での使い方**: AI参謀が実装品質を自動検証し、PASS/FAILで次アクション判定

#### 6. GitHub統合方針 (06_github_integration_policy.md)
- コミット単位の標準化（1タスク=1コミット〜複数関連コミット）
- コミットメッセージフォーマット（タイプ・スコープ・説明・詳細）
- 外部リソース参照の記録方法
- 復帰可能性の確保（ロールバック・ブランチ隔離・タグ記録）
- PR フォーマット・マージ戦略
- **フェーズ5での使い方**: AI参謀がGitHub差分・PR・履歴からコード変更の意図と背景を自動追跡

#### 7. フェーズ5接続メモ（このファイル）
- フェーズ4成果物の全景説明
- フェーズ5での使い方明示
- AI参謀がアクセスすべきファイル・ルール・判定フロー

---

## フェーズ5での使用方法

### AI参謀の基本動作フロー

```
フェーズ5開始
  ↓
新しい課題・要件が発生
  ↓
[実行フロー定義] で現在位置を確認
  ↓
次に何をするかの判定
  ├─ 新規ツール発見? → [新規ツール即時投入ルール] で評価
  ├─ ツール選定必要? → [ツール最大活用方針] で P1/P2 確認
  ├─ 作業分割必要? → [作業単位定義] で粒度判定
  ├─ 実装・修正? → [品質保証ルール] で検証方法確認
  ├─ GitHub推移? → [GitHub統合方針] でコミット・PR手順確認
  └─ 状態判定不明? → [フェーズ4作業指示書] で中間状態を確認

  ↓
該当ルール・フロー を参照して実行
  ↓
[完了条件チェックリスト] で完了判定
  ↓
[GitHub統合方針] で差分・コミット記録
  ↓
次の課題へ (ループ)
```

### 各ルールへのアクセスパターン

#### パターン1: 新規ツール発見時
```
1. [新規ツール即時投入ルール] を開く
2. 4段階判定フロー実行（約15分）
3. 採用判定 → [ツール最大活用方針] でユースケース確認
4. 試験採用なら段階的実装フロー参照
5. [作業単位定義] で記録単位設定
```

#### パターン2: 複数候補から判定する時
```
1. [ツール最大活用方針] の P1/P2 リストで候補確認
2. 複数候補が同等なら、フェーズ2の比較結果参照
3. [作業単位定義] の比較単位フロー実行
4. [実行フロー定義] の比較ステップで採用判定
```

#### パターン3: 実装・テストする時
```
1. [作業単位定義] で対象タスク単位確認
2. [品質保証ルール] の 4階層検証方法確認
3. 実装 → 自己検証 → 差分確認
4. [GitHub統合方針] で commit/push手順実行
5. [完了条件チェックリスト] で完了判定
```

#### パターン4: 問題が発生した時
```
1. [品質保証ルール] の問題隠蔽禁止ルール確認
2. 以下のいずれかを選択：
   a) その場で修正 → [作業単位定義] の修正単位フロー
   b) 一時的に隔離 → コメント化・未完了報告
   c) ロールバック → [GitHub統合方針] の復帰可能性確認
3. [GitHub統合方針] の PR フォーマットで進捗報告
```

#### パターン5: 進捗確認する時
```
1. [GitHub統合方針] で commit 履歴確認（git log）
2. [作業単位定義] の記録フォーマットで各タスク確認
3. [実行フロー定義] で全体進行状況を判定
4. 未完了事項あれば [品質保証ルール] で対応方針決定
```

---

## AI参謀が直接アクセスすべきファイル

### 常時参照（毎実行時）

1. **01_execution_flow.md** - 現在位置の確認、次ステップ判定
2. **04_work_unit_definitions.md** - タスク単位の明確化、記録フォーマット
3. **05_quality_assurance_rules.md** - 検証方法、完了条件確認

### 選択的参照（判定時）

4. **02_tool_maximization_policy.md** - ツール選定時
5. **03_new_tool_intake_rules.md** - 新規ツール発見時
6. **06_github_integration_policy.md** - git操作時

### 初回設定時

7. **10.フェーズ4作業指示書.md** - フェーズ4全体の中間状態確認
8. **9.フェーズ4 要件定義書.md** - フェーズ4の完了条件再確認

### 外部参照（コンテキスト）

- **phase3_knowledge_foundation/** - 知識活用ルール、再確認ルール
- **phase2_decision_foundation/** - ツール採用状態、比較結果
- **GitHub差分・コミット履歴** - 実行履歴トレース

---

## フェーズ5での自動判定ロジック

### 判定1：次ステップの判定

```python
def determine_next_step(current_state):
    """
    [実行フロー定義] の 7ステップに基づき、
    現在の完了状態から次に何をするかを判定
    """
    if not all(completion_check(current_step)):
        return "self_verify"      # 検証ステップへ
    elif has_issues():
        return "fix_step"         # 修正ステップへ
    elif current_step == "investigation":
        return "comparison"       # 次ステップへ
    else:
        return "github_integration"  # 最終ステップへ
```

### 判定2：ツール選定の判定

```python
def select_tools(task_type):
    """
    [ツール最大活用方針] と [新規ツール即時投入ルール] に基づき、
    タスクタイプから最適なツール組み合わせを自動選定
    """
    # P1優先から確認
    candidates = search_in_policy(
        tool_maximization_policy.p1_priority
    )
    
    # P2優先と試験採用を検討
    if not sufficient(candidates):
        candidates += search_in_policy(
            tool_maximization_policy.p2_priority,
            tool_maximization_policy.d2_trial
        )
    
    return rank_by_effectiveness(candidates, task_type)
```

### 判定3：新規ツール評価の判定

```python
def evaluate_new_tool(tool_candidate):
    """
    [新規ツール即時投入ルール] の 4段階フロー
    """
    # 段階1：直接影響判定
    if not directly_affects_work(tool_candidate):
        return "REJECT"
    
    # 段階2：既存との比較
    if not better_than_existing(tool_candidate):
        return "REJECT"
    
    # 段階3：セットアップ時間判定
    setup_time = estimate_setup_time(tool_candidate)
    
    if setup_time < 30:
        return "ADOPT_IMMEDIATELY"
    elif setup_time < 120:
        return "TRIAL_ADOPTION"
    else:
        return "DEFER_TO_NEXT_PHASE"
```

### 判定4：品質検証の自動実行

```python
def auto_verify_quality(implementation):
    """
    [品質保証ルール] の 4階層検証を自動実行
    """
    results = {
        "syntax_validation": check_syntax(implementation),
        "import_validation": check_imports(implementation),
        "functional_validation": run_tests(implementation),
        "performance_validation": check_perf(implementation)
    }
    
    if all(results.values()):
        return "PASS"
    else:
        return "FAIL", problem_details(results)
```

### 判定5：GitHub変更の自動記録

```python
def auto_record_github(changes):
    """
    [GitHub統合方針] に基づき、
    変更を自動的に commit/push/PR として記録
    """
    # 1. git diff で変更確認
    diff_result = verify_diff(changes)
    
    # 2. 変更単位を判定
    units = categorize_by_work_unit(changes)
    
    # 3. 各単位でコミット
    for unit in units:
        commit_message = generate_commit_message(unit)
        git_commit(unit, commit_message)
    
    # 4. PR 必要なら作成
    if needs_pr(units):
        create_pr(units)
    
    # 5. main へ push
    git_push("origin", "main")
```

---

## フェーズ4→5の移行チェックリスト

### 移行前に確認すべき項目

```
フェーズ4完了時チェックリスト:

自己検証
  [ ] 全実装に4階層検証が完了している
  [ ] FAIL項目が全て修正・再検証されている
  [ ] 検証結果が記録されている

差分確認
  [ ] 全変更ファイルが git diff で確認可能
  [ ] 意図しない変更がない
  [ ] 必要な変更が全て含まれている

完了条件確認
  [ ] 全作業に完了条件が定義されている
  [ ] 全完了条件がチェックされている
  [ ] 未チェック項目がない

影響範囲確認
  [ ] 全変更に対して関連ファイルが洗い出されている
  [ ] 関連ファイルで影響テストが実施されている
  [ ] 副作用がないことが確認されている

未完了報告
  [ ] スコープ外事項が明記されている
  [ ] 後回し事項が明記されている（対応時期付き）
  [ ] 課題が明記されている（対応内容付き）
  [ ] 隠蔽事項がない

コード品質
  [ ] パフォーマンス基準を満たしている
  [ ] セキュリティ基準を満たしている
  [ ] コード品質基準を満たしている

GitHub連携
  [ ] 全変更がコミット履歴に記録されている
  [ ] 各タスク単位で履歴が追跡可能
  [ ] 必要に応じて復帰可能
  [ ] PR がすべてマージ済み
  [ ] origin/main が最新の状態

→ すべてチェック後、フェーズ5へ移行可能
```

---

## フェーズ5での最初の操作

### 初期化手順

```bash
# 1. 最新コードを pull
git pull origin main

# 2. フェーズ4成果物ディレクトリ構造確認
ls -la phase4_execution_foundation/

# 3. フェーズ4の完了状態を確認
cat 10.フェーズ4作業指示書.md | grep -A 10 "完了状態"

# 4. 最新コミット確認
git log -10 --oneline

# 5. フェーズ5初期化スクリプト（あれば）実行
# bash scripts/phase5_init.sh
```

### 初期設定

```python
# フェーズ5 AI参謀の初期化例
class Phase5Strategist:
    def __init__(self):
        # フェーズ4の実行基盤をロード
        self.execution_flow = load_file("01_execution_flow.md")
        self.tool_policy = load_file("02_tool_maximization_policy.md")
        self.tool_intake_rules = load_file("03_new_tool_intake_rules.md")
        self.work_units = load_file("04_work_unit_definitions.md")
        self.qa_rules = load_file("05_quality_assurance_rules.md")
        self.github_policy = load_file("06_github_integration_policy.md")
        
        # 現在の実行状態を確認
        self.git_log = get_git_log()
        self.phase4_status = get_phase4_completion_status()
    
    def run(self, new_requirement):
        """新しい要件が発生したときの実行フロー"""
        # 実行フロー定義で判定
        current_step = self.execution_flow.identify_step(self.phase4_status)
        next_step = self.execution_flow.determine_next_step(current_step)
        
        # ツール選定（最大活用方針）
        tools = self.tool_policy.select_for(new_requirement)
        
        # 作業単位で分割
        tasks = self.work_units.divide_into_units(new_requirement)
        
        # 実行 → 検証 → GitHub記録
        for task in tasks:
            self.execute_task(task, tools)
            self.qa_rules.verify(task)
            self.github_policy.record(task)
        
        # 完了判定
        return self.qa_rules.is_complete(new_requirement)
```

---

## サポート＆トラブルシューティング

### Q. AI参謀が実行フローのどこにいるか分からない

**A.** `git log --oneline | head -20` で最新コミットを確認し、コミットメッセージから現在位置を判定。  
不明な場合は `10.フェーズ4作業指示書.md` の「中間状態」セクションを参照。

### Q. 新規ツールが発見されたが、採用すべきか分からない

**A.** `03_new_tool_intake_rules.md` の 4段階判定フロー（約15分）を実行。  
不採用判定なら「未完了報告」として記録。

### Q. テストが FAIL したが、どう対応すべき

**A.** `05_quality_assurance_rules.md` の「ルール6：エラー・問題の隠蔽禁止」を参照。  
以下のいずれかを選択：
1. その場で修正 → 再検証
2. 一時的に隔離 → コメント化
3. ロールバック → 別アプローチ

### Q. GitHub操作が不明確

**A.** `06_github_integration_policy.md` の「GitHub作業の標準フロー」セクションで該当パターン確認。  
PR フォーマットも同ファイルに記載。

---

## まとめ

フェーズ4は、フェーズ1-3で整備した情報基盤・判断基盤・知識基盤を、**実際の実行で最大効率・最高品質を実現するための基盤へ変換した**。

フェーズ5のAI参謀は、このフェーズ4成果物を常時参照し、以下を自動化する：

1. **実行フロー判定** - 現在位置と次ステップを自動判定
2. **ツール選定** - 最大活用方針に基づく最適ツール自動選定
3. **新規ツール評価** - 即時投入ルールで自動判定
4. **品質検証** - 4階層検証の自動実行と PASS/FAIL判定
5. **GitHub記録** - 変更の自動コミット・PR・push

---

## 関連ファイル参照マップ

```
フェーズ4成果物
├─ 01_execution_flow.md (ステップ判定)
├─ 02_tool_maximization_policy.md (ツール選定)
├─ 03_new_tool_intake_rules.md (新規ツール評価)
├─ 04_work_unit_definitions.md (タスク単位化)
├─ 05_quality_assurance_rules.md (品質検証)
├─ 06_github_integration_policy.md (GitHub記録)
└─ 07_phase5_handoff_memo.md (このファイル)

関連ドキュメント
├─ 9.フェーズ4 要件定義書.md (要件確認)
├─ 10.フェーズ4作業指示書.md (中間状態確認)
├─ phase3_knowledge_foundation/ (知識活用ルール)
├─ phase2_decision_foundation/ (採用判定・比較結果)
└─ GitHub logs & diffs (実行履歴トレース)
```
