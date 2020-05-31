<html>
<head>

<style>

</style>


<?php
if (file_exists ('usedarktheme.txt')) {
echo '<link href="darkTheme.css" rel="stylesheet">';
} else {
echo '<link href="lightTheme.css" rel="stylesheet">';
}
?>

</head>
</body>

<?php

  // GET VARS FROM REFERRING PAGE
  $step = $_POST['step'];
  $scenarioFilePath = $_POST['scenarioFilePath'];


    $scenarioFile = fopen("$scenarioFilePath", "r");
    $currentScenario = json_decode(fread($scenarioFile, filesize($scenarioFilePath)), true);
    fclose($scenarioFile);

/*
 //  DEBUG PRINT OUTPUT OF _POST TO CHECK VARS 
  echo "<p>Output of _POST</p><pre>";
  print_r($_POST);
  echo "</pre>";
*/

  // SET $CURRENTSCENARIO WITH NEW KEY => VALUE FROM _POST

foreach ($_POST as $key => $i) {       
    //FIRST MATCH THE SCENARIO DATA KEYS STARTING 1_ 
   if (preg_match('/^1_/', $key)) {		// MATCH STEP KEYS
     $key = preg_replace('/^1_/', '', $key); 
      
      $keys = explode("::", $key);
   
     /* DEBUG
       echo "<pre>";
       print_r($keys);
       echo "</pre>";
       echo $keys[1];
       echo "<br>" . $currentScenario[$step]['data'][0][$keys[0]] . "<br>";
     */

    if(count($keys) == 1) {
      if (array_key_exists($keys[0], $currentScenario[$step]['data'][0]) && !(is_array($currentScenario[$step]['data'][0][$keys[0]]))) {
        $currentScenario[$step]['data'][0][$keys[0]] = $i;
      }
    } elseif(count($keys) == 2) {
      if (array_key_exists($keys[1], $currentScenario[$step]['data'][0][$keys[0]]) && !(is_array($currentScenario[$step]['data'][0][$keys[0]][$keys[1]]))) {
          $currentScenario[$step]['data'][0][$keys[0]][$keys[1]] = $i;
      }
    } elseif(count($keys) == 3) {
      if (array_key_exists($keys[2], $currentScenario[$step]['data'][0][$keys[0]][$keys[1]]) && !(is_array($currentScenario[$step]['data'][0][$keys[0]][$keys[1]][$keys[2]]))) {
        $currentScenario[$step]['data'][0][$keys[0]][$keys[1]][$keys[2]] = $i;
       }
    } elseif(count($keys) == 4) {
      if (array_key_exists($keys[3], $currentScenario[$step]['data'][0][$keys[0]][$keys[1]][$keys[2]]) && !(is_array($currentScenario[$step]['data'][0][$keys[0]][$keys[1]][$keys[2]][$keys[3]]))) {
        $currentScenario[$step]['data'][0][$keys[0]][$keys[1]][$keys[2]][$keys[3]] = $i;
      }
    } elseif(count($keys) == 5) {
      if (array_key_exists($keys[4], $currentScenario[$step]['data'][0][$keys[0]][$keys[1]][$keys[2]][$keys[3]]) && !(is_array($currentScenario[$step]['data'][0][$keys[0]][$keys[1]][$keys[2]][$keys[3]][$keys[4]]))) {
        $currentScenario[$step]['data'][0][$keys[0]][$keys[1]][$keys[2]][$keys[3]][$keys[4]] = $i;
      }
    } elseif(count($keys) == 6) {
      if (array_key_exists($keys[5], $currentScenario[$step]['data'][0][$keys[0]][$keys[1]][$keys[2]][$keys[3]][$keys[4]]) && !(is_array($currentScenario[$step]['data'][0][$keys[0]][$keys[1]][$keys[2]][$keys[3]][$keys[4]][$keys[5]]))) {
        $currentScenario[$step]['data'][0][$keys[0]][$keys[1]][$keys[2]][$keys[3]][$keys[4]][$keys[5]] = $i;
      }
    } elseif(count($keys) == 7) {
       if (array_key_exists($keys[6], $currentScenario[$step]['data'][0][$keys[0]][$keys[1]][$keys[2]][$keys[3]][$keys[4]][$keys[5]]) && !(is_array($currentScenario[$step]['data'][0][$keys[0]][$keys[1]][$keys[2]][$keys[3]][$keys[4]][$keys[5]][$keys[6]]))) {
        $currentScenario[$step]['data'][0][$keys[0]][$keys[1]][$keys[2]][$keys[3]][$keys[4]][$keys[5]][$keys[6]] = $i;
       }
    }
 }
}

  // WRITE $CURRENTSCENARIO TO FILE
  // LIMIT TO 2000000 BYTES TO PREVENT ABUSE
  $scenarioFileOpen = fopen("$scenarioFilePath", "w+");
  if (!fwrite($scenarioFileOpen, json_encode($currentScenario, JSON_PRETTY_PRINT), 2000000) ) {
    echo "<h2>$scenarioFilePath inacessible, file not saved!</h2>";
  } else {
    echo "<h2>Saved.</h2>";
  }

  fclose($scenarioFileOpen);

/*
  // FOR DEBUG
  echo "<p>Output of currentScenario</p>";
  echo "<pre>";
  print_r($currentScenario); 
  echo "</pre><br>";
  echo $scenarioFilePath; 
*/

?>


<form method="post" action="scenario_builder.php" target="">
  <input type="submit" name="submit" value="Click to Return" class="smallButton">
</form>


</body>
<html>
