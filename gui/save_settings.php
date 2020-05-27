<html>
<head>

<style>

  body {
    font-family: arial;
  }
 
  table, th, td {
    padding: 10px;
    border: 1px solid;
    border-collapse: collapse;
  }

</style>

</head>
</body>

<?php

  // GET VARS FROM REFERRING PAGE
 
  $settingsFilePath = $_POST['settingsFilePath'];

$settingsFile = fopen($settingsFilePath, "r");
$currentSettings =  json_decode(fread($settingsFile, filesize($settingsFilePath)), true);
fclose($settingsFile);


/*
  //  DEBUG PRINT OUTPUT OF _POST TO CHECK VARS 
  echo "<p>Output of _POST</p>";
  print_r($_POST);
  echo "</pre>";
*/

  // SET $CURRENTSCENARIO WITH NEW KEY => VALUE FROM _POST

  foreach ($_POST as $key => $i) {       
   if (array_key_exists($key, $currentSettings)) {
      //   CHECK VALID KEY TO PREVENT OTHER _POST VARS BEING ADDED TO STEP DATA 
      $currentSettings[$key] = $i;
    }
  } 
  
  // WRITE $CURRENTSCENARIO TO FILE
  // LIMIT TO 1000000 BYTES TO PREVENT ABUSE
  $settingsFile = fopen("$settingsFilePath", "w+");
  if (!fwrite($settingsFile, json_encode($currentSettings, JSON_PRETTY_PRINT), 1000000)) {
    echo "<h2>$settingsFilePath inaccessible, settings not saved!</h2>";
  } else { 
    echo "<h2>File saved</h2>";
  }
  fclose($settingsFile);

/*
  // FOR DEBUG
  echo "<p>Output of currentScenario</p>";
  echo "<pre>";
  print_r($currentScenario); 
  echo "</pre><br>";
  echo $scenarioFilePath; 
*/

?>


<form method="post" action="settings.php" target="">
  <input type="submit" name="submit" value="Click to Return">
</form>


</body>
<html>
