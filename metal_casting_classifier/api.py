# import frappe
# import cv2
# import numpy as np
# import tensorflow as tf
# from werkzeug.utils import secure_filename
# from datetime import datetime

# # Load the model
# import os

# # Correct file path for the model
# model_path = os.path.join(frappe.get_app_path('metal_casting_classifier'), 'trained_model.h5')

# # Load the model
# model = tf.keras.models.load_model(model_path)

# def preprocess_image(img):
#     # Resize the image to the input size of the model
#     img = cv2.resize(img, (64, 64))  # Adjust size to match your model
#     img = img / 255.0  # Normalize pixel values to [0, 1]

#     # Reshape the image to the correct input size for Dense layer
#     # Flatten image to 1D array

#     # Add batch dimension
#     img = np.expand_dims(img, axis=0)  # Now it should be (1, 224*224*3)

#     return img



# @frappe.whitelist()
# def classify_image(image_url):
#     if not image_url:
#         return {"error": "Image URL is required"}

#     try:
#         frappe.log("Received image_url: {}".format(image_url))

#         file_doc = frappe.get_doc("File", {"file_url": image_url})
#         image_path = file_doc.get_full_path()

#         frappe.log("Full image path: {}".format(image_path))

#         img = cv2.imread(image_path)
#         prediction = classify_casting(img)

#         casting_doc = frappe.get_doc({
#             "doctype": "casting",
#             "image": image_url,
#             "prediction": prediction,
#             "timestamp": datetime.now(),
#             "status": "Success"
#         })
#         casting_doc.insert()
#         frappe.db.commit()

#         return {"result": prediction, "casting_id": casting_doc.name}
#     except Exception as e:
#         frappe.log_error(f"Error in classify_image: {str(e)}", "Classify Image")
#         return {"error": str(e)}



# def classify_casting(img):
#     # Preprocess the image
#     preprocessed_img = preprocess_image(img)

#     # Predict
#     predictions = model.predict(preprocessed_img)
#     class_idx = np.argmax(predictions)  # Get the class with the highest probability

#     # Map the class index to the result (e.g., OK or Not OK)
#     classes = ["Defective", "OK"]
#     return classes[class_idx]




# @frappe.whitelist(allow_guest=True)
# def upload_image(image=None):
#     if not image:
#         return {"error": "No image path provided"}

#     try:
#         # Ensure the path exists before proceeding
#         image_path = image.strip('"')  # Clean up the path if quotes are included
#         if not os.path.exists(image_path):
#             return {"error": "Image path does not exist"}

#         # Read the file content
#         with open(image_path, 'rb') as file:
#             file_data = file.read()

#         # Get the filename from the path
#         filename = os.path.basename(image_path)

#         # Create the file document and save it
#         file_doc = frappe.get_doc({
#             "doctype": "File",
#             "file_name": filename,
#             "is_private": 0,
#             "content": file_data,
#         })

#         # Save the file and return its URL
#         file_doc.save()
#         return {"file_url": file_doc.file_url}
#     except Exception as e:
#         frappe.log_error(frappe.get_traceback(), "File Upload Error")
#         return {"error": str(e)}


# @frappe.whitelist()
# def get_all_predictions():
#     try:
#         predictions = frappe.get_all("casting", fields=["image", "prediction", "timestamp", "Status"])
#         return {"data": predictions}
#     except Exception as e:
#         frappe.log_error(f"Error in get_all_predictions: {str(e)}", "Fetch Predictions")
#         return {"error": str(e)}


# @frappe.whitelist()
# def create_project(name, description=""):
#     project = frappe.get_doc({
#         "doctype": "projectlist",
#         "name": name,
#         "description": description
#     })
#     project.insert()
#     return {"message": "Project Created", "data": project}


# import frappe
# from frappe.model.document import Document
# import os
# import torch
# import torchvision.transforms as transforms
# from torchvision import models
# from torch.utils.data import DataLoader, Dataset
# from PIL import Image
# import io
# import json
# from frappe.utils.file_manager import save_file
# from werkzeug.utils import secure_filename

# # ✅ Check if GPU is available
# DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# # ✅ Function to transform images for training/prediction
# def get_transform():
#     return transforms.Compose([
#         transforms.Resize((224, 224)),
#         transforms.ToTensor(),
#     ])

# # ✅ Custom dataset class
# class CustomImageDataset(Dataset):
#     def __init__(self, images, labels, label_map):
#         self.images = images
#         self.labels = [label_map[label] for label in labels]  # Convert labels to numerical format
#         self.transform = get_transform()
    
#     def __len__(self):
#         return len(self.images)
    
#     def __getitem__(self, idx):
#         image = Image.open(io.BytesIO(self.images[idx])).convert('RGB')
#         image = self.transform(image)
#         label = self.labels[idx]
#         return image, label

# # ✅ API for uploading dataset and training
# @frappe.whitelist(allow_guest=True)
# def upload_dataset():
#     if frappe.request.method != "POST":
#         return {"error": "Invalid request method"}

#     if 'images' not in frappe.request.files or 'labels' not in frappe.request.form:
#         return {"error": "Missing images or labels"}

#     images = []
#     labels = frappe.request.form['labels'].split(",")  # Convert string to list

#     for key in frappe.request.files:
#         file = frappe.request.files[key]
#         images.append(file.read())  # Read image as bytes

#     return train_model(images, labels)

# # ✅ Train Model Function
# @frappe.whitelist(allow_guest=True)
# def train_model(images, labels):
#     if len(images) == 0 or len(labels) == 0:
#         return {"error": "No images or labels provided"}

#     # ✅ Create a label mapping dictionary (for consistent class assignment)
#     unique_labels = sorted(set(labels))
#     label_map = {label: idx for idx, label in enumerate(unique_labels)}

#     # ✅ Store label mapping for future predictions
#     with open("label_map.json", "w") as f:
#         json.dump(label_map, f)

#     dataset = CustomImageDataset(images, labels, label_map)
#     dataloader = DataLoader(dataset, batch_size=8, shuffle=True)

#     num_classes = len(label_map)
#     model = models.resnet18(pretrained=True)
#     model.fc = torch.nn.Linear(model.fc.in_features, num_classes)
#     model = model.to(DEVICE)

#     criterion = torch.nn.CrossEntropyLoss()
#     optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
#     scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=3, gamma=0.1)

#     model.train()
#     for epoch in range(5):
#         running_loss = 0.0
#         for imgs, lbls in dataloader:
#             imgs, lbls = imgs.to(DEVICE), lbls.to(DEVICE)

#             optimizer.zero_grad()
#             outputs = model(imgs)
#             loss = criterion(outputs, lbls.long())  # Ensure labels are tensors
#             loss.backward()
#             optimizer.step()
#             running_loss += loss.item()

#         scheduler.step()
#         print(f"Epoch [{epoch+1}/5], Loss: {running_loss / len(dataloader):.4f}")

#     torch.save(model.state_dict(), 'trained_model.pth')
#     return {"message": "Training Completed!"}

# # ✅ API for Predicting on a New Image
# @frappe.whitelist(allow_guest=True)
# def predict_image():
#     # if frappe.request.method != "POST":
#     #     return {"error": "Invalid request method"}

#     # if 'image' not in frappe.request.files:
#     #     return {"error": "No image provided"}

#     try:
#         # ✅ Load label mapping
#         with open("label_map.json", "r") as f:
#             label_map = json.load(f)
#         reverse_label_map = {v: k for k, v in label_map.items()}  # Reverse mapping

#         num_classes = len(label_map)
#         model = models.resnet18(pretrained=False)
#         model.fc = torch.nn.Linear(model.fc.in_features, num_classes)
#         model.load_state_dict(torch.load('trained_model.pth', map_location=DEVICE))
#         model.to(DEVICE)
#         model.eval()

#         image = Image.open(io.BytesIO(frappe.request.files['image'].read())).convert('RGB')
#         transform = get_transform()
#         img_tensor = transform(image).unsqueeze(0).to(DEVICE)

#         with torch.no_grad():
#             output = model(img_tensor)
#             predicted_idx = torch.argmax(output, dim=1).item()
#             predicted_label = reverse_label_map[predicted_idx]

#         return {'predicted_label': predicted_label}

#     except Exception as e:
#         return {"error": str(e)}


# @frappe.whitelist(allow_guest=True)
# def upload_image():
#     try:
#         # Check if image and label are in the request
#         if 'image' not in frappe.request.files:
#             return {"error": "No image file provided"}
#         if not frappe.form_dict.get('label'):
#             return {"error": "No label provided"}

#         # Get the uploaded file and label
#         uploaded_file = frappe.request.files['image']
#         label = frappe.form_dict.get('label').lower()  # Convert label to lowercase

#         # Ensure the label is valid
#         if label not in ["ok", "defective"]:
#             return {"error": "Invalid label. Allowed values are 'ok' or 'defective'"}

#         # Set folder based on label
#         folder = f"Home/{label.capitalize()}"  # e.g., "Home/Ok" or "Home/Defective"

#         # Create folder if it doesn't exist
#         if not frappe.db.exists("File", {"file_name": label.capitalize()}):
#             frappe.get_doc({
#                 "doctype": "File",
#                 "file_name": label.capitalize(),
#                 "is_folder": 1,
#                 "folder": "Home",
#             }).insert()

#         # Save the file to the specified folder
#         filename = secure_filename(uploaded_file.filename)
#         file_doc = save_file(
#             filename=filename,
#             content=uploaded_file.read(),
#             dt=None,  # No associated DocType
#             dn=None,  # No associated DocName
#             folder=folder,  # Save in the 'ok' or 'defective' folder
#             is_private=0,  # Set to 1 for private files
#         )

#         return {
#             "message": "Image uploaded successfully",
#             "file_url": file_doc.file_url,
#             "folder": folder,
#         }

#     except Exception as e:
#         frappe.log_error(frappe.get_traceback(), "Image Upload Error")
#         return {"error": str(e)}







# frappe-bench/apps/your_app/your_app/api.py

# import frappe
# import json
# import base64

# @frappe.whitelist()
# def upload_training_data(training_data):
#     try:
#         training_data = json.loads(training_data) if isinstance(training_data, str) else training_data
#         for data in training_data:
#             doc = frappe.new_doc("metalcasttrain") # Replace with your DocType
#             doc.image = data.get("image")
#             doc.label = data.get("label")
#             doc.insert()
#         frappe.msgprint("Training data uploaded successfully")
#     except Exception as e:
#         frappe.log_error(title="Error uploading training data", message=frappe.get_traceback())
#         frappe.msgprint("Failed to upload training data")

