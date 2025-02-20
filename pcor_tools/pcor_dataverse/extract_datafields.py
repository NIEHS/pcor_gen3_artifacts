import json
import os

# Folder containing JSON files
folder_path = "../tests/test_resources/dataverse_dump_02_03_2025"

# Output file
output_file = "../tests/test_resources/dataverse_dump_02_03_2025/extracted/unique_subjects_keywords.txt"

# Sets to store unique subjects and keywords
unique_subjects = set()
unique_keywords = set()

# Iterate through all JSON files in the folder
for filename in os.listdir(folder_path):
    if filename.endswith(".json"):  # Process only JSON files
        file_path = os.path.join(folder_path, filename)

        # Read JSON data from the file
        with open(file_path, "r", encoding="utf-8") as file:
            json_data = json.load(file)

        fields = json_data.get("data", {}).get("metadataBlocks", {}).get("citation", {}).get("fields", [])

        # Iterate through fields to find subjects and keywords
        for field in fields:
            type_name = field.get("typeName")

            if type_name == "subject":
                value = field.get("value")
                if isinstance(value, list):
                    unique_subjects.update(value)  # Add multiple subjects
                elif value:
                    unique_subjects.add(value)  # Add single subject

            elif type_name == "keyword":
                for kw in field.get("value", []):
                    keyword_value = kw.get("keywordValue", {}).get("value")
                    if keyword_value:
                        unique_keywords.add(keyword_value)

# Sort unique values for better readability
sorted_subjects = sorted(unique_subjects)
sorted_keywords = sorted(unique_keywords)

# Prepare text output
output_text = "Unique Subjects:\n" + "\n".join(sorted_subjects) + "\n\n"
output_text += "Unique Keywords:\n" + "\n".join(sorted_keywords) + "\n"

# Write output to file
with open(output_file, "w", encoding="utf-8") as f:
    f.write(output_text)

print(f"\nUnique subjects and keywords have been written to {output_file}")
