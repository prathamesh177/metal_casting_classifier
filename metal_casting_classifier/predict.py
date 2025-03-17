from flask import Flask, request, jsonify
import tensorflow as tf
import numpy as np
from tensorflow.keras.preprocessing.image import load_img, img_to_array
from tensorflow.keras.applications.resnet50 import preprocess_input

app = Flask(__name__)
model = tf.keras.models.load_model("casting_model.h5")

@app.route("/predict", methods=["POST"])
def predict():
    file = request.files["image"]
    img = load_img(file, target_size=(224, 224))
    img = img_to_array(img)
    img = preprocess_input(img)
    img = np.expand_dims(img, axis=0)  # Add batch dimension
    
    prediction = model.predict(img)[0][0]
    classification = "OK" if prediction > 0.5 else "Not OK"
    
    return jsonify({"classification": classification, "confidence": float(prediction)})

if __name__ == "_main_":
    app.run(port=5000, debug=True)