# @frappe.whitelist()
# def upload_prediction_data(image, prediction):
#     try:
#         doc = frappe.new_doc("metalres") # Replace with your DocType
#         doc.image = image
#         doc.prediction = prediction
#         doc.insert()
#         frappe.msgprint("Prediction data uploaded successfully")
#     except Exception as e:
#         frappe.log_error(title="Error uploading prediction data", message=frappe.get_traceback())
#         frappe.msgprint("Failed to upload prediction data")

# @frappe.whitelist()
# def upload_model(files=None):
#     try:
#         if not files:
#             frappe.msgprint("No files were uploaded.")
#             return

#         # Assuming only one file is uploaded, adjust accordingly if needed
#         model_file = files[0]

#         # Get file content
#         file_content = base64.b64decode(model_file.content)
#         filename = model_file.filename

#         # Create a Frappe File document
#         f = frappe.new_doc("File")
#         f.file_name = filename
#         f.content = file_content  # File content as base64 encoded
#         f.folder = "Home/Attachments"  # Or any other folder
#         f.is_private = 1
#         f.insert()

#         frappe.msgprint("Model uploaded successfully.")

#     except Exception as e:
#         frappe.log_error(title="Error uploading model", message=frappe.get_traceback())
#         frappe.msgprint("Failed to upload model.")






# import frappe
# import json
# import base64

# @frappe.whitelist()
# @frappe.validate_auth
# def get_projects():
#     """Returns a list of projects for the current user."""
#     user = frappe.session.user
#     projects = frappe.db.get_all("Project", filters={"owner": user}, fields=["name"])  # Assuming you have a Project DocType
#     return projects

# @frappe.whitelist()
# @frappe.validate_auth
# def create_project(project_name):
#     """Creates a new project for the current user."""
#     if not project_name:
#         frappe.throw("Project name is required")

#     user = frappe.session.user
#     try:
#         project = frappe.new_doc("Project")  # Assuming you have a Project DocType
#         project.name = project_name # Use name instead of project_name, Frappe standard.
#         project.owner = user
#         project.insert()
#         frappe.db.commit()
#         return "Project created successfully"
#     except Exception as e:
#         frappe.db.rollback()
#         frappe.throw(f"Error creating project: {e}")

# @frappe.whitelist()
# @frappe.validate_auth
# def upload_training_data(training_data, project_name):
#     """Saves training data to a project."""
#     # Verify project exists and the user has access
#     project = frappe.db.exists("Project", project_name)
#     if not project:
#         frappe.throw("Project does not exist")

#     user = frappe.session.user
#     project_owner = frappe.db.get_value("Project", project_name, "owner")
#     if project_owner != user:
#         frappe.throw("You do not have permission to access this project")

#     try:
#         training_data = json.loads(training_data) if isinstance(training_data, str) else training_data
#         for data in training_data:
#             training_doc = frappe.new_doc("metalcasttrain") # Replace with your DocType
#             training_doc.image = data.get("image")
#             training_doc.label = data.get("label")
#             training_doc.project = project_name  # Link to the project
#             training_doc.insert()

#         frappe.db.commit()
#         return "Training data saved successfully"
#     except Exception as e:
#         frappe.db.rollback()
#         frappe.log_error(title="Error uploading training data", message=frappe.get_traceback())
#         frappe.throw("Failed to upload training data")

# @frappe.whitelist()
# @frappe.validate_auth
# def upload_prediction_data(image, prediction, project_name):
#     """Saves prediction data to a project."""
#     # Verify project exists and the user has access
#     project = frappe.db.exists("Project", project_name)
#     if not project:
#         frappe.throw("Project does not exist")

#     user = frappe.session.user
#     project_owner = frappe.db.get_value("Project", project_name, "owner")
#     if project_owner != user:
#         frappe.throw("You do not have permission to access this project")

#     try:
#         doc = frappe.new_doc("metalres") # Replace with your DocType
#         doc.image = image
#         doc.prediction = prediction
#         doc.project = project_name  # Link to the project
#         doc.insert()
#         frappe.db.commit()
#         return "Prediction data uploaded successfully"
#     except Exception as e:
#         frappe.db.rollback()
#         frappe.log_error(title="Error uploading prediction data", message=frappe.get_traceback())
#         frappe.throw("Failed to upload prediction data")


# @frappe.whitelist()
# @frappe.validate_auth
# def upload_model(files=None, project_name=None):
#     """Saves the model file to a project."""

#     if not project_name:
#         frappe.throw("Project name is required")

#      # Verify project exists and the user has access
#     project = frappe.db.exists("Project", project_name)
#     if not project:
#         frappe.throw("Project does not exist")

#     user = frappe.session.user
#     project_owner = frappe.db.get_value("Project", project_name, "owner")
#     if project_owner != user:
#         frappe.throw("You do not have permission to access this project")

#     try:
#         if not files:
#             frappe.throw("No files were uploaded.")


#         uploaded_file = files.split(",")[0] #Access the uploaded file from the files string
#         # Extract filename and content from the data URL
#         file_content = base64.b64decode(uploaded_file.split(",")[1])
#         filename = frappe.utils.sanitize_filename(frappe.form_dict.file_name)

#         # Create a Frappe File document
#         f = frappe.new_doc("File")
#         f.file_name = filename
#         f.file_url = "/private/files/" + filename  #Important
#         f.attached_to_doctype = "Project"  # Attach the file to the Project DocType
#         f.attached_to_name = project_name  # Attach to the specific project
#         f.is_private = 1 # Ensure the file is private
#         f.folder = "Home/Attachments"
#         f.content = file_content
#         f.insert()
#         frappe.db.commit()

#         return "Model saved successfully"

#     except Exception as e:
#         frappe.db.rollback()
#         frappe.log_error(title="Error uploading model", message=frappe.get_traceback())
#         frappe.throw("Failed to upload model.")


# creating project

# import frappe
# import json
# import base64

# @frappe.whitelist()
# def get_projects():
#     """Returns a list of projects for the current user."""
#     user = frappe.session.user
#     projects = frappe.db.get_all("Project", filters={"owner": user}, fields=["name"])  # Assuming you have a Project DocType
#     return projects

# @frappe.whitelist()
# def create_project():
#     """Creates a new project for the current user."""
#     project_name = frappe.form_dict.get("project_name")  # Access project_name from frappe.form_dict

#     if not project_name:
#         frappe.throw("Project name is required")

#     user = frappe.session.user
#     try:
#         project = frappe.new_doc("Project")  # Assuming you have a Project DocType
#         project.name = project_name # Use name instead of project_name, Frappe standard.
#         project.owner = user
#         project.insert()
#         frappe.db.commit()
#         return "Project created successfully"
#     except Exception as e:
#         frappe.db.rollback()
#         frappe.throw(f"Error creating project: {e}")

# @frappe.whitelist()
# def upload_training_data(training_data, project_name):
#     """Saves training data to a project."""
#     # Verify project exists and the user has access
#     project = frappe.db.exists("Project", project_name)
#     if not project:
#         frappe.throw("Project does not exist")

#     user = frappe.session.user
#     project_owner = frappe.db.get_value("Project", project_name, "owner")
#     if project_owner != user:
#         frappe.throw("You do not have permission to access this project")

#     try:
#         training_data = json.loads(training_data) if isinstance(training_data, str) else training_data
#         for data in training_data:
#             training_doc = frappe.new_doc("Metalcasttrain") # Replace with your DocType
#             training_doc.image = data.get("image")
#             training_doc.label = data.get("label")
#             training_doc.project = project_name  # Link to the project
#             training_doc.insert()

#         frappe.db.commit()
#         return "Training data saved successfully"
#     except Exception as e:
#         frappe.db.rollback()
#         frappe.log_error(title="Error uploading training data", message=frappe.get_traceback())
#         frappe.throw("Failed to upload training data")

# @frappe.whitelist()
# def upload_prediction_data(image, prediction, project_name):
#     """Saves prediction data to a project."""
#     # Verify project exists and the user has access
#     project = frappe.db.exists("Project", project_name)
#     if not project:
#         frappe.throw("Project does not exist")

#     user = frappe.session.user
#     project_owner = frappe.db.get_value("Project", project_name, "owner")
#     if project_owner != user:
#         frappe.throw("You do not have permission to access this project")

#     try:
#         doc = frappe.new_doc("Metalres") # Replace with your DocType
#         doc.image = image
#         doc.prediction = prediction
#         doc.project = project_name  # Link to the project
#         doc.insert()
#         frappe.db.commit()
#         return "Prediction data uploaded successfully"
#     except Exception as e:
#         frappe.db.rollback()
#         frappe.log_error(title="Error uploading prediction data", message=frappe.get_traceback())
#         frappe.throw("Failed to upload prediction data")


# @frappe.whitelist()
# def upload_model(files=None, project_name=None):
#     """Saves the model file to a project."""

#     if not project_name:
#         frappe.throw("Project name is required")

#      # Verify project exists and the user has access
#     project = frappe.db.exists("Project", project_name)
#     if not project:
#         frappe.throw("Project does not exist")

#     user = frappe.session.user
#     project_owner = frappe.db.get_value("Project", project_name, "owner")
#     if project_owner != user:
#         frappe.throw("You do not have permission to access this project")

#     try:
#         if not files:
#             frappe.throw("No files were uploaded.")


#         uploaded_file = files.split(",")[0] #Access the uploaded file from the files string
#         # Extract filename and content from the data URL
#         file_content = base64.b64decode(uploaded_file.split(",")[1])
#         filename = frappe.utils.sanitize_filename(frappe.form_dict.file_name)

#         # Create a Frappe File document
#         f = frappe.new_doc("File")
#         f.file_name = filename
#         f.file_url = "/private/files/" + filename  #Important
#         f.attached_to_doctype = "Project"  # Attach the file to the Project DocType
#         f.attached_to_name = project_name  # Attach to the specific project
#         f.is_private = 1 # Ensure the file is private
#         f.folder = "Home/Attachments"
#         f.content = file_content
#         f.insert()
#         frappe.db.commit()

#         return "Model saved successfully"

#     except Exception as e:
#         frappe.db.rollback()
#         frappe.log_error(title="Error uploading model", message=frappe.get_traceback())
#         frappe.throw("Failed to upload model.")


# accesing project 



# import frappe
# import json
# import base64

