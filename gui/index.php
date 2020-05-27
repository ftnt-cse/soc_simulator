<html>
<head>

<style>

  body {
    font-family: arial;
  }

 
  table.regularTable, table.regularTable tr, table.regularTable td { 
    border: 1px solid;
    border-collapse: collapse;
    padding: 5px; 
  }
   

.button {
  background-color: dimgrey;
  color: white;
  font-size: 16px;
  font-weight: bold;
  border: 5px solid lightgrey;
  text-align: center;
  width: 100%;
  padding: 10px 20px;
  white-space: normal;		<!-- THIS ALLOWS WORD WRAP ON BUTTON --> 
}

.activeButton {
  background-color: dimgrey;
  color: white;
  font-size: 16px;
  font-weight: bold;
  border: 5px solid orange;
  text-align: center;
  width: 100%;
  padding: 10px 20px;

}
.header {
  text-align: center;
  padding: 10px;
  background-color: lightgrey;

}

.container {
  display: flex;
  flex-direction: row;
}


.topMenu {
  background: lightgrey;
  display: flex;
  justify-content: center;
}

.sideMenu {
  width: 250;
  padding: 20px;
  background: lightgrey;
  display: inline-block;
}

.scenario {
  width: 100%; 
  padding-top: 45%;		/* this is important, it sets the aspect ratio of the iframe */
  position: relative;
}

.scenario iframe {
  border: none;
  width: 100%;
  left: 0;
  position: absolute;
  top: 0;
  height: 100%;
}

.steps {
  padding: 20px;
}

</style>

</head>
<body>

<div class="header">
  <h1>Alert Simulator</h1>
</div>

<div class="topMenu">

 <?php

    // BUILD TOP MENU BUTTONS FROM SCENARIOS FOLDER

    $files1 = array_slice(scandir("../scenarios/"), 2);

    foreach ($files1 as $value1) {
        if (is_dir('../scenarios/' . $value1 )) {
          if ($_POST['scenario_folder'] == $value1) {		// HIGHLIGHTS ACTIVE BUTTON BY CHANGING CSS CLASS 
?> 
           <form action="" method="post">
              <input type="hidden" name="scenario_folder" value="<?php echo $value1;?>"> 
              <input type="submit" name="name" class="activeButton" value="<?php echo preg_replace('/_/', ' ', $value1); ?>">
            </form>
  <?php  
          } else {
  ?>

          <form action="" method="post">
            <input type="hidden" name="scenario_folder" value="<?php echo $value1;?>"> 
            <input type="submit" name="name" class="button" value="<?php echo preg_replace('/_/', ' ', $value1); ?>">
          </form>
  <?php
          } 
       }
    }

    if (isset($_POST['settings'])) { 
?> 

    <form action="" method="post" target="">
        <input type="hidden" name="settings" value="settings">
        <input type="submit" name="name" class="activeButton" value="Settings">
      </form>

  <?php  
          } else {
  ?>
    <form action="" method="post" target="">
        <input type="hidden" name="settings" value="settings">
        <input type="submit" name="name" class="button" value="Settings">
      </form>

  <?php
          
       }
  ?>

     </div>

<div class="container">

<div class="sideMenu">
   <?php

    if (isset($_POST['settings'])) {		// LEAVE SIDE MENU BLANK IF IN SETTINGS TAB
    ?> 
      <h2 style="text-align:center;">Settings</h2> 
    <?php  
    } else { 		// IF NOT IN SETTINGS THEN BUILD MENU
      
      ?>      
      
      <h2 style="text-align:center;">Scenarios</h2>
      
      <?php
      // BUILD SIDE MENU BUTTONS FROM SCENARIOS SUB-FOLDER USING SCENARIO_FOLDER FROM _POST SUBMISSION
        
      $scenarioGroupFolder = $_POST['scenario_folder'];
      $scenarios = array_slice(scandir("../scenarios/$scenarioGroupFolder/"), 2);
      foreach ($scenarios as $scenario) {
        if (is_dir('../scenarios/' . $scenarioGroupFolder . '/' . $scenario)) {
  ?>

          <form action="run_scenario.php" method="post" target="main_pane">
            <input type="hidden" name="run_scenario" value="run_scenario">
            <input type="hidden" name="scenario_folder" value="<?php echo $scenarioGroupFolder;?>"> 
            <input type="hidden" name="scenario_id" value="<?php echo $scenarioGroupFolder . "/" . $scenario;?>"> 
            <input type="submit" name="submit" class="button" value="<?php echo preg_replace('/_/', ' ', $scenario); ?>">
          </form>
 
  <?php
        }
    }

    echo "<br><br>";

    if ($scenarioGroupFolder == "my_scenarios") {		// IF MY SCENARIOS THEN SHOW SCENARIO BUILDER BUTTON

    ?>

      <h2 align="center">Scenario Builder</h2>
      
        <form action="" method="post" target="">
          <input type="hidden" name="scenario_folder" value="<?php echo $scenarioGroupFolder;?>"> 
          <input type="hidden" name="scenario_builder" value="scenario_builder">
          <input type="submit" name="submit" class="button" value="Scenario Builder [Beta]">
        </form>
   
    <?php
    }
    ?>
 
  <br><br>

  <?php
  }
  ?>

  <br><br>
  <p><i>(c) 2020 Fortinet<br>Mahdi Naili, Ben Britton</i></p>

</div>

<div class="scenario">

  <?php  if($_POST["run_scenario"]) {    // GET SCENARIO ID FROM SCENARIO SELECTION CHOICE
  ?>

              <iframe name="main_pane" src="run_scenario.php"></iframe>

  <?php } elseif ($_POST["scenario_builder"]) {      // ACTION IF SCENARIO BUILDER BUTTON PRESSED
   
  ?> 
              <iframe name="main_pane" src="scenario_builder.php"></iframe>

  <?php
  } elseif ($_POST["settings"]) {		// ACTION IF SETTINGS BUTTON PRESSED

  ?>

              <iframe name="main_pane" src="settings.php"></iframe>

  <?php
  } else { 		// CREATE BLANK IFRAME TO ALLOW IT TO BE POPULATED BY BUTTON PRESS
  ?>
    <iframe name="main_pane" src="">
    </iframe>
  
  <?php
  }
  ?>

</div>


</div>
</body>
</html>
