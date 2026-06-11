#!/usr/bin/env python3
"""
generate_markers.py
-------------------
Helper script to generate ArUco marker images for printing.
It automatically handles both modern OpenCV (ArucoDetector) and legacy OpenCV APIs.

Usage:
  python3 generate_markers.py --ids 1 2 3 --dict DICT_4X4_50 --size 400 --output_dir ./markers
"""

import os
import argparse
import cv2

def get_aruco_dict(dict_name):
    mapping = {
        'DICT_4X4_50': cv2.aruco.DICT_4X4_50,
        'DICT_4X4_100': cv2.aruco.DICT_4X4_100,
        'DICT_4X4_250': cv2.aruco.DICT_4X4_250,
        'DICT_4X4_1000': cv2.aruco.DICT_4X4_1000,
        'DICT_5X5_50': cv2.aruco.DICT_5X5_50,
        'DICT_5X5_100': cv2.aruco.DICT_5X5_100,
        'DICT_5X5_250': cv2.aruco.DICT_5X5_250,
        'DICT_5X5_1000': cv2.aruco.DICT_5X5_1000,
        'DICT_6X6_50': cv2.aruco.DICT_6X6_50,
        'DICT_6X6_100': cv2.aruco.DICT_6X6_100,
        'DICT_6X6_250': cv2.aruco.DICT_6X6_250,
        'DICT_6X6_1000': cv2.aruco.DICT_6X6_1000,
        'DICT_APRILTAG_16H5': cv2.aruco.DICT_APRILTAG_16h5,
        'DICT_APRILTAG_25H9': cv2.aruco.DICT_APRILTAG_25h9,
        'DICT_APRILTAG_36H10': cv2.aruco.DICT_APRILTAG_36h10,
        'DICT_APRILTAG_36H11': cv2.aruco.DICT_APRILTAG_36h11,
    }
    val = mapping.get(dict_name.upper())
    if val is None:
        raise ValueError(f"Unknown ArUco dictionary: {dict_name}")
    return cv2.aruco.getPredefinedDictionary(val)

def generate_marker(dictionary, marker_id, pixel_size):
    try:
        # Modern OpenCV API
        img = cv2.aruco.generateImageMarker(dictionary, marker_id, pixel_size)
    except AttributeError:
        # Legacy OpenCV API
        img = cv2.aruco.drawMarker(dictionary, marker_id, pixel_size)
        
    # Add a white "quiet zone" around the black tag. 
    # ArUco algorithms require a white border to contrast with the black tag edge.
    padding = int(pixel_size * 0.15) # 15% padding
    img_with_quiet_zone = cv2.copyMakeBorder(
        img,
        top=padding,
        bottom=padding,
        left=padding,
        right=padding,
        borderType=cv2.BORDER_CONSTANT,
        value=[255, 255, 255]
    )
    return img_with_quiet_zone

def main():
    parser = argparse.ArgumentParser(description="Generate ArUco markers for printing.")
    parser.add_argument('--ids', type=int, nargs='+', default=[1, 2], help='List of marker IDs to generate')
    parser.add_argument('--dict', type=str, default='DICT_4X4_50', help='ArUco dictionary name')
    parser.add_argument('--size', type=int, default=400, help='Image resolution (width/height in pixels)')
    parser.add_argument('--output_dir', type=str, default='/home/smr/workspaces/mini_amr/amrROS2_ws/src/marker_localization/markers', help='Directory to save marker images')
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)
    
    try:
        dictionary = get_aruco_dict(args.dict)
    except ValueError as e:
        print(f"Error: {e}")
        return

    print(f"Generating markers from dictionary {args.dict}...")
    for mid in args.ids:
        img = generate_marker(dictionary, mid, args.size)
        filename = os.path.join(args.output_dir, f"marker_{args.dict}_{mid}.png")
        cv2.imwrite(filename, img)
        print(f"Saved: {filename}")

if __name__ == '__main__':
    main()
