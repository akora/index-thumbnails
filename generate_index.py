#!/usr/bin/env python3

import os
from pathlib import Path
from wand.image import Image
from wand.drawing import Drawing
from wand.color import Color
import logging
from typing import List, Dict, Tuple
import argparse
import math
import re

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Supported image formats
SUPPORTED_FORMATS = {
    '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp',
    # Raw formats
    '.cr2', '.nef', '.arw', '.orf', '.rw2', '.raf', '.dng'
}

def is_image_file(file_path: str) -> bool:
    """Check if a file is a supported image format."""
    return Path(file_path).suffix.lower() in SUPPORTED_FORMATS

def collect_images_by_month(directory: str) -> Dict[str, List[str]]:
    """
    Collect images assuming YYYY/YYYY-MM/YYYY-MM-DD directory structure.
    Returns a dictionary with YYYY-MM as keys and lists of image paths as values.
    """
    image_groups = {}
    month_pattern = re.compile(r'\d{4}-\d{2}')
    
    for root, dirs, files in os.walk(directory):
        # Get the month from the path (parent directory of date folders)
        path_parts = Path(root).parts
        month = None
        
        # Look for YYYY-MM pattern in the path
        for part in path_parts:
            if month_pattern.match(part):
                month = part
                break
        
        if month:
            if month not in image_groups:
                image_groups[month] = []
            
            # Add all images in this directory
            for file in files:
                if is_image_file(file):
                    image_groups[month].append(os.path.join(root, file))
    
    # Sort images within each month by filename (which includes the date)
    for month in image_groups:
        image_groups[month].sort()
    
    return image_groups

