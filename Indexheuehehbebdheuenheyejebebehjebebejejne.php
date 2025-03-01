<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Image Upload</title>
    <style>
        .image-preview {
            width: 300px;
            height: 300px;
            border: 2px dashed #ccc;
            display: flex;
            align-items: center;
            justify-content: center;
            overflow: hidden;
        }
        .image-preview img {
            width: 100%;
            height: auto;
        }
    </style>
</head>
<body>

    <h2>Upload Image</h2>
    <form action="upload.php" method="POST" enctype="multipart/form-data">
        <input type="file" name="image" required>
        <button type="submit">Upload</button>
    </form>

    <?php
    if (isset($_GET["image"])) {
        $imagePath = "uploads/" . basename($_GET["image"]);
        echo '<h3>Uploaded Image:</h3>
              <div class="image-preview">
                  <img src="' . $imagePath . '" alt="Uploaded Image">
              </div>';
    }
    ?>

</body>
</html>











<?php
if ($_SERVER["REQUEST_METHOD"] == "POST" && isset($_FILES["image"])) {
    $uploadDir = "uploads/";

    if (!is_dir($uploadDir)) {
        mkdir($uploadDir, 0777, true);
    }

    $fileName = basename($_FILES["image"]["name"]);
    $targetFile = $uploadDir . time() . "_" . $fileName;
    $fileType = strtolower(pathinfo($targetFile, PATHINFO_EXTENSION));
    $allowedTypes = ["jpg", "jpeg", "png", "gif"];

    if (!in_array($fileType, $allowedTypes)) {
        die("Only JPG, JPEG, PNG, and GIF files are allowed.");
    }

    if (move_uploaded_file($_FILES["image"]["tmp_name"], $targetFile)) {
        header("Location: index.php?image=" . urlencode(basename($targetFile)));
        exit;
    } else {
        echo "Error uploading image.";
    }
} else {
    echo "No file uploaded.";
}
?>
