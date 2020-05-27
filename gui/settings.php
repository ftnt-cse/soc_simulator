<html>
<head>

<style>

  body {
    font-family: arial;
  }

  table, th, td {
    border: 1px solid;
    border-collapse: collapse;
    padding: 10px;
  }

  .button {
    padding: 10px 20px;
  }

</style>

</head>
<body>

<h1>Settings</h1>

<form method="post" action="save_settings.php">

<table>
  <tr>
    <th>Setting</th>
    <th>Existing Value</th>
    <th>New Setting</th>
  </tr>
 
<?php
// OPEN SETTINGS FILE AND READ

$settingsFilePath = "../config.json";
$settingsFile = fopen($settingsFilePath, "r");
$currentSettings =  json_decode(fread($settingsFile, filesize($settingsFilePath)), true);
fclose($settingsFile);

// BUILD TABLE

foreach ($currentSettings as $key => $value) {
  if (preg_match('/^GUI_mode/', $key)) {		// MATCH STEP KEYS
  ?>
    <tr>
      <td><?php echo $key; ?></td>
      <td><?php echo $value; ?></td>
      <td>
        <input type="radio" name="<?php echo $key; ?>" value="local" <?php if ($value == "local") {echo "checked";} ?>> 
        <label for="local"> local</label><br>
        <input type="radio" name="<?php echo $key; ?>" value="remote" <?php if ($value == "remote") {echo "checked";} ?>>
        <label for="remote"> remote</label>
      </td>
    </tr>
<?php     
  } else {
?>

  <tr>
    <td><?php echo $key; ?></td>
    <td><?php echo $value; ?></td>
    <td><input type="text" name="<?php echo $key; ?>" size="40" value="<?php echo $value; ?>"></td>
  </tr>

<?php
   }
  } 
?>
<tr>
  <td colspan="3">
    <p><b><i>Passwords are stored as clear text, do not enter sensitive data!</i></b></p> 
<!--  </td>
</tr>

<tr>
  <td colspan="3"> 
-->
    <input type="hidden" name="settingsFilePath" value="<?php echo $settingsFilePath; ?>">
    <input type="submit" class="button" name="submit" value="Save">
  </td>
</tr>
</table>

</form>





</body>
</html>
