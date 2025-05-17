# Create destination directory if it doesn't exist
New-Item -ItemType Directory -Force -Path "static"

# Copy all files and subdirectories from source to destination
Copy-Item -Path "my_restaurant\Static\*" -Destination "static\" -Recurse -Force

Write-Host "Static files copied successfully!" 