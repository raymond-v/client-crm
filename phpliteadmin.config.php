<?php
ini_set('display_errors', 1);
ini_set('display_startup_errors', 1);
error_reporting(E_ALL);

// No password
$password = null;

// Define your database
$databases = array(
    'Client DB' => array(
        'path' => 'client.db',
        'name' => 'client.db'
    )
);
?>