import shutil
import os
from pathlib import Path

def copy_assets():
    base_dir = Path(r"d:\My Works\Binco_Ecommerce")
    src_static = base_dir / "backend" / "static"
    dest_public = base_dir / "frontend" / "public"

    if not src_static.exists():
        print(f"Source {src_static} does not exist.")
        return

    # Copy css
    src_css = src_static / "css"
    dest_css = dest_public / "css"
    if src_css.exists():
        if dest_css.exists():
            shutil.rmtree(dest_css)
        shutil.copytree(src_css, dest_css)
        print("Copied css/")

    # Copy images
    src_images = src_static / "images"
    dest_images = dest_public / "images"
    if src_images.exists():
        if dest_images.exists():
            shutil.rmtree(dest_images)
        shutil.copytree(src_images, dest_images)
        print("Copied images/")
        
    print("Assets copied successfully to frontend/public/")

if __name__ == "__main__":
    copy_assets()
