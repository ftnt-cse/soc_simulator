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

<h2>Scenario Builder</h2>

<hr>

<?php
    $scenarioFileName = "scenario.json";
    $scenarioFolder = "../scenarios/my_scenarios/MyScenario";
    $scenarioFilePath = $scenarioFolder . "/" . $scenarioFileName;
    $scenarioFile = fopen("$scenarioFilePath", "r");
    $currentScenario = json_decode(fread($scenarioFile, filesize($scenarioFilePath)), true);
    fclose($scenarioFile);

    $stepCount = count($currentScenario);
    echo "<b>Scenario File : </b>" . $scenarioFilePath . "<hr>";
    
    ?>
    
    <?php
    
    for ($x = 0; $x < $stepCount; $x++) {
      $humanReadableStep = $x + 1;
      ?>
        <table class="noborder">		<!-- table to lay out title and buttons -->
          <tr>
            <td><h3>Step <?php echo $humanReadableStep; ?></h3></td>
            <td>
              <form method="post" action="edit_step.php" target="" >  <!-- set target="step_editor" to use the iframe -->
               <input type="hidden" name="scenarioFilePath" value="<?php echo $scenarioFilePath; ?>">
               <input type="hidden" name="step" value="<?php echo $x; ?>">
               <button type="submit" name="submit" class="smallButton">Edit Step <?php echo $humanReadableStep;?></button>
              </form>  
            </td>
            <td>
              <form method="post" action="delete_step.php" target="">
                <input type="hidden" name="scenarioFilePath" value="<?php echo $scenarioFilePath; ?>">     
                <input type="hidden" name="step" value="<?php echo $x; ?>">
                <button type="submit" name="submit" class="smallButton">Delete Step <?php echo $humanReadableStep;?></button>
              </form>  
            </td>
            <td>   
              <form method="post" action="Insert_step.php" target="">
                <input type="hidden" name="scenarioFilePath" value="<?php echo $scenarioFilePath; ?>">
                <input type="hidden" name="step" value="<?php echo $x; ?>">
                <button type="submit" name="submit" class="smallButton">Insert Step </button>
              </form>  
            </td>
          </tr>
        </table>

      <?php
 
        echo "<pre>";
    //    print_r ($currentScenario[$x][data][0]);
        print_r ($currentScenario[$x]);
        echo "</pre><hr>";
    }

      ?>

</body>
</html>
