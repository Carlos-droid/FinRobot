import re
from .prompts import order_template


def instruction_trigger(sender):
    # Check if the last message contains the path to the instruction text file
    if not hasattr(sender, "last_message") or not callable(sender.last_message):
        return False

    last_msg = sender.last_message()
    if isinstance(last_msg, dict) and "content" in last_msg:
        content = last_msg["content"]
        if isinstance(content, str):
            return "instruction & resources saved to" in content

    return False


def instruction_message(recipient, messages, sender, config):
    # Extract the path to the instruction text file from the last message
    full_order = recipient.chat_messages_for_summary(sender)[-1]["content"]
    txt_path = full_order.replace("instruction & resources saved to ", "").strip()
    with open(txt_path, "r") as f:
        instruction = f.read() + "\n\nReply TERMINATE at the end of your response."
    return instruction


def order_trigger(sender, name, pattern):
    # print(pattern)
    # print(sender.name)
    return sender.name == name and pattern in sender.last_message()["content"]


def order_message(pattern, recipient, messages, sender, config):
    full_order = recipient.chat_messages_for_summary(sender)[-1]["content"]
    pattern = rf"\[{pattern}\](?::)?\s*(.+?)(?=\n\[|$)"
    match = re.search(pattern, full_order, re.DOTALL)
    if match:
        order = match.group(1).strip()
    else:
        order = full_order
    return order_template.format(order=order)
