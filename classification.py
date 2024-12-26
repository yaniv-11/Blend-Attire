import os
import tensorflow as tf
import streamlit as st
import numpy as np
from PIL import Image

# Streamlit header
st.header("AI POWERED:MEN'S BLEND ATTIRE")
st.header('                              ')
st.header('Classification CNN Model')

# Define the class names
class_names = ['pant', 'shirt', 'shoes', 'watch']

# Load the model using TensorFlow's Keras API
model = tf.keras.models.load_model(r"C:/Users/vinays/img_cls_yaniv.h5")

# Define a function to classify images
def classify_images(image_path):
    # Load and preprocess the image
    input_image = tf.keras.utils.load_img(image_path, target_size=(180, 180))  # Adjust target size to match your model
    input_image_array = tf.keras.utils.img_to_array(input_image)  # Convert to array
    input_image_exp_dim = tf.expand_dims(input_image_array, 0)  # Add batch dimension

    # Predict using the model
    predictions = model.predict(input_image_exp_dim)
    result = tf.nn.softmax(predictions[0])  # Apply softmax for probabilities
    predicted_class_index = np.argmax(result)
    accuracy = np.max(result) * 100  # Get confidence score
    predicted_class = class_names[predicted_class_index]

    outcome = (
        f"The image belongs to '{predicted_class}' "
        f"with a confidence score of {accuracy:.2f}%."
    )
    return predicted_class, outcome

# File upload
uploaded_file = st.file_uploader('Upload an Image')
if uploaded_file is not None:
    # Save the uploaded file to a temporary directory
    temp_dir = "upload"
    os.makedirs(temp_dir, exist_ok=True)
    file_path = os.path.join(temp_dir, uploaded_file.name)
    with open(file_path, 'wb') as f:
        f.write(uploaded_file.getbuffer())
    
    # Display the uploaded image
    st.image(file_path, width=200)

    # Classify the image
    predicted_class, classification_result = classify_images(file_path)

    # Display the classification result
    st.markdown(classification_result)

    # Save the image to a folder with the class name
    output_dir = os.path.join("classified_images", predicted_class)
    os.makedirs(output_dir, exist_ok=True)  # Create the class directory if it doesn't exist
    output_path = os.path.join(output_dir, uploaded_file.name)

    # Save the image
    with Image.open(file_path) as img:
        img.save(output_path)

    st.success(f"Image saved to folder: {output_path}")
