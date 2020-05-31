<html>

<head>

<style>

body {
 font-family: monospace;
 color: cornflowerblue;
  font-size: 16px;
}

</style>


</head>
<body>


<?php 

// GET SETTINGS FROM CONFIG FILE

    $settingsFilePath = "../config.json";
    $settingsFile = fopen($settingsFilePath, "r");
    $currentSettings = json_decode(fread($settingsFile, filesize($settingsFilePath)), true);
    fclose($settingsFile);
//    var_dump($currentSettings);
    $mode = $currentSettings["GUI_mode"];
    $sshHost = $currentSettings["GUI_sshHost"];
    $sshPort = $currentSettings["GUI_sshPort"];
    $sshUser = $currentSettings["GUI_sshUser"];
    $sshPass = $currentSettings["GUI_sshPass"];

//GET STEP NUMBER FROM INDEX.PHP RUN STEP BUTTON

$step = $_POST["step"];
$scenario = $_POST['scenario_id'];

// echo "Mode : " . $mode . "<br>";

//COMMAND TO EXECUTE

echo $scenario . "<br>";

// USE THIS COMMAND TO EXECUTE THE SIMULATOR
$command = "sudo python3 ../soc_simulator.py -f scenarios/$scenario -j $step";

// USE THIS COMMAND FOR GUI TROUBLE SHOOTING
// $command = "uptime";

// CHECK ERROR FILE LOCATION WRITABLE OTHERWISE SEND TO /DEV/NULL

if(fopen("../simulator_error.log", "w")) {
  $errorFile = "../simulator_error.log";
//  fclose("../simulator_error.log");
} else {
  echo "Can't open error file location.<br>Redirect error to /dev/null.";
  $errorFile = "/dev/null";
}

// CHECK $mode AND EXECUTE COMMAND LOCALLY OR BY SSH

if($mode == "local") {

$descr = array(
  0 => array("pipe", "r"),
  1 => array("pipe", "w"),
  2 => array("file", $errorFile, "w")
);

$pipes = array();

$process = proc_open($command, $descr, $pipes);

// fwrite($pipes[0], "y"); 
// fclose($pipes[0])u// echo stream_get_contents($pipes[1]);
// echo stream_get_contents($pipes[1]);
// fclose($pipes[1]);

if (is_resource($process)) {
  while ($f = fgets($pipes[1])) {
  echo "<p>" . $f . "</p>";
  }
  fclose($pipes[1]);
  proc_close($process);
}

} elseif ($mode == "remote") {

// IF SSH DOESNT WORK, CHECK SELINUX ISNT BLOCKING HTTPD NET ACCESS
// ENABLE WITH CLI 'setsebool -P httpd_can_network_connect 1'

$connection = ssh2_connect($sshHost, $sshPort);

ssh2_auth_password($connection, $sshUser, $sshPass);

$ssh_stream = ssh2_exec($connection, $command);

stream_set_blocking($ssh_stream, true);                                                                                                

while ($f = fgets($ssh_stream)) {
  echo "<p>Remote mode</p>";
  echo "<p>" . $f . "</p>";
}

fclose($ssh_stream);     

}

?> 

</body>
</html>
