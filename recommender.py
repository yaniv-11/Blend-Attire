import os
import random
import streamlit as st
import json

# Global Variables
dataset_path = r"D:\Desktop\cloths\train"  # Path to your dataset
ratings_file = "ratings.json"  # Path to store ratings

# Function to load dataset
def load_dataset(dataset_path):
    classes = os.listdir(dataset_path)
    outfit = {}
    for cls in classes:
        class_path = os.path.join(dataset_path, cls)
        if os.path.isdir(class_path):
            images = os.listdir(class_path)
            if images:
                outfit[cls] = random.choice(images)
    return outfit

# Function to initialize the ratings file
def initialize_ratings_file():
    if not os.path.exists(ratings_file) or os.path.getsize(ratings_file) == 0:
        with open(ratings_file, 'w') as f:
            json.dump([], f)  # Write an empty list as valid JSON

# Function to check if user exists in JSON file
def user_exists(user_id):
    initialize_ratings_file()
    with open(ratings_file, 'r') as f:
        data = json.load(f)
        for entry in data:
            if entry["user_id"] == user_id:
                return True
    return False

# Function to save ratings
def save_outfit_rating(outfit, rating, user_id, item_ratings=None):
    initialize_ratings_file()  # Ensure the file exists and is initialized
    outfit_str = ";".join([f"{cls}:{img}" for cls, img in outfit.items()])
    
    with open(ratings_file, 'r') as f:
        data = json.load(f)
    
    new_row = {"user_id": user_id, "outfit": outfit_str, "rating": rating}
    if item_ratings:
        new_row["item_ratings"] = item_ratings  # Save individual item ratings
    
    data.append(new_row)
    
    with open(ratings_file, 'w') as f:
        json.dump(data, f, indent=4)

# Function to recommend outfits
def recommend_outfits(ratings_file, user_id):
    initialize_ratings_file()
    with open(ratings_file, 'r') as f:
        data = json.load(f)

    if not data:
        return None  # No data to recommend from

    # Collect ratings for individual items by class
    item_ratings_by_class = {}
    for entry in data:
        if "item_ratings" in entry and entry["user_id"] == user_id:
            for cls, rating in entry["item_ratings"].items():
                if cls not in item_ratings_by_class:
                    item_ratings_by_class[cls] = []
                item_ratings_by_class[cls].append((entry["outfit"], rating))  # Collect outfit and rating

    # Find the top-rated items for each class
    recommended_outfit = {}
    for cls, ratings in item_ratings_by_class.items():
        # Sort items by rating and take the top-3 rated ones
        sorted_ratings = sorted(ratings, key=lambda x: x[1], reverse=True)
        top_items = sorted_ratings[:3]  # Take the top-3 items from the sorted list

        # Randomly select one item from the top-3
        random_item = random.choice(top_items)
        outfit_items = random_item[0].split(";")  # Get the outfit string and split it into items
        for item in outfit_items:
            item_cls, item_img = item.split(":")
            if item_cls == cls:
                recommended_outfit[cls] = item_img  # Add top item to recommended outfit

    return recommended_outfit

# Streamlit Interface
st.title("AI-POWERED: MEN'S BLEND ATTIRE")
user_id = st.text_input("Enter your User ID", value="User1", key="user_id_input")

# Check if user exists
if user_exists(user_id):
    if 'recommended_outfit' not in st.session_state:
        st.session_state.recommended_outfit = recommend_outfits(ratings_file, user_id)
    if 'random_outfit' not in st.session_state:
        st.session_state.random_outfit = load_dataset(dataset_path)

    cols = st.columns(2)
    with cols[0]:
        st.subheader("Recommended Outfit")
        for cls, image in st.session_state.recommended_outfit.items():
            img_path = os.path.join(dataset_path, cls, image)
            if os.path.exists(img_path):
                st.image(img_path, caption=f"Recommended: {cls.capitalize()} - {image}")
            else:
                st.warning(f"Image not found for recommended {cls} - {image}")

    with cols[1]:
        st.subheader("Randomly Generated Outfit")
        if 'item_ratings' not in st.session_state:
            random_item_ratings = {}
        for cls, image in st.session_state.random_outfit.items():
            img_path = os.path.join(dataset_path, cls, image)
            if os.path.exists(img_path):
                sub_cols = st.columns([3, 1])  # Image on the left, rating slider on the right
                with sub_cols[0]:
                    st.image(img_path, caption=f"Random: {cls.capitalize()} - {image}")
                with sub_cols[1]:
                    random_item_ratings[cls] = st.slider(
                        f"Rate Random {cls.capitalize()}", 1, 10, 5, key=f"random_{cls}_rating"
                    )
            else:
                st.warning(f"Image not found for random {cls} - {image}")

        # Overall rating for the random outfit
        random_outfit_rating = st.slider(
            "Rate the overall Random Outfit (1-10)", 1, 10, 5, key="random_outfit_overall_rating"
        )

        if st.button("Submit Random Outfit Rating"):
            save_outfit_rating(st.session_state.random_outfit, random_outfit_rating, user_id, random_item_ratings)
            st.success("Thank you for rating the random outfit! Ratings updated.")
else:
    st.session_state.ratings_count = 0
    st.session_state.current_outfit = load_dataset(dataset_path)
    st.session_state.user_ratings = []

    st.header("Please rate 5 outfits to get personalized recommendations!")
    if st.session_state.ratings_count < 5:
        item_ratings = {}
        for cls, image in st.session_state.current_outfit.items():
            img_path = os.path.join(dataset_path, cls, image)
            if os.path.exists(img_path):
                cols = st.columns([3, 1])
                with cols[0]:
                    st.image(img_path, caption=f"{cls.capitalize()} - {image}")
                with cols[1]:
                    item_ratings[cls] = st.slider(f"Rate {cls.capitalize()}", 1, 10, 5, key=f"{cls}_rating")

        overall_rating = st.slider("Rate the whole outfit (1-10)", 1, 10, 5, key="overall_rating")

        if st.button("Submit Rating"):
            save_outfit_rating(st.session_state.current_outfit, overall_rating, user_id, item_ratings)
            st.session_state.ratings_count += 1
            if st.session_state.ratings_count < 5:
                st.session_state.current_outfit = load_dataset(dataset_path)
                st.success(f"Rated {st.session_state.ratings_count} outfits. {5 - st.session_state.ratings_count} to go!")
            else:
                st.success("You've rated 5 outfits! Reload to get recommendations.")
