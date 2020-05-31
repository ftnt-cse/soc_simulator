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
<body>



  <?php 
  $scenario = $_POST["scenario_id"];
  ?>

<div class="container">
<div class"scenario">

  <table width="1000" class="regularTable">
  <tr>
    <td colspan="2">
      <h2>Scenario : <?php echo $scenario; ?> </h2>
 
      <form method="post" action="load_scenario.php">
        <input type="hidden" name="scenarioName" value="<?php echo $scenario; ?>"> 
        <input type="submit" name="submit" class="smallButton" value="Customize (Overwrite existing custom scenario)">
      </form>
    </td>
  </tr>

   <?php
 
    // SET FILE PATHS
 
    $infoFilePath = "../scenarios/$scenario/info.json";
    $scenarioFilePath = "../scenarios/$scenario/scenario.json";

  // READ AND PROCESS THE SCENARIO DESCRIPTION FILE INFO.JSON TO A HTML TABLE
  // READ FILE AND PARSE TO A PHP ASSOCIATIVE ARRAYi
  
  if(file_exists($infoFilePath)) {
    $infoFile = fopen($infoFilePath, "r");
    $descriptionArray = json_decode(fread($infoFile, filesize($infoFilePath)), true);
    fclose($infoFile);

    // BUILD HTML TABLE ROWS FROM ARRAY BASED ON INFO.JSON

    foreach($descriptionArray as $x => $x_value) {
      if (is_array($descriptionArray[$x])) {  
         echo "<tr><td><b>" . $x . "</b></td><td>";
         print_r($descriptionArray[$x]); 
         echo  "</pre></td></tr>";  
      } else {
        echo "<tr><td><b>" .  $x . "</b></td><td>" . $x_value . "</td></tr>";  
      }
    }
  } else {
    echo "<tr><td>No info.json Found</tr></td>";
  }

    ?>

    <tr>
    <td colspan="2">
	
    <?php		// DISPLAY DIAGRAM
 
    if (file_exists("../scenarios/$scenario/infographics.gif")) {
    ?>
      <img src="../scenarios/<?php echo $_POST['scenario_id']; ?>/infographics.gif" width="960" height="540" align="centre">
    <?php
    } elseif (file_exists("../scenarios/$scenario/diagram.jpg")) {
    ?>
      <img src="../scenarios/<?php echo $_POST['scenario_id']; ?>/diagram.jpg" width="960" height="540" align="centre">";
    <?php
    } else {
      echo "Diagram not found";
    }
   ?> 

    </td>
    </tr>
    </table>

</div>
<div class="steps">
 

  
    <?php
    
      $scenarioFilePath = "../scenarios/$scenario/scenario.json"; 

      if ( file_exists($scenarioFilePath)) {
        $scenarioFile = fopen($scenarioFilePath, "r");
        $scenarioArray = json_decode(fread($scenarioFile, filesize($scenarioFilePath)), true);
        fclose($scenarioFile);

        // COUNT THE DATA ELEMENTS IN THE ARRAY

         $stepCount = count($scenarioArray);
      }
      ?>

      <table class="regularTable">

      <?php

      // EXTRACT THE DEMO MESSAGE FROM EACH DATA ELEMENT AND PRINT

      for ($x = 0; $x < $stepCount; $x++) {

      $humanReadableStep = $x + 1;
      echo "<tr><td><p><b>Step $humanReadableStep - " .  $scenarioArray[$x]['data'][0]['name'] . "</b></p>";
      echo "<p>" . $scenarioArray[$x]['data'][0]['demo_message'] . "<p>";

      ?>

      <form method="post" action="run_step.php" target="stepResultsFrame<?php echo $humanReadableStep; ?>">
        <input type="hidden" name="step" value="<?php echo $humanReadableStep; ?>">
        <input type="hidden" name="mode" value="<?php echo $_POST["mode"]; ?>">
        <input type="hidden" name="scenario_id" value="<?php echo $_POST["scenario_id"]; ?>">
        <button type="submit" name="executefunction" class="smallButton">Execute Step <?php echo $humanReadableStep;?></button>
      </form>

      <iframe name="stepResultsFrame<?php echo $humanReadableStep; ?>" src="" height="100" width="500" class="iframe"></iframe>

      </td></tr>

      <?php

      }		//END FOR
    

    ?>

    </table>
</div>

</body>
</html>

