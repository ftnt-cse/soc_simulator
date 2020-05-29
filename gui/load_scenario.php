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

$scenario = $_POST['scenarioName'];
$sourceFile = "../scenarios/$scenario/scenario.json";
$targetFile = "../scenarios/my_scenarios/MyScenario/scenario.json";

if (!($_POST['confirm'] or $_POST['cancel'])) {

?>

<h2>Warning! This will overwrite the existing custom scenario!</h2>
<p>Check the box to confirm</p>

  <form method="post" action="" target="main_pane" >
     <input type="hidden" name="scenarioName" value="<?php echo $scenario; ?>">
     <br>
     <input type="checkbox" name="confirm" value="confirm">	
     <label for="confirm">Confirm</label>
     <br>
     <input type="checkbox" name="cancel" value="cancel">
     <label for="cancel">Cancel</label>
     <br><br>
     <input type="submit" name="submit" value="Continue" class="smallButton">   
  </form>

<br>

<?php
}

if ($_POST['confirm']) {
  if (!copy($sourceFile, $targetFile)) {
    echo "<h2>Error, Could not write $targetFile.</h2>";
  } else {
?>
  <h2>Save successful</h2>
  <form method="post" action="index.php" target="_top">
    <input type="hidden" name="scenario_folder" value="my_scenarios">		<!-- HIDDEN VALUES TO SET SCENARIO BUILDER PAGE WHEN RELOADING INDEX.PHP -->
    <input type="hidden" name="scenario_builder" value="scenario_builder">
  <input type="submit" name="submit" value="Continue" class="smallButton">
  </form>

<?php
  }
} elseif ($_POST['cancel']) {
?>

  <h2>Cancelled!</h2>

  <form method="post" action="index.php" target="_top">
    <input type="hidden" name="scenario_folder" value="my_scenarios">	<!--	 HIDDEN VALUES TO SET SCENARIO BUILDER PAGE WHEN RELOADING INDEX.PHP -->
    <input type="hidden" name="scenario_builder" value="scenario_builder"> 
  <input type="submit" name="submit" value="Continue" class="smallButton" >
  </form>
<?php
}
?>

</body>
</html>

