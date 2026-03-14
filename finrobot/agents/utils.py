import re
from .prompts import order_template


def instruction_trigger(sender):
    # Check if the last message contains the path to the instruction text file
    return "instruction & resources saved to" in sender.last_message()["content"]


def instruction_message(recipient, messages, sender, config):
    # Extract the path to the instruction text file from the last message
    full_order = recipient.chat_messages_for_summary(sender)[-1]["content"]
    txt_path = full_order.replace("instruction & resources saved to ", "").strip()
    with open(txt_path, "r") as f:
        instruction = f.read() + "\n\nReply TERMINATE at the end of your response."
    return instruction


def order_trigger(sender, name, pattern):
    if not sender or not hasattr(sender, "name") or not hasattr(sender, "last_message"):
        return False

    sender_name = sender.name
    if not isinstance(sender_name, str):
        return False

    last_msg = sender.last_message()
    if not isinstance(last_msg, dict) or "content" not in last_msg:
        return False

    msg_content = last_msg["content"]
    if not isinstance(msg_content, str):
        return False

    if not isinstance(name, str) or not isinstance(pattern, str):
        return False

    return (
        sender_name.strip().lower() == name.strip().lower()
        and pattern.strip().lower() in msg_content.strip().lower()
    )


def order_message(pattern, recipient, messages, sender, config):
    full_order = recipient.chat_messages_for_summary(sender)[-1]["content"]
    pattern = rf"\[{pattern}\](?::)?\s*(.+?)(?=\n\[|$)"
    match = re.search(pattern, full_order, re.DOTALL)
    if match:
        order = match.group(1).strip()
    else:
        order = full_order
    return order_template.format(order=order)
