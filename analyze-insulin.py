import re


# read text from the file
with open("preproinsulin-seq.txt", "r") as f:
    text = f.read()

    # Use regex to remove "ORIGIN" (case insensitive) and any non-letter characters
    cleaned_text = re.sub(r'[^a-zA-Z]', '', text)
    cleaned_text = re.sub(r'ORIGIN', '', cleaned_text, flags=re.IGNORECASE)

    # Remove the double slashes (//) at the end
    cleaned_text = cleaned_text.rstrip('/')

    # Truncate the string to 110 characters
    if len(cleaned_text) != 110:
        raise ValueError('The cleaned text should have 110 characters')

    print(cleaned_text)

# Save "preproinsulin-seq-clean.txt"
# malwmrllpllallalwgpdpaaafvnqhlcgshlvealylvcgergffytpktrreaedlqvgqvelgggpgagslqplalegslqkrgiveqcctsicslyqlenycn
with open("preproinsulin-seq-clean.txt", "w+") as f:
    f.write(cleaned_text)

# Save "lsinsulin-seq-clean.txt"
# malwmrllpllallalwgpdpaaa
with open("lsinsulin-seq-clean.txt", "w+") as f:
    f.write(cleaned_text[:24])

# Save "binsulin-seq-clean.txt"
# fvnqhlcgshlvealylvcgergffytpkt
with open("binsulin-seq-clean.txt", "w+") as f:
    f.write(cleaned_text[24:54])

# Save "cinsulin-seq-clean.txt"
# rreaedlqvgqvelgggpgagslqplalegslqkr
with open("cinsulin-seq-clean.txt", "w+") as f:
    f.write(cleaned_text[54:89])

# Save "ainsulin-seq-clean.txt"
# giveqcctsicslyqlenycn
with open("ainsulin-seq-clean.txt", "w+") as f:
    f.write(cleaned_text[89:])
