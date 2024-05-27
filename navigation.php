<?php

/* Generated by chatGPT 4o */

function readDirectory($dir) {
    $result = [];
    $files = scandir($dir);
    natsort($files);

    foreach ($files as $file) {
        if ($file == '.' || $file == '..') continue;
        $filePath = $dir . DIRECTORY_SEPARATOR . $file;
        if (is_dir($filePath)) {
            $result[$file] = readDirectory($filePath);
        } else {
            if ($file == 'index.txt' || preg_match('/\.(png|jpg|jpeg|gif)$/i', $file)) continue; // Skip index.txt and image files
            $result[$file] = $filePath;
        }
    }

    return $result;
}

$dataPath = realpath(__DIR__ . '/Data');
$dataStructure = readDirectory($dataPath);

function generateMainMenu($data) {
    foreach ($data as $key => $value) {
        $displayKey = preg_replace('/^#\d+\s*/', '', $key); // Remove #X prefixes
        if (is_array($value)) {
            if ($key == '#1 Welcome') {
                echo "<li class='main-folder active' data-folder='$key'>$displayKey</li>";
            } else {
                echo "<li class='main-folder' data-folder='$key'>$displayKey</li>";
            }
        }
    }
}

generateMainMenu($dataStructure);
?>