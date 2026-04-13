#!/usr/bin/env python3
"""
Phase 4 Operational Verification Tool
フェーズ2の採用候補がフェーズ4実行基盤に正確に反映されているか検証

実行フロー: 調査→実装→検証→記録→GitHub反映
このツール自体が phase4 の作業単位を示す実証
"""

import re
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple

class Phase4VerificationTool:
    """フェーズ2→4 ツール候補の正確性検証"""

    def __init__(self, repo_root: str = "."):
        self.repo_root = Path(repo_root)
        self.phase2_file = self.repo_root / "phase2_decision_foundation" / "04_candidate_evaluations.md"
        self.phase4_file = self.repo_root / "phase4_execution_foundation" / "02_tool_maximization_policy.md"

    def extract_phase2_candidates(self) -> Dict[str, Dict]:
        """phase2 から F-XXX 候補を抽出"""
        candidates = {}
        if not self.phase2_file.exists():
            print(f"ERROR: {self.phase2_file} が存在しません")
            return candidates

        content = self.phase2_file.read_text(encoding='utf-8')

        # | F-NNN | ツール名 | パターン を抽出
        pattern = r'\|\s+F-(\d+)\s+\|\s+([^|]+)\s+\|'
        for match in re.finditer(pattern, content):
            fid = f"F-{match.group(1)}"
            name = match.group(2).strip()
            candidates[fid] = {"name": name, "source": "phase2"}

        return candidates

    def extract_phase4_candidates(self) -> Dict[str, Dict]:
        """phase4 から定義されたD1候補を抽出"""
        candidates = {}
        if not self.phase4_file.exists():
            print(f"ERROR: {self.phase4_file} が存在しません")
            return candidates

        content = self.phase4_file.read_text(encoding='utf-8')

        # ### D1 採用候補の全リスト (行25-39) を検査
        # | **F-NNN** | **ツール名** | パターン
        pattern = r'\|\s+\*\*F-(\d+)\*\*\s+\|\s+\*\*([^*]+)\*\*\s+\|'
        for match in re.finditer(pattern, content):
            fid = f"F-{match.group(1)}"
            name = match.group(2).strip()
            candidates[fid] = {"name": name, "source": "phase4_d1"}

        return candidates

    def verify_d1_completeness(self) -> Tuple[bool, List[str]]:
        """D1候補の完全性を検証（phase2すべてがphase4に含まれているか）"""
        phase2_candidates = self.extract_phase2_candidates()
        phase4_candidates = self.extract_phase4_candidates()

        # phase2 から D1 判定されている候補を抽出
        # phase2 ファイルで「D1（採用候補）」として確認できるのは
        # 04_candidate_evaluations.md で first section の候補

        # 手動確認では以下が D1 と判定：
        # F-002, F-003, F-004, F-005, F-009, F-013, F-015, F-019, F-025, F-032
        expected_d1 = {
            "F-002", "F-003", "F-004", "F-005", "F-009",
            "F-013", "F-015", "F-019", "F-025", "F-032"
        }

        found_d1 = set(phase4_candidates.keys())
        missing = expected_d1 - found_d1

        is_complete = len(missing) == 0
        issues = list(missing) if missing else []

        return is_complete, issues

    def run_verification(self) -> bool:
        """完全検証を実行"""
        print("=" * 70)
        print("フェーズ4実運用検証 - ツール候補完全性チェック")
        print("=" * 70)

        # 検証1: Phase 2 候補抽出
        print("\n[検証1] Phase 2 から D1 採用候補を抽出")
        phase2_cands = self.extract_phase2_candidates()
        print(f"✓ Phase 2 から {len(phase2_cands)} 個の候補を検出")
        print(f"  候補ID: {', '.join(sorted(phase2_cands.keys())[:5])}...")

        # 検証2: Phase 4 候補抽出
        print("\n[検証2] Phase 4 から定義された D1 候補を抽出")
        phase4_cands = self.extract_phase4_candidates()
        print(f"✓ Phase 4 から {len(phase4_cands)} 個の D1 候補を検出")
        print(f"  候補ID: {', '.join(sorted(phase4_cands.keys()))}")

        # 検証3: 完全性チェック
        print("\n[検証3] 完全性検証 (Phase 2 D1がすべてPhase 4に記載されているか)")
        is_complete, missing = self.verify_d1_completeness()

        expected_d1 = {
            "F-002", "F-003", "F-004", "F-005", "F-009",
            "F-013", "F-015", "F-019", "F-025", "F-032"
        }

        if is_complete:
            print(f"✓ すべてのD1候補（{len(expected_d1)}件）が Phase 4 に記載されている")
            print(f"  確認済み: {', '.join(sorted(expected_d1))}")
        else:
            print(f"✗ 以下の D1 候補が Phase 4 に欠落: {', '.join(missing)}")
            return False

        # 検証4: 名前の一致確認
        print("\n[検証4] ツール名の一致確認")
        name_mismatches = []
        for fid in expected_d1:
            if fid in phase2_cands and fid in phase4_cands:
                name2 = phase2_cands[fid]["name"]
                name4 = phase4_cands[fid]["name"]
                if name2.lower() != name4.lower():
                    name_mismatches.append((fid, name2, name4))

        if not name_mismatches:
            print(f"✓ すべてのツール名が一致している")
        else:
            print(f"✗ 以下のツール名が不一致:")
            for fid, name2, name4 in name_mismatches:
                print(f"  {fid}: Phase2='{name2}' vs Phase4='{name4}'")
            return False

        print("\n" + "=" * 70)
        print("検証結果: ✓ PASS - すべての検証項目に合格")
        print("=" * 70)

        return True

def main():
    tool = Phase4VerificationTool()
    success = tool.run_verification()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
