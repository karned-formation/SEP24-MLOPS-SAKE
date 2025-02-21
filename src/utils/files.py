import base64


def encode_files(files):
    files_base64 = []
    for uploaded_file in files:
        file_content = uploaded_file.read()
        encoded_string = base64.b64encode(file_content).decode('utf-8')
        files_base64.append({
            "name": uploaded_file.name,
            "content": encoded_string
        })
    return files_base64