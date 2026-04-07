#!/usr/bin/env python3
"""
商业分析报告完整性验证脚本
检查报告是否包含所有必需部分

用法：
  python verify_report.py <报告文件路径>
  python verify_report.py <报告文件路径> --strict
"""

import sys
import re
import argparse
from pathlib import Path

# 必需章节（按出现顺序）
REQUIRED_SECTIONS = [
    "执行摘要",
    "市场规模",
    "区域",
    "竞争",
    "消费者",
    "监管",
    "风险",
    "财务",
    "GTM",
    "结论"
]

# 必需数据点
REQUIRED_DATA_POINTS = [
    "TAM",
    "增长率",
    "CAGR",
    "主要区域",
    "主要玩家"
]

# 必需分析维度
REQUIRED_DIMENSIONS = [
    ("印度", "印度市场"),
    ("北美", "北美市场"),
    ("中国", "中国市场"),
    ("东南亚", "东南亚市场")
]

# 可信度标记
CONFIDENCE_MARKERS = ["🟢", "🟡", "🟠", "🔴", "高可信", "中可信", "低可信"]

# 来源标记
SOURCE_MARKERS = ["来源", "source", "数据来源", "according to", "based on"]


class ReportVerifier:
    def __init__(self, report_path: str, strict: bool = False):
        self.report_path = Path(report_path)
        self.report_text = ""
        self.strict = strict
        self.results = {
            "passed": True,
            "missing_sections": [],
            "missing_data": [],
            "missing_dimensions": [],
            "warnings": [],
            "errors": []
        }
    
    def load_report(self) -> bool:
        """加载报告文件"""
        try:
            with open(self.report_path, "r", encoding="utf-8") as f:
                self.report_text = f.read()
            return True
        except FileNotFoundError:
            self.results["errors"].append(f"文件不存在: {self.report_path}")
            return False
        except Exception as e:
            self.results["errors"].append(f"读取文件错误: {e}")
            return False
    
    def check_sections(self):
        """检查必需章节"""
        for section in REQUIRED_SECTIONS:
            if section not in self.report_text:
                self.results["missing_sections"].append(section)
                self.results["passed"] = False
    
    def check_data_points(self):
        """检查必需数据点"""
        for data in REQUIRED_DATA_POINTS:
            if data not in self.report_text:
                self.results["missing_data"].append(data)
                self.results["passed"] = False
    
    def check_dimensions(self):
        """检查必需分析维度"""
        for keyword, display_name in REQUIRED_DIMENSIONS:
            if keyword not in self.report_text:
                self.results["missing_dimensions"].append(display_name)
                self.results["passed"] = False
    
    def check_confidence(self):
        """检查置信度标注"""
        has_confidence = any(marker in self.report_text for marker in CONFIDENCE_MARKERS)
        if not has_confidence:
            self.results["warnings"].append("报告缺少置信度标注（🟢🟡🟠🔴）")
            if self.strict:
                self.results["passed"] = False
    
    def check_sources(self):
        """检查数据来源标注"""
        has_source = any(marker.lower() in self.report_text.lower() for marker in SOURCE_MARKERS)
        if not has_source:
            self.results["warnings"].append("报告缺少数据来源标注")
            if self.strict:
                self.results["passed"] = False
    
    def check_cross_validation(self):
        """检查交叉验证记录"""
        validation_keywords = ["验证", "validation", "交叉验证", "数据验证"]
        has_validation = any(keyword in self.report_text for keyword in validation_keywords)
        if not has_validation:
            self.results["warnings"].append("报告缺少交叉验证记录")
    
    def check_financial_model(self):
        """检查财务模型完整性"""
        financial_keywords = ["P&L", "利润", "亏损", "收入", "成本", "LTV", "CAC"]
        has_financial = any(keyword in self.report_text for keyword in financial_keywords)
        if not has_financial:
            self.results["warnings"].append("报告可能缺少财务建模部分")
    
    def check_gtm(self):
        """检查GTM策略"""
        gtm_keywords = ["GTM", "进入", "定价", "渠道", "获客", "Go-To-Market"]
        has_gtm = any(keyword in self.report_text for keyword in gtm_keywords)
        if not has_gtm:
            self.results["missing_dimensions"].append("GTM策略")
            self.results["passed"] = False
    
    def verify(self) -> bool:
        """执行所有检查"""
        if not self.load_report():
            return False
        
        self.check_sections()
        self.check_data_points()
        self.check_dimensions()
        self.check_confidence()
        self.check_sources()
        self.check_cross_validation()
        self.check_financial_model()
        self.check_gtm()
        
        return self.results["passed"]
    
    def print_report(self):
        """打印验证报告"""
        print("=" * 60)
        print("📋 商业分析报告验证报告")
        print("=" * 60)
        print(f"文件: {self.report_path}")
        print(f"模式: {'严格模式' if self.strict else '标准模式'}")
        print("-" * 60)
        
        # 整体结果
        if self.results["passed"]:
            print("✅ 验证通过 - 报告完整性合格")
        else:
            print("❌ 验证未通过 - 存在以下问题:")
        
        print()
        
        # 缺失章节
        if self.results["missing_sections"]:
            print(f"📑 缺失章节 ({len(self.results['missing_sections'])}):")
            for s in self.results["missing_sections"]:
                print(f"   - {s}")
            print()
        
        # 缺失数据点
        if self.results["missing_data"]:
            print(f"📊 缺失数据点 ({len(self.results['missing_data'])}):")
            for d in self.results["missing_data"]:
                print(f"   - {d}")
            print()
        
        # 缺失维度
        if self.results["missing_dimensions"]:
            print(f"🎯 缺失分析维度 ({len(self.results['missing_dimensions'])}):")
            for d in self.results["missing_dimensions"]:
                print(f"   - {d}")
            print()
        
        # 警告
        if self.results["warnings"]:
            print(f"⚠️  警告 ({len(self.results['warnings'])}):")
            for w in self.results["warnings"]:
                print(f"   - {w}")
            print()
        
        # 错误
        if self.results["errors"]:
            print(f"🚫 错误 ({len(self.results['errors'])}):")
            for e in self.results["errors"]:
                print(f"   - {e}")
            print()
        
        # 统计
        print("-" * 60)
        total_issues = (
            len(self.results["missing_sections"]) +
            len(self.results["missing_data"]) +
            len(self.results["missing_dimensions"])
        )
        total_warnings = len(self.results["warnings"])
        
        print(f"问题总数: {total_issues}")
        print(f"警告总数: {total_warnings}")
        print("=" * 60)
        
        # 建议
        if not self.results["passed"]:
            print("\n💡 建议:")
            if self.results["missing_sections"]:
                print("   - 补充缺失的章节")
            if self.results["missing_data"]:
                print("   - 补充缺失的数据点")
            if self.results["missing_dimensions"]:
                print("   - 补充缺失的分析维度（特别是区域市场分析）")
            if self.results["warnings"]:
                print("   - 添加置信度标注和数据来源")
        
        print()


def main():
    parser = argparse.ArgumentParser(
        description="商业分析报告完整性验证脚本",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python verify_report.py report.md
  python verify_report.py report.md --strict
  python verify_report.py "path/to/report.pdf.txt"
        """
    )
    
    parser.add_argument(
        "report_path",
        help="报告文件路径"
    )
    
    parser.add_argument(
        "--strict",
        action="store_true",
        help="严格模式：警告也将导致验证失败"
    )
    
    args = parser.parse_args()
    
    verifier = ReportVerifier(args.report_path, strict=args.strict)
    passed = verifier.verify()
    verifier.print_report()
    
    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
