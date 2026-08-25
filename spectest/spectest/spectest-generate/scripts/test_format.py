#!/usr/bin/env python3
"""
测试脚本：验证 testcases.json 格式和字段映射
"""
import json
import sys
import os

def get_field(tc, field_name):
    """获取测试用例字段，支持多种字段名映射。"""
    field_mappings = {
        "title": ["name"],
        "test_type": ["type"],
        "expected_result": ["expected"]
    }

    # 优先使用直接字段名
    if field_name in tc and tc[field_name]:
        return tc[field_name]

    # 查找映射字段名
    if field_name in field_mappings:
        for mapped_name in field_mappings[field_name]:
            if mapped_name in tc and tc[mapped_name]:
                return tc[mapped_name]

    # 未找到，返回空字符串
    return ""

def validate_testcases(json_file):
    """验证 testcases.json 格式"""
    print(f"[INFO] Validating: {json_file}")

    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            testcases = json.load(f)
    except FileNotFoundError:
        print(f"[ERROR] File not found: {json_file}")
        return False
    except json.JSONDecodeError as e:
        print(f"[ERROR] JSON decode error: {e}")
        return False

    if not isinstance(testcases, list):
        print(f"[ERROR] JSON should be an array of test cases")
        return False

    print(f"[OK] Total {len(testcases)} test cases")

    # 验证必需字段
    required_fields = ['project', 'module', 'feature', 'test_item',
                       'title', 'preconditions', 'steps', 'expected_result',
                       'priority', 'case_type', 'test_type']

    errors = []
    for idx, tc in enumerate(testcases, 1):
        for field in required_fields:
            # 使用 get_field 测试字段映射
            value = get_field(tc, field)
            if not value:
                errors.append(f"用例 {idx} 缺少字段: {field}")

    if errors:
        print(f"[ERROR] Found {len(errors)} issues:")
        for error in errors[:10]:  # 只显示前10个错误
            print(f"   - {error}")
        if len(errors) > 10:
            print(f"   ... and {len(errors) - 10} more issues")
        return False

    print("[OK] All required fields exist")

    # 统计测试类型分布
    type_counts = {}
    for tc in testcases:
        tc_type = get_field(tc, "test_type")
        type_counts[tc_type] = type_counts.get(tc_type, 0) + 1

    print("\n[STATS] Test type distribution:")
    for tc_type, count in sorted(type_counts.items()):
        percentage = count / len(testcases) * 100
        print(f"   {tc_type}: {count} ({percentage:.0f}%)")

    # 统计优先级分布
    priority_counts = {}
    for tc in testcases:
        priority = tc.get("priority", "P1")
        priority_counts[priority] = priority_counts.get(priority, 0) + 1

    print("\n[STATS] Priority distribution:")
    for priority, count in sorted(priority_counts.items()):
        percentage = count / len(testcases) * 100
        print(f"   {priority}: {count} ({percentage:.0f}%)")

    return True

def main():
    if len(sys.argv) < 2:
        print("Usage: python test_format.py <testcases.json>")
        sys.exit(1)

    json_file = sys.argv[1]

    if validate_testcases(json_file):
        print("\n[SUCCESS] Validation passed!")
        print("[INFO] You can now run generate_excel.py to generate Excel file")
        return 0
    else:
        print("\n[ERROR] Validation failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