def create_index_thumbnail(images: List[str], output_path: str, 
                         thumbnails_per_row: int = 5,
                         thumbnail_width: int = 200,
                         thumbnail_height: int = 200,
                         background_color: str = '#ffffff',
                         max_thumbnails: int = 100,
                         page_number: int = 1) -> Tuple[bool, bool]:
    """
    Create an index thumbnail from a list of images.
    Returns a tuple of (success, has_more_pages).
    """
    try:
        if not images:
            return False, False

        # Calculate start and end indices for this page
        start_idx = (page_number - 1) * max_thumbnails
        end_idx = min(start_idx + max_thumbnails, len(images))
        current_page_images = images[start_idx:end_idx]
        has_more_pages = end_idx < len(images)

        # Parameters for text and spacing
        text_height = 40
        padding = 10
        frame_color = Color('black')
        
        # Calculate grid dimensions
        num_images = len(current_page_images)
        rows = (num_images + thumbnails_per_row - 1) // thumbnails_per_row
        cols = min(num_images, thumbnails_per_row)

        # Create blank canvas
        canvas_width = cols * (thumbnail_width + 2 * padding)
        canvas_height = rows * (thumbnail_height + text_height + 2 * padding)

        # Add page information if there are multiple pages
        if len(images) > max_thumbnails:
            canvas_height += 40  # Extra space for page information

        with Image(width=canvas_width, height=canvas_height, background=background_color) as canvas:
            with Drawing() as draw:
                # Set up drawing properties
                draw.font_size = 14
                for font in ['Helvetica', 'Arial', 'DejaVu Sans', 'Liberation Sans']:
                    try:
                        draw.font = font
                        break
                    except Exception:
                        continue
                
                draw.fill_color = Color('black')
                draw.stroke_color = frame_color
                draw.stroke_width = 1
                draw.text_alignment = 'center'

                # Process images in the current page
                for idx, img_path in enumerate(current_page_images):
                    try:
                        logger.info(f"Processing image {start_idx + idx + 1} of {len(images)}: {img_path}")
                        with Image(filename=img_path) as img:
                            # Resize maintaining aspect ratio
                            img.transform(resize=f'{thumbnail_width}x{thumbnail_height}')
                            
                            # Calculate position
                            row = idx // thumbnails_per_row
                            col = idx % thumbnails_per_row
                            x = col * (thumbnail_width + 2 * padding) + padding
                            y = row * (thumbnail_height + text_height + 2 * padding) + padding

                            # Draw frame
                            draw.fill_opacity = 0
                            draw.rectangle(
                                left=int(x - 1),
                                top=int(y - 1),
                                right=int(x + thumbnail_width + 1),
                                bottom=int(y + thumbnail_height + 1)
                            )
                            
                            # Composite image onto canvas
                            canvas.composite(img, left=int(x), top=int(y))
                            
                            # Add filename text
                            filename = os.path.basename(img_path)
                            if len(filename) > 25:
                                filename = filename[:22] + "..."
                            
                            # Calculate text position
                            text_x = x + thumbnail_width // 2
                            text_y = y + thumbnail_height + 25
                            
                            # Draw text background
                            metrics = draw.get_font_metrics(canvas, filename)
                            text_width = int(metrics.text_width)
                            text_height = int(metrics.text_height)
                            
                            # Draw semi-transparent background for text
                            with Drawing() as bg_draw:
                                bg_draw.fill_color = Color('white')
                                bg_draw.fill_opacity = 0.7
                                bg_draw.stroke_opacity = 0
                                bg_draw.rectangle(
                                    left=int(text_x - text_width//2 - 5),
                                    top=int(text_y - text_height - 5),
                                    right=int(text_x + text_width//2 + 5),
                                    bottom=int(text_y + 5)
                                )
                                bg_draw(canvas)
                            
                            # Draw text
                            draw.fill_opacity = 1
                            draw.text(
                                x=int(text_x),
                                y=int(text_y),
                                body=filename
                            )

                    except Exception as e:
                        logger.error(f"Error processing image {img_path}: {str(e)}")
                        continue

                # Add page information if there are multiple pages
                if len(images) > max_thumbnails:
                    total_pages = math.ceil(len(images) / max_thumbnails)
                    page_info = f"Page {page_number} of {total_pages}"
                    metrics = draw.get_font_metrics(canvas, page_info)
                    
                    # Draw page information at the bottom
                    draw.text(
                        x=int(canvas_width // 2),
                        y=int(canvas_height - 15),
                        body=page_info
                    )

                # Apply all drawing operations to the canvas
                draw(canvas)

            # Save the index thumbnail
            canvas.save(filename=output_path)
            logger.info(f"Saved index thumbnail: {output_path}")
            return True, has_more_pages

    except Exception as e:
        logger.error(f"Error creating index thumbnail for {output_path}: {str(e)}")
        return False, False

def main():
    parser = argparse.ArgumentParser(description='Generate index thumbnails for image directories')
    parser.add_argument('directory', help='Root directory to process')
    parser.add_argument('--thumbnails-per-row', type=int, default=10,
                      help='Number of thumbnails per row (default: 10)')
    parser.add_argument('--thumbnail-width', type=int, default=150,
                      help='Width of each thumbnail in pixels (default: 150)')
    parser.add_argument('--thumbnail-height', type=int, default=150,
                      help='Height of each thumbnail in pixels (default: 150)')
    parser.add_argument('--max-thumbnails', type=int, default=200,
                      help='Maximum number of thumbnails per index image (default: 200)')
    parser.add_argument('--output-dir', type=str,
                      help='Optional output directory for index files. If not specified, index files will be created in their source directories.')
    args = parser.parse_args()

    root_dir = args.directory
    if not os.path.isdir(root_dir):
        logger.error(f"Directory not found: {root_dir}")
        return

    # Create output directory if specified
    if args.output_dir:
        os.makedirs(args.output_dir, exist_ok=True)

    # Collect all images grouped by month
    logger.info(f"Scanning directory: {root_dir}")
    image_groups = collect_images_by_month(root_dir)

    # Sort months chronologically
    sorted_months = sorted(image_groups.keys())

    # Process each month
    for month in sorted_months:
        images = image_groups[month]
        if not images:
            continue

        logger.info(f"Processing month: {month} ({len(images)} images)")
        
        # Calculate total number of pages
        total_pages = (len(images) + args.max_thumbnails - 1) // args.max_thumbnails
        page_number = 1
        
        while True:
            # Generate index filename with 3-digit padding
            if total_pages > 1:
                index_filename = f"index_{month}_{page_number:03d}.jpg"
            else:
                index_filename = f"index_{month}.jpg"
            
            # Determine output path
            if args.output_dir:
                output_filename = os.path.join(args.output_dir, index_filename)
            else:
                # If no output directory specified, place in the year directory
                year = month[:4]
                output_filename = os.path.join(root_dir, year, index_filename)
            
            success, has_more_pages = create_index_thumbnail(
                images,
                output_filename,
                args.thumbnails_per_row,
                args.thumbnail_width,
                args.thumbnail_height,
                max_thumbnails=args.max_thumbnails,
                page_number=page_number
            )
            
            if not success:
                logger.error(f"Failed to create index thumbnail for month: {month}")
                break
                
            if not has_more_pages:
                break
                
            page_number += 1

if __name__ == "__main__":
    main()