# @frappe.whitelist()
# def get_projects():
#     """Returns a list of projects for the current user."""
#     user = frappe.session.user
#     projects = frappe.db.get_all("Project", filters={"owner": user}, fields=["name"])  # Assuming you have a Project DocType
#     return projects

# @frappe.whitelist()
# def create_project():
#     """Creates a new project for the current user."""
#     project_name = frappe.form_dict.get("project_name")  # Access project_name from frappe.form_dict

#     if not project_name:
#         frappe.throw("Project name is required")

#     user = frappe.session.user
#     try:
#         project = frappe.new_doc("Project")  # Assuming you have a Project DocType
#         project.name = project_name # Use name instead of project_name, Frappe standard.
#         project.owner = user
#         project.insert()
#         frappe.db.commit()
#         return "Project created successfully"
#     except Exception as e:
#         frappe.db.rollback()
#         frappe.throw(f"Error creating project: {e}")
# @frappe.whitelist()
# def upload_training_data(training_data):
#     try:
#         training_data = json.loads(training_data) if isinstance(training_data, str) else training_data
#         for data in training_data:
#             doc = frappe.new_doc("metalcasttrain") # Replace with your DocType
#             doc.image = data.get("image")
#             doc.label = data.get("label")
#             doc.insert()
#         frappe.msgprint("Training data uploaded successfully")
#     except Exception as e:
#         frappe.log_error(title="Error uploading training data", message=frappe.get_traceback())
#         frappe.msgprint("Failed to upload training data")

# @frappe.whitelist()
# def upload_prediction_data(image, prediction):
#     try:
#         doc = frappe.new_doc("metalres") # Replace with your DocType
#         doc.image = image
#         doc.prediction = prediction
#         doc.insert()
#         frappe.msgprint("Prediction data uploaded successfully")
#     except Exception as e:
#         frappe.log_error(title="Error uploading prediction data", message=frappe.get_traceback())
#         frappe.msgprint("Failed to upload prediction data")


# @frappe.whitelist()
# def upload_model(files=None):
#     """Saves the model file."""
#     try:
#         if not files:
#             frappe.throw("No files were uploaded.")

#         # Assuming only one file is uploaded, adjust accordingly if needed
#         model_file = frappe.form_dict.get('files')  # Access from frappe.form_dict
#         file_name = frappe.form_dict.get('file_name')

#         # Get file content
#         file_content = base64.b64decode(model_file.split(",")[1])

#         # Create a Frappe File document
#         f = frappe.new_doc("File")
#         f.file_name = file_name
#         f.file_url = "/private/files/" + file_name  # Important: Set file_url
#         f.content = file_content  # Set file content
#         f.folder = "Home/Attachments"  # Or any other folder
#         f.is_private = 1
#         f.insert()
#         frappe.db.commit()

#         return "Model uploaded successfully."

#     except Exception as e:
#         frappe.db.rollback()
#         frappe.log_error(title="Error uploading model", message=frappe.get_traceback())
#  
# 
#        frappe.throw("Failed to upload model: " + str(e))



from __future__ import unicode_literals
import frappe
import json
import base64
import tensorflow as tf
import numpy as np
import io
from PIL import Image
import os

from frappe.utils.file_manager import save_file
from frappe import _
import hashlib
import uuid

@frappe.whitelist()
def get_projects():
    """Returns a list of projects for the current user."""
    user = frappe.session.user
    projects = frappe.db.get_all("Project", filters={"owner": user}, fields=["name","project_name"])  # Assuming you have a Project DocType
    return projects

@frappe.whitelist()
def create_project(project_name):
    """Creates a new project for the current user."""
    # project_name = frappe.form_dict.get("project_name")  # Access project_name from frappe.form_dict

    if not project_name:
        frappe.throw("Project name is required")

    user = frappe.session.user
    try:
        project = frappe.new_doc("Project")  # Assuming you have a Project DocType
        project.project_name = project_name # Use name instead of project_name, Frappe standard.
        project.owner = user
        project.insert()
        frappe.db.commit()
        return "Project created successfully"
    except Exception as e:
        frappe.db.rollback()
        frappe.throw(f"Error creating project: {e}")


# @frappe.whitelist()
# def upload_training_data(project_name, training_data):
#     """Uploads training data (images and labels) to Frappe.

#     Args:
#         project_name (str): The name of the project to associate the training data with.
#         training_data (list): A list of dictionaries, where each dictionary contains:
#             - image (str): The base64 encoded image data.
#             - label (str): The label for the image ('ok' or 'defective').
#     """
#     try:
#         training_data = json.loads(training_data) if isinstance(training_data, str) else training_data

#         # Validate that project exists (optional)
#         if not frappe.db.exists("Project", project_name):
#             frappe.throw(f"Project '{project_name}' does not exist.")


#         for data in training_data:
#             doc = frappe.new_doc("metalcasttrain")  # Replace with your actual DocType name
#             doc.project = project_name  # Link to the project
#             doc.image = data.get("image")
#             doc.label = data.get("label")
#             doc.insert()

#         frappe.db.commit()
#         return "Training data uploaded successfully"

#     except Exception as e:
#         frappe.db.rollback()
#         frappe.log_error(title="Error uploading training data", message=frappe.get_traceback())
#         frappe.throw(f"Failed to upload training data: {e}")





import frappe
import json
import base64
import os
from frappe.utils import get_files_path
import datetime
# @frappe.whitelist()
# def upload_training_data(project_name, training_data):
#     """Uploads training data (images and labels) to the Frappe file system.
#     Args:
#         project_name (str): The name of the project to associate the training data with.
#         training_data (list): A list of dictionaries, where each dictionary contains:
#             - image (str): The base64 encoded image data.
#             - label (str): The label for the image ('ok' or 'defective').
#     """
#     try:
#         training_data = json.loads(training_data) if isinstance(training_data, str) else training_data
        
#         # Validate that project exists
#         if not frappe.db.exists("Project", project_name):
#             frappe.throw(f"Project '{project_name}' does not exist.")
        
#         # Function to create folder and return the folder document
#         def create_folder(folder_name, parent_folder="Home"):
#             """Create a folder in Frappe's file system if it doesn't exist"""
#             # Determine the exact parent folder name for querying
#             parent_name = parent_folder
#             if parent_folder != "Home":
#                 parent_doc = frappe.get_doc("File", parent_folder)
#                 parent_name = parent_doc.name
            
#             # Check if folder already exists under the parent
#             folder_exists = frappe.db.exists(
#                 "File", 
#                 {"file_name": folder_name, "folder": parent_name, "is_folder": 1}
#             )
            
#             if folder_exists:
#                 return frappe.get_doc(
#                     "File", 
#                     {"file_name": folder_name, "folder": parent_name, "is_folder": 1}
#                 )
            
#             # Create new folder
#             folder = frappe.new_doc("File")
#             folder.file_name = folder_name
#             folder.is_folder = 1
#             folder.folder = parent_name
            
#             # Important: these fields help ensure the folder is visible in File Manager
#             folder.is_private = 1
#             folder.attached_to_doctype = "Project"
#             folder.attached_to_name = project_name
            
#             folder.insert(ignore_permissions=True)
#             frappe.db.commit()  # Commit immediately to ensure folder is created
            
#             return folder
        
#         # Create folder structure (training_data/project_name/[ok, defective])
#         training_data_folder = create_folder("training_data")
#         project_folder = create_folder(project_name, training_data_folder.name)
#         ok_folder = create_folder("ok", project_folder.name)
#         defective_folder = create_folder("defective", project_folder.name)
#         model_folder = create_folder("model", project_folder.name)

        
#         # Create physical directories
#         site_path = frappe.get_site_path()
#         private_files_path = os.path.join(site_path, "private", "files")
        
#         # Create full physical paths matching Frappe's folder structure
#         base_path = os.path.join(private_files_path, "Home")
#         training_data_path = os.path.join(base_path, "training_data")
#         project_path = os.path.join(training_data_path, project_name)
#         ok_path = os.path.join(project_path, "ok")
#         defective_path = os.path.join(project_path, "defective")
#         model_path=os.path.join(project_path,"model")
        
#         # Create physical directories if they don't exist
#         os.makedirs(training_data_path, exist_ok=True)
#         os.makedirs(project_path, exist_ok=True)
#         os.makedirs(ok_path, exist_ok=True)
#         os.makedirs(defective_path, exist_ok=True)
#         os.makedirs(model_path, exist_ok=True)

        
#         uploaded_files = []
        
#         for idx, data in enumerate(training_data):
#             label = data.get("label", "").lower()
#             image_data = data.get("image")
            
#             if not image_data or not label:
#                 frappe.throw("Invalid training data format: Missing image or label.")
                
#             # Determine parent folder and path based on label
#             if label == "ok":
#                 parent_folder = ok_folder
#                 folder_path = ok_path
#             elif label=="defective":  # Assume "defective" for any other label
#                 parent_folder = defective_folder
#                 folder_path = defective_path
#             else :
#                 parent_folder=model_folder
#                 folder_path=model_path
                
#             # Generate a unique file name with index to avoid collisions
#             file_name = f"{project_name}_{label}_{idx+1}_{frappe.generate_hash(length=6)}.png"
#             file_path = os.path.join(folder_path, file_name)
            
#             # Decode base64 image data and save to file system
#             try:
#                 # Remove potential data URL prefix
#                 if "," in image_data:
#                     image_data = image_data.split(",")[1]
                    
#                 with open(file_path, "wb") as f:
#                     f.write(base64.b64decode(image_data))
#             except Exception as e:
#                 frappe.throw(f"Error saving image file: {str(e)}")
                
#             # Create File document to make it visible in File Manager
#             file_doc = frappe.new_doc("File")
#             file_doc.file_name = file_name
#             file_doc.is_private = 1
#             file_doc.folder = parent_folder.name
            
#             # Important: Link file to the project document type
#             file_doc.attached_to_doctype = "Project"
#             file_doc.attached_to_name = project_name
            
#             file_doc.file_size = os.path.getsize(file_path)
#             file_doc.content_hash = frappe.generate_hash(length=10)
            
#             # Set the correct file URL
#             relative_url = f"private/files/Home/training_data/{project_name}/{label}/{file_name}"
#             file_doc.file_url = f"/{relative_url}"
            
#             file_doc.insert(ignore_permissions=True)
            
