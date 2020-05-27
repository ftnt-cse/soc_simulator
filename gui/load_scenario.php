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

$scenario = $_POST['scenarioName'];
$sourceFile = "../scenarios/$scenario/scenario.json";
$targetFile = "../scenarios/my_scenarios/MyScenario/scenario.json";

if (!copy($sourceFile, $targetFile)) {
  echo "<h2>Error, Could not write $targetFile.</h2>";
} else {
  echo "<h2>Scenaio Loaded!</h2>";
}

?>

<form method="post" action="scenario_builder.php" target="main_pane">
<input type="submit" name="submit" value="Continue">
</form>

</body>
</html>

