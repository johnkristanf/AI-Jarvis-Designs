import os 
import uuid


from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from flask import send_file

from enchancements import PromptEnchancements, EnchancementsProperties
from dotenv import load_dotenv


IMAGE_FOLDER = "generated_images"

app = Flask(__name__)
CORS(app, origins=["http://localhost:3000", "https://jarvis-designs.it.com"], supports_credentials=True)  

pe = PromptEnchancements()
ep = EnchancementsProperties()
generate_image_count = 6

load_dotenv()


def delete_old_generated_designs(folder_path):
    if not os.path.isdir(folder_path):
        print(f"Error: Folder not found at {folder_path}")
        return

    deleted_count = 0
    errors = []

    # Delete files directly within the folder
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path):
            try:
                os.remove(file_path)
                print(f"Deleted file: {file_path}")
                deleted_count += 1
            except OSError as e:
                errors.append(f"Error deleting file {file_path}: {e}")

    if deleted_count >= generate_image_count:
        print(f"Successfully deleted {deleted_count} item(s) inside {folder_path}.")

    if errors:
        print("Encountered the following errors:")
        for error in errors:
            print(f"- {error}")



def save_image(result_image):
    filename = f"{uuid.uuid4().hex}.png"
    filepath = os.path.join(IMAGE_FOLDER, filename)
    result_image.save(filepath)
    return filename


@app.route('/generate/design', methods=['POST'])
def process_user_submission():

    # DELETE SAVED OLD GENERATED IMAGES BEFORE CREATING NEW ONES
    delete_old_generated_designs(IMAGE_FOLDER)

    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON payload received"}), 400
    
    user_prompt = data.get('prompt')
    style_preference = data.get('style_preference')

    cleaned_prompt = pe.sanitize_prompt(user_prompt)

    if style_preference:
        if style_preference in ep.STYLE_PREFERENCE:
            cleaned_prompt = f"{cleaned_prompt}, {ep.STYLE_PREFERENCE[style_preference]}"

    image_urls = []

    for idx in range(generate_image_count):
        result_image = pe.generate_optimized_image(cleaned_prompt, ep.ECHANCEMENTS)
        if result_image:
            filename = save_image(result_image)
            image_urls.append(filename)

    print("image_urls: ", image_urls)
    return jsonify({"image_urls": image_urls}), 200


# SERVING THE IMAGE TO THE BROWSER
@app.route('/generated/image/<filename>', methods=['GET'])
def serve_image(filename):
    return send_from_directory(IMAGE_FOLDER, filename)



# DOWNLOADING THE IMAGE
@app.route('/download/image/<filename>', methods=['GET'])
def download_image(filename):
    file_path = os.path.join(IMAGE_FOLDER, filename)
    try:
        return send_file(file_path, as_attachment=True, download_name=f"design_{filename}")
    except FileNotFoundError:
        return jsonify({"error": "File not found"}), 404


@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy'}), 200


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)



