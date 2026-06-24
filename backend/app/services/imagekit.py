# backend/app/services/imagekit.py
"""
Purpose: Handle PDF document file persistence.
Responsibilities:
- Upload documents to ImageKit using requests API (Basic Auth).
- Automatically fall back to local disk storage in UPLOAD_FOLDER if ImageKit keys are missing.
- Return the file accessibility URL for database record entry.
"""

import os
import base64
import requests
import logging
from werkzeug.utils import secure_filename

logger = logging.getLogger(__name__)

class StorageService:
    def __init__(self, public_key=None, private_key=None, url_endpoint=None, upload_folder='uploads'):
        self.public_key = public_key
        self.private_key = private_key
        self.url_endpoint = url_endpoint
        self.upload_folder = upload_folder

        # Check if ImageKit keys are fully available
        self.use_imagekit = all([self.public_key, self.private_key, self.url_endpoint])
        if self.use_imagekit:
            logger.info("StorageService: ImageKit.io configuration detected. Using Cloud Storage.")
        else:
            logger.info("StorageService: ImageKit.io credentials missing. Using Local Storage fallback.")

    def upload_file(self, file_storage, filename):
        """
        Uploads a file to ImageKit or saves it locally.
        Returns the public file URL.
        """
        safe_filename = secure_filename(filename)

        if self.use_imagekit:
            try:
                # 1. Prepare Basic Auth header
                auth_str = f"{self.private_key}:"
                auth_bytes = auth_str.encode('utf-8')
                auth_base64 = base64.b64encode(auth_bytes).decode('utf-8')
                
                headers = {
                    "Authorization": f"Basic {auth_base64}"
                }
                
                # Reset file cursor just in case
                file_storage.seek(0)
                
                # ImageKit upload parameters
                files = {
                    'file': (safe_filename, file_storage.read(), 'application/pdf'),
                }
                
                data = {
                    'fileName': safe_filename,
                    'folder': '/smart-sheet-pdf/',
                    'useUniqueFileName': 'true'
                }
                
                logger.info(f"Uploading {safe_filename} to ImageKit...")
                response = requests.post(
                    "https://upload.imagekit.io/api/v1/files/upload",
                    headers=headers,
                    files=files,
                    data=data
                )
                
                if response.status_code == 200:
                    res_json = response.json()
                    file_url = res_json.get('url')
                    logger.info(f"Successfully uploaded to ImageKit. URL: {file_url}")
                    return file_url
                else:
                    logger.error(f"ImageKit API upload failed ({response.status_code}): {response.text}")
                    # Fallback to local storage if API call fails
            except Exception as e:
                logger.error(f"Error calling ImageKit API: {e}. Falling back to local storage.")
        
        # 2. Local Storage Fallback
        file_storage.seek(0)
        local_path = os.path.join(self.upload_folder, safe_filename)
        
        # Avoid duplicate names by appending a suffix if path already exists
        base, extension = os.path.splitext(safe_filename)
        counter = 1
        while os.path.exists(local_path):
            new_filename = f"{base}_{counter}{extension}"
            local_path = os.path.join(self.upload_folder, new_filename)
            safe_filename = new_filename
            counter += 1

        file_storage.save(local_path)
        logger.info(f"Saved file locally at: {local_path}")
        
        # Return a relative URL path that our server can serve
        return f"/api/documents/file/{safe_filename}"