#             # Save record in the database
#             doc = frappe.new_doc("metalcasttrain")
#             doc.project = project_name
#             doc.image = file_doc.file_url
#             doc.label = label
#             doc.insert(ignore_permissions=True)
            
#             uploaded_files.append({
#                 "name": file_name,
#                 "url": file_doc.file_url,
#                 "label": label,
#                 "docname": file_doc.name
#             })
            
#         frappe.db.commit()
        
#         # Force refresh file manager to make files visible immediately
#         frappe.msgprint("Training data uploaded successfully. Please refresh the file manager to see all files.")
        
#         return {
#             "message": "Training data uploaded successfully",
#             "files": uploaded_files,
#             "project": project_name,
#             "count": len(uploaded_files),
#             "folder_path": f"/app/file/Home/training_data/{project_name}"
#         }
        
#     except Exception as e:
#         frappe.db.rollback()
#         frappe.log_error(title="Error uploading training data", message=frappe.get_traceback())
#         frappe.throw(f"Failed to upload training data: {str(e)}")

import json
import os
import base64
import frappe

# @frappe.whitelist()
# def upload_training_data(project_name, training_data):
#     """Uploads training data (images and labels) to the Frappe file system.
#     Args:
#         project_name (str): The name of the project to associate the training data with.
#         training_data (list): A list of dictionaries, where each dictionary contains:
#             - image (str): The base64 encoded image data.
#             - label (str): The label for the image ('ok' or 'defective').
#     """
#     try:
#         training_data = json.loads(training_data) if isinstance(training_data, str) else training_data
        
#         # Validate that project exists
#         if not frappe.db.exists("Project", project_name):
#             frappe.throw(f"Project '{project_name}' does not exist.")
        
#         # Function to create folder and return the folder document
#         def create_folder(folder_name, parent_folder="Home"):
#             """Create a folder in Frappe's file system if it doesn't exist"""
#             # Determine the exact parent folder name for querying
#             parent_name = parent_folder
#             if parent_folder != "Home":
#                 parent_doc = frappe.get_doc("File", parent_folder)
#                 parent_name = parent_doc.name
            
#             # Check if folder already exists under the parent
#             folder_exists = frappe.db.exists(
#                 "File", 
#                 {"file_name": folder_name, "folder": parent_name, "is_folder": 1}
#             )
            
#             if folder_exists:
#                 return frappe.get_doc(
#                     "File", 
#                     {"file_name": folder_name, "folder": parent_name, "is_folder": 1}
#                 )
            
#             # Create new folder
#             folder = frappe.new_doc("File")
#             folder.file_name = folder_name
#             folder.is_folder = 1
#             folder.folder = parent_name
            
#             # Important: these fields help ensure the folder is visible in File Manager
#             folder.is_private = 1
#             folder.attached_to_doctype = "Project"
#             folder.attached_to_name = project_name
            
#             folder.insert(ignore_permissions=True)
#             frappe.db.commit()  # Commit immediately to ensure folder is created
            
#             return folder
        
#         # Create folder structure (training_data/project_name/[ok, defective])
#         training_data_folder = create_folder("training_data")
#         project_folder = create_folder(project_name, training_data_folder.name)
#         ok_folder = create_folder("ok", project_folder.name)
#         defective_folder = create_folder("defective", project_folder.name)
#         model_folder = create_folder("model", project_folder.name)

        
#         # Create physical directories
#         site_path = frappe.get_site_path()
#         private_files_path = os.path.join(site_path, "private", "files")
        
#         # Create full physical paths matching Frappe's folder structure
#         base_path = os.path.join(private_files_path, "Home")
#         training_data_path = os.path.join(base_path, "training_data")
#         project_path = os.path.join(training_data_path, project_name)
#         ok_path = os.path.join(project_path, "ok")
#         defective_path = os.path.join(project_path, "defective")
#         model_path = os.path.join(project_path, "model")

        
#         # Create physical directories if they don't exist
#         os.makedirs(training_data_path, exist_ok=True)
#         os.makedirs(project_path, exist_ok=True)
#         os.makedirs(ok_path, exist_ok=True)
#         os.makedirs(defective_path, exist_ok=True)
#         os.makedirs(model_path, exist_ok=True)

        
#         uploaded_files = []
        
#         for idx, data in enumerate(training_data):
#             label = data.get("label", "").lower()
#             image_data = data.get("image")
            
#             if not image_data or not label:
#                 frappe.throw("Invalid training data format: Missing image or label.")
                
#             # Determine parent folder and path based on label
#             if label == "ok":
#                 parent_folder = ok_folder
#                 folder_path = ok_path
#             elif label=="defective":  # Assume "defective" for any other label
#                 parent_folder = defective_folder
#                 folder_path = defective_path
#             else:
#                 parent_folder=model_folder
#                 folder_path=model_path
                
#             # Generate a unique file name with index to avoid collisions
#             file_name = f"{project_name}_{label}_{idx+1}_{frappe.generate_hash(length=6)}.png"
#             file_path = os.path.join(folder_path, file_name)
            
#             # Decode base64 image data and save to file system
#             try:
#                 # Remove potential data URL prefix
#                 if "," in image_data:
#                     image_data = image_data.split(",")[1]
                    
#                 with open(file_path, "wb") as f:
#                     f.write(base64.b64decode(image_data))
#             except Exception as e:
#                 frappe.throw(f"Error saving image file: {str(e)}")
                
#             # Create File document to make it visible in File Manager
#             file_doc = frappe.new_doc("File")
#             file_doc.file_name = file_name
#             file_doc.is_private = 1
#             file_doc.folder = parent_folder.name
            
#             # Important: Link file to the project document type
#             file_doc.attached_to_doctype = "Project"
#             file_doc.attached_to_name = project_name
            
#             file_doc.file_size = os.path.getsize(file_path)
#             file_doc.content_hash = frappe.generate_hash(length=10)
            
#             # Set the correct file URL
#             relative_url = f"private/files/Home/training_data/{project_name}/{label}/{file_name}"
#             file_doc.file_url = f"/{relative_url}"
            
#             file_doc.insert(ignore_permissions=True)
            
#             # Save record in the database
#             doc = frappe.new_doc("metalcasttrain")
#             doc.project = project_name
#             doc.image = file_doc.file_url
#             doc.label = label
#             doc.insert(ignore_permissions=True)
            
#             uploaded_files.append({
#                 "name": file_name,
#                 "url": file_doc.file_url,
#                 "label": label,
#                 "docname": file_doc.name
#             })
            
#         frappe.db.commit()
        
#         # Force refresh file manager to make files visible immediately
#         frappe.msgprint("Training data uploaded successfully. Please refresh the file manager to see all files.")
        
#         return {
#             "message": "Training data uploaded successfully",
#             "files": uploaded_files,
#             "project": project_name,
#             "count": len(uploaded_files),
#             "folder_path": f"/app/file/Home/training_data/{project_name}"
#         }
        
#     except Exception as e:
#         frappe.db.rollback()
#         frappe.log_error(title="Error uploading training data", message=frappe.get_traceback())
#         frappe.throw(f"Failed to upload training data: {str(e)}")

