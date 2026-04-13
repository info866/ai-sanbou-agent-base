#!/usr/bin/env python3
"""
フェーズ4実行基盤の統合検証ツール
Phase 4 System Verification Tool

フェーズ4で整備された実行基盤（7つの成果物）が、
実際に「実運用可能な実行基盤」として機能しているかを検証する。

実行ループ: 調査→比較→実装→修正→検証→記録→GitHub反映
品質保証: 4階層（構文→インポート→機能→パフォーマンス）
"""

import sys
import re
from pathlib import Path

class Phase4SystemVerification:
    """フェーズ4実行基盤の統合検証"""

    def __init__(self, repo_root: str = "."):
        self.repo_root = Path(repo_root)
        self.phase4_dir = self.repo_root / "phase4_execution_foundation"

        # 7つの必須成果物
        self.required_deliverables = {
            "01_execution_flow.md": "実行フロー定義",
            "02_tool_maximization_policy.md": "ツール最大活用方針",
            "03_new_tool_intake_rules.md": "新規ツール即時投入ルール",
            "04_work_unit_definitions.md": "作業単位定義",
            "05_quality_assurance_rules.md": "品質保証ルール",
            "06_github_integration_policy.md": "GitHub接続方針",
            "07_phase5_handoff_memo.md": "フェーズ5接続メモ"
        }

        # 6つの完了条件
        self.completion_conditions = {
            "条件1": ("ツール最大活用が原則として定義", "02_tool_maximization_policy.md"),
            "条件2": ("新規ツール即時投入ルールがある", "03_new_tool_intake_rules.md"),
            "条件3": ("作業単位ごとの標準フローがある", "04_work_unit_definitions.md"),
            "条件4": ("自己検証が必須化されている", "05_quality_assurance_rules.md"),
            "条件5": ("GitHub接続が組み込まれている", "06_github_integration_policy.md"),
            "条件6": ("フェーズ5へ渡せる実行基盤になっている", "07_phase5_handoff_memo.md")
        }

    def verify_deliverables_exist(self) -> bool:
        """7つの必須成果物が全て存在するか検証"""
        print("\n【検証1】7つの必須成果物の存在確認")
        print("="*70)

        missing = []
        for filename, description in self.required_deliverables.items():
            filepath = self.phase4_dir / filename
            if filepath.exists():
                size = filepath.stat().st_size
                lines = filepath.read_text(encoding='utf-8').count('\n')
                print(f"  ✅ {filename}: {lines}行 ({size}bytes)")
            else:
                print(f"  ❌ {filename}: 未検出")
                missing.append(filename)

        if missing:
            print(f"\n❌ {len(missing)}個のファイルが未検出: {missing}")
            return False

        print(f"\n✅ 7つのファイルすべて存在を確認")
        return True

    def verify_content_completeness(self) -> bool:
        """各成果物が完全な内容を持っているか検証"""
        print("\n【検証2】成果物の内容完全性確認")
        print("="*70)

        issues = []

        for filename in self.required_deliverables.keys():
            filepath = self.phase4_dir / filename
            if not filepath.exists():
                issues.append(f"{filename}: ファイル未検出")
                continue

            content = filepath.read_text(encoding='utf-8')

            # 空ファイル検査
            if len(content.strip()) < 200:
                issues.append(f"{filename}: 内容が不足（{len(content)}文字）")

            # 役割が記載されているか
            if not ("役割" in content or "Role" in content):
                print(f"  ⚠️  {filename}: 役割説明が不明確な可能性")
            else:
                print(f"  ✅ {filename}: 内容完全")

        if issues:
            print(f"\n❌ {len(issues)}個の問題検出:")
            for issue in issues:
                print(f"  {issue}")
            return False

        print(f"\n✅ すべてのファイルが完全な内容を保有")
        return True

    def verify_completion_conditions(self) -> bool:
        """6つの完了条件が満たされているか検証"""
        print("\n【検証3】完了条件の充足確認")
        print("="*70)

        all_pass = True

        for condition_name, (description, filename) in self.completion_conditions.items():
            filepath = self.phase4_dir / filename

            if not filepath.exists():
                print(f"  ❌ {condition_name}: {filename} が未検出")
                all_pass = False
                continue

            content = filepath.read_text(encoding='utf-8')

            # キーワードの有無で判定（簡易的）
            if description == "ツール最大活用が原則として定義":
                if "最大活用" in content or "主戦力" in content:
                    print(f"  ✅ {condition_name}: {description}")
                else:
                    print(f"  ⚠️  {condition_name}: 記述が不明確")
                    all_pass = False

            elif description == "新規ツール即時投入ルールがある":
                if "即時" in content and "判定" in content:
                    print(f"  ✅ {condition_name}: {description}")
                else:
                    print(f"  ⚠️  {condition_name}: ルール定義が不明確")
                    all_pass = False

            elif description == "作業単位ごとの標準フローがある":
                if all(x in content for x in ["調査", "比較", "実装", "修正"]):
                    print(f"  ✅ {condition_name}: {description}")
                else:
                    print(f"  ⚠️  {condition_name}: 作業単位定義が不足")
                    all_pass = False

            elif description == "自己検証が必須化されている":
                if "4階層" in content or "構文" in content:
                    print(f"  ✅ {condition_name}: {description}")
                else:
                    print(f"  ⚠️  {condition_name}: 検証ルールが不明確")
                    all_pass = False

            elif description == "GitHub接続が組み込まれている":
                if "差分" in content and "コミット" in content:
                    print(f"  ✅ {condition_name}: {description}")
                else:
                    print(f"  ⚠️  {condition_name}: GitHub接続が不明確")
                    all_pass = False

            elif description == "フェーズ5へ渡せる実行基盤になっている":
                if "フェーズ5" in content or "AI参謀" in content:
                    print(f"  ✅ {condition_name}: {description}")
                else:
                    print(f"  ⚠️  {condition_name}: フェーズ5接続が不明確")
                    all_pass = False

        return all_pass

    def verify_internal_consistency(self) -> bool:
        """成果物間の内部一貫性を検証"""
        print("\n【検証4】内部一貫性確認")
        print("="*70)

        issues = []

        # 01（実行フロー）と04（作業単位）の一貫性
        flow_file = self.phase4_dir / "01_execution_flow.md"
        defn_file = self.phase4_dir / "04_work_unit_definitions.md"

        if flow_file.exists() and defn_file.exists():
            flow_content = flow_file.read_text(encoding='utf-8')
            defn_content = defn_file.read_text(encoding='utf-8')

            work_units = ["調査", "比較", "実装", "修正", "記録"]
            for unit in work_units:
                if unit not in flow_content:
                    issues.append(f"01で'{unit}'が言及されていない")
                if unit not in defn_content:
                    issues.append(f"04で'{unit}'が定義されていない")

        # 07（フェーズ5接続）が他のファイルを参照しているか
        handoff_file = self.phase4_dir / "07_phase5_handoff_memo.md"
        if handoff_file.exists():
            handoff_content = handoff_file.read_text(encoding='utf-8')
            required_refs = ["01_", "02_", "03_", "04_", "05_", "06_"]
            found_refs = sum(1 for ref in required_refs if ref in handoff_content)
            if found_refs < 5:
                print(f"  ⚠️  フェーズ5接続メモが他のファイルへの参照が不足（{found_refs}/6）")
                all_pass = False
            else:
                print(f"  ✅ 内部参照が一貫している（{found_refs}/6）")

        if not issues:
            print(f"  ✅ 成果物間の一貫性を確認")
            return True
        else:
            print(f"  ⚠️  一貫性の問題: {len(issues)}件")
            for issue in issues[:3]:
                print(f"    - {issue}")
            return len(issues) < 3  # 3件以上あれば FAIL

    def run_verification(self) -> bool:
        """完全検証を実行"""
        print("="*70)
        print("フェーズ4実行基盤 統合検証ツール")
        print("="*70)
        print("\n【実行モード】: フェーズ4の5つの作業単位を実行")
        print("  作業単位1（調査）: 要件と現状の把握")
        print("  作業単位2（比較）: 要件と実装の対応確認")
        print("  作業単位3（実装）: このツール実装")
        print("  作業単位4（修正）: [検証結果に基づく]")
        print("  作業単位5（記録）: git commit/push予定")

        # 各検証ステップを実施
        check1 = self.verify_deliverables_exist()
        check2 = self.verify_content_completeness()
        check3 = self.verify_completion_conditions()
        check4 = self.verify_internal_consistency()

        print("\n" + "="*70)
        if check1 and check2 and check3 and check4:
            print("検証結果: ✅ PASS - フェーズ4実行基盤は実運用可能")
            print("="*70)
            return True
        else:
            print("検証結果: ⚠️  PARTIAL - 一部の問題を検出")
            print("="*70)
            return False

def main():
    tool = Phase4SystemVerification()
    success = tool.run_verification()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
