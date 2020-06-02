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
$updateServer = $_POST['updateServer'];
$updateUser = $_POST['updateUser'];
$updatePassword = $_POST['updatePassword'];
$scenarioName = $_POST['scenarioName'];
?>

<h1>Scenario Update</h1>


<form method="post" action="">

<table>
  <tr>
    <th>Scenario Server</th>
    <td><input type="text" name="updateServer" size="40" value=""></td>
  </tr>
  <tr>
    <th>Username</th>
    <td><input type="text" name="updateUser" size="40" value=""></td>
  </tr>
  <tr>
    <th>Password</th>
    <td><input type="text" name="updatePassword" size="40" value=""></td>
  </tr>
  <tr>
    <th>Scenario Name</th>
    <td><input type="text" name="scenarioName" size="40" value="update.tar"></td>
  </tr>
  <tr>
    <th>Validate Certificate</th>
    <td><input type="checkbox" name="validateCert"></td>
  </tr>
  <tr>
    <td colspan="2">
      <input type="hidden" name="update" value="update">
      <input type="submit" class="smallButton" name="submit" value="Update">
    </td>
  </tr>
</table>

</form>

<?php
if ($_POST['update']) {

  if ($_POST['validateCert']) {		// OPTION FOR WGET CERT VALIDATION
    $command = "wget --user $updateUser --password $updatePassword -O ../scenarios/update.tar https://$updateServer/updates/{$scenarioName}"; 
    exec(escapeshellcmd($command));
  } else {
    $command = "wget --no-check-certificate --user $updateUser --password $updatePassword -O ../scenarios/update.tar https://$updateServer/updates/{$scenarioName}"; 
    exec(escapeshellcmd($command));
  }

  // NOW EXTRACT THE SCENARIOS

  $command = "tar xvf ../scenarios/update.tar -C ../scenarios/";
  exec(escapeshellcmd($command));

  echo '<a href="index.php" target="_top" style="color:orange;">Continue</a>';

}
?>

</body>
</html>
