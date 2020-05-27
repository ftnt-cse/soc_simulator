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


?>

<h2>Edit Step <?php echo $step + 1; ?></h2>


<?php

  // OPEN SCENARIO FILE AND READ STEP

    $scenarioFile = fopen("$scenarioFilePath", "r");
    $currentScenario = json_decode(fread($scenarioFile, filesize($scenarioFilePath)), true);
    fclose($scenarioFile);

?>

<form method="post" action="save_step.php">

<table style="width:80%">		<!-- TABLE FOR STEP DATA -->
  <colgroup>
    <col span="1" style="width:20%">
    <col span="1" style="width:40%">
    <col span="1" style="width:40%">
  <colgroup>
  <tbody>
    <tr><td colspan="3"><b>Step Data</b></td></tr>
    <tr>
      <th>Attribute</th>
      <th>Existing Value</th>
      <th>New Value</th>
    </tr>

<?php		// READ ARRAY AND BUILD TABLE
		// NAME PREFIX WITH _1 TO DIFFERENITATE STEP DATA FROM INCIDNET DATA IN _POST

foreach ($currentScenario[$step][data][0] as $key => $i) {
?>
  <tr>
     <td><label for="<?php echo $key; ?>"><?php echo $key; ?></label></td>
     <td><?php echo $i; ?></td>
     <td><input type="text" size="50" id="<?php echo $key; ?>" name="1_<?php echo $key; ?>" value="<?php echo $i; ?>"</td>
   </tr>

<?php
}
?>

</tbody>
</table>

<br>
<table style="width:80%">			<!-- TABLE FOR INCIDENT DATA -->
  <colgroup>
    <col span="1" style="width:20%">
    <col span="1" style="width:40%">
    <col span="1" style="width:40%">
  <colgroup>

<tbody>

<tr><td colspan="3"><b>Incident Data</b></td></tr>
<?php

foreach ($currentScenario[$step][data][0][sourcedata][incident] as $key => $i) {
?>
  <tr>
     <td><label for="<?php echo $key; ?>"><?php echo $key; ?></label></td>
     <td><?php echo $i; ?></td>
     <td><input type="text" size="50" id="<?php echo $key; ?>" name="<?php echo $key; ?>" value="<?php echo $i; ?>"</td>
   </tr>

<?php
}

?>

  <tr>
    <td colspan="3">
      <input type="hidden" name="save" value="save">
      <!-- send $step and $scenariofilePath on when form is resubmitted -->
      <input type="hidden" name="scenarioFilePath" value="<?php echo $scenarioFilePath; ?>">
      <input type="hidden" name="step" value="<?php echo $step; ?>">
      <input type="submit" name="submit" value="Save">
    </td>
  </tr>
  </tbody>
</table>

</form>

</body>
<html>
