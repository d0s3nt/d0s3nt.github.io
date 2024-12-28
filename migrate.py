import os
import shutil
import re
from datetime import datetime

def create_jekyll_front_matter(title, date):
    """Create Jekyll front matter with categories and tags"""
    # Clean the title and create tags
    clean_title = title.replace('-', ' ').title()
    return f"""---
layout: post
title: "{clean_title}"
date: {date}
author: cotes
categories: [Writeup, HackTheBox]
tags: [HTB, Writeup, Security]
pin: true
math: true
mermaid: true
image:
  path: /assets/img/commons/hackthebox.png
  lqip: data:image/webp;base64,UklGRpoAAABXRUJQVlA4WAoAAAAQAAAADwAABwAAQUxQSDIAAAARL0AmbZurmr57yyIiqE8oiG0bejIYEQTgqiDA9vqnsUSI6H+oAERp2HZ65qP/VIAWAFZQOCBCAAAA8AEAnQEqEAAIAAVAfCWkAALp8sF8rgRgAP7o9FDvMCkMde9PK7euH5M1m6VWoDXf2FkP3BqV0ZYbO6NA/VFIAAAA
  alt: Hackthebox Image
---

"""

def sanitize_image_filename(filename):
    """Sanitize image filename for web usage"""
    # Remove special characters and spaces
    clean_name = re.sub(r'[^a-zA-Z0-9.-]', '-', filename)
    return clean_name.lower()

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
    jekyll_filename = f"{date_str}-{title.lower().replace(' ', '-')}.md"
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
        orig_img_name = os.path.basename(img_ref)
        orig_img_path = os.path.join(directory, orig_img_name)
        
        if os.path.exists(orig_img_path):
            # Create new image filename
            new_img_filename = sanitize_image_filename(f"{title.lower()}-{orig_img_name}")
            new_img_path = os.path.join(images_dir, new_img_filename)
            
            # Copy image to new location
            os.makedirs(os.path.dirname(new_img_path), exist_ok=True)
            shutil.copy2(orig_img_path, new_img_path)
            
            # Update image reference in content
            content = content.replace(
                f']({img_ref})', 
                f'](/assets/img/posts/{new_img_filename})'
            )
    
    # Add Jekyll front matter
    content = create_jekyll_front_matter(title, date_str) + content
    
    # Write new Jekyll post
    with open(jekyll_filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return jekyll_filename

def migrate_to_jekyll(source_dir, jekyll_dir):
    """Migrate all markdown files and images to Jekyll structure"""
    # Create necessary directories
    posts_dir = os.path.join(jekyll_dir, '_posts')
    images_dir = os.path.join(jekyll_dir, 'assets', 'img', 'posts')
    
    os.makedirs(posts_dir, exist_ok=True)
    os.makedirs(images_dir, exist_ok=True)
    
    # Process all markdown files
    processed_files = []
    for root, dirs, files in os.walk(source_dir):
        for file in files:
            if file.endswith('.md'):
                src_path = os.path.join(root, file)
                try:
                    processed_file = process_markdown_file(src_path, posts_dir, images_dir)
                    processed_files.append(processed_file)
                    print(f"Successfully processed: {file}")
                except Exception as e:
                    print(f"Error processing {file}: {str(e)}")
    
    return processed_files

if __name__ == "__main__":
    source_directory = "source"  # Source folder containing all writeups
    jekyll_directory = "."  # Current directory (blog root)
    
    try:
        processed_posts = migrate_to_jekyll(source_directory, jekyll_directory)
        print(f"\nSuccessfully processed {len(processed_posts)} posts:")
        for post in processed_posts:
            print(f"- {post}")
    except Exception as e:
        print(f"Error during migration: {str(e)}")
