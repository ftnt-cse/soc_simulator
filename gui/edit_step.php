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
		// NAME PREFIX WITH _1  _2 etc TO DIFFERENITATE NESTED ARRAYS IN _POST

foreach ($currentScenario[$step]['data'][0] as $key => $i) {
  if(!is_array($i)) {		// CHECK THIS ISNT AN ARRAY AND PRINT VAR
?>
  <tr>
     <td><label for="<?php echo $key; ?>"><?php echo $key; ?></label></td>
     <td><?php echo $i; ?></td>
     <td><input type="text" size="50" id="<?php echo $key; ?>" name="1_<?php echo $key ; ?>" value="<?php echo $i; ?>"</td>
   </tr>

<?php
  } else { 		// OTHERWISE IT IS AN ARRAY, STEP DOWN
    echo "<tr><td colspan=\"3\">$key</td></tr>";		// ADD A TITLE ROW FOR SUB ARRAY
    foreach ($currentScenario[$step]['data'][0][$key] as $key2 => $i2) {
      if(!is_array($i2)) {		// CHECK ISNT ANOTHER SUB ARRAY
?>
        <tr>
          <td><label for="<?php echo $key2; ?>"><?php echo $key2; ?></label></td>
          <td><?php echo $i2; ?></td>
          <td><input type="text" size="50" id="<?php echo $key2; ?>" name="1_<?php echo $key; ?>::<?php echo $key2; ?>" value="<?php echo $i2; ?>"</td>
        </tr>
    
<?php
      } else {
        echo "<tr><td colspan=\"3\">$key2</td></tr>";		// ADD A TITLE ROW FOR SUB ARRAY
        foreach ($currentScenario[$step]['data'][0][$key][$key2] as $key3 => $i3) {
          if(!is_array($i3)) {		// CHECK ISNT ANOTHER SUB ARRAY
?>
            <tr>
              <td><label for="<?php echo $key3; ?>"><?php echo $key3; ?></label></td>
              <td><?php echo $i3; ?></td>
              <td><input type="text" size="50" id="<?php echo $key3; ?>" name="1_<?php echo $key; ?>::<?php echo $key2; ?>::<?php echo $key3; ?>" value="<?php echo $i3; ?>"</td>
            </tr>

<?php
          } else {
            echo "<tr><td colspan=\"3\">$key3</td></tr>";		// ADD A TITLE ROW OF PREVIOUS KEY VALUE FOR SUB ARRAY
            foreach ($currentScenario[$step]['data'][0][$key][$key2][$key3] as $key4 => $i4) {
              if(!is_array($i4)) {		// CHECK ISNT ANOTHER SUB ARRAY
?>
                <tr>
                  <td><label for="<?php echo $key4; ?>"><?php echo $key4; ?></label></td>
                  <td><?php echo $i4; ?></td>
                  <td><input type="text" size="50" id="<?php echo $key4; ?>" name="1_<?php echo $key; ?>::<?php echo $key2; ?>::<?php echo $key3; ?>::<?php echo $key4; ?>" value="<?php echo $i4; ?>"</td>
                </tr>
<?php
              } else {
                echo "<tr><td colspan=\"3\">$key4</td></tr>";		// ADD A TITLE ROW OF PREVIOUS KEY VALUE FOR SUB ARRAY
                foreach ($currentScenario[$step]['data'][0][$key][$key2][$key3][$key4] as $key5 => $i5) {
                  if(!is_array($i5)) {		// CHECK ISNT ANOTHER SUB ARRAY
?>
                  <tr>
                    <td><label for="<?php echo $key5; ?>"><?php echo $key5; ?></label></td>
                    <td><?php echo $i5; ?></td>
                    <td><input type="text" size="50" id="<?php echo $key5; ?>" name="1_<?php echo $key; ?>::<?php echo $key2; ?>::<?php echo $key3; ?>::<?php echo $key4; ?>::<?php echo $key5; ?>" value="<?php echo $i5; ?>"</td>
                  </tr>
<?php
                  } else {
                     echo "<tr><td colspan=\"3\">$key5</td></tr>";		// ADD A TITLE ROW OF PREVIOUS KEY VALUE FOR SUB ARRAY
                    foreach ($currentScenario[$step]['data'][0][$key][$key2][$key3][$key4][$key5] as $key6 => $i6) {
                      if(!is_array($i6)) {		// CHECK ISNT ANOTHER SUB ARRAY
?>
                       <tr>
                        <td><label for="<?php echo $key6; ?>"><?php echo $key6; ?></label></td>
                        <td><?php echo $i6; ?></td>
                        <td><input type="text" size="50" id="<?php echo $key6; ?>" name="1_<?php echo $key; ?>::<?php echo $key2; ?>::<?php echo $key3; ?>::<?php echo $key4; ?>::<?php echo $key5; ?>::<?php echo $key6; ?>" value="<?php echo $i6; ?>"</td>
                       </tr>
<?php
                     } else {
                       echo "<tr><td colspan=\"3\">$key5</td></tr>";		// ADD A TITLE ROW OF PREVIOUS KEY VALUE FOR SUB ARRAY
                       foreach ($currentScenario[$step]['data'][0][$key][$key2][$key3][$key4][$key5] as $key6 => $i6) {
                         if(!is_array($i6)) {		// CHECK ISNT ANOTHER SUB ARRAY
?>
                           <tr>
                             <td><label for="<?php echo $key6; ?>"><?php echo $key6; ?></label></td>
                             <td><?php echo $i6; ?></td>
                             <td><input type="text" size="50" id="<?php echo $key6; ?>" name="1_<?php echo $key; ?>::<?php echo $key2; ?>::<?php echo $key3; ?>::<?php echo $key4; ?>::<?php echo $key5; ?>::<?php echo $key6; ?>" value="<?php echo $i6; ?>"</td>
                           </tr>
<?php
                         } else {
                           echo "<tr><td colspan=\"3\">$key6</td></tr>";		// ADD A TITLE ROW OF PREVIOUS KEY VALUE FOR SUB ARRAY
                           foreach ($currentScenario[$step]['data'][0][$key][$key2][$key3][$key4][$key5][$key6] as $key7 => $i7) {
                             if(!is_array($i7)) {		// CHECK ISNT ANOTHER SUB ARRAY
?>
                               <tr>
                                 <td><label for="<?php echo $key7; ?>"><?php echo $key7; ?></label></td>
                                 <td><?php echo $i7; ?></td>
                                 <td><input type="text" size="50" id="<?php echo $key7; ?>" name="1_<?php echo $key; ?>::<?php echo $key2; ?>::<?php echo $key3; ?>::<?php echo $key4; ?>::<?php echo $key5; ?>::<?php echo $key6; ?>::<?php echo $key7; ?>" value="<?php echo $i7; ?>"</td>
                               </tr>
<?php
                             } else {

                               echo "<tr><td colspan=\"3\"><b>ERROR MAXIMUM ARRAY DEPTH REACHED!!</b></td></tr>";    
                             }
                           }  
                         }
                       }
                     }
                   }
                 }
               }
             }
           }
         }
       }
     }
   }
} 
} 
?>

</tbody>
</table>

  <tr>
    <td colspan="3">
      <input type="hidden" name="save" value="save">
      <!-- send $step and $scenariofilePath on when form is resubmitted -->
      <input type="hidden" name="scenarioFilePath" value="<?php echo $scenarioFilePath; ?>">
      <input type="hidden" name="step" value="<?php echo $step; ?>">
      <input type="submit" name="submit" value="Save" class="smallButton">
    </td>
  </tr>
  </tbody>
</table>

</form>

</body>
<html>