@frappe.whitelist()
def upload_training_data(project_name, training_data, model_file=None):
    """Uploads training data (images and labels) to the Frappe file system.
    Also allows uploading a trained model file in .h5 format.
    
    Args:
        project_name (str): The name of the project to associate the training data with.
        training_data (list): A list of dictionaries, where each dictionary contains:
            - image (str): The base64 encoded image data.
            - label (str): The label for the image ('ok' or 'defective').
        model_file (dict, optional): Dictionary containing:
            - file_data (str): The base64 encoded model file data (.h5 format).
            - file_name (str): The name of the model file.
    """
    try:
        training_data = json.loads(training_data) if isinstance(training_data, str) else training_data
        model_file = json.loads(model_file) if isinstance(model_file, str) and model_file else model_file
        
        # Validate that project exists
        if not frappe.db.exists("Project", project_name):
            frappe.throw(f"Project '{project_name}' does not exist.")
        
        # Function to create folder and return the folder document
        def create_folder(folder_name, parent_folder="Home"):
            """Create a folder in Frappe's file system if it doesn't exist"""
            # Determine the exact parent folder name for querying
            parent_name = parent_folder
            if parent_folder != "Home":
                parent_doc = frappe.get_doc("File", parent_folder)
                parent_name = parent_doc.name
            
            # Check if folder already exists under the parent
            folder_exists = frappe.db.exists(
                "File", 
                {"file_name": folder_name, "folder": parent_name, "is_folder": 1}
            )
            
            if folder_exists:
                return frappe.get_doc(
                    "File", 
                    {"file_name": folder_name, "folder": parent_name, "is_folder": 1}
                )
            
            # Create new folder
            folder = frappe.new_doc("File")
            folder.file_name = folder_name
            folder.is_folder = 1
            folder.folder = parent_name
            
            # Important: these fields help ensure the folder is visible in File Manager
            folder.is_private = 1
            folder.attached_to_doctype = "Project"
            folder.attached_to_name = project_name
            
            folder.insert(ignore_permissions=True)
            frappe.db.commit()  # Commit immediately to ensure folder is created
            
            return folder
        
        # Create folder structure (training_data/project_name/[ok, defective, model])
        training_data_folder = create_folder("training_data")
        project_folder = create_folder(project_name, training_data_folder.name)
        ok_folder = create_folder("ok", project_folder.name)
        defective_folder = create_folder("defective", project_folder.name)
        model_folder = create_folder("model", project_folder.name)
        
        # Create physical directories
        site_path = frappe.get_site_path()
        private_files_path = os.path.join(site_path, "private", "files")
        
        # Create full physical paths matching Frappe's folder structure
        base_path = os.path.join(private_files_path, "Home")
        training_data_path = os.path.join(base_path, "training_data")
        project_path = os.path.join(training_data_path, project_name)
        ok_path = os.path.join(project_path, "ok")
        defective_path = os.path.join(project_path, "defective")
        model_path = os.path.join(project_path, "model")
        
        # Create physical directories if they don't exist
        os.makedirs(training_data_path, exist_ok=True)
        os.makedirs(project_path, exist_ok=True)
        os.makedirs(ok_path, exist_ok=True)
        os.makedirs(defective_path, exist_ok=True)
        os.makedirs(model_path, exist_ok=True)
        
        uploaded_files = []
        
        # Process training data images
        for idx, data in enumerate(training_data):
            label = data.get("label", "").lower()
            image_data = data.get("image")
            
            if not image_data or not label:
                frappe.throw("Invalid training data format: Missing image or label.")
                
            # Determine parent folder and path based on label
            if label == "ok":
                parent_folder = ok_folder
                folder_path = ok_path
            elif label == "defective":
                parent_folder = defective_folder
                folder_path = defective_path
            else:
                continue  # Skip any label that's not 'ok' or 'defective' for images
                
            # Generate a unique file name with index to avoid collisions
            file_name = f"{project_name}_{label}_{idx+1}_{frappe.generate_hash(length=6)}.png"
            file_path = os.path.join(folder_path, file_name)
            
            # Decode base64 image data and save to file system
            try:
                # Remove potential data URL prefix
                if "," in image_data:
                    image_data = image_data.split(",")[1]
                    
                with open(file_path, "wb") as f:
                    f.write(base64.b64decode(image_data))
            except Exception as e:
                frappe.throw(f"Error saving image file: {str(e)}")
                
            # Create File document to make it visible in File Manager
            file_doc = frappe.new_doc("File")
            file_doc.file_name = file_name
            file_doc.is_private = 1
            file_doc.folder = parent_folder.name
            
            # Important: Link file to the project document type
            file_doc.attached_to_doctype = "Project"
            file_doc.attached_to_name = project_name
            
            file_doc.file_size = os.path.getsize(file_path)
            file_doc.content_hash = frappe.generate_hash(length=10)
            
            # Set the correct file URL
            relative_url = f"private/files/Home/training_data/{project_name}/{label}/{file_name}"
            file_doc.file_url = f"/{relative_url}"
            
            file_doc.insert(ignore_permissions=True)
            
            # Save record in the database
            # doc = frappe.new_doc("metalcasttrain")
            # doc.project = project_name
            # doc.image = file_doc.file_url
            # doc.label = label
            # doc.insert(ignore_permissions=True)
            
            uploaded_files.append({
                "name": file_name,
                "url": file_doc.file_url,
                "label": label,
                "docname": file_doc.name
            })
        
        # Process model file if provided
        model_file_info = None
        if model_file and model_file.get("file_data") and model_file.get("file_name"):
            file_data = model_file.get("file_data")
            original_file_name = model_file.get("file_name")
            
            # Ensure the file has .h5 extension
            file_name_parts = os.path.splitext(original_file_name)
            base_name = file_name_parts[0]
            extension = file_name_parts[1].lower() if len(file_name_parts) > 1 else ""
            
            if extension != ".h5":
                # Force .h5 extension if not provided
                extension = ".h5"
                
            # Generate a unique model file name with .h5 extension
            model_file_name = f"{project_name}_model_{frappe.generate_hash(length=8)}{extension}"
            model_file_path = os.path.join(model_path, model_file_name)
            
            # Decode base64 model data and save to file system
            try:
                # Remove potential data URL prefix
                if "," in file_data:
                    file_data = file_data.split(",")[1]
                    
                with open(model_file_path, "wb") as f:
                    f.write(base64.b64decode(file_data))
            except Exception as e:
                frappe.throw(f"Error saving model file: {str(e)}")
                
            # Create File document for the model
            file_doc = frappe.new_doc("File")
            file_doc.file_name = model_file_name
            file_doc.is_private = 1
            file_doc.folder = model_folder.name
            
            # Link file to the project
            file_doc.attached_to_doctype = "Project"
            file_doc.attached_to_name = project_name
            
            file_doc.file_size = os.path.getsize(model_file_path)
            file_doc.content_hash = frappe.generate_hash(length=10)
            
            # Set the correct file URL
            relative_url = f"private/files/Home/training_data/{project_name}/model/{model_file_name}"
            file_doc.file_url = f"/{relative_url}"
            
            file_doc.insert(ignore_permissions=True)
            
            # Save model record in the database (using same metalcasttrain table with special label)
            # doc = frappe.new_doc("metalcasttrain")
            # doc.project = project_name
            # doc.image = file_doc.file_url
            # doc.label = "model"  # Special label for model files
            # doc.insert(ignore_permissions=True)
            
            model_file_info = {
                "name": model_file_name,
                "original_name": original_file_name,
                "url": file_doc.file_url,
                "docname": file_doc.name
            }
            
            # Add to uploaded files list
            uploaded_files.append({
                "name": model_file_name,
                "url": file_doc.file_url,
                "label": "model",
                "docname": file_doc.name
            })
            
        frappe.db.commit()
        
        # Prepare message based on what was uploaded
        upload_message = "Training data"
        if model_file_info:
            upload_message += " and model file (.h5)"
        upload_message += " uploaded successfully. Please refresh the file manager to see all files."
        
        frappe.msgprint(upload_message)
        
        response = {
            "message": upload_message,
            "files": uploaded_files,
            "project": project_name,
            "count": len(uploaded_files),
            "folder_path": f"/app/file/Home/training_data/{project_name}"
        }
        
        # Add model info if available
        if model_file_info:
            response["model_file"] = model_file_info
            
        return response
        
    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(title="Error uploading training data or model", message=frappe.get_traceback())
        frappe.throw(f"Failed to upload training data or model: {str(e)}")
# @frappe.whitelist()
# def upload_prediction_data(project_name, image, predictedLabel):
#     """Uploads prediction data (image and prediction) to Frappe.

#     Args:
#         project_name (str): The name of the project to associate the prediction with.
#         image (str): The base64 encoded image data.
#         prediction (str): The predicted label ('ok' or 'defective').
#     """
#     try:
#         # Validate that the project exists
#         if not frappe.db.exists("Project", project_name):
#             frappe.throw(f"Project '{project_name}' does not exist.")

#         # Create a new document for the prediction data
#         doc = frappe.new_doc("metalres")  # Replace with your actual DocType name
#         doc.project = project_name  # Link to the project
#         doc.image = image  # Store the image data
#         doc.label = predictedLabel  # Save the predicted label
#         doc.insert()
#         frappe.db.commit()

#         return {
#             "status": "success",
#             "message": "Prediction data uploaded successfully",
#             "docname": doc.name,  # Return the document name for reference
#         }

#     except Exception as e:
#         frappe.db.rollback()
#         frappe.log_error(title="Error uploading prediction data", message=frappe.get_traceback())
#         frappe.throw(f"Failed to upload prediction data: {e}")

@frappe.whitelist(allow_guest=True)
def upload_model(files=None, file_name=None, project_name=None):
    """Saves the model file."""
    try:
        if not files:
            frappe.throw("No files were uploaded.")

        # Parse the JSON string
        model_json_str = files  # Directly using the string
        model_json = json.loads(model_json_str)

        # Create a Frappe File document
        f = frappe.new_doc("File")
        f.file_name = file_name
        f.attached_to_doctype = "Project"
        f.attached_to_name = project_name
        f.file_url = "/files/" + file_name  # Important: Public file
        f.file_content = json.dumps(model_json)  # Save JSON string
        f.folder = "Home"  # Default folder for public files
        f.is_private = 0  # Public file
        f.insert()
        frappe.db.commit()

        # Link the file to the project (optional)
        project = frappe.get_doc("Project", project_name)
        project.model_file = f.name  # Assuming you have a Link field named 'model_file' in Project doctype
        project.save()
        frappe.db.commit()

        # Add CORS headers
        frappe.local.response["http_status_code"] = 200
        frappe.local.response["headers"] = {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization",
        }

        return {"message": "Model uploaded successfully."}

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Model Upload Error")
        frappe.local.response["http_status_code"] = 500
        frappe.local.response["headers"] = {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization",
        }
        return {"error": f"Error uploading model: {str(e)}"}

@frappe.whitelist()
def get_training_data(project_name):
    """Retrieves training data for a given project.

    Args:
        project_name (str): The name of the project.

    Returns:
        list: A list of dictionaries, where each dictionary represents a training data point
              and contains the image (base64 encoded) and label.
    """
    try:
        # Validate project exists
        if not frappe.db.exists("Project", project_name):
            frappe.throw(f"Project '{project_name}' does not exist.")

        training_data = frappe.db.get_all(
            "metalcasttrain",  # Replace with your DocType
            filters={"project": project_name},
            fields=["image", "label"]
        )
        return training_data

    except Exception as e:
        frappe.log_error(title="Error getting training data", message=frappe.get_traceback())
        frappe.throw(f"Failed to get training data: {e}")


