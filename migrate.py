import os
import shutil
import re
from datetime import datetime

def create_jekyll_post_front_matter(title, date):
    """Create Jekyll front matter for posts"""
    return f"""---
layout: post
title: "{title}"
date: {date}
categories: hackthebox
---

"""

def process_markdown_file(src_path, dest_dir, images_dir):
    """Process a single markdown file and its images"""
    # Get the directory and filename
    directory = os.path.dirname(src_path)
    filename = os.path.basename(src_path)
    title = os.path.splitext(filename)[0]
    
    # Create date from file modification time (or you can use current date)
    file_date = datetime.fromtimestamp(os.path.getmtime(src_path))
    date_str = file_date.strftime('%Y-%m-%d')
    
    # Create new Jekyll post filename
    jekyll_filename = f"{date_str}-{title.lower()}.md"
    jekyll_filepath = os.path.join(dest_dir, jekyll_filename)
    
    # Read original content
    with open(src_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find all image references
    image_pattern = r'!\[.*?\]\((.*?)\)'
    image_refs = re.findall(image_pattern, content)
    
    # Process each image reference
    for img_ref in image_refs:
        # Get original image path
        orig_img_path = os.path.join(directory, os.path.basename(img_ref))
        if os.path.exists(orig_img_path):
            # Create new image filename
            new_img_filename = f"{title.lower()}-{os.path.basename(img_ref)}"
            new_img_path = os.path.join(images_dir, new_img_filename)
            
            # Copy image to new location
            shutil.copy2(orig_img_path, new_img_path)
            
            # Update image reference in content
            content = content.replace(img_ref, f"/assets/images/{new_img_filename}")
    
    # Add Jekyll front matter
    content = create_jekyll_post_front_matter(title, date_str) + content
    
    # Write new Jekyll post
    with open(jekyll_filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return jekyll_filename

def migrate_to_jekyll(source_dir, jekyll_dir):
    """Migrate all markdown files and images to Jekyll structure"""
    # Create necessary directories
    posts_dir = os.path.join(jekyll_dir, '_posts')
    images_dir = os.path.join(jekyll_dir, 'assets', 'images')
    
    os.makedirs(posts_dir, exist_ok=True)
    os.makedirs(images_dir, exist_ok=True)
    
    # Process all markdown files
    processed_files = []
    for root, dirs, files in os.walk(source_dir):
        for file in files:
            if file.endswith('.md'):
                src_path = os.path.join(root, file)
                processed_file = process_markdown_file(src_path, posts_dir, images_dir)
                processed_files.append(processed_file)
    
    return processed_files

# Usage example
if __name__ == "__main__":
    source_directory = "source"  # Current directory with your folders
    jekyll_directory = "."  # Destination Jekyll blog directory
    
    processed_posts = migrate_to_jekyll(source_directory, jekyll_directory)
    print(f"Successfully processed {len(processed_posts)} posts:")
    for post in processed_posts:
        print(f"- {post}")
