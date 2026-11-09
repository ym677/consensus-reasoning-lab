"""Self-consistency voting with visible, synthetic offline candidate traces."""
import re
from collections import Counter
from fractions import Fraction

SPEC = {
    "title": "多路径推理与一致性投票",
    "subtitle": "对多个候选答案进行归一化、投票与拒答判定，观察一致性与正确性之间的区别。",
    "slug": "10-consensus-reasoning-lab",
    "accent": "#805445",
    "sample_input": "设备每小时处理 120 件，计划工作 7 小时，中途停机 45 分钟，实际处理多少件？",
    "input_label": "输入一道有数值答案的推理题",
}

DEMO_TASK = SPEC["sample_input"]
DEMO_CANDIDATES = [
    "工作时间为 7 - 45/60 = 6.25 小时，处理量为 120 × 6.25。\nFINAL: 750",
    "计划处理 840 件，停机损失 90 件，实际为 750。\nFINAL: 750.0",
    "将工作时间换成分钟，420 - 45 = 375 分钟，每分钟 2 件。\nFINAL: 750",
    "忽略停机，120 × 7 = 840 件。\nFINAL: 840",
    "6.25 小时乘以每小时 120 件。\nFINAL: 1500/2",
]


def normalize_answer(value):
    value = str(value).strip().replace(",", "")
    if not re.fullmatch(r"[+-]?(?:\d+(?:\.\d+)?|\.\d+)(?:/\d+(?:\.\d+)?)?", value):
        return None
    try:
        if "/" in value:
            numerator, denominator = value.split("/", 1)
            number = Fraction(numerator) / Fraction(denominator)
        else:
            number = Fraction(value)
    except (ValueError, ZeroDivisionError):
        return None
    if abs(number) > 10 ** 30:
        return None
    return str(number)


def extract_answer(text):
    match = re.search(r"^\s*FINAL\s*[:：]\s*([^\n]+)", text, re.MULTILINE | re.IGNORECASE)
    return normalize_answer(match.group(1)) if match else None


def aggregate(candidates, min_share=0.6):
    parsed = [extract_answer(candidate) for candidate in candidates]
    votes = Counter(answer for answer in parsed if answer is not None)
    if not votes:
        return {"answer": None, "share": 0, "votes": votes, "parsed": parsed, "accepted": False}
    answer, count = votes.most_common(1)[0]
    share = count / len(candidates)
    tied = sum(value == count for value in votes.values()) > 1
    accepted = len(candidates) >= 3 and share >= min_share and not tied
    return {"answer": answer, "share": share, "votes": votes, "parsed": parsed, "accepted": accepted}


def run(payload, client):
    question = payload["text"].strip()
    if not question:
        raise ValueError("请输入推理题。")
    if client.enabled:
        strategies = ["先列方程", "先计算损失再相减", "统一单位后计算", "检查另一种解法", "核对边界和单位"]
        candidates = []
        for strategy in strategies:
            candidates.append(client.complete(
                "解答数值推理题。给出简短计算说明，最后一行严格使用 FINAL: 数值，可写分数，不附加单位。",
                f"问题\n{question}\n本次核对视角\n{strategy}",
                max_tokens=350,
                temperature=0.8,
            ))
        provenance = "本次从已配置模型实际请求 5 个候选。多次请求可能相关，投票一致不保证正确。"
    else:
        if question != DEMO_TASK:
            raise ValueError("本地模式提供固定合成题目的投票实验。请恢复示例，或连接 API 处理新问题。")
        candidates = DEMO_CANDIDATES
        provenance = "固定合成候选，包含一条故意忽略停机的错误解答。它们用于验证算法，不是模型实测输出。"
    result = aggregate(candidates)
    if result["accepted"]:
        summary = f"投票答案为 {result['answer']}，获得 {result['share']:.0%} 候选支持。"
    else:
        summary = "候选未满足至少 3 条、支持率 60% 且无并列的条件，建议补充核验。"
    rows = [[index + 1, candidate, result["parsed"][index] or "格式无效"] for index, candidate in enumerate(candidates)]
    return {
        "summary": summary,
        "metrics": {"候选数量": len(candidates), "有效答案": sum(answer is not None for answer in result["parsed"]), "投票支持率": f"{result['share']:.0%}", "通过投票规则": "是" if result["accepted"] else "否"},
        "sections": [
            {"title": "候选来源", "text": provenance},
            {"title": "候选与数值归一化", "table": {"columns": ["路径", "候选说明", "归一化答案"], "rows": rows}},
            {"title": "投票分布", "table": {"columns": ["答案", "票数"], "rows": [[key, value] for key, value in result["votes"].items()]}},
            {"title": "解释与限制", "items": ["750、750.0 和 1500/2 被归并为同一数值。", "格式无效的输出仍计入候选总数，避免只保留有利结果。", "相同模型的候选可能共同犯错，一致性不能代替正确答案验证。", "仅当题目与固定示例完全一致时，本地模式才允许使用示例候选。"]},
        ],
    }
