<html>
<head>

<style>

  body {
    font-family: arial;
  }
 
  table, th, td {
    padding: 5px;
    border: none;
    border-collapse: collapse;
  }

   plaintable {
     padding: 0px;
    border: none;
    border-collapse: collapse;
  }

</style>

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
        <table>		<!-- table to lay out title and buttons -->
          <tr>
            <td><h3>Step <?php echo $humanReadableStep; ?></h3></td>
            <td>
              <form method="post" action="edit_step.php" target="" >  <!-- set target="step_editor" to use the iframe -->
               <input type="hidden" name="scenarioFilePath" value="<?php echo $scenarioFilePath; ?>">
               <input type="hidden" name="step" value="<?php echo $x; ?>">
               <button type="submit" name="submit">Edit Step <?php echo $humanReadableStep;?></button>
              </form>  
            </td>
            <td>
              <form method="post" action="delete_step.php" target="">
                <input type="hidden" name="scenarioFilePath" value="<?php echo $scenarioFilePath; ?>">     
                <input type="hidden" name="step" value="<?php echo $x; ?>">
                <button type="submit" name="submit">Delete Step <?php echo $humanReadableStep;?></button>
              </form>  
            </td>
            <td>   
              <form method="post" action="Insert_step.php" target="">
                <input type="hidden" name="scenarioFilePath" value="<?php echo $scenarioFilePath; ?>">
                <input type="hidden" name="step" value="<?php echo $x; ?>">
                <button type="submit" name="submit">Insert Step </button>
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
