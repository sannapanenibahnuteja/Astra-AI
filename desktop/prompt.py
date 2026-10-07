"""Keep prompt growth proportional to the selected local-model context."""
import json


def build_messages(system, settings, memories, apps, history):
    # A conservative UTF-8 byte budget, not an exact model tokenizer. Reserve
    # space for tool definitions, chat framing and the generated response.
    budget = max(3200, settings['context_size'] * 2 - 1600)

    def clip(text, maximum):
        encoded = text.encode('utf-8')
        if len(encoded) <= maximum:
            return text
        marker = '\n[Excerpt shortened for context.]'
        return encoded[:max(0, maximum - len(marker.encode()))].decode('utf-8', errors='ignore') + marker

    current = history[-1] if history else {'role': 'user', 'content': ''}
    current_text = clip(current['content'], max(600, budget // 2))
    memory_budget = max(100, budget // 8)
    facts = []
    # Prioritize facts related to this request before unrelated background facts.
    words = set(current['content'].lower().split())
    ranked = sorted(memories, key=lambda m: -len(words.intersection((m['key'] + ' ' + m['value']).lower().split())))
    for item in ranked:
        candidate = facts + [item]
        if len(json.dumps(candidate, ensure_ascii=False).encode()) <= memory_budget:
            facts = candidate
    # Keep saved facts and preferences even when instructions/context are long.
    suffix = '\nUser preferences:\n' + clip(settings['personality'], max(100, budget // 12))
    suffix += '\nSome available apps:\n' + clip(', '.join(sorted(apps)), max(100, budget // 12))
    suffix += '\nSaved facts (JSON data):\n' + json.dumps(facts, ensure_ascii=False)
    # Action context can include long file paths. Reserve room for the current
    # request even when those observations exceed the smallest model context.
    prompt = clip(system, budget - max(400, budget // 5) - len(suffix.encode())) + suffix
    current_text = clip(current_text, max(200, budget - len(prompt.encode())))
    result = [{'role': current['role'], 'content': current_text}]
    remaining = budget - len(prompt.encode()) - len(current_text.encode())
    for item in reversed(history[:-1]):
        cost = len(item['content'].encode())
        if cost > remaining:
            break
        result.insert(0, item)
        remaining -= cost
    return [{'role': 'system', 'content': prompt}] + result
