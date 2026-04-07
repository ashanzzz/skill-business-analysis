#!/usr/bin/env python3
"""
增强版验证脚本：检查逻辑正确性和数据质量
用法：python verify_report_v2.py <报告文件>
"""

import re
import sys
import argparse

def check_logical_consistency(report_text):
    """检查逻辑一致性"""
    issues = []
    
    # 检查1：市场份额总和是否合理（通常≤100%）
    # 寻找CR3/CR5/CR10等格式的市场份额
    cr_patterns = re.findall(r'CR[_\d]+[：:]\s*(\d+(?:\.\d+)?\s*%)', report_text)
    for cr in cr_patterns:
        val = float(re.sub(r'[^\d.]', '', cr))
        if val > 100:
            issues.append(f"⚠️ 市场份额总和={val}%，超过100%，逻辑错误")
    
    # 检查2：增速描述与数值是否矛盾
    has_negative = bool(re.search(r'负增长|下降|\-\s*\d+%', report_text))
    has_high_growth = bool(re.search(r'高增长|快速增长|显著增长', report_text))
    if has_negative and has_high_growth:
        issues.append("⚠️ 同时存在'负增长'和'高增长'描述，逻辑矛盾")
    
    # 检查3：成熟市场vs高增长描述
    if re.search(r'成熟市场', report_text):
        if re.search(r'CAGR\s*[>]?\s*\d{2}%', report_text):
            issues.append("⚠️ '成熟市场'通常增长<5%，却描述高增长，逻辑矛盾")
    
    # 检查4：检查数值范围合理性
    # 例如：说"市场规模$100亿"又说"TAM $1000亿"可能矛盾
    all_amounts = re.findall(r'\$(\d+(?:\.\d+)?)\s*亿', report_text)
    if len(all_amounts) >= 2:
        amounts = [float(a) for a in all_amounts]
        if min(amounts) * 10 < max(amounts):
            # 小值与大值差距10倍以上，需要确认是否有层级说明
            pass  # 暂时跳过，可能有多层级
    
    return issues

def check_data_quality(report_text):
    """检查数据质量"""
    issues = []
    
    # 检查1：是否标注来源
    has_source = bool(re.search(r'来源|数据来源|source|according to', report_text, re.I))
    if not has_source:
        issues.append("⚠️ 缺少数据来源标注")
    
    # 检查2：是否标注置信度
    has_confidence = bool(re.search(r'[🟢🟡🟠🔴]|可信度|置信度|confidence', report_text))
    if not has_confidence:
        issues.append("⚠️ 缺少置信度标注（应使用🟢🟡🟠🔴标注）")
    
    # 检查3：是否有时间/年份标注
    has_year = bool(re.search(r'20[12]\d', report_text))
    if not has_year:
        issues.append("⚠️ 缺少数据时效标注（应标注数据年份）")
    
    # 检查4：是否包含关键章节
    required_sections = {
        '市场规模': r'市场规模',
        '执行摘要': r'执行摘要',
        '竞争格局': r'竞争',
        '风险评估': r'风险',
        '结论': r'结论'
    }
    for name, pattern in required_sections.items():
        if not re.search(pattern, report_text):
            issues.append(f"⚠️ 缺少必要章节：{name}")
    
    return issues

def check_cross_validation(report_text):
    """检查交叉验证记录"""
    issues = []
    
    # 检查是否进行了交叉验证
    has_validation = bool(re.search(r'验证|validation|交叉|确认', report_text))
    if not has_validation:
        issues.append("⚠️ 缺少交叉验证记录")
    
    # 检查是否有三个独立来源的记录
    source_count = len(re.findall(r'来源[123A-C]|[Ll]\d|source\s*[123]', report_text))
    if source_count < 3 and not has_validation:
        issues.append("⚠️ 可能缺少多源验证（建议至少3个独立来源）")
    
    return issues

def verify_report(report_path):
    """完整验证"""
    try:
        with open(report_path, 'r', encoding='utf-8') as f:
            text = f.read()
    except FileNotFoundError:
        print(f"❌ 文件不存在: {report_path}")
        return False
    except Exception as e:
        print(f"❌ 读取错误: {e}")
        return False
    
    print("=" * 60)
    print("🔍 增强版报告验证")
    print("=" * 60)
    print(f"文件: {report_path}")
    print("-" * 60)
    
    all_issues = []
    
    # 1. 逻辑一致性检查
    print("\n📐 逻辑一致性检查:")
    logic_issues = check_logical_consistency(text)
    if logic_issues:
        for issue in logic_issues:
            print(f"  {issue}")
        all_issues.extend(logic_issues)
    else:
        print("  ✅ 逻辑一致性检查通过")
    
    # 2. 数据质量检查
    print("\n📊 数据质量检查:")
    quality_issues = check_data_quality(text)
    if quality_issues:
        for issue in quality_issues:
            print(f"  {issue}")
        all_issues.extend(quality_issues)
    else:
        print("  ✅ 数据质量检查通过")
    
    # 3. 交叉验证检查
    print("\n🔄 交叉验证检查:")
    validation_issues = check_cross_validation(text)
    if validation_issues:
        for issue in validation_issues:
            print(f"  {issue}")
        all_issues.extend(validation_issues)
    else:
        print("  ✅ 交叉验证记录完整")
    
    # 总结
    print("-" * 60)
    if all_issues:
        print(f"❌ 发现 {len(all_issues)} 个问题")
        print("\n建议修复后重新验证")
    else:
        print("✅ 所有检查通过")
    
    print("=" * 60)
    
    return len(all_issues) == 0

def main():
    parser = argparse.ArgumentParser(
        description="增强版报告验证脚本",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('report_path', help='报告文件路径')
    parser.add_argument('--strict', action='store_true', help='严格模式（警告也视为问题）')
    
    args = parser.parse_args()
    
    passed = verify_report(args.report_path)
    
    if args.strict and not passed:
        # 在strict模式下，任何问题都导致失败
        sys.exit(1)
    elif not passed:
        # 非strict模式下，问题不导致程序失败
        sys.exit(0)  # 即使有问题也正常退出

if __name__ == "__main__":
    main()
