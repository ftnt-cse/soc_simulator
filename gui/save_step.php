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
  $step = $_POST['step'];
  $scenarioFilePath = $_POST['scenarioFilePath'];


    $scenarioFile = fopen("$scenarioFilePath", "r");
    $currentScenario = json_decode(fread($scenarioFile, filesize($scenarioFilePath)), true);
    fclose($scenarioFile);

/*
  //  DEBUG PRINT OUTPUT OF _POST TO CHECK VARS 
  echo "<p>Output of _POST</p>";
  print_r($_POST);
  echo "</pre>";
*/

  // SET $CURRENTSCENARIO WITH NEW KEY => VALUE FROM _POST

  foreach ($_POST as $key => $i) {       
    //FIRST MATCH THE SCENARIO DATA KEYS STARTING 1_ 
    if (preg_match('/^1_/', $key)) {		// MATCH STEP KEYS
      $key2 = preg_replace('/^1_/', '', $key); 
      // CHECK KEY EXISTS, AND THAT IT IS NOT A NESTED ARRAY TO PREVENT OVERWRITNG 
      if (array_key_exists($key2, $currentScenario[$step][data][0]) && !(is_array($currentScenario[$step][data][0][$key2]))) {
        $currentScenario[$step][data][0][$key2] = $i;
      }
    } 
    // NOW MATCH INCIDENT DATA
    if (array_key_exists($key, $currentScenario[$step][data][0][sourcedata][incident])) {
      //  HANDLE INCIDNET DATA KEYS, CHECK VALID KEY TO PREVENT OTHER _POST VARS BEING ADDED TO STEP DATA 
      $currentScenario[$step][data][0][sourcedata][incident][$key] = $i;
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
  <input type="submit" name="submit" value="Click to Return">
</form>


</body>
<html>
