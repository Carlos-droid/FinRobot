import timeit
import random
import string

def generate_random_string(length):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def generate_mock_data(num_items):
    return {f"Section_{i}": generate_random_string(500) for i in range(num_items)}

def baseline_concatenation(data_dict):
    relevant_section_text = ""
    for section, text in data_dict.items():
        relevant_section_text += section + ": "
        relevant_section_text += text + "\n\n"
    return relevant_section_text

def optimized_concatenation(data_dict):
    return "".join(f"{section}: {text}\n\n" for section, text in data_dict.items())

def baseline_dict_concat(docs):
    relevant_section_dict = {}
    for doc in docs:
        section = doc['section_name']
        section_text = doc['page_content']
        if section not in relevant_section_dict:
            relevant_section_dict[section] = section_text
        else:
            relevant_section_dict[section] += " " + section_text
    return relevant_section_dict

def optimized_dict_concat(docs):
    relevant_section_dict = {}
    for doc in docs:
        section = doc['section_name']
        section_text = doc['page_content']
        if section not in relevant_section_dict:
            relevant_section_dict[section] = [section_text]
        else:
            relevant_section_dict[section].append(section_text)
    return {k: " ".join(v) for k, v in relevant_section_dict.items()}


if __name__ == "__main__":
    num_items = 10000
    print(f"Generating mock data with {num_items} items...")
    mock_data = generate_mock_data(num_items)

    docs_data = [{'section_name': f"Section_{random.randint(1, 100)}", 'page_content': generate_random_string(50)} for _ in range(num_items)]

    print("\n--- Benchmarking Dictionary Iteration & Concatenation ---")
    baseline_time = timeit.timeit(lambda: baseline_concatenation(mock_data), number=100)
    optimized_time = timeit.timeit(lambda: optimized_concatenation(mock_data), number=100)

    print(f"Baseline (+= loop): {baseline_time:.4f} seconds")
    print(f"Optimized (''.join): {optimized_time:.4f} seconds")
    print(f"Speedup: {baseline_time / optimized_time:.2f}x")

    print("\n--- Benchmarking Grouping Concatenation (relevant_section_dict) ---")
    baseline_dict_time = timeit.timeit(lambda: baseline_dict_concat(docs_data), number=100)
    optimized_dict_time = timeit.timeit(lambda: optimized_dict_concat(docs_data), number=100)

    print(f"Baseline (dict +=): {baseline_dict_time:.4f} seconds")
    print(f"Optimized (dict list append & join): {optimized_dict_time:.4f} seconds")
    print(f"Speedup: {baseline_dict_time / optimized_dict_time:.2f}x")
