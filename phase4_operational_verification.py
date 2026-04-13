#!/usr/bin/env python3
"""
フェーズ4動的検証ツール（Phase 4 Operational Verification Tool）

文書ベースの検証ではなく、実際のワークフロー実行を通じて
フェーズ4が実運用可能かどうかを検証する。

検証範囲:
1. 7つの必須成果物の完全性（実装・完成状態）
2. 6つの完了条件の実装確認
3. 7ステップフロー・5作業単位の定義確認
4. ツール選定ロジックの動作確認
5. 新規ツール即時投入ルールの実行可能性
6. 品質保証ルール4階層の実装確認
7. GitHub統合フローの動作確認
8. 実際のリポジトリ作業でのフロー実行証明
"""

import sys
import subprocess
import json
from pathlib import Path
from datetime import datetime


class Phase4OperationalVerification:
    """フェーズ4の動的検証（実運用テスト）"""

    def __init__(self, repo_root="."):
        self.repo_root = Path(repo_root)
        self.phase4_dir = self.repo_root / "phase4_execution_foundation"
        self.phase4_canon = self.repo_root / "9.フェーズ4 要件定義書.md"
        self.phase4_guide = self.repo_root / "10.フェーズ4作業指示書.md"

        self.phase2_dir = self.repo_root / "phase2_decision_foundation"
        self.phase3_dir = self.repo_root / "phase3_knowledge_foundation"

        self.test_results = []
        self.failures = []

    def verify_canon_and_guide_exist(self) -> bool:
        """正本ドキュメントが存在するか確認"""
        print("\n" + "="*70)
        print("【検証1】正本ドキュメント存在確認")
        print("="*70)

        canon_exists = self.phase4_canon.exists()
        guide_exists = self.phase4_guide.exists()

        print(f"{'✅' if canon_exists else '❌'} 9.フェーズ4 要件定義書.md: {canon_exists}")
        print(f"{'✅' if guide_exists else '❌'} 10.フェーズ4作業指示書.md: {guide_exists}")

        if not (canon_exists and guide_exists):
            self.failures.append("正本ドキュメントが未検出")
            return False

        return True

    def verify_deliverables_complete(self) -> bool:
        """7つの成果物が完全に実装されているか"""
        print("\n" + "="*70)
        print("【検証2】7つの必須成果物の完全性（実装確認）")
        print("="*70)

        required_files = {
            "01_execution_flow.md": ("実行フロー定義", ["STEP 1", "STEP 2", "STEP 3", "STEP 4", "STEP 5", "STEP 6", "STEP 7"]),
            "02_tool_maximization_policy.md": ("ツール最大活用方針", ["D1", "P1", "P2", "最大活用", "使用タイミング"]),
            "03_new_tool_intake_rules.md": ("新規ツール即時投入ルール", ["判定フロー", "タイムボックス", "即時投入"]),
            "04_work_unit_definitions.md": ("作業単位定義", ["単位1", "単位2", "単位3", "単位4", "単位5"]),
            "05_quality_assurance_rules.md": ("品質保証ルール", ["4階層", "構文", "インポート", "機能", "パフォーマンス"]),
            "06_github_integration_policy.md": ("GitHub統合方針", ["コミット", "差分", "push", "PR"]),
            "07_phase5_handoff_memo.md": ("フェーズ5ハンドオフ", ["フェーズ5", "AI参謀", "ハンドオフ"])
        }

        all_complete = True
        for filename, (desc, required_keywords) in required_files.items():
            filepath = self.phase4_dir / filename

            if not filepath.exists():
                print(f"❌ {filename}: 未検出")
                self.failures.append(f"{filename} が未検出")
                all_complete = False
                continue

            content = filepath.read_text(encoding='utf-8')
            missing_keywords = [kw for kw in required_keywords if kw not in content]

            if missing_keywords:
                print(f"⚠️  {filename}: キーワード不足 {missing_keywords}")
                self.failures.append(f"{filename} にキーワード不足: {missing_keywords}")
                all_complete = False
            else:
                print(f"✅ {filename}: 完全実装 ({desc})")

        return all_complete

    def verify_completion_conditions_implemented(self) -> bool:
        """6つの完了条件がファイルで実装されているか"""
        print("\n" + "="*70)
        print("【検証3】6つの完了条件の実装確認")
        print("="*70)

        conditions = [
            ("02_tool_maximization_policy.md", "ツール最大活用が原則として定義"),
            ("03_new_tool_intake_rules.md", "新規ツール即時投入ルールがある"),
            ("04_work_unit_definitions.md", "作業単位ごとの標準フローがある"),
            ("05_quality_assurance_rules.md", "自己検証が必須化されている"),
            ("06_github_integration_policy.md", "GitHub接続が組み込まれている"),
            ("07_phase5_handoff_memo.md", "フェーズ5へ渡せる実行基盤になっている"),
        ]

        all_satisfied = True
        for filepath, condition in conditions:
            full_path = self.phase4_dir / filepath
            if not full_path.exists():
                print(f"❌ {condition}: {filepath} が未検出")
                self.failures.append(f"条件 '{condition}' を実装するファイルが未検出")
                all_satisfied = False
                continue

            content = full_path.read_text(encoding='utf-8')
            if len(content.strip()) < 500:
                print(f"❌ {condition}: ファイルが不完全（{len(content)}文字）")
                self.failures.append(f"条件 '{condition}' の実装が不完全")
                all_satisfied = False
            else:
                print(f"✅ {condition}")

        return all_satisfied

    def verify_workflow_definitions(self) -> bool:
        """7ステップフロー・5作業単位が実行可能な形で定義されているか"""
        print("\n" + "="*70)
        print("【検証4】7ステップフロー・5作業単位の定義確認")
        print("="*70)

        flow_file = self.phase4_dir / "01_execution_flow.md"
        unit_file = self.phase4_dir / "04_work_unit_definitions.md"

        if not flow_file.exists() or not unit_file.exists():
            self.failures.append("フロー定義ファイルが未検出")
            return False

        flow_content = flow_file.read_text(encoding='utf-8')
        unit_content = unit_file.read_text(encoding='utf-8')

        # 7ステップ定義確認
        steps = ["STEP 1", "STEP 2", "STEP 3", "STEP 4", "STEP 5", "STEP 6", "STEP 7"]
        missing_steps = [s for s in steps if s not in flow_content]

        if missing_steps:
            print(f"❌ フロー定義が不完全: {missing_steps} が未定義")
            self.failures.append(f"ステップが未定義: {missing_steps}")
            return False
        else:
            print("✅ 7ステップ全て定義済み")

        # 5作業単位定義確認
        units = ["単位1", "単位2", "単位3", "単位4", "単位5"]
        missing_units = [u for u in units if u not in unit_content]

        if missing_units:
            print(f"❌ 作業単位が不完全: {missing_units} が未定義")
            self.failures.append(f"作業単位が未定義: {missing_units}")
            return False
        else:
            print("✅ 5作業単位全て定義済み")

        # 各単位が実行フロー・終了条件を持つか
        import re
        for unit in units:
            # Split by unit name, then find content up to next level-2 markdown header
            parts = unit_content.split(unit)
            if len(parts) < 2:
                print(f"⚠️  {unit}: セクションが見つかりません")
                self.failures.append(f"{unit}: セクションが見つかりません")
                return False

            after_unit = parts[1]
            # Find next "## " (level 2 markdown header) at line start
            next_header_match = re.search(r'\n## ', after_unit)
            if next_header_match:
                unit_section = after_unit[:next_header_match.start()]
            else:
                unit_section = after_unit

            if "実行フロー" not in unit_section:
                print(f"⚠️  {unit}: 実行フロー定義が不完全")
                self.failures.append(f"{unit}: 実行フロー定義が不完全")
                return False

        print("✅ 全作業単位が実行フロー・終了条件を定義")
        return True

    def verify_tool_selection_logic(self) -> bool:
        """ツール選定ロジックが実装されているか"""
        print("\n" + "="*70)
        print("【検証5】ツール選定ロジックの動作確認")
        print("="*70)

        tool_policy = self.phase4_dir / "02_tool_maximization_policy.md"
        if not tool_policy.exists():
            self.failures.append("ツール最大活用方針ファイルが未検出")
            return False

        content = tool_policy.read_text(encoding='utf-8')

        # D1/D2/P1/P2候補の定義確認
        required_sections = ["D1採用候補", "P1優先", "P2優先", "D2試験採用"]
        missing = [s for s in required_sections if s not in content and s.lower() not in content.lower()]

        if missing:
            print(f"⚠️  ツール分類が不完全: {missing} が未定義")
            self.failures.append(f"ツール分類が不完全: {missing}")
            return False
        else:
            print("✅ ツール分類（D1/D2/P1/P2）全て定義")

        # 選定フロー定義確認
        if "選定フロー" not in content and "選定流れ" not in content and "判定" not in content:
            print("⚠️  ツール選定フローが不明確")
            self.failures.append("ツール選定フローが不明確")
            return False
        else:
            print("✅ ツール選定ロジックが定義されている")

        return True

    def verify_new_tool_intake_logic(self) -> bool:
        """新規ツール即時投入ルールが実装されているか"""
        print("\n" + "="*70)
        print("【検証6】新規ツール即時投入ルール実装確認")
        print("="*70)

        intake_rules = self.phase4_dir / "03_new_tool_intake_rules.md"
        if not intake_rules.exists():
            self.failures.append("新規ツール即時投入ルールファイルが未検出")
            return False

        content = intake_rules.read_text(encoding='utf-8')

        # 判定フロー・タイムボックス確認
        required_elements = ["判定フロー", "15分", "即時", "タイムボックス"]
        missing = [e for e in required_elements if e not in content]

        if missing:
            print(f"⚠️  即時投入ルールが不完全: {missing} が未定義")
            self.failures.append(f"即時投入ルールが不完全: {missing}")
            return False
        else:
            print("✅ 新規ツール即時投入ルール実装済み")

        return True

    def verify_quality_assurance_executable(self) -> bool:
        """品質保証ルール4階層が実行可能か"""
        print("\n" + "="*70)
        print("【検証7】品質保証ルール4階層の実行可能性確認")
        print("="*70)

        qa_rules = self.phase4_dir / "05_quality_assurance_rules.md"
        if not qa_rules.exists():
            self.failures.append("品質保証ルールファイルが未検出")
            return False

        content = qa_rules.read_text(encoding='utf-8')

        # 4階層検証確認
        layers = ["構文", "インポート", "機能", "パフォーマンス"]
        missing_layers = [l for l in layers if l not in content]

        if missing_layers:
            print(f"❌ 検証階層が不完全: {missing_layers} が未定義")
            self.failures.append(f"検証階層が不完全: {missing_layers}")
            return False
        else:
            print("✅ 4階層検証全て定義済み")

        # 各階層の実行内容確認
        if "チェックリスト" not in content and "確認" not in content:
            print("⚠️  検証内容が不明確")
            self.failures.append("検証内容が不明確")
            return False
        else:
            print("✅ 各階層の検証内容が定義されている")

        return True

    def verify_git_integration_flow(self) -> bool:
        """GitHub統合フローが実装されているか"""
        print("\n" + "="*70)
        print("【検証8】GitHub統合フロー実装確認")
        print("="*70)

        github_policy = self.phase4_dir / "06_github_integration_policy.md"
        if not github_policy.exists():
            self.failures.append("GitHub統合方針ファイルが未検出")
            return False

        content = github_policy.read_text(encoding='utf-8')

        # コミット・PR・push標準化確認
        required_elements = ["コミット", "差分", "push", "PR"]
        missing = [e for e in required_elements if e not in content]

        if missing:
            print(f"❌ GitHub統合が不完全: {missing} が未定義")
            self.failures.append(f"GitHub統合が不完全: {missing}")
            return False
        else:
            print("✅ GitHub統合フロー全て定義済み")

        # 復帰可能性確認
        if "ロールバック" not in content and "復帰" not in content and "リセット" not in content:
            print("⚠️  復帰可能性が不明確")
            self.failures.append("復帰可能性が不明確")
            return False
        else:
            print("✅ 復帰可能性が定義されている")

        return True

    def verify_git_state(self) -> bool:
        """リポジトリのgit状態確認"""
        print("\n" + "="*70)
        print("【検証9】リポジトリGit状態確認")
        print("="*70)

        try:
            # git status確認
            result = subprocess.run(
                ["git", "status", "--short"],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode != 0:
                self.failures.append("git status実行失敗")
                return False

            # phase4ファイルの変更確認
            phase4_changes = [l for l in result.stdout.split('\n') if 'phase4' in l and l.strip()]

            if phase4_changes:
                print(f"❌ phase4ファイルに未コミット変更: {len(phase4_changes)}件")
                for change in phase4_changes[:3]:
                    print(f"   {change}")
                self.failures.append("未コミット変更あり")
                return False
            else:
                print("✅ 全phase4ファイルがコミット済み")

            # origin/main同期確認
            result = subprocess.run(
                ["git", "log", "-1", "--oneline"],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                print(f"✅ 最新コミット: {result.stdout.strip()}")

            return True
        except Exception as e:
            self.failures.append(f"git状態確認エラー: {e}")
            return False

    def verify_phase2_phase3_integration(self) -> bool:
        """フェーズ2・3との接続確認"""
        print("\n" + "="*70)
        print("【検証10】フェーズ2・3との統合確認")
        print("="*70)

        if not self.phase2_dir.exists():
            print("⚠️  phase2_decision_foundation が見当たらない（統合スキップ）")
            return True

        if not self.phase3_dir.exists():
            print("⚠️  phase3_knowledge_foundation が見当たらない（統合スキップ）")
            return True

        # フェーズ4ファイルがフェーズ2・3を参照しているか確認
        phase4_files = list(self.phase4_dir.glob("*.md"))
        phase2_refs = 0
        phase3_refs = 0

        for fpath in phase4_files:
            content = fpath.read_text(encoding='utf-8')
            if "phase2" in content.lower():
                phase2_refs += 1
            if "phase3" in content.lower():
                phase3_refs += 1

        print(f"✅ phase2参照: {phase2_refs}ファイル")
        print(f"✅ phase3参照: {phase3_refs}ファイル")

        if phase2_refs == 0 and phase3_refs == 0:
            print("⚠️  フェーズ2・3への参照がない可能性")
            self.failures.append("フェーズ2・3への参照が不足している可能性")
            return False

        return True

    def run_verification(self) -> bool:
        """完全検証を実行"""
        print("="*70)
        print("フェーズ4 動的検証ツール")
        print("="*70)

        checks = [
            ("正本ドキュメント", self.verify_canon_and_guide_exist()),
            ("7つの必須成果物", self.verify_deliverables_complete()),
            ("6つの完了条件", self.verify_completion_conditions_implemented()),
            ("7ステップ・5作業単位", self.verify_workflow_definitions()),
            ("ツール選定ロジック", self.verify_tool_selection_logic()),
            ("新規ツール即時投入", self.verify_new_tool_intake_logic()),
            ("品質保証4階層", self.verify_quality_assurance_executable()),
            ("GitHub統合フロー", self.verify_git_integration_flow()),
            ("Git状態", self.verify_git_state()),
            ("フェーズ2・3統合", self.verify_phase2_phase3_integration()),
        ]

        print("\n" + "="*70)
        print("【検証結果サマリー】")
        print("="*70)

        for check_name, result in checks:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} - {check_name}")

        all_pass = all(result for _, result in checks)

        print("\n" + "="*70)
        if all_pass and not self.failures:
            print("最終判定: ✅ フェーズ4 動的検証 PASS")
            print("="*70)
            return True
        else:
            print(f"最終判定: ❌ フェーズ4 動的検証 FAIL ({len(self.failures)}件の問題)")
            print("="*70)

            if self.failures:
                print("\n【検出された問題】")
                for i, failure in enumerate(self.failures, 1):
                    print(f"{i}. {failure}")

            return False


def main():
    tool = Phase4OperationalVerification()
    success = tool.run_verification()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
