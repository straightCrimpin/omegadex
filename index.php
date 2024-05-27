<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OMEGADEX</title>
    <link rel="stylesheet" href="assets/styles.css">
    <link rel="icon" type="image/x-icon" href="favicon.ico">
</head>
<body>
    <header>
        <span>OMEGADEX</span>
        <div class="menu-toggle" id="menu-toggle">&#9776;</div>
    </header>
    <div class="wrapper">
        <div class="nav-wrapper" id="nav-wrapper">
            <div class="nav-menu" id="main-menu-container">
                <ul id="main-menu">
                    <?php include 'navigation.php'; ?>
                </ul>
            </div>
            <div id="nav-container"></div>
        </div>
        <div class="content" id="content">
            <?php include 'content.php'; ?>
        </div>
    </div>
    <script src="assets/script.js"></script>
</body>
</html>