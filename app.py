# from flask import Flask, request, jsonify
# from flask_cors import CORS  # Import CORS
# import os
# import tensorflow as tf
# from tensorflow import keras
# import numpy as np
# from werkzeug.utils import secure_filename

# app = Flask(__name__)
# CORS(app, resources={r"/api/*": {"origins": "*"}})  # Allow CORS for all API routes

# UPLOAD_FOLDER = 'uploads'
# os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# @app.route('/api/upload', methods=['POST'])
# def upload_images():
#     try:
#         images = request.files.getlist("images")
#         labels = request.form.getlist("labels")
#         data = []

#         for image, label in zip(images, labels):
#             filename = secure_filename(image.filename)
#             image_path = os.path.join(UPLOAD_FOLDER, filename)
#             image.save(image_path)
#             data.append((image_path, label))

#         train_model(data)
#         return jsonify({"message": "Training started"}), 200
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

# def train_model(data):
#     images = []
#     labels = []

#     for image_path, label in data:
#         img = keras.preprocessing.image.load_img(image_path, target_size=(224, 224))  
#         img = keras.preprocessing.image.img_to_array(img)  # Convert to array
#         images.append(img)  # Add image to list
#         labels.append(int(label))  # Convert label to int

#     images = np.array(images, dtype=np.float32) / 255.0  # Normalize and convert to float
#     labels = np.array(labels, dtype=np.int32)

#     # Ensure shape is correct
#     print(f"Images shape: {images.shape}")  # Should print (num_samples, 224, 224, 3)
#     print(f"Labels shape: {labels.shape}")  # Should print (num_samples,)

#     # Ensure labels are categorical if multi-class
#     if len(set(labels)) > 2:  
#         labels = keras.utils.to_categorical(labels)  # One-hot encoding for multi-class

#     model = keras.Sequential([
#         keras.layers.Conv2D(32, (3,3), activation='relu', input_shape=(224,224,3)),
#         keras.layers.MaxPooling2D(2,2),
#         keras.layers.Flatten(),
#         keras.layers.Dense(128, activation='relu'),
#         keras.layers.Dense(1, activation='sigmoid')  # Change to Dense(len(set(labels)), softmax) for multi-class
#     ])

#     model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
#     model.fit(images, labels, epochs=5)  # Batch size added

#     model.save("model.h5")
#     return "Training Complete"


# if __name__ == '__main__':
#     app.run(debug=True, port=8000)


import os
import requests
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator, load_img, img_to_array
from tensorflow.keras.applications.resnet50 import ResNet50, preprocess_input
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Dense, Flatten
from tensorflow.keras.optimizers import Adam
import json

# Frappe API endpoint to fetch images
FRAPPE_API_URL = "http://localhost:8004/api/method/casting_classification.api.get_images"

# Load images from Frappe
def load_data():
    response = requests.get(FRAPPE_API_URL)
    data = response.json()
    
    images, labels = [], []
    for item in data:
        image_url = "http://localhost:8004" + item["image"]
        label = 1 if item["label"] == "OK" else 0  # Convert to binary
        
        img = load_img(image_url, target_size=(224, 224))  # Load and resize image
        img = img_to_array(img)
        img = preprocess_input(img)
        
        images.append(img)
        labels.append(label)

    return np.array(images), np.array(labels)

# Prepare data
X, y = load_data()

# Define ResNet50-based CNN model
base_model = ResNet50(weights="imagenet", include_top=False, input_shape=(224, 224, 3))
for layer in base_model.layers:
    layer.trainable = False  # Freeze base model layers

x = Flatten()(base_model.output)
x = Dense(128, activation="relu")(x)
x = Dense(1, activation="sigmoid")(x)

model = Model(inputs=base_model.input, outputs=x)
model.compile(optimizer=Adam(learning_rate=0.0001), loss="binary_crossentropy", metrics=["accuracy"])

# Train model
model.fit(X, y, epochs=10, batch_size=8, validation_split=0.2)

# Save model
model.save("casting_model.h5")
print("Model saved successfully!")