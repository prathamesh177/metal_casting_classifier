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