@frappe.whitelist(allow_guest=True)
def get_model(project_name=None):
    """Loads the model for the given project and returns its summary as a string."""
    try:
        if not project_name:
            frappe.throw("Project name is required.")

        # Get the project document
        project = frappe.get_doc("Project", project_name)
        if not project.model_file:
            frappe.throw("No model file found for the specified project.")

        # Fetch the File document using the file identifier from the Project
        model_file = frappe.get_doc("File", project.model_file)
        if not model_file.file_url:
            frappe.throw("Model file URL not found.")

        # Construct the full file path correctly using os.path.join
        base_path = frappe.utils.get_files_path()  # e.g., './sites/assets'
        # Remove the "/files/" prefix from the URL
        relative_path = model_file.file_url.replace("/files/", "")
        file_path = os.path.join(base_path, relative_path)

        # Check if the file exists
        if not os.path.exists(file_path):
            frappe.throw(f"Model file not found at path: {file_path}")

        # Load the model using TensorFlow/Keras
        model = tf.keras.models.load_model(file_path)

        # Capture the model summary into a string
        stream = io.StringIO()
        model.summary(print_fn=lambda x: stream.write(x + "\n"))
        summary_str = stream.getvalue()

        # Add CORS headers to the response
        frappe.local.response["http_status_code"] = 200
        frappe.local.response["headers"] = {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization",
        }

        return {
            "message": "Model loaded successfully.",
            "summary": summary_str
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Model Fetch Error")
        frappe.throw(f"Error fetching model: {str(e)}")
import easyocr
tf.config.set_visible_devices([], 'GPU')

# Initialize EasyOCR Reader with optimized settings
reader = easyocr.Reader(['en'], gpu=False)

@frappe.whitelist()
def get_all_projects():
    """Returns all projects (Superadmin only)."""
    user = frappe.session.user
    user_info = frappe.db.get_value('User', user, ['username', 'email', 'user_type'], as_dict=True)

    if user_info['user_type'] == 'System User':
        projects = frappe.get_all('Project', fields=['name'])  # Assuming 'Project' is your DocType
        return projects
    else:
        frappe.throw("You do not have permission to access all projects.", frappe.PermissionError)

@frappe.whitelist()
def get_projects_for_admin(username: str):
    """Returns projects for a specific admin."""
    # Assuming you have a way to link admins to projects (e.g., a custom DocType)
    # This is just a placeholder, adapt it to your data model
    projects = frappe.get_all('Project', filters={'admin': username}, fields=['name'])
    return projects



# @frappe.whitelist()
# def predict_image(**kwargs):
#     try:
#         project_name = kwargs.get("project_name")
#         image_data = kwargs.get("image_data")

#         if not project_name or not image_data:
#             return "Missing required parameters"

#         model_path = f"/home/prathamesh/chat-bench/apps/metal_casting_classifier/metal_casting_classifier/models/{project_name}_model.h5"
#         model = tf.keras.models.load_model(model_path)

#         image_data = base64.b64decode(image_data.split(',')[1])  # Remove header
#         image = Image.open(io.BytesIO(image_data)).resize((64, 64))
#         image_array = np.array(image) / 255.0  # Normalize
#         image_array = np.expand_dims(image_array, axis=0)  # Add batch dimension

#         prediction = model.predict(image_array)[0][0]  # Get the prediction value

#         return "ok" if prediction > 0.5 else "defective"

#     except Exception as e:
#         frappe.log_error(f"Error during prediction: {e}", title="Prediction Error")
#         return f"Error during prediction: {e}"


def detect_text(image):
    results = reader.readtext(image)
    detected_text = [text for (_, text, _) in results]
    
    # Draw bounding boxes
    annotated_image = image.copy()
    for (bbox, text, _) in results:
        top_left, bottom_right = tuple(map(int, bbox[0])), tuple(map(int, bbox[2]))
        cv2.rectangle(annotated_image, top_left, bottom_right, (0, 255, 0), 2)
        cv2.putText(annotated_image, text, (top_left[0], top_left[1] - 5), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
    return detected_text, annotated_image

@frappe.whitelist()
def predict_image(**kwargs):
    try:
        project_name = kwargs.get("project_name")
        image_data = kwargs.get("image")
        expected_text = kwargs.get("expected_text", "").lower()

        # Validate inputs
        if not all([project_name, image_data]):
            frappe.throw("Missing required parameters")

        # Load project-specific model
        model_path = f"/home/prathamesh/chat-bench/apps/metal_casting_classifier/metal_casting_classifier/models/PROJ-0028_model_20250228113119.h5"
        model = tf.keras.models.load_model(model_path)

        # Process image
        image_data = base64.b64decode(image_data.split(',')[1])
        image = Image.open(io.BytesIO(image_data))
        
        # Convert to OpenCV format for text detection
        cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # Perform text detection
        detected_texts, annotated_image = detect_text(cv_image)
        
        # Clean detected texts for matching
        detected_texts_clean = [text.lower().strip() for text in detected_texts]

        # Convert annotated image to base64
        _, buffer = cv2.imencode('.png', annotated_image)
        annotated_image_b64 = base64.b64encode(buffer).decode('utf-8')

        # Make prediction
        processed_image = image.resize((64, 64)).convert('RGB')
        image_array = np.array(processed_image) / 255.0
        prediction_value = model.predict(np.expand_dims(image_array, axis=0))[0][0]
        
        # Verify text match against expected input
        text_match = expected_text in detected_texts_clean if expected_text else True

        return {
            "prediction": float(prediction_value),
            "text_match": text_match,
            "detected_texts": detected_texts,
            "annotated_image": annotated_image_b64
        }

    except Exception as e:
      frappe.log_error(f"Prediction error: {str(e)}")
      return {"error": str(e)}



@frappe.whitelist()
def train_model(project_name, training_data):
    """
    Trains the TensorFlow model using the provided training data and saves it.
    
    Args:
        project_name (str): The name of the project
        training_data (list/str): List of dictionaries or JSON string containing image data and labels
        
    Returns:
        dict: Success or error message
    """
    try:
        if not project_name:
            return {"status": "error", "message": "Project name is required."}
        
        if not training_data:
            return {"status": "error", "message": "Training data cannot be None."}
        
        if isinstance(training_data, str):
            training_data = json.loads(training_data)
        
        if not frappe.db.exists("Project", project_name):
            return {"status": "error", "message": f"Project '{project_name}' does not exist."}
        
        images = []
        labels = []
        label_map = {"ok": 1, "defective": 0}
        
        for item in training_data:
            try:
                image_data = item['image']
                if ',' in image_data:
                    image_data = image_data.split(',')[1]
                
                decoded_image = base64.b64decode(image_data)
                image = Image.open(io.BytesIO(decoded_image)).convert('RGB').resize((64, 64))
                image_array = np.array(image) / 255.0
                images.append(image_array)
                
                label = item['label']
                labels.append(label_map.get(label, 0))
            except Exception as e:
                return {"status": "error", "message": f"Error processing image: {str(e)}"}
        
        if not images:
            return {"status": "error", "message": "No valid images found in training data."}
        
        images = np.array(images)
        labels = np.array(labels)
        
        model = tf.keras.models.Sequential([
            tf.keras.layers.Conv2D(32, (3, 3), activation='relu', padding='same', input_shape=(64, 64, 3)),
            tf.keras.layers.BatchNormalization(),
            tf.keras.layers.MaxPooling2D((2, 2)),
            
            tf.keras.layers.Conv2D(64, (3, 3), activation='relu', padding='same'),
            tf.keras.layers.BatchNormalization(),
            tf.keras.layers.MaxPooling2D((2, 2)),
            
            tf.keras.layers.Conv2D(128, (3, 3), activation='relu', padding='same'),
            tf.keras.layers.BatchNormalization(),
            tf.keras.layers.MaxPooling2D((2, 2)),
            
            tf.keras.layers.Flatten(),
            tf.keras.layers.Dropout(0.5),
            tf.keras.layers.Dense(128, activation='relu'),
            tf.keras.layers.Dropout(0.3),
            tf.keras.layers.Dense(1, activation='sigmoid')
        ])
        
        model.compile(
            optimizer=tf.keras.optimizers.Adam(learning_rate=0.0001),
            loss='binary_crossentropy',
            metrics=['accuracy']
        )
        
        history = model.fit(
            images, labels,
            epochs=20,
            batch_size=min(32, len(images)),
            validation_split=0.2,
            verbose=1
        )
        
        site_path = frappe.get_site_path()
        private_files_path = os.path.join(site_path, "private", "files")
        model_folder_path = os.path.join(private_files_path, "Home", "training_data", project_name, "model")
        
        # Create the directory if it doesn't exist
        os.makedirs(model_folder_path, exist_ok=True)
        
        # Generate unique filename with timestamp
        timestamp = frappe.utils.now_datetime().strftime("%Y%m%d%H%M%S")
        model_filename = f"{project_name}_model_{timestamp}.h5"
        file_path = os.path.join(model_folder_path, model_filename)
        
        # Save the model file
        model.save(file_path)
        
        # Check if model folder exists in Frappe's database
        model_folder_exists = frappe.db.exists(
            "File",
            {"file_name": "model", "folder": f"Home/training_data/{project_name}", "is_folder": 1}
        )
        
        if not model_folder_exists:
            # Ensure project folder exists before inserting model folder
            project_folder = frappe.db.exists(
                "File",
                {"file_name": project_name, "folder": "Home/training_data", "is_folder": 1}
            )
            if not project_folder:
                return {"status": "error", "message": "Project folder does not exist in File Manager."}
            
            model_folder = frappe.new_doc("File")
            model_folder.file_name = "model"
            model_folder.is_folder = 1
            model_folder.folder = f"Home/training_data/{project_name}"
            model_folder.is_private = 1
            model_folder.attached_to_doctype = "Project"
            model_folder.attached_to_name = project_name
            model_folder.insert(ignore_permissions=True)
        else:
            model_folder = frappe.get_doc(
                "File",
                {"file_name": "model", "folder": f"Home/training_data/{project_name}", "is_folder": 1}
            )
        
        # Create File document for the model file
        file_doc = frappe.new_doc("File")
        file_doc.file_name = model_filename
        file_doc.is_private = 1
        file_doc.folder = model_folder.name
        file_doc.attached_to_doctype = "Project"
        file_doc.attached_to_name = project_name
        file_doc.file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
        file_doc.content_hash = frappe.generate_hash(length=10)
        
        # Set the correct file URL
        relative_url = f"private/files/Home/training_data/{project_name}/model/{model_filename}"
        file_doc.file_url = f"/{relative_url}"
        
        file_doc.insert(ignore_permissions=True)
        
        # Save model record in the database (using metalcasttrain table with special label)
        if frappe.db.exists("DocType", "metalcasttrain"):
            doc = frappe.new_doc("metalcasttrain")
            doc.project = project_name
            doc.image = file_doc.file_url
            doc.label = "model"  # Special label for model files
            doc.insert(ignore_permissions=True)
        
        # Update the project document with the file URL instead of the file path
        try:
            project = frappe.get_doc("Project", project_name)
            project.model_path = file_doc.file_url
            project.last_trained = frappe.utils.now_datetime()
            project.training_accuracy = float(history.history['accuracy'][-1])
            project.save()
        except Exception as e:
            return {"status": "error", "message": f"Error updating project document: {str(e)}"}
        
        return {
            "status": "success",
            "message": f"Model training completed successfully with accuracy {history.history['accuracy'][-1]:.2%}",
            "model_path": file_doc.file_url,
            "model_file": {
                "name": model_filename,
                "url": file_doc.file_url,
                "docname": file_doc.name
            },
            "accuracy": float(history.history['accuracy'][-1]),
            "val_accuracy": float(history.history['val_accuracy'][-1]) if 'val_accuracy' in history.history else None
        }
    
    except Exception as e:
        return {"status": "error", "message": f"Error during training: {str(e)}"}


# @frappe.whitelist()
# def train_model(project_name, training_data):
#     """
#     Trains the TensorFlow model using the provided training data and saves it.
    
#     Args:
#         project_name (str): The name of the project
#         training_data (list/str): List of dictionaries or JSON string containing image data and labels
        
#     Returns:
#         dict: Success or error message
#     """
#     try:
#         # Validate inputs
#         if not project_name:
#             frappe.throw("Project name is required.")
        
#         if not training_data:
#             frappe.throw("Training data cannot be None.")
        
#         # Parse training data if it's a string
#         if isinstance(training_data, str):
#             training_data = json.loads(training_data)
        
#         frappe.msgprint(title="Model Training Started", message=f"Training model for project: {project_name} with {len(training_data)} samples")

        
#         # Validate the project exists
#         if not frappe.db.exists("Project", project_name):
#             frappe.throw(f"Project '{project_name}' does not exist.")
        
#         # Prepare the training data
#         images = []
#         labels = []
#         label_map = {"ok": 1, "defective": 0}  # Map text labels to numeric values
        
#         for item in training_data:
#             try:
#                 # Decode base64 image
#                 image_data = item['image']
#                 if ',' in image_data:  # Handle data URI format
#                     image_data = image_data.split(',')[1]
                
#                 # Decode and process image
#                 decoded_image = base64.b64decode(image_data)
#                 image = Image.open(io.BytesIO(decoded_image)).convert('RGB').resize((64, 64))
#                 image_array = np.array(image) / 255.0  # Normalize
#                 images.append(image_array)
                
#                 # Process label
#                 label = item['label']
#                 if label in label_map:
#                     labels.append(label_map[label])
#                 else:
#                     # Handle text labels directly if not in map
#                     labels.append(1 if label.lower() == "ok" else 0)
                    
#             except Exception as e:
#                 frappe.throw(f"Error processing image: {str(e)}", title="Training Data Processing Error")
#                 continue
        
#         if not images:
#             frappe.throw("No valid images found in training data")
        
#         # Convert to numpy arrays
#         images = np.array(images)
#         labels = np.array(labels)
        
#         # Log data shapes for debugging
        
        
#         # Define model architecture with improved structure
#         model = tf.keras.models.Sequential([
#             # Input layer
#             tf.keras.layers.Conv2D(32, (3, 3), activation='relu', padding='same', input_shape=(64, 64, 3)),
#             tf.keras.layers.BatchNormalization(),
#             tf.keras.layers.MaxPooling2D((2, 2)),
            
#             # Middle layers
#             tf.keras.layers.Conv2D(64, (3, 3), activation='relu', padding='same'),
#             tf.keras.layers.BatchNormalization(),
#             tf.keras.layers.MaxPooling2D((2, 2)),
            
#             tf.keras.layers.Conv2D(128, (3, 3), activation='relu', padding='same'),
#             tf.keras.layers.BatchNormalization(),
#             tf.keras.layers.MaxPooling2D((2, 2)),
            
#             # Output layers
#             tf.keras.layers.Flatten(),
#             tf.keras.layers.Dropout(0.5),
#             tf.keras.layers.Dense(128, activation='relu'),
#             tf.keras.layers.Dropout(0.3),
#             tf.keras.layers.Dense(1, activation='sigmoid')
#         ])
        
#         # Compile model with better hyperparameters
#         model.compile(
#             optimizer=tf.keras.optimizers.Adam(learning_rate=0.0001),
#             loss='binary_crossentropy',
#             metrics=['accuracy', tf.keras.metrics.Precision(), tf.keras.metrics.Recall()]
#         )
        
#         # Add callbacks for better training
#         callbacks = [
#             tf.keras.callbacks.EarlyStopping(
#                 monitor='val_loss',
#                 patience=5,
#                 restore_best_weights=True
#             ),
#             tf.keras.callbacks.ReduceLROnPlateau(
#                 monitor='val_loss',
#                 factor=0.5,
#                 patience=3,
#                 min_lr=0.00001
#             )
#         ]
        
#         # Train with validation split
#         history = model.fit(
#             images, labels,
#             epochs=20,
#             batch_size=min(32, len(images)),  # Adjust batch size based on data size
#             validation_split=0.2,
#             callbacks=callbacks,
#             verbose=1
#         )
        
#         # Create directory if it doesn't exist
#         model_dir = f"/home/prathamesh/chat-bench/apps/metal_casting_classifier/metal_casting_classifier/models"
#         os.makedirs(model_dir, exist_ok=True)
        
#         # Save the model with timestamp to prevent overwrites
#         timestamp = frappe.utils.now_datetime().strftime("%Y%m%d%H%M%S")
#         file_path = os.path.join(model_dir, f"{project_name}_model_{timestamp}.h5")
#         model.save(file_path)
        
#         # Update the project document with model info
#         try:
#             project = frappe.get_doc("Project", project_name)
#             project.model_path = file_path
#             project.last_trained = frappe.utils.now_datetime()
#             project.training_accuracy = float(history.history['accuracy'][-1])
#             project.save()
#         except Exception as e:
#             return {
#                 "status": "error",
#                 "message": f'Error updating project document: {str(e)}"}
            
#             # frappe.throw(f"Error updating project document: {str(e)}", 
#             #                  title="Project Update Error")
        
#         # Log training completion
#         # frappe.msgprint(
#         #     f"Model trained successfully: Final accuracy={history.history['accuracy'][-1]:.4f}, " +
#         #     f"Val accuracy={history.history['val_accuracy'][-1]:.4f}", 
#         #     title="Model Training Completed"
#         # )
        
#         return {
#             "status": "success",
#             "message": f"Model training completed successfully with accuracy {history.history['accuracy'][-1]:.2%}",
#             "model_path": file_path,
#             "accuracy": float(history.history['accuracy'][-1]),
#             "val_accuracy": float(history.history['val_accuracy'][-1]) if 'val_accuracy' in history.history else None
#         }
        
#     except Exception as e:
#         error_msg = f"Error during training: {str(e)}"
#         # frappe.throw(message=f"{error_msg}\n{frappe.get_traceback()}", title="Model Training Failed")
#         return {
#         "status": "error",
#         "message": error_msg
#         }






# @frappe.whitelist()
# def get_projects():
#     """Returns a list of projects for the current user."""
#     user = frappe.session.user
#     projects = frappe.db.get_all("Project", filters={"owner": user}, fields=["name","project_name"])  # Assuming you have a Project DocType
#     return projects

# @frappe.whitelist()
# def create_project(project_name):
#     """Creates a new project for the current user."""
#     # project_name = frappe.form_dict.get("project_name")  # Access project_name from frappe.form_dict

#     if not project_name:
#         frappe.throw("Project name is required")

#     user = frappe.session.user
#     try:
#         project = frappe.new_doc("Project")  # Assuming you have a Project DocType
#         project.project_name = project_name # Use name instead of project_name, Frappe standard.
#         project.owner = user
#         project.insert()
#         frappe.db.commit()
#         return "Project created successfully"
#     except Exception as e:
#         frappe.db.rollback()
#         frappe.throw(f"Error creating project: {e}")


# @frappe.whitelist()
# def upload_training_data(project_name, training_data):
#     """Uploads training data (images and labels) to Frappe.

#     Args:
#         project_name (str): The name of the project to associate the training data with.
#         training_data (list): A list of dictionaries, where each dictionary contains:
#             - image (str): The base64 encoded image data.
#             - label (str): The label for the image ('ok' or 'defective').
#     """
#     try:
#         training_data = json.loads(training_data) if isinstance(training_data, str) else training_data

#         # Validate that project exists (optional)
#         if not frappe.db.exists("Project", project_name):
#             frappe.throw(f"Project '{project_name}' does not exist.")


#         for data in training_data:
#             doc = frappe.new_doc("metalcasttrain")  # Replace with your actual DocType name
#             doc.project = project_name  # Link to the project
#             doc.image = data.get("image")
#             doc.label = data.get("label")
#             doc.insert()

#         frappe.db.commit()
#         return "Training data uploaded successfully"

#     except Exception as e:
#         frappe.db.rollback()
#         frappe.log_error(title="Error uploading training data", message=frappe.get_traceback())
#         frappe.throw(f"Failed to upload training data: {e}")



@frappe.whitelist()
def upload_prediction_data(project_name, image, predictedLabel):
    """Uploads prediction data (image and prediction) to Frappe.

    Args:
        project_name (str): The name of the project to associate the prediction with.
        image (str): The base64 encoded image data.
        prediction (str): The predicted label ('ok' or 'defective').
    """
    try:
        # Validate that the project exists
        if not frappe.db.exists("Project", project_name):
            frappe.throw(f"Project '{project_name}' does not exist.")

        # Create a new document for the prediction data
        doc = frappe.new_doc("metalres")  # Replace with your actual DocType name
        doc.project = project_name  # Link to the project
        doc.image = image  # Store the image data
        doc.label = predictedLabel  # Save the predicted label
        doc.insert()
        frappe.db.commit()

        return {
            "status": "success",
            "message": "Prediction data uploaded successfully",
            "docname": doc.name,  # Return the document name for reference
        }

    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(title="Error uploading prediction data", message=frappe.get_traceback())
        frappe.throw(f"Failed to upload prediction data: {e}")


# @frappe.whitelist()
# def upload_model(files=None, file_name=None, project_name=None):
#     """Saves the model file."""
#     try:
#         if not files:
#             frappe.throw("No files were uploaded.")

#         #The files are strings.  Need to load them.
#         model_json = json.loads(files)

#         # Create a Frappe File document
#         f = frappe.new_doc("File")
#         f.file_name = file_name
#         f.file_url = "/private/files/" + file_name  # Important: Set file_url
#         f.file_content = json.dumps(model_json)  # Save JSON string
#         f.folder = "Home/Attachments"  # Or any other folder
#         f.is_private = 1
#         f.insert()
#         frappe.db.commit()

#         # Link the file to the project (optional, but recommended)
#         project = frappe.get_doc("Project", project_name)
#         project.model_file = f.name  # Assuming you have a Link field named 'model_file' in Project doctype
#         project.save()
#         frappe.db.commit()

#         return "Model uploaded successfully."

#     except Exception as e:
#         frappe.db.rollback()
#         frappe.log_error(title="Error uploading model", message=frappe.get_traceback())
#         frappe.throw(f"Failed to upload model: {e}")


# @frappe.whitelist()
# def get_training_data(project_name):
#     """Retrieves training data for a given project.

#     Args:
#         project_name (str): The name of the project.

#     Returns:
#         list: A list of dictionaries, where each dictionary represents a training data point
#               and contains the image (base64 encoded) and label.
#     """
#     try:
#         # Validate project exists
#         if not frappe.db.exists("Project", project_name):
#             frappe.throw(f"Project '{project_name}' does not exist.")

#         training_data = frappe.db.get_all(
#             "metalcasttrain",  # Replace with your DocType
#             filters={"project": project_name},
#             fields=["image", "label"]
#         )
#         return training_data

#     except Exception as e:
#         frappe.log_error(title="Error getting training data", message=frappe.get_traceback())
#         frappe.throw(f"Failed to get training data: {e}")



# @frappe.whitelist()
# def get_model(project_name):
#     """Retrieves the model (as JSON) for a given project.

#     Args:
#         project_name (str): The name of the project.

#     Returns:
#         str: The JSON string representing the model.
#     """
#     try:
#         # Validate project exists
#         if not frappe.db.exists("Project", project_name):
#             frappe.throw(f"Project '{project_name}' does not exist.")

#         project = frappe.get_doc("Project", project_name)
#         if not project.model_file:
#             frappe.throw("No model file found for this project.")

#         model_file = frappe.get_doc("File", project.model_file)
#         model_json = model_file.get_content() # Get content as string

#         if not model_json:
#            frappe.throw("Model JSON is empty in File document.")

#         # Attempt to parse the JSON to validate it
#         json.loads(model_json)

#         return model_json

#     except Exception as e:
#         frappe.log_error(title="Error getting model", message=frappe.get_traceback())
#         frappe.throw(f"Failed to get model: {e}")




# @frappe.whitelist(allow_guest=True)
# def train_and_save_model():
#     import tensorflow as tf
#     import numpy as np
#     import base64
#     from io import BytesIO
#     from PIL import Image

#     try:
#         # Parse request data
#         data = frappe.form_dict
#         project_name = data.get("project_name")
#         ok_images = data.get("ok_images", [])
#         defective_images = data.get("defective_images", [])

#         if not project_name or not ok_images or not defective_images:
#             frappe.throw("Project name and labeled images are required!")

#         # Decode Base64 images and preprocess
#         def decode_and_preprocess(image_data):
#             image = Image.open(BytesIO(base64.b64decode(image_data.split(",")[1]))).convert("RGB")
#             image = image.resize((64, 64))  # Resize to model input shape
#             return np.array(image) / 255.0  # Normalize to [0, 1]

#         ok_images_array = np.array([decode_and_preprocess(img) for img in ok_images])
#         defective_images_array = np.array([decode_and_preprocess(img) for img in defective_images])

#         # Create labels (1 for 'ok', 0 for 'defective')
#         ok_labels = np.ones(len(ok_images_array))
#         defective_labels = np.zeros(len(defective_images_array))

#         # Combine data and labels
#         images = np.concatenate([ok_images_array, defective_images_array], axis=0)
#         labels = np.concatenate([ok_labels, defective_labels], axis=0)

#         # Shuffle the data
#         indices = np.arange(len(images))
#         np.random.shuffle(indices)
#         images, labels = images[indices], labels[indices]

#         # Define and train the model
#         model = tf.keras.Sequential([
#             tf.keras.layers.Conv2D(32, (3, 3), activation='relu', input_shape=(64, 64, 3)),
#             tf.keras.layers.MaxPooling2D((2, 2)),
#             tf.keras.layers.Flatten(),
#             tf.keras.layers.Dense(128, activation='relu'),
#             tf.keras.layers.Dense(1, activation='sigmoid'),
#         ])

#         model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
#         model.fit(images, labels, epochs=10, batch_size=32, verbose=1)

#         # Save the model
#         model_path = frappe.utils.get_files_path(f"{project_name}_model.h5")
#         model.save(model_path)

#         return {"message": "Model trained and saved successfully!", "model_path": model_path}

#     except Exception as e:
#         frappe.log_error(frappe.get_traceback(), "Training Error")
#         frappe.throw(str(e))

from frappe.utils import validate_email_address
import re
import easyocr
import cv2
import numpy as np
import pandas as pd
from PIL import Image
import tensorflow as tf
from tensorflow.keras.models import load_model

# Frappe Framework Imports
from frappe import _
import uuid
import hashlib

@frappe.whitelist(allow_guest=True)
def create_company_registration(**kwargs):
    try:
        # Validate required fields
        required_fields = ['first_name', 'last_name', 'email', 'mobile', 'password', 
                         'identification_type', 'company_name', 'currency', 'country']
        
        for field in required_fields:
            if not kwargs.get(field):
                frappe.throw(_("Field {0} is required").format(field))

        # Validate email format
        if not validate_email_address(kwargs.get('email')):
            frappe.throw(_("Invalid email address"))

        # Validate mobile number (basic validation)
        if not re.match(r'^\d{10}$', kwargs.get('mobile')):
            frappe.throw(_("Invalid mobile number. Please enter 10 digits"))

        # Validate identification numbers based on type
        if kwargs.get('identification_type') == 'GST':
            if not kwargs.get('gst_number'):
                frappe.throw(_("GST number is required"))
            # Add GST format validation if needed
        elif kwargs.get('identification_type') == 'PAN':
            if not kwargs.get('pan_number'):
                frappe.throw(_("PAN number is required"))
            # Add PAN format validation if needed

        # Check if company with same email already exists
        if frappe.db.exists("companyreg", {"email": kwargs.get('email')}):
            frappe.throw(_("Company with this email already exists"))

        # Create new company registration
        doc = frappe.get_doc({
            "doctype": "companyreg",
            "first_name": kwargs.get('first_name'),
            "last_name": kwargs.get('last_name'),
            "email": kwargs.get('email'),
            "mobile": kwargs.get('mobile'),
            "password": kwargs.get('password'),  # Note: Consider hashing the password
            "identification_type": kwargs.get('identification_type'),
            "gst_number": kwargs.get('gst_number'),
            "pan_number": kwargs.get('pan_number'),
            "company_name": kwargs.get('company_name'),
            "currency": kwargs.get('currency'),
            "country": kwargs.get('country'),
            "status": "Pending"
        })

        doc.insert(ignore_permissions=True)
        frappe.db.commit()

        return {
            "status": "success",
            "message": "Company registration created successfully",
            "data": {
                "name": doc.name,
                "company_name": doc.company_name
            }
        }

    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(frappe.get_traceback(), _("Company Registration Failed"))
        return {
            "status": "error",
            "message": str(e)
        }
#Add team members--------------------------
JWT_SECRET = "prathamesh"

def generate_invitation_token(email):
    """Generates a unique, but non-expiring, invitation token using UUID and SHA256."""
    # Generate a UUID
    unique_id = uuid.uuid4()

    # Combine UUID with email and hash it using SHA256
    hash_string = f"{unique_id}{email}{frappe.conf.get('secret_key')}".encode('utf-8')
    invitation_token = hashlib.sha256(hash_string).hexdigest()
    return invitation_token

def verify_invitation_token(token, email):
    """Verifies the token by re-generating it and comparing."""
    hash_string = f"{token[:36]}{email}{frappe.conf.get('secret_key')}".encode('utf-8') # Assuming UUID is 36 characters
    expected_token = hashlib.sha256(hash_string).hexdigest()
    return token == expected_token



@frappe.whitelist(allow_guest=True)
def add_team_member(full_name, email, mobile, status, role):
    """Adds a team member if they don't exist; otherwise, updates their info."""
    try:
        # Check if a user with the given email already exists
        existing_user = frappe.db.exists("User", {"email": email})

        if existing_user:
            return {"success": False, "message": _("User with this email already exists.")}

        # Create a new team member document
        team_member = frappe.new_doc("Add Member")  # Replace with your actual Doctype
        team_member.full_name = full_name
        team_member.email = email
        team_member.mobile = mobile
        team_member.status = status
        team_member.role = role
        team_member.insert(ignore_permissions=True)
        team_member.save(ignore_permissions=True)

        # Create a new user document
        # user = frappe.new_doc("User")
        # user.first_name = full_name.split()[0]
        # user.last_name = ' '.join(full_name.split()[1:])
        # user.email = email
        # user.mobile_no = mobile
        # user.role_profile_name = role
        # user.enabled = 1
        # user.user_type = "System User"

        # # Assign roles
        # if role == "Admin":
        #     user.add_roles("Administrator", "System Manager")
        # elif role == "Super Admin":
        #     user.add_roles("Super Admin")
        # elif role == "User":
        #     user.add_roles("User")
        # else:
        #     user.add_roles("User")

        # user.insert(ignore_permissions=True)

        # Generate the invitation token
        invitation_token = generate_invitation_token(email)

        # Create the invitation link
        site_url = frappe.utils.get_url()  # Automatically fetch site URL
        invitation_link = f"{site_url}/invite?token={invitation_token}&email={email}"

        # Send invitation email
        send_invitation_email(email, full_name, invitation_link)

        return {"success": True, "message": _("Team member added and invitation sent.")}

    except frappe.exceptions.DuplicateEntryError as e:
        frappe.db.rollback()
        return {"success": False, "message": _("User with this email already exists.")}

    except Exception as e:
        frappe.db.rollback()
        frappe.log_error("Error adding team member", frappe.get_traceback())
        return {"success": False, "message": _("An error occurred: {0}").format(str(e))}


@frappe.whitelist(allow_guest=True)
def send_invitation_email(recipient, full_name, invitation_link):
    """Sends an invitation email to join a company project with enhanced formatting and error handling."""
    try:
        email_subject = _("Invitation to Join Our Company Project")
        email_message = """\
        <p>Dear {0},</p>

        <p>We are excited to invite you to participate in an important project at <strong>Quantbit Technologies</strong>. Your expertise and perspective will be invaluable to the success of this initiative.</p>

        <p>To join the project and get started, please click the button below:</p>

        <p><a href="http://192.168.1.17:5173/" style="display: inline-block; padding: 10px 20px; font-size: 16px; color: #ffffff; background-color: #007bff; text-decoration: none; border-radius: 5px;">Join the Project</a></p>

        <p>If you have any questions or require further details, please do not hesitate to reach out.</p>

        <p>We look forward to your positive response and to collaborating with you on this exciting project!</p>

        <p>Best regards,</p>
        <p><strong>The Quantbit Technologies Team</strong></p>
        """.format(full_name, invitation_link)

        frappe.sendmail(
            recipients=[recipient],
            sender="no-reply@erpdata.ai",
            subject=email_subject,
            message=email_message,
        )

        return {
            "success": True,
            "message": _("Invitation email successfully sent to {0}").format(recipient),
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Error Sending Invitation Email")
        return {
            "success": False,
            "message": _("Failed to send invitation email: {0}").format(str(e)),
        }



@frappe.whitelist(allow_guest=True)
def validate_invite(token, email):
    """Validates the invite token and returns the email if valid."""
    if verify_invitation_token(token, email):
        return {"success": True, "email": email}
    else:
        return {"success": False, "message": _("Invalid or expired invitation link.